#!/usr/bin/env python3
# Copyright (c) 2015-2016 The Bitcoin Core developers
# Copyright (c) 2021 The Dogecoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from test_framework.mininode import *
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
import time
from test_framework.blocktools import create_block, create_coinbase, create_transaction

'''
AcceptBlockTest -- test processing of unrequested blocks.

Since behavior differs when receiving unrequested blocks from whitelisted peers
versus non-whitelisted peers, this tests the behavior of both (effectively two
separate tests running in parallel).

Setup: two nodes, node0 and node1, not connected to each other.  Node0 does not
whitelist localhost, but node1 does. They will each be on their own chain for
this test.

We have one NodeConn connection to each, test_node and white_node respectively.

The test:
1. Generate one block on each node, to leave IBD.

2. Mine a new block on each tip, and deliver to each node from node's peer.
   The tip should advance.

3. Mine a block that forks the previous block, and deliver to each node from
   corresponding peer.
   Node0 should not process this block (just accept the header), because it is
   unrequested and doesn't have more work than the tip.
   Node1 should process because this is coming from a whitelisted peer.

4. Send another block that builds on the forking block.
   Node0 should process this block but be stuck on the shorter chain, because
   it's missing an intermediate block.
   Node1 should reorg to this longer chain.

4b.Send 1440 more blocks on the longer chain.
   Node0 should process all but the last block (too far ahead in height).
   Send all headers to Node1, and then send the last block in that chain.
   Node1 should accept the block because it's coming from a whitelisted peer.

5. Send a duplicate of the block in #3 to Node0.
   Node0 should not process the block because it is unrequested, and stay on
   the shorter chain.

6. Send Node0 an inv for the height 3 block produced in #4 above.
   Node0 should figure out that Node0 has the missing height 2 block and send a
   getdata.

7. Send Node0 the missing block again.
   Node0 should process and the tip should advance.

8. Create a fork which is invalid at a height longer than the current chain
   (ie to which the node will try to reorg) but which has headers built on top
   of the invalid block. Check that we get disconnected if we send more headers
   on the chain the node now knows to be invalid.

9. Test Node1 is able to sync when connected to node0 (which should have sufficient
   work on its chain).
'''

# TestNode: bare-bones "peer".  Used mostly as a conduit for a test to sending
# p2p messages to a node, generating the messages in the main testing logic.
class TestNode(NodeConnCB):
    def __init__(self, timeout_factor=1):
        NodeConnCB.__init__(self)
        self.connection = None
        self.ping_counter = 1
        self.last_pong = msg_pong()

    def add_connection(self, conn):
        self.has_been_disconnected = False
        self.connection = conn

    # Track the last getdata message we receive (used in the test)
    def on_getdata(self, conn, message):
        self.last_getdata = message

    # Spin until verack message is received from the node.
    # We use this to signal that our test can begin. This
    # is called from the testing thread, so it needs to acquire
    # the global lock.
    def wait_for_verack(self):
        while True:
            with mininode_lock:
                if self.verack_received:
                    return
            time.sleep(0.05)

    # Wrapper for the NodeConn's send_message function
    def send_message(self, message):
        self.connection.send_message(message)

    def on_pong(self, conn, message):
        self.last_pong = message

    # Sync up with the node after delivery of a block
    def sync_with_ping(self, timeout=30):
        self.connection.send_message(msg_ping(nonce=self.ping_counter))
        received_pong = False
        sleep_time = 0.05
        while not received_pong and timeout > 0:
            time.sleep(sleep_time)
            timeout -= sleep_time
            with mininode_lock:
                if self.last_pong.nonce == self.ping_counter:
                    received_pong = True
        self.ping_counter += 1
        return received_pong

    # wait for the socket to be in a closed state
    def wait_for_disconnect(self, timeout=60):
        if self.connection == None:
            return True
        sleep_time = 0.05
        is_closed = self.connection.state == "closed"
        while not is_closed and timeout > 0:
            time.sleep(sleep_time)
            timeout -= sleep_time
            is_closed = self.connection.state == "closed"
        return is_closed

