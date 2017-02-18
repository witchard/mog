# `mog` 

A different take on the UNIX tool `cat`.

![example](mog.gif)

## What is this?

The man page for `cat` says that it can: concatenate files and print on the standard output. Often (at least for me) its main use is for the latter... `mog` tries to help you "print on the standard output" in a more intelligent way. For example, it can be configured to:

* Syntax highlight scripts
* Print a hex dump of binary files
* Show details of image files
* Perform `objdump` on executables
* List a directory

## Installation

The simplest way is to install via pip: `[sudo] pip install mog`. If you plan on using the default configuration file, then you will also want `poppler-utils` and `mediainfo` installed (e.g. `sudo apt install poppler-utils mediainfo`).

For the latest development version: 
* `[sudo] pip install git+https://github.com/witchard/mog`
* Or clone this repository and then run `[sudo] python ./setup.py install`

## How does it work?

`mog` reads the `$HOME/.mogrc` config file which describes a series of operations it can do in an ordered manner. Each operation has a match command and an action command. For each file you give to `mog` it will test each match command in turn, when one matches it will perform the action. A reasonably useful config file is generated when you first run it.

### Matches

Currently the following match commands are supported:

* `name=<regex>` - Check if the file name matches the regex
* `file=<regex>` - Check if the output of `file` matches the regex
* `file_mime=<regex>` - Check if the output of `file --mime` matches the regex
* `pygmentize=<regex>` - Check if the output of `pygmentize -N` matches the regex
* `pygmentsmime=<regex>` - Check if the pygments lexer for the files mimetype matches the regex. Always failes when there is no pygments lexer for the specified mimetype

Note, one can specify `invert_match`, you can use this to cause a match when the regex does not match.

### Actions

The following actions are supported:

* `arg=<program>` - Pass the file name as an argument to the program
* `argreplace=<program>` - Replace %F in `<program>` with the filename. Replace %N (where N is an integer) in `<program>` with matching capture group from match regex. Execute the result.

### Config file format

The config file is an ini style format defined as follows:

```ini
[settings]
showname=yes
showsection=no
viewinless=no

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
* `showname` - default: `True`. Show the name of each file before performing the action.
* `showsection` - default: `False`. Show config file section where match occurred next to file name. `showname` must be `True` for this to work.
* `viewinless` - default: `False`. Output everything in a pager (`less -S`).

The `invert_match` value is optional and will cause the match to be inverted - i.e. you can use this to cause a match when the regex does not match.

Matches and actions will be processed in the order found in the file.

It should be noted that `mog` uses the name of the script to determine what config file to read. So for example one can `ln -s mog feline` and then it would use the `$HOME/.felinerc` as the config file. This means you can have multiple configurations for different names.

