#!/bin/bash
$1

echo 'path: '$1

name=$(more "$1"/Dockerfile  | grep 'name=')
name=${name#*=\"}
name='dijksterhuis/'${name%\" \\}

tag=$(more "$1"/Dockerfile  | grep 'version=')
tag=${tag#*=\"}
tag=${tag%\"}

echo 'building: '$name
echo 'tag: '$tag
echo 'build context: ' $(pwd)

docker build --no-cache -t $name:$tag "$1"/