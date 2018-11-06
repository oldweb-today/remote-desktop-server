#!/bin/bash

CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
pushd $CURR_DIR/build-all

docker-compose build

popd
