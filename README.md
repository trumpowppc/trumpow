<h1 align="center">
<img src="https://i.imgur.com/sSswTOM.png" alt="Trumpow" width="300"/>
<br/><br/>
TrumPOW [$TRMP]
</h1>


TrumPOW introduces an innovative world of meme-inspired cryptocurrency, blending humor with blockchain technology. It is created to bring joy, entertainment, and interaction to the crypto community. Operating on a decentralized, community-focused ecosystem, TrumPOW seeks to merge the excitement of memes with the advancements of blockchain.

Unlike all iterations before it, Trumpow is a layer 1 coin. This means there are no liquidity pools to drain, no blacklisting wallets, and no confusing smart contracts. Trumpow is a simple blockchain.

The TrumPOW software allows anyone to operate a node in the Trumpow blockchain networks and uses the Scrypt hashing method for Proof of Work. It is adapted from Dogecoin Core, Bitcoin Core, and other cryptocurrencies.

For information about the default fees used on the Trumpow network, please
refer to the [fee recommendation](doc/fee-recommendation.md).

**Website:** [trumpow.meme](https://trumpow.meme/)

## Dogecoin Differences

Trumpow is a fork of Dogecoin. For the sake of familiarity, we will attempt to keep Trumpow similar to Dogecoin.

Changes:

* Addresses start with `T` instead of `D`
* BIPS features will start block 1000
* AuxPow / Merged mining starts at block 60,000 (Chain ID: 168)
* GUI themed for Trumpow (same as DOGE)
* Coin Name    : TrumPOW
* Coin ticker  : $TRMP
* Algorithm    : Scrypt (same as DOGE)
* Block Time   : 60 seconds
* Explorer #1   : https://explorer.trumpow.meme
* Explorer #1   : https://explorer-1.trumpow.meme


## Usage 💻

To start your journey with TrumPOW, see the [installation guide](INSTALL.md) and the [getting started](doc/getting-started.md) tutorial.

The JSON-RPC API provided by TrumPOW is self-documenting and can be browsed with `trumpow-cli help`, while detailed information for each command can be viewed with `trumpow-cli help <command>`. Alternatively, see the [Bitcoin Core documentation](https://developer.bitcoin.org/reference/rpc/) - which implement a similar protocol - to get a browsable version.

&nbsp;</p>
<font face="Verdana"><b>### Block Rewards Distribution</b></font><br>

<table border="1" width="46%">
	<tr>
		<td width="250"><b>Block Range</b></td>
		<td><b>Rewards</b></td>
	</tr>
	<tr>
		<td width="250">1 - 99,999</td>
		<td>1,000,000</td>
	</tr>
	<tr>
		<td width="250">100,000 - 199,999</td>
		<td>500,000</td>
	</tr>
	<tr>
		<td width="250">200,000 - 299,999</td>
		<td>250,000</td>
	</tr>
	<tr>
		<td width="250">300,000 - 399,999</td>
		<td>125,000</td>
	</tr>
	<tr>
		<td width="250">400,000 - 499,999</td>
		<td>62,500</td>
	</tr>
	<tr>
		<td width="250">500,000 - 599,999</td>
		<td>31,250</td>
	</tr>
	<tr>
		<td width="250">600,000 - 699,999</td>
		<td>15,625</td>
	</tr>
	<tr>
		<td width="250">700,000 - unlimited supply</td>
		<td>10,000</td>
	</tr>
</table>


### Ports

TrumPOW by default uses port `33884` for peer-to-peer communication that
is needed to synchronize the "mainnet" blockchain and stay informed of new
transactions and blocks. It is strongly recommended to not
expose RPC ports to the public internet.

| Function | mainnet | testnet | regtest |
| :------- | ------: | ------: | ------: |
| P2P      |   33884 |   44884 |   18544 |
| RPC      |   33883 |   44883 |   18432 |

## Ongoing development 💻

TrumPOW is an open source and community driven software. The development
process is open and publicly visible; anyone can see, discuss and work on the
software.

Main development resources:

* [GitHub Projects](https://github.com/trumpowppc/trumpow/projects) is used to
  follow planned and in-progress work for upcoming releases.
* [GitHub Discussion](https://github.com/trumpowppc/trumpow/discussions) is used
  to discuss features, planned and unplanned, related to both the development of
  the TrumPOW software, the underlying protocols and the TRMP asset.


### Version strategy
Version numbers are following ```major.minor.patch``` semantics.

### Branches
Please use Main branch in this repository:

- **main:** Sstable, contains the latest code.

***Submit your pull requests against `main`***

## Contributing 🤝

If you find a bug or experience issues with this software, please report it
using the [issue system](https://github.com/trumpowppc/trumpow/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5Bbug%5D+).

Please see [the contribution guide](CONTRIBUTING.md) to see how you can
participate in the development of TrumPOW. There are often
[topics seeking help](https://github.com/trumpowppc/trumpow/labels/help%20wanted)
where your contributions will have high impact and get very appreciation.

## Communities 🐸

You can join the communities on different social media.
To see what's going on, meet people & discuss, find the latest meme, learn
about Trumpow, give or ask for help, to share your project.

Here are some places to visit:

* [Discord](https://discord.gg/rqtkgwsk6j)
* [Website](https://trumpow.meme/)
* [Telegram EN](https://t.me/TrumPOWEN)
* [Telegram CN](https://t.me/TrumPOWCN)
* [X](https://x.com/TrmPow)
* Explorer #1   : https://explorer.trumpow.meme
* Explorer #2   : https://explorer-1.trumpow.meme

## Future Plan

- Please check the roadmap in our website

## Frequently Asked Questions ❓

Do you have a question regarding Trumpow? An answer is perhaps already in the [FAQ](doc/FAQ.md) or the [Q&A section](https://github.com/trumpowppc/trumpow/discussions/categories/q-a) of the discussion board!

## License ⚖️
TrumPOW is released under the terms of the MIT license. See
[COPYING](COPYING) for more information or see
[opensource.org](https://opensource.org/licenses/MIT)
