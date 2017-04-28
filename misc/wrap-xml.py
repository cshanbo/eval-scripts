#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

def meth1():
    if len(sys.argv) < 6:
        sys.stderr.write('usage: %s + input.sl.sgm + plain-txt + sl + tl + add-xmlhead + sysid [optional]\n' % __file__)
        sys.exit(-1)

    sysid = 'default-system'
    if len(sys.argv) >= 7:
        sysid = ' '.join(sys.argv[6:])

    sl = sys.argv[3]
    tl = sys.argv[4]

    if sys.argv[5] != '0':
        print '<?xml version="1.0" encoding="UTF-8"?>'
    with open(sys.argv[1], 'r') as source_sgm, open(sys.argv[2], 'r') as plain:
        for line in source_sgm:
            line = line.strip()
            if line.startswith('<srcset'):
                setidfs = line.split('setid')
                srclangfs = line.split('srclang')
                trglangfs = line.split('trglang')
                if len(setidfs) < 2:
                    sys.stderr.write('ERROR: setid NOT SET, EXIT!!!\n')
                    sys.exit(-1)
                try:
                    srcl = srclangfs[1].split('"')[1]
                    trgl = trglangfs[1].split('"')[1]
                    if srcl != sl:
                        sys.stderr.write('Source language not match: (%s and %s)\n' % (srcl, sl))
                    if trgl != tl:
                        sys.stderr.write('Target language not match: (%s and %s)\n' % (trgl, tl))

                    print '<tstset setid="%s" srclang="%s" trglang="%s">' % (setidfs[1].split('"')[1], srcl, trgl)
                except:
                    sys.stderr.write('ERROR: setid, srclang or trglang NOT SET in original file! Using given srclang and trglang!!!\n')
                    print '<tstset setid="%s" srclang="%s" trglang="%s">' % (setidfs[1].split('"')[1], sl, tl)
                print '<system site="SOGOU" sysid="%s">' % sysid
                print '</system>'
            elif line.startswith('</srcset'):
                print line.replace('srcset', 'tstset')
            elif line.startswith('<seg id'):
                pl = plain.readline().strip()
                id = line.split('>')[0] + '>'
                print id + pl + '</seg>'
            elif line.startswith('<doc'):
                sysdd = line.split('sysid')[1].split('"')[1]
                if 'sysid=' in line:
                    print line.replace(sysdd, sysid)
                else:
                    print line[:-1] + ' sysid="%s"' % sysid + ">"
            else:
                print line


if __name__ == '__main__':
    meth1()
