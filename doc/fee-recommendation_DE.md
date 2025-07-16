Trumpow-Gebührenempfehlung
----------------------------

_zuletzt aktualisiert für 1.0.0_

Die Trumpow-Kette hat ein relativ niedrigen Blockintervall, 1 Megabyte Blockspace
und zielt darauf ab, den Leuten eine kostengünstige Möglichkeit für Transaktionen zu bieten. Daher ist Spam die größte
Bedrohung für die Trumpow-Kette als Ganzes. Trumpow verwendet eine Transaktionsgebühr
und einen Dust-Abschreckungseffekt, um On-Chain-Spam zu bekämpfen.

Trumpow Core implementiert eine Reihe von Standardeinstellungen in die Software, die die
Empfehlungen der Entwickler zu Gebühren- und Dust-Grenzen widerspiegeln, die zum Zeitpunkt der
Veröffentlichung die beste Einschätzung der Entwickler darstellen, wie diese Grenzen
parametrisiert werden sollten. Die empfohlenen Standardwerte, wie sie in der Trumpow Core-Wallet implementiert sind, sind:

- **0,01 TRMP pro Kilobyte** Transaktionsgebühr
- **0,01 TRMP** Staubgrenze (Verwerfungsschwelle)
- **0,001 TRMP** Ersetzung durch Gebühreninkremente

Die Wallet lehnt Transaktionen ab, deren Ausgaben unter der Staubgrenze liegen, und
verwirft Wechselgeld in Gebühr, wenn es unter diese Grenze fällt.

Gebühren werden über die genaue Größe einer Transaktion berechnet. Beispielsweise muss für eine 192-Byte-Transaktion nur eine TRMP-Gebühr von `0,01 / 1000 * 192 = 0,00192` gezahlt werden.

## Standardmäßige Einschlussrichtlinien für Miner

Die Standardwerte für Miner, um eine Transaktion in einen Block einzuschließen, wurden
genau auf die empfohlene Gebühr von **0,01 TRMP/kB** festgelegt. Staubgrenzen werden durch
die Mempool-Richtlinie des Miners definiert, siehe unten.

## Relay- und Mempool-Richtlinien

Die Relay- und Mempool-Akzeptanzrichtlinien sind standardmäßig niedriger als die Empfehlungen, um einen Spielraum für zukünftige Änderungen der Empfehlungen (oder Benutzerpräferenzen) zu lassen, ohne dass im Voraus eine angepasste Softwareversion erforderlich ist.
Dies vereinfacht zukünftige Richtlinienempfehlungen erheblich. Da die meisten Relay-Knoten diese Standardeinstellungen historisch nicht ändern, stellen diese oft ein absolutes Minimum dar.

### Transaktionsgebühr

Die standardmäßige Mindesttransaktionsgebühr für Relay ist auf **0,001 TRMP/kB** festgelegt,
genau ein Zehntel der empfohlenen Gebühr. Dies gibt Minern und Relay-Betreibern
aus Sicht des Spam-Managements einen 10-fachen Abwärtsspielraum, innerhalb dessen sie arbeiten können.

### Staubgrenzen

Die Mempool-Logik implementiert 2 Staubgrenzen, eine harte Staubgrenze, unter der eine Transaktion als nicht standardmäßig angesehen und abgelehnt wird, und eine weiche Staubgrenze,
die erfordert, dass die Grenze selbst zur Transaktionsgebühr hinzugefügt wird, wodurch das Ergebnis wirtschaftlich unrentabel wird.

- Das Hard Dust-Limit ist auf **0,001 TRMP** festgelegt – Ausgaben unter diesem Wert sind
ungültig und werden abgelehnt.
- Das Soft Dust-Limit ist auf **0,01 TRMP** festgelegt – beim Senden einer Transaktion mit Ausgaben
unter diesem Wert müssen für jede solche Ausgabe 0,01 TRMP hinzugefügt werden, andernfalls
wird die Gebühr als zu niedrig angesehen und abgelehnt.

### Ersetzung durch Gebühr und Mempool-Begrenzungsinkremente

Die Inkremente, die für Ersetzung durch Gebühr und Begrenzung des Mempools verwendet werden, sobald dieser
seine lokal definierte Maximalgröße erreicht hat, sind standardmäßig auf ein Zehntel
der Relay-Gebühr oder **0,0001 TRMP** festgelegt.
