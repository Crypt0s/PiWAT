#!/bin/bash
openssl req -config ../conf/openssl.cnf -extensions v3_ca -days 3650 -new -x509 -keyout ../certs/proxy.key -out ../certs/proxyca.crt -nodes
