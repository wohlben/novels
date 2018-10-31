#!/usr/bin/env bash

if ! git diff --exit-code --name-only development.requirements requirements.txt > /dev/null; then
  git config --global user.email droneci
  git config --global user.email ci@wohlben.de
  git add -f development.requirements requirements.txt
  git commit -m "updated requirements"
  git push origin
fi
