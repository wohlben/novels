#!/usr/bin/env bash

git config --global user.email droneci
git config --global user.email ci@wohlben.de

if [[ "$(git remote get-url origin)" == "https://github.com/wohlben/novels.git" ]]; then
  echo  "fixing remote"
  git remote set-url origin git@github.com:wohlben/novels.git
fi

if ! git diff --exit-code --name-only development.requirements requirements.txt > /dev/null; then
  echo "found new requirements, commiting them"
  git add -f development.requirements requirements.txt
  git commit -m "updated requirements"
  git push origin 
fi
