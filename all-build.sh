#!/bin/bash

CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
pushd $CURR_DIR/

docker-compose build

popd
