.. Copyright (C) 2019, Nokia

Running and developing Robot framework tests
============================================

To run tests, please first create variable as described in
*examplehosts.py*. Then, execute::

   # tox -e robottests -- -V myhosts.py

For development, use *HOST1* and *HOST2* hosts and make sure
that your change work at least in some Linux systems.

Homma: Halutaan saada CI sellaiseen kuntoon, että yksikötestit ajaa travis automaattisesti kontissa.
Näin ei tarvitse luoda uusia vm-ympäristöjä manuaalisesti ja CI pysyy yhtenäisempänä.
Vaiheet: Valaise itseäsi Traviksesta, mikä homma, mitä, missä, miten, ja miten.
Selvitä miten muut ovat toteuttaneet/ajatelleet tällaista operaatiota. Selvitä myös miten tox ja travis
pelaa yhteen, sekä miten python testaus on yleensä hoidettu traviksella.



Katso voiko Travis CI:llä ajaa yksikkötestejä kontissa dokkerilla
Katso onko VM:llä dockeria, voiko sitä asentaa ja miten
Katso travisin käytänteet dockereista.

Pitäisi toimia myös kuten "meidän" dockereissa.

Aja kaikki muut robotscriptit paitsi ne, joissa verrataan remotescriptiä ja remoterunneria
Korjaa remotescript ja remoterunner.

