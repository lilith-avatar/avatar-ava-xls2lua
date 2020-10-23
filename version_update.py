#! /usr/bin/env python
# -*- coding: utf-8 -*
# description: Update other python file version
# git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import codecs
import os
import sys

__authors__ = ['Yuancheng Zhang']
__copyright__ = 'Copyright 2020, Lilith Games, Project DaVinci, Avatar Team'
__credits__ = ['Yuancheng Zhang']
__license__ = 'MIT'
__version__ = '0.1'
__maintainer__ = 'Yuancheng Zhang'
__status__ = 'Development'


def update_version(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as fin:
        lines = fin.readlines()
        with codecs.open(file_path + '.tmp', 'w', 'utf-8') as fout:
            for line in lines:
                if line.startswith('__version__'):
                    delim = '"' if '"' in line else "'"
                    old_version = line.split(delim)[1]
                    new_version = get_git_version()
                    print('%s \t%s => %s' %
                          (file_path, old_version, new_version))
                    line = "__version = '%s'\n" % (new_version)
                fout.write(line)


def get_git_version():
    version = os.popen('git describe --tags').read()
    version = version.rstrip()[:-9]
    return version


def main(argv):
    print(argv)
    for i in range(len(argv)):
        print(update_version(argv[i]))


if __name__ == '__main__':
    print(get_git_version())
    main(sys.argv[1:])
