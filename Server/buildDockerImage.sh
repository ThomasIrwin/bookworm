#!/bin/zsh

cp -r ../DataModel/ src/DataModel/

docker build -t thomasirwin26/bookworm:$1 .
