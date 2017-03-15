#!/usr/bin/env python

from __future__ import print_function
import os
import os.path
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
try:
    from pipes import quote
except ImportError:
    from shlex import quote
import sys
import re
import subprocess
from functools import partial
import argparse
import platform

def myprint(s):
    '''
    Overriding print...
    why!? because it seems print in python3 does magic that doesn't work when we pipe through less
    '''
    try:
        if sys.version_info[0] == 3 and not hasattr(sys.stdout, 'buffer'):
            # In viewinless mode and python3... print as binary
            sys.stdout.write('{}\n'.format(s).encode('utf-8'))
        else:
            print(s)
        sys.stdout.flush()
    except IOError:
        pass

# Open dev null once
DEVNULL = open('/dev/null', 'w')

default_config_file = """; mog config file
[settings]
showname=yes
showsection=no
viewinless=no
toponly=no
toplines=10
followsymlinks=no
recursive=no

[pygments]
; Pygmentize returns 'text' when it can't highlight, so we use an inverted match for text.
invert_match=yes
pygmentize=text
arg=pygmentize

[pygmentsmime]
pygmentsmime=(.*)
argreplace=pygmentize -l '%0' %F

[elfs]
file=.*ELF
arg=objdump -ft

[filesystem]
file_mime=.*(\sinode\/|x-symlink|x-directory|x-fifo)
arg=ls -lh{}

[media]
file_mime=.*\s(video|image)\/
arg=mediainfo

[pdfs]
file=.*PDF document
argreplace=pdftotext %F -

[tarballs]
name=.*\.tar(\.gz|\.bz2|\.Z|\.xz)?$
arg=tar --list -f

[deb]
name=.*\.deb$
arg=dpkg -I

[rpm]
name=.*\.rpm$
arg=rpm -qip

[csv]
name=.*\.csv$
arg=column -xt -s,

[tsv]
name=.*\.tsv$
arg=column -xt

[ASCII]
file=.*ASCII
arg=cat

[binary]
; We assume anything thats left is binary
name=.*
arg=xxd
""".format(" --color=always" if platform.system() != "Darwin" else "")

##### Matches
def match_file(regex, name):
    tosearch = subprocess.check_output(['file', '-h', name]).decode("utf-8")
    return re.match(regex, tosearch)

def match_file_mime(regex, name):
    tosearch = subprocess.check_output(['file', '--mime', '-k', '-h', name]).decode("utf-8").split('\n')[0]
    return re.match(regex, tosearch)

def match_pygmentize(regex, name):
    tosearch = subprocess.check_output(['pygmentize', '-N', name]).decode("utf-8")
    return re.match(regex, tosearch)

def match_pygmentsmime(regex, name):
    mimetype = subprocess.check_output(['file', '-b', '-k', '-h', '--mime-type', name]).decode("utf-8").split('\n')[0].strip()
    import pygments.lexers
    try:
        tosearch = pygments.lexers.get_lexer_for_mimetype(mimetype).aliases[0]
        if tosearch == 'text':
            return None # Skip raw text
        return re.match(regex, tosearch)
    except:
        return None

def match_inverted(func, regex, name):
    return not func(regex, name)

##### Actions
def run_program(cmd):
    try:
        subprocess.check_call(cmd, shell=True, stdout=sys.stdout, stderr=DEVNULL)
    except subprocess.CalledProcessError as e:
        myprint('==> Error processing file: {} <=='.format(e))

def action_arg(action, name, match_result, suffix):
    run_program('{} {} {}'.format(action, quote(name), suffix).strip())

def action_argreplace(action, name, match_result, suffix):
    for i, val in enumerate(match_result.groups()):
        action = action.replace('%' + str(i), val)
    run_program(action.replace('%F', quote(name) + ' ' + suffix).strip())

##### Helpers
def config_get(func, value, default, section='settings'):
    try:
        return func(section, value)
    except configparser.NoSectionError:
        return default
    except configparser.NoOptionError:
        return default
    except ValueError:
        myprint("Invalid settings variable {} in section {} - should be boolean".format(value, section))
        sys.exit(1)

def create_default_config(path):
    with open(path, 'w') as cfg:
        cfg.write(default_config_file)

##### Parsing
def parse_config(cfg):
    matches = {'file': match_file,
               'file_mime': match_file_mime,
               'name': re.match,
               'pygmentize': match_pygmentize,
               'pygmentsmime': match_pygmentsmime}
    actions = {'arg': action_arg,
               'argreplace': action_argreplace}

    # Parse config
    things = configparser.RawConfigParser()
    if not os.path.exists(cfg):
        create_default_config(cfg)
    things.read(cfg)

    # Extract settings
    settings = {'showname'   : config_get(things.getboolean, 'showname', True),
                'showsection': config_get(things.getboolean, 'showsection', False),
                'viewinless' : config_get(things.getboolean, 'viewinless', False),
                'toponly'    : config_get(things.getboolean, 'toponly', False),
                'toplines'   : config_get(things.getint, 'toplines', 10),
                'followsymlinks' : config_get(things.getboolean, 'followsymlinks', False),
                'recursive'  : config_get(things.getboolean, 'recursive', False)}

    # Extract matches and actions
    things_to_do = []
    for thing in things.sections():
        # Skip settings section
        if thing == 'settings':
            continue
        # Parse others
        invert_match = config_get(things.getboolean, 'invert_match', False, thing)
        bits = things.items(thing)
        match = None
        action = None
        for bit in bits:
            if bit[0] == 'invert_match':
                pass # Handled earlier
            elif not match and bit[0] in matches.keys():
                if invert_match:
                    match = partial(match_inverted, matches[bit[0]], bit[1])
                else:
                    match = partial(matches[bit[0]], bit[1])
            elif not action and bit[0] in actions.keys():
                action = partial(actions[bit[0]], bit[1])
            else:
                myprint("Invalid config variable {} in section {}".format(bit[0], thing))
                sys.exit(1)
        if match and action:
            things_to_do.append((match, action, thing))

    if len(things_to_do) == 0:
        myprint("Please define what you want me to do in " + cfg)
    return (settings,things_to_do)

