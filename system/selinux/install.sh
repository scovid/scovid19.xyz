#!/usr/bin/env bash

# Reference:
# https://relativkreativ.at/articles/how-to-compile-a-selinux-policy-package
# https://nts.strzibny.name/allowing-nginx-to-use-a-pumaunicorn-unix-socket-with-selinux/

file=$1

if [[ -z $file || ! -f $file ]]; then
	echo "ERROR: First argument should be path to type enforcement file"
	exit 1
fi

cd $(dirname $file)

basename=$(basename $file .te)
checkmodule -M -m -o ${basename}.mod $file
semodule_package -o ${basename}.pp -m ${basename}.mod
sudo semodule -i ${basename}.pp

rm ${basename}.pp ${basename}.mod
