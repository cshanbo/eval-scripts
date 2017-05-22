#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import codecs
import io

def meth1():
    if len(sys.argv) != 9:
        sys.stderr.write('usage: %s + input.sl.sgm + plain-txt + sl + tl + add-xmlhead + output-file + site + sysid\n' % __file__)
        sys.exit(-1)

    sl = sys.argv[3]
    tl = sys.argv[4]
    site = sys.argv[7]
    sysid = sys.argv[8]
    outputfile = sys.argv[6]
    output = []

    if sys.argv[5] != '0':
        output.append('<?xml version="1.0" encoding="UTF-8"?>')
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

                    output.append('<tstset setid="%s" srclang="%s" trglang="%s">' % (setidfs[1].split('"')[1], srcl, trgl))
                except:
                    sys.stderr.write('ERROR: setid, srclang or trglang NOT SET in original file! Using given srclang and trglang!!!\n')
                    output.append('<tstset setid="%s" srclang="%s" trglang="%s">' % (setidfs[1].split('"')[1], sl, tl))
                output.append('<system site="%s" sysid="%s">' % (site, sysid))
                output.append('</system>')
            elif line.startswith('</srcset'):
                output.append(line.replace('srcset', 'tstset'))
            elif line.startswith('<seg id'):
                pl = plain.readline().strip()
                id = line.split('>')[0] + '>'
                output.append(id + pl + '</seg>')
            elif line.startswith('<doc') or line.startswith('<DOC'):
                if 'sysid=' in line:
                    sysdd = line.split('sysid')[1].split('"')[1]
                    output.append(line.replace(sysdd, sysid))
                else:
                    output.append(line[:-1] + ' sysid="%s"' % sysid + ">")
            else:
                output.append(line)
    with codecs.open(outputfile, "w", "utf-8-sig") as ofile:
        for v in output:
            ofile.write(v.strip().decode('utf-8-sig') + '\n')

if __name__ == '__main__':
    meth1()
