#!/bin/bash

cd test

# Set mdv to use the same theme... otherwise it picks a random one
export MDV_THEME=729.8953

function run_test {
  cmp <($2) <($3)
  if [ $? -ne 0 ]
  then
    echo "Missmatch when running test $1:"
	echo
	echo "Command 1 [$2] output:"
	$2
	echo
	echo "Command 2 [$3] output:"
	$3
	exit 1
  fi
}

run_test "markdown" "./mog -nf README.md" "mdv README.md"

run_test "pygments extension" "./mog -n helloworld.py" "pygmentize -l python helloworld.py"

run_test "pygments mime" "./mog -n helloworld" "pygmentize -l python helloworld"

run_test "elf" "./mog -n /bin/cat" "objdump -ft /bin/cat"

run_test "filesystem" "./mog -n mog.gif" "ls -lh mog.gif --color=always"

run_test "image" "./mog -nf mog.gif" "mediainfo `readlink -f mog.gif`"

echo "All tests passed"
