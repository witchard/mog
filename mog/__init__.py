#!/usr/bin/env python

from __future__ import print_function
import os
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

default_config_file = """; mog config file
[settings]
showname=yes
showsection=no

[markdown]
name=.*\.md
arg=mdv

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
file_mime=.*\sinode\/
arg=ls -lh --color=always

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

[ASCII]
file=.*ASCII
arg=cat

[binary]
; We assume anything thats left is binary
name=.*
arg=xxd
"""

##### Matches
def match_file(regex, name):
    tosearch = subprocess.check_output(['file', name]).decode("utf-8")
    return re.match(regex, tosearch)

def match_file_mime(regex, name):
    tosearch = subprocess.check_output(['file', '--mime', name]).decode("utf-8")
    return re.match(regex, tosearch)

def match_pygmentize(regex, name):
    tosearch = subprocess.check_output(['pygmentize', '-N', name]).decode("utf-8")
    return re.match(regex, tosearch)

def match_pygmentsmime(regex, name):
    mimetype = subprocess.check_output(['file', '-b', '--mime-type', name]).decode("utf-8").strip()
    import pygments.lexers
    try:
        tosearch = pygments.lexers.get_lexer_for_mimetype(mimetype).aliases[0]
        return re.match(regex, tosearch)
    except:
        return None

def match_inverted(func, regex, name):
    return not func(regex, name)

##### Actions
def action_arg(action, name, match_result):
    os.system('{} {}'.format(action, quote(name)))

def action_argreplace(action, name, match_result):
    for i, val in enumerate(match_result.groups()):
        action = action.replace('%' + str(i), val)
    os.system(action.replace('%F', quote(name)))

##### Helpers
def config_get_bool(cfg, value, default, section='settings'):
    try:
        return cfg.getboolean(section, value)
    except configparser.NoSectionError:
        return default
    except configparser.NoOptionError:
        return default
    except ValueError:
        print("Invalid settings variable {} in section {} - should be boolean".format(value, section))
        sys.exit(1)

def flush_swallow():
    try:
        sys.stdout.flush()
    except:
        pass

def create_default_config(path):
    with open(path, 'w') as cfg:
        cfg.write(default_config_file)

##### Parsing
def parse_config():
    matches = {'file': match_file,
               'file_mime': match_file_mime,
               'name': re.match,
               'pygmentize': match_pygmentize,
               'pygmentsmime': match_pygmentsmime}
    actions = {'arg': action_arg,
               'argreplace': action_argreplace}

    # Parse config
    things = configparser.RawConfigParser()
    cfg = os.path.expanduser("~/." + os.path.basename(sys.argv[0]) + "rc")
    if not os.path.exists(cfg):
        create_default_config(cfg)
    things.read(cfg)

    # Extract settings
    settings = {'showname': config_get_bool(things, 'showname', True),
                'showsection': config_get_bool(things, 'showsection', False)}

    # Extract matches and actions
    things_to_do = []
    for thing in things.sections():
        # Skip settings section
        if thing == 'settings':
            continue
        # Parse others
        invert_match = config_get_bool(things, 'invert_match', False, thing)
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
                print("Invalid config variable {} in section {}".format(bit[0], thing))
                sys.exit(1)
        if match and action:
            things_to_do.append((match, action, thing))

    if len(things_to_do) == 0:
        print("Please define what you want me to do in " + cfg)
    return (settings,things_to_do)

##### Running
def run_match_action(settings, things_to_do, file_name):
    for match, action, cfg_section in things_to_do:
        match_result = match(file_name)
        if match_result:
            if settings['showname']:
                msg = file_name
                if settings['showsection']:
                    msg = "{} [{}]".format(msg, cfg_section)
                print('==> {} <=='.format(msg))
                flush_swallow()
            action(file_name, match_result)
            print()
            flush_swallow()
            return
    print("==> Warning: don't know what to do with {} <==".format(file_name))

def run(settings, things_to_do, files):
    for f in files:
        try:
            run_match_action(settings, things_to_do, f)
        except Exception as e:
            print('==> Error: "{}" when processing file {} <=='.format(repr(e), f))
            flush_swallow()

def main():
    settings, config = parse_config()
    if len(config) == 0:
        sys.exit(1)
    run(settings, config, sys.argv[1:])

if __name__ == "__main__":
    main()
