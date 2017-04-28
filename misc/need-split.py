#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def needSplit(zh='', en='', percent=0.8, length=30):
    sw = zh.split()
    tw = en.split()
    return len(sw) > length and (float(len(sw)) / len(tw) < percent or float(len(tw)) / len(sw) < percent)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.stderr.write('usage: %s + source-plain-txt + translation + percentage + length-thresh\n' % __file__)
        sys.exit(-1)

    with open(sys.argv[1]) as source, open(sys.argv[2]) as translation:
        l_num = 0
        for line in source:
            line = line.strip()
            tran = translation.readline().strip()
            if needSplit(line, tran, float(sys.argv[3]), int(sys.argv[4])):
                print l_num
            l_num += 1
