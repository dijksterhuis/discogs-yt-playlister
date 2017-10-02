#!/bin/bash

path=$(pwd)/$0
path=${path%'build.sh'}

echo 'path: '$path

name=$(more "$path"/Dockerfile  | grep 'name=')
name=${name#*=\"}
name=${name%\" \\}

tag=$(more "$path"/Dockerfile  | grep 'version=')
tag=${tag#*=\"}
tag=${tag%\"}

echo 'building: '$name
echo 'tag: '$tag
echo 'build context: ' $(pwd)

docker build --no-cache -t $name:$tag "$path"/