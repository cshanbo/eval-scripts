#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def merge_nbest(filenames=[]):
    if len(filenames) == 0:
        return
    files = [open(filename, 'r') for filename in filenames]
    index = 0
    output = []
    for file in files:
        for line in file:
            sntid = int(line.split('|||')[0].strip())
            if len(output) <= sntid:
                output.append([line.strip()])
            else:
                output[sntid].append(line)

    for nbest in output:
        for line in nbest:
            print line.strip()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write('usage: %s + input.nbest.0 + input.nbest.1 ...\n' % __file__)
        sys.exit(-1)
    merge_nbest(sys.argv[1:])
