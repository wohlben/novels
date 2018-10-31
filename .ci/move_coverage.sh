#!/usr/bin/env bash

set -x

if [[ -d /coverage/$DRONE_BRANCH ]]; then
  rm -R /coverage/$DRONE_BRANCH
fi

mv coverage /coverage/$DRONE_BRANCH