##### Running
def run_match_action(settings, things_to_do, file_name):
    suffix = ''
    if settings['toponly']:
        suffix = '| head -n {}'.format(settings['toplines'])
    for match, action, cfg_section in things_to_do:
        match_result = match(file_name)
        if match_result:
            if settings['showname']:
                msg = file_name
                if settings['showsection']:
                    msg = "{} [{}]".format(msg, cfg_section)
                myprint('==> {} <=='.format(msg))
            action(file_name, match_result, suffix)
            return
    myprint("==> Warning: don't know what to do with {} <==".format(file_name))

def run(settings, things_to_do, files):
    first = True
    for f in files:
        if first:
            first = False
        else:
            myprint('')
        try:
            run_match_action(settings, things_to_do, f)
        except Exception as e:
            myprint('==> Error: "{}" when processing file {} <=='.format(repr(e), f))

def exists_file(f):
    if os.path.lexists(f):
        return f
    else:
        raise argparse.ArgumentTypeError("can't open {}: does not exist".format(f))

def add_pre_args(parser):
    default = os.path.expanduser("~/." + os.path.basename(sys.argv[0]) + "rc")
    parser.add_argument('-c', '--config', help='config file to use, default: {}'.format(default), default=default)

def parse_pre_args():
    parser = argparse.ArgumentParser(add_help=False)
    add_pre_args(parser)
    args, _ = parser.parse_known_args()
    return args.config

def parse_args(settings):
    help_text = {'name':    {True: 'show file names before displaying file',
                             False: 'do not show file names before displaying file'},
                 'section': {True: 'show config file section that matched before displaying file',
                             False: 'do not show config file section that matched before displaying file'},
                 'less':    {True: 'send output to less',
                             False: 'do not send output to less'},
                 'top':     {True: lambda x: 'show only top n lines of file, default (just -t): {}'.format(x),
                             False: lambda x: 'show whole files instead of only top {} lines'.format(x)},
                 'follow':  {True: 'follow symlinks to display the linked file',
                             False: 'display symlinks as is'},
                 'recurse': {True: 'recurse into directories to find files to display',
                             False: 'display directories as is'}}

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', action='store_true',
            help=help_text['name'][not settings['showname']])
    parser.add_argument('-s', '--section', action='store_true',
            help=help_text['section'][not settings['showsection']])
    parser.add_argument('-l', '--less', action='store_true',
            help=help_text['less'][not settings['viewinless']])
    parser.add_argument('-t', '--top', nargs='?', const=settings['toplines'],
            help=help_text['top'][not settings['toponly']](settings['toplines']))
    parser.add_argument('-f', '--followsymlinks', action='store_true',
            help=help_text['follow'][not settings['followsymlinks']])
    parser.add_argument('-r', '--recursive', action='store_true',
            help=help_text['recurse'][not settings['recursive']])
    parser.add_argument('FILE', nargs='+', help='file(s) to process', type=exists_file)
    add_pre_args(parser)
    args = parser.parse_args()

    if args.name:
        settings['showname'] = not settings['showname']
    if args.section:
        settings['showsection'] = not settings['showsection']
    if args.less:
        settings['viewinless'] = not settings['viewinless']
    if args.top:
        settings['toponly'] = not settings['toponly']
        settings['toplines'] = args.top
    if args.followsymlinks:
        settings['followsymlinks'] = not settings['followsymlinks']
    if args.recursive:
        settings['recursive'] = not settings['recursive']

    return args.FILE

def munge_files(files, settings):
    # Note we use a set to remove duplicates when playing with symlinks
    if settings['followsymlinks']:
        files = set(filter(os.path.exists, map(os.path.realpath, files)))
    if settings['recursive']:
        newfiles = set()
        for f in files:
            if os.path.isdir(f):
                for root, dirs, newfs in os.walk(f, followlinks=settings['followsymlinks']):
                    if not settings['followsymlinks']:
                        # symlinks to dirs appear in dirs, if we aren't following them we had better add them
                        for d in dirs:
                            d = os.path.join(root, d)
                            if os.path.islink(d):
                                newfiles.add(d)
                    for newf in newfs:
                        newfile = os.path.join(root, newf)
                        if settings['followsymlinks']:
                            newfile = os.path.realpath(newfile)
                        if os.path.exists(newfile):
                            newfiles.add(newfile)
            else:
                newfiles.add(f)
        files = newfiles
    return files

def main():
    cfg = parse_pre_args()
    settings, config = parse_config(cfg)
    files = parse_args(settings)
    files = munge_files(files, settings)
    if len(config) == 0:
        sys.exit(1)
    if settings['viewinless']:
        less = subprocess.Popen(['less', '-Sr'], stdin=subprocess.PIPE)
        sys.stdout.close()
        sys.stdout = less.stdin
    else:
        less = None
    run(settings, config, files)
    try:
        sys.stdout.close()
    except BrokenPipeError:
        pass
    if less:
        less.wait()

if __name__ == "__main__":
    main()
