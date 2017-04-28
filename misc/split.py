#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re


period = '。'

def rule0(inp=''):
    inp = inp.strip()
    if '|||' not in inp and not inp.endswith(period):
        return inp.strip().replace(period, period + ' |||')
    return inp.strip()

def rule1(inp=''):
    quote = ': “'
    quote1 = '： “'
    inp = inp.strip()
    if len(inp.split()) > 50:
        return inp.replace(quote, '||| ' + quote).replace(quote1, '||| ' + quote1)
    return inp

def rule2(inp='', seg_num=3):
    if '|||' in inp or len(inp.split()) < 50:
        return inp
    fs = re.split(',|，', inp)
    f = [x.strip() for x in fs]
    if len(fs) <= seg_num:
        return inp
    else:
        return ' , '.join(f[:seg_num]) + ' , ||| ' +  ' , '.join(f[seg_num:])

def needSplit(zh='', en='', percent=0.8):
    sw = zh.split()
    tw = en.split()
    return (float(len(sw)) / len(tw) < percent or float(len(tw)) / len(sw) < percent)
    # return (len(sw) > 50 and (float(len(sw)) / len(tw) < percent or float(len(tw)) / len(sw) < percent))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('usage: cmd + input-source-sentence + translation\n')
        sys.exit(-1)

    with open(sys.argv[1], 'r') as input, open(sys.argv[2], 'r') as trans:
        for line in input:
            line = line.strip()
            tline = trans.readline().strip()
            if needSplit(line, tline):
                # step0 = rule0(line)
                # step1 = rule1(step0)
                step2 = rule2(line)
                print step2
            else:
                print line
