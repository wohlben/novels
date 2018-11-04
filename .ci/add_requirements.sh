#!/usr/bin/env bash

set -x

git config --global user.email droneci
git config --global user.email ci@wohlben.de

if [[ "$(git remote get-url origin)" == "https://github.com/wohlben/novels.git" ]]; then
  echo  "fixing remote"
  git remote set-url origin git@github.com:wohlben/novels.git
fi

if ! ssh-keygen -F github.com; then
  echo "importing github pubkey"
  ssh-keyscan github.com >> ~/.ssh/known_hosts
fi

if ! git diff --exit-code --name-only development.requirements requirements.txt > /dev/null; then
  echo "found new requirements, committing them"
  git add -f development.requirements requirements.txt
  git commit -m "updated requirements"
  git push origin HEAD:$DRONE_BRANCH
fi
