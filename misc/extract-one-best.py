import sys

id = -1
for line in open(sys.argv[1]):
    fs = line.strip().split('|||')
    sntid = fs[0].strip()
    if sntid != id:
        print fs[1].strip()
        id = sntid
