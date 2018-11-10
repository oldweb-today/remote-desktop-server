#!/bin/bash

if [[ -n "$PROXY_HOST" ]]; then
    # resolve to ip now, if possible
    IP=$(host $PROXY_HOST | head -n 1 | cut -d ' ' -f 4)
    if (( $? == 0 )); then
        export PROXY_HOST=$IP
        echo "IP: $IP"
    fi

    export http_proxy=http://$PROXY_HOST:$PROXY_PORT
    export https_proxy=http://$PROXY_HOST:$PROXY_PORT
fi

# Run browser here
eval "$@"

