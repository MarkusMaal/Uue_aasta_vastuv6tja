#!/bin/sh
PIP3=$(which pip3) && echo "Leidsime pip3 asukohas $PIP3" || echo "Python3 ja Pip3 pole arvutisse paigaldatud! Serveri laadimiseks on vaja Python3 installida"
$PIP3 install flask mutagen waitress && echo "Valmis." || echo "Ilmnes viga. Veakood tagastati."
