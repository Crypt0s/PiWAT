#!/bin/bash

# build
java -jar apktool.jar b out "$1"

# sign
java -jar signapk.jar -w testkey.x509.pem testkey.pk8 "$1" "$2"

