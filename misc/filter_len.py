#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

if len(sys.argv) != 4:
    sys.stderr.write("usage: %s + input-src + input-ref + len\n"%(__file__))
    sys.exit(-1)

sent_len=int(sys.argv[3])
with open(sys.argv[1], 'r') as src, open(sys.argv[2], 'r') as ref:
    with open(sys.argv[1] + '.flt', 'w') as src_flt, open(sys.argv[2] + '.flt', 'w') as ref_flt:
        for s in src:
            s = s.strip()
            r = ref.readline().strip()
            fs = s.split()
            if len(fs) >= sent_len:
                src_flt.write(s + '\n')
                ref_flt.write(r + '\n')