class AcceptBlockTest(BitcoinTestFramework):
    def add_options(self, parser):
        parser.add_option("--testbinary", dest="testbinary",
                          default=os.getenv("TRUMPOWD", "trumpowd"),
                          help="trumpowd binary to test")

    def __init__(self):
        super().__init__()
        self.setup_clean_chain = True
        self.num_nodes = 2

    def setup_network(self):
        # Node0 will be used to test behavior of processing unrequested blocks
        # from peers which are not whitelisted, while Node1 will be used for
        # the whitelisted case.
        self.nodes = []
        self.nodes.append(start_node(0, self.options.tmpdir, ["-debug"],
                                     binary=self.options.testbinary))
        self.nodes.append(start_node(1, self.options.tmpdir,
                                     ["-debug", "-whitelist=127.0.0.1"],
                                     binary=self.options.testbinary))

    def run_test(self):
        # Setup the p2p connections and start up the network thread.
        test_node = TestNode()   # connects to node0 (not whitelisted)
        white_node = TestNode()  # connects to node1 (whitelisted)

        connections = []
        connections.append(NodeConn('127.0.0.1', p2p_port(0), self.nodes[0], test_node))
        connections.append(NodeConn('127.0.0.1', p2p_port(1), self.nodes[1], white_node))
        test_node.add_connection(connections[0])
        white_node.add_connection(connections[1])

        NetworkThread().start() # Start up network handling in another thread

        # Test logic begins here
        test_node.wait_for_verack()
        white_node.wait_for_verack()

        # 1. Have both nodes mine a block (leave IBD)
        [ n.generate(1) for n in self.nodes ]
        tips = [ int("0x" + n.getbestblockhash(), 0) for n in self.nodes ]

        # 2. Send one block that builds on each tip.
        # This should be accepted.
        blocks_h2 = []  # the height 2 blocks on each node's chain
        block_time = int(time.time()) + 1
        for i in range(2):
            blocks_h2.append(create_block(tips[i], create_coinbase(2), block_time))
            blocks_h2[i].solve()
            block_time += 1
        test_node.send_message(msg_block(blocks_h2[0]))
        white_node.send_message(msg_block(blocks_h2[1]))

        [ x.sync_with_ping() for x in [test_node, white_node] ]
        assert_equal(self.nodes[0].getblockcount(), 2)
        assert_equal(self.nodes[1].getblockcount(), 2)
        print("First height 2 block accepted by both nodes")

        # 3. Send another block that builds on the original tip.
        blocks_h2f = []  # Blocks at height 2 that fork off the main chain
        for i in range(2):
            blocks_h2f.append(create_block(tips[i], create_coinbase(2), blocks_h2[i].nTime+1))
            blocks_h2f[i].solve()
        test_node.send_message(msg_block(blocks_h2f[0]))
        white_node.send_message(msg_block(blocks_h2f[1]))

        [ x.sync_with_ping() for x in [test_node, white_node] ]
        for x in self.nodes[0].getchaintips():
            if x['hash'] == blocks_h2f[0].hash:
                assert_equal(x['status'], "headers-only")

        for x in self.nodes[1].getchaintips():
            if x['hash'] == blocks_h2f[1].hash:
                assert_equal(x['status'], "valid-headers")

        print("Second height 2 block accepted only from whitelisted peer")

        # 4. Now send another block that builds on the forking chain.
        blocks_h3 = []
        for i in range(2):
            blocks_h3.append(create_block(blocks_h2f[i].sha256, create_coinbase(3), blocks_h2f[i].nTime+1))
            blocks_h3[i].solve()
        test_node.send_message(msg_block(blocks_h3[0]))
        white_node.send_message(msg_block(blocks_h3[1]))

        [ x.sync_with_ping() for x in [test_node, white_node] ]
        # Since the earlier block was not processed by node0, the new block
        # can't be fully validated.
        for x in self.nodes[0].getchaintips():
            if x['hash'] == blocks_h3[0].hash:
                assert_equal(x['status'], "headers-only")

        # But this block should be accepted by node0 since it has more work.
        self.nodes[0].getblock(blocks_h3[0].hash)
        print("Unrequested more-work block accepted from non-whitelisted peer")

        # Node1 should have accepted and reorged.
        assert_equal(self.nodes[1].getblockcount(), 3)
        print("Successfully reorged to length 3 chain from whitelisted peer")

        # 4b. Now mine 1440 more blocks and deliver; all should be processed but
        # the last (height-too-high) on node0.  Node1 should process the tip if
        # we give it the headers chain leading to the tip.
        tips = blocks_h3
        headers_message = msg_headers()
        all_blocks = []   # node0's blocks
        for j in range(2):
            for i in range(1440):
                next_block = create_block(tips[j].sha256, create_coinbase(i + 4), tips[j].nTime+1)
                next_block.solve()
                if j==0:
                    test_node.send_message(msg_block(next_block))
                    all_blocks.append(next_block)
                else:
                    headers_message.headers.append(CBlockHeader(next_block))
                tips[j] = next_block

        time.sleep(2)
        # Blocks 1-1439 should be accepted, block 1440 should be ignored because it's too far ahead
        for x in all_blocks[:-1]:
            self.nodes[0].getblock(x.hash)
        assert_raises_jsonrpc(-1, "Block not found on disk", self.nodes[0].getblock, all_blocks[-1].hash)

        headers_message.headers.pop() # Ensure the last block is unrequested
        white_node.send_message(headers_message) # Send headers leading to tip
        white_node.send_message(msg_block(tips[1]))  # Now deliver the tip
        white_node.sync_with_ping()
        self.nodes[1].getblock(tips[1].hash)
        print("Unrequested block far ahead of tip accepted from whitelisted peer")

        # 5. Test handling of unrequested block on the node that didn't process
        # Should still not be processed (even though it has a child that has more
        # work).
        test_node.send_message(msg_block(blocks_h2f[0]))

        # Here, if the sleep is too short, the test could falsely succeed (if the
        # node hasn't processed the block by the time the sleep returns, and then
        # the node processes it and incorrectly advances the tip).
        # But this would be caught later on, when we verify that an inv triggers
        # a getdata request for this block.
        test_node.sync_with_ping()
        assert_equal(self.nodes[0].getblockcount(), 2)
        print("Unrequested block that would complete more-work chain was ignored")

        # 6. Try to get node to request the missing block.
        # Poke the node with an inv for block at height 3 and see if that
        # triggers a getdata on block 2 (it should if block 2 is missing).
        with mininode_lock:
            # Clear state so we can check the getdata request
            test_node.last_getdata = None
            test_node.send_message(msg_inv([CInv(2, blocks_h3[0].sha256)]))

        test_node.sync_with_ping()
        with mininode_lock:
            getdata = test_node.last_getdata

        # Check that the getdata includes the right block
        assert_equal(getdata.inv[0].hash, blocks_h2f[0].sha256)
        print("Inv at tip triggered getdata for unprocessed block")

        # 7. Send the missing block for the third time (now it is requested)
        test_node.send_message(msg_block(blocks_h2f[0]))

        test_node.sync_with_ping()
        assert_equal(self.nodes[0].getblockcount(), 1442)
        self.nodes[0].getblock(all_blocks[1438].hash)
        assert_equal(self.nodes[0].getbestblockhash(), all_blocks[1438].hash)
        assert_raises_jsonrpc(-1, "Block not found on disk", self.nodes[0].getblock, all_blocks[1439].hash)
        print("Successfully reorged to longer chain from non-whitelisted peer")

        # 8. Create a chain which is invalid at a height longer than the
        # current chain, but which has more blocks on top of that
        block_1441f = create_block(all_blocks[1436].sha256, create_coinbase(1441), all_blocks[1436].nTime+1)
        block_1441f.solve()
        block_1442f = create_block(block_1441f.sha256, create_coinbase(1440), block_1441f.nTime+1)
        block_1442f.solve()
        block_1443 = create_block(block_1442f.sha256, create_coinbase(1441), block_1442f.nTime+1)
        # block_1443 spends a coinbase below maturity!
        block_1443.vtx.append(create_transaction(block_1442f.vtx[0], 0, b"42", 1))
        block_1443.hashMerkleRoot = block_1443.calc_merkle_root()
        block_1443.solve()
        block_1444 = create_block(block_1443.sha256, create_coinbase(1444), block_1443.nTime+1)
        block_1444.solve()

        # Now send all the headers on the chain and enough blocks to trigger reorg
        headers_message = msg_headers()
        headers_message.headers.append(CBlockHeader(block_1441f))
        headers_message.headers.append(CBlockHeader(block_1442f))
        headers_message.headers.append(CBlockHeader(block_1443))
        headers_message.headers.append(CBlockHeader(block_1444))
        test_node.send_message(headers_message)

        test_node.sync_with_ping()
        tip_entry_found = False
        for x in self.nodes[0].getchaintips():
            if x['hash'] == block_1444.hash:
                assert_equal(x['status'], "headers-only")
                tip_entry_found = True
        assert(tip_entry_found)
        assert_raises_jsonrpc(-1, "Block not found on disk", self.nodes[0].getblock, block_1444.hash)

        test_node.send_message(msg_block(block_1441f))
        test_node.send_message(msg_block(block_1442f))

        test_node.sync_with_ping()
        self.nodes[0].getblock(block_1441f.hash)
        self.nodes[0].getblock(block_1442f.hash)

        test_node.send_message(msg_block(block_1443))

        # At this point we've sent an obviously-bogus block,
        # and we must get disconnected
        assert_equal(test_node.wait_for_disconnect(), True)
        print("Successfully got disconnected after sending an invalid block")

        # recreate our malicious node
        test_node = TestNode()   # connects to node (not whitelisted)
        connections[0] = NodeConn('127.0.0.1', p2p_port(0), self.nodes[0], test_node)
        test_node.add_connection(connections[0])
        test_node.wait_for_verack()

        # We should have failed reorg and switched back to 1442 (but have block 1443)
        assert_equal(self.nodes[0].getblockcount(), 1442)
        assert_equal(self.nodes[0].getbestblockhash(), all_blocks[1438].hash)
        assert_equal(self.nodes[0].getblock(block_1443.hash)["confirmations"], -1)

        # Now send a new header on the invalid chain, indicating we're forked
        # off, and expect to get disconnected
        block_1445 = create_block(block_1444.sha256, create_coinbase(1445), block_1444.nTime+1)
        block_1445.solve()
        headers_message = msg_headers()
        headers_message.headers.append(CBlockHeader(block_1445))
        test_node.send_message(headers_message)
        assert_equal(test_node.wait_for_disconnect(), True)
        print("Successfully got disconnected after building on an invalid block")

        # 9. Connect node1 to node0 and ensure it is able to sync
        connect_nodes(self.nodes[0], 1)
        sync_blocks([self.nodes[0], self.nodes[1]])
        print("Successfully synced nodes 1 and 0")

        [ c.disconnect_node() for c in connections ]

if __name__ == '__main__':
    AcceptBlockTest().main()
