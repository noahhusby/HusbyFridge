#!/bin/bash
#
# MIT License
#
# Copyright 2021 noahhusby
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

set -o errexit

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 1>&2
   exit 1
fi

#Get the checkout directory
GIT_DIR="$(realpath $(dirname ${BASH_SOURCE[0]})/..)"

#Get the owner of the checkout directory
GIT_OWNER="$(ls -ld "$GIT_DIR" | awk 'NR==1 {print $3}')"

cd "$(dirname "${BASH_SOURCE[0]}")/.."
repo_path="$PWD"


for service in systemd/*.service; do
	sed "s:/home/__USER__/HusbyFridge:${repo_path}:g;s:__USER__:${GIT_OWNER}:g" "$service" \
	 > "/lib/systemd/system/$(basename "$service")"
done
