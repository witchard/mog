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

function run_test_prepost {
  $4
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
	$5
	exit 1
  fi
  $5
}

run_test "markdown" "./mog -nf README.md" "pygmentize README.md"

run_test "pygments extension" "./mog -n helloworld.py" "pygmentize -l python helloworld.py"

run_test "pygments mime" "./mog -n helloworld" "pygmentize -l python helloworld"

if [ `uname` != 'Darwin' ]
then
  run_test "elf" "./mog -n /bin/cat" "objdump -ft /bin/cat"
fi

if [ `uname` == 'Darwin' ]
then
  run_test "filesystem" "./mog -n mog.gif" "ls -lh mog.gif"
else
  run_test "filesystem" "./mog -n mog.gif" "ls -lh mog.gif --color=always"
fi

run_test "image" "./mog -nf mog.gif" "mediainfo `python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' mog.gif`"

run_test_prepost "tar" "./mog -n foo.tar" "tar --list -f foo.tar" "tar cf foo.tar hello*" "rm foo.tar"

run_test "csv" "./mog -n data.csv" "column -xt -s, data.csv"

run_test "tsv" "./mog -n data.tsv" "column -xt data.tsv"

run_test "ascii" "./mog -n hello" "cat hello"

run_test_prepost "binary" "./mog -n foo" "xxd foo" "bash ./create_binary.sh" "rm foo"

echo "All tests passed"
