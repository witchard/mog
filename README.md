# `mog` 

A different take on the UNIX tool `cat`.

![example](mog.gif)

## What is this?

The man page for `cat` says that it can: concatenate files and print on the standard output. Often (at least for me) it's main use is for the latter... `mog` tries to help you "print on the standard output" in a more intelligent way. For example, it can be configured to:

* Syntax highlight scripts
* Print a hex dump of binary files
* Show details of image files
* Perform `objdump` on executables
* List a directory

## How does it work?

`mog` reads the `$HOME/.mogrc` config file which describes a series of operations it can do in an ordered manner. Each operation has a match command and an action command. For each file you give to `mog` it will test each match command in turn, when one matches it will perform the action.

### Matches

Currently the following match commands are supported:

* `name=<regex>` - Check if the file name matches the regex
* `file=<regex>` - Check if the output of `file` matches the regex
* `pygmentize=<regex>` - Check if the output of `pygmentize -N` matches the regex

Note, one can specify `invert_match`, you can use this to cause a match when the regex does not match.

### Actions

The following actions are supported:

* `arg=<program>` - Pass the file name as an argument to the program

### Config file format

The config file is an ini style format defined as follows:

```ini
[settings]
showname=yes

[name-of-match-action-1]
match=arg
action=arg
invert_match=boolean

[name-of-match-action-2]
match=arg
action=arg
invert_match=boolean
```

The `settings` section may contain the following:
* showname - default: True. Show the name of each file before performing the action.

The `invert_match` value is optional and will cause the match to be inverted - i.e. you can use this to cause a match when the regex does not match.

You can find some examples in the example-configs directory.

Matches and actions will be processed in the order found in the file.

It should be noted that `mog` uses the name of the script to determine what config file to read. So for example one can `ln -s mog feline` and then it would use the `$HOME/.felinerc` as the config file. This means you can have multiple configurations for different names.

## Installation

Simply download the `mog` script and place it somewhere in your path. E.g:

```bash
# Get the script
mkdir $HOME/bin
cd $HOME/bin
wget https://raw.githubusercontent.com/witchard/mog/master/mog

# Get the config
cd $HOME
wget https://github.com/witchard/mog/blob/master/example-configs/mogrc -o .mogrc

# Setup path
echo '$PATH=$PATH:$HOME/bin' >> .bashrc
# logout and back in
```

