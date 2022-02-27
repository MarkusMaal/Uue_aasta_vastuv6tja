#!/bin/sh 
# search for Python3 and run pyserver.py
PY3=$(which python3) || echo "Python3 pole arvutisse paigaldatud! Serveri laadimiseks on vaja Python3 installida" && echo "Python3 leidi asukohast $PY3"
$PY3 pyserver.py || echo "Probleem serveri käivitamisel. Veakood tagastati."
