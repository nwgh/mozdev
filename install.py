#!/usr/bin/env python

import difflib
import getopt
import os
import subprocess
import sys


def modify_gitconfig(local_gitconfig, expected_include):
    gitconfig_additions = ['[include]\n', '\tpath = %s\n' % (expected_include,)]
    if not os.path.exists(local_gitconfig):
        orig_gitconfig = []
    else:
        with file(local_gitconfig, 'r') as f:
            orig_gitconfig = f.readlines()

    in_include = False
    found = False
    for line in orig_gitconfig:
        if in_include:
            if line.strip() == 'path = ' + expected_include:
                found = True
                break
        elif line.strip() == '[include]':
            in_include = True

    if found:
        # No changes
        return (orig_gitconfig, orig_gitconfig)

    return (orig_gitconfig, orig_gitconfig + gitconfig_additions)


def modify_hgrc(local_hgrc, expected_include):
    hgrc_additions = ['%%include %s\n' % (expected_include,)]
    if not os.path.exists(local_hgrc):
        orig_hgrc = []
    else:
        with file(local_hgrc, 'r') as f:
            orig_hgrc = f.readlines()

    found = False
    for line in orig_hgrc:
        if line.strip() == '%include ' + expected_include:
            found = True
            break

    if found:
        return (orig_hgrc, orig_hgrc)

    return (orig_hgrc, orig_hgrc + hgrc_additions)


def modify_zshrc(local_zshrc, expected_source):
    zshrc_additions = ['source %s\n' % (expected_source,)]
    if not os.path.exists(local_zshrc):
        orig_zshrc = []
    else:
        with file(local_zshrc, 'r') as f:
            orig_zshrc = f.readlines()

    found = False
    for line in orig_zshrc:
        if line.strip() == 'source ' + expected_source:
            found = True
            break

    if found:
        return (orig_zshrc, orig_zshrc)

    return (orig_zshrc, orig_zshrc + zshrc_additions)


def maybe_update_file(path, old, new):
    if ''.join(old) == ''.join(new):
        # Nothing to do here!
        return

    filename = os.path.basename(path)

    for line in difflib.unified_diff(old, new, fromfile='%s.old' % (filename,), tofile='%s.new' % (filename,)):
        sys.stdout.write(line)

    answer = raw_input('Write changes to %s [y/N]? ' % (path,))
    if answer.strip().lower().startswith('y'):
        with file(path, 'w') as f:
            f.writelines(new)


def usage(configdir, mozdevdir):
    print >>sys.stderr, '%s [-c configdir] [-m mozdevdir]' % (sys.argv[0],)
    print >>sys.stderr, '    -c configdir    Where local config lives (default %s)' % (configdir,)
    print >>sys.stderr, '    -m mozdevdir    Where the mozdev repo lives (default %s)' % (mozdevdir,)
    sys.exit(1)


def main():
    configdir = os.path.join(os.environ['HOME'], '.local')
    mozdevdir = os.path.abspath(os.path.dirname(__file__))

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:m:')
    except:
        usage(configdir, mozdevdir)

    for o, a in opts:
        if o == '-c':
            configdir = a
        elif o == '-m':
            mozdevdir = a
        else:
            usage()

    if args:
        usage()

    if not os.path.exists(configdir):
        answer = raw_input('Config dir %s does not exist. Create it [Y/n]? ' % (configdir,))
        if not answer.strip().lower().startswith('n'):
            os.makedirs(configdir)

    if not os.path.isdir(configdir):
        print >>sys.stderr, 'Config dir %s is not a directory. Bailing.' % (configdir,)
        sys.exit(1)

    if not os.path.exists(mozdevdir) or not os.path.isdir(mozdevdir):
        print >>sys.stderr, 'mozdev dir %s does not exist or is not a directory. Bailing.' % (mozdevdir,)
        sys.exit(1)

    local_gitconfig = os.path.join(configdir, 'gitconfig')
    mozdev_gitconfig = os.path.join(mozdevdir, 'config', 'gitconfig')
    if not os.path.exists(mozdev_gitconfig):
        print >>sys.stderr, 'mozdev gitconfig %s does not exist. Skipping.' % (mozdev_gitconfig,)
    else:
        orig_gitconfig, new_gitconfig = modify_gitconfig(local_gitconfig, mozdev_gitconfig)
        maybe_update_file(local_gitconfig, orig_gitconfig, new_gitconfig)

    local_hgrc = os.path.join(configdir, 'hgrc')
    mozdev_hgrc = os.path.join(mozdevdir, 'config', 'hgrc')
    if not os.path.exists(mozdev_hgrc):
        print >>sys.stderr, 'mozdev hgrc %s does not exist. Skipping.' % (mozdev_hgrc,)
    else:
        orig_hgrc, new_hgrc = modify_hgrc(local_hgrc, mozdev_hgrc)
        maybe_update_file(local_hgrc, orig_hgrc, new_hgrc)

    local_zshrc = os.path.join(configdir, 'zshrc')
    mozdev_zshrc = os.path.join(mozdevdir, 'config', 'zshrc')
    if not os.path.exists(mozdev_zshrc):
        print >>sys.stderr, 'mozdev zshrc %s does not exist. Skipping.' % (mozdev_zshrc,)
    else:
        orig_zshrc, new_zshrc = modify_zshrc(local_zshrc, mozdev_zshrc)
        maybe_update_file(local_zshrc, orig_zshrc, new_zshrc)


if __name__ == '__main__':
    main()
