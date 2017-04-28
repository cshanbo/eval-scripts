bin=~/mt/nmt/nematus-mgpu/
if [ $# -ne 2 ]
then
    echo "usage: $0 + input.sgm + language"
    exit
fi

cat $1 | sed "s/&apos;/'/g" | sed "s/&amp;/\&/g" | sed "s/&lt;/</g" | sed "s/&gt;/>/g" | sed "s/&quot;/\"/g" | $bin/utils/normalize-punctuation.perl $2 > $1.wmt.sgm
