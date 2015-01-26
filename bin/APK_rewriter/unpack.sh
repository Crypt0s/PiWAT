#!/bin/bash

rm -rf out
java -jar apktool.jar d "$1" out
