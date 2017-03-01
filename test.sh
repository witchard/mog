#!/bin/bash

cd test

cmp <(./mog -n helloworld.py) <(pygmentize -l python helloworld.py) || exit 1

echo "All tests passed"
