#! /usr/bin/env python
# -*- coding: utf-8 -*
# description: Update other python file version
# git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua

import codecs
import os
import sys

__authors__ = ['Yuancheng Zhang']
__copyright__ = 'Copyright 2020, Lilith Games, Project DaVinci, Avatar Team'
__credits__ = ['Yuancheng Zhang']
__license__ = 'MIT'
__version__ = '1.0'
__maintainer__ = 'Yuancheng Zhang'
__status__ = 'Production'


def update_version(file_path):
    tmp_file_path = file_path + '.tmp'
    with codecs.open(file_path, 'r', 'utf-8') as fin, codecs.open(tmp_file_path, 'w', 'utf-8') as fout:
        lines = fin.readlines()
        for line in lines:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                old_version = line.split(delim)[1]
                new_version = get_git_version()
                print('%s \t%s => %s' %
                      (file_path.ljust(20), old_version, new_version))
                line = "__version__ = '%s'\n" % (new_version)
            fout.write(line)
    os.remove(file_path)
    os.rename(tmp_file_path, file_path)


def get_git_version():
    version = os.popen('git describe --tags').read()
    version = version.split('-')
    if (len(version) == 3):
        version[0] = version[0] + '.' + version[1]
    return version[0]


def main(argv):
    print(argv)
    for i in range(len(argv)):
        update_version(argv[i])


if __name__ == '__main__':
    print(get_git_version())
    main(sys.argv[1:])
