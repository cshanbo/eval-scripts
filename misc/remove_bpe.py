#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re

for line in sys.stdin:
    line = line.strip()
    snt = line.split(' ')
    output = ''
    for i in xrange(len(snt)):
        if snt[i].endswith('@@'):
            # if the following word starts with a digit, we don't remove the space key
            if i + 1 < len(snt) and (snt[i + 1][0].isdigit() or snt[i + 1][0] == '|'):
                output += snt[i].replace('@@', ' ')
            else:
                output += snt[i].replace('@@', '')
        else:
            output += snt[i] + ' '
    print output
