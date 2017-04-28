#!/bin/bash

bin=~/mt/nmt/nematus-mgpu
device=gpu1

if [ $# != 2 ]; then
    echo "$0 start end"
    exit
fi

# stage control
start=$1
end=$2

# models & data
models=../models
data=data
files=(valid)
valid=valid
mdir=exp/100-alpha-0.2-rerank/mira
ndir=exp/100-alpha-0.2-rerank/nbest
rdir=exp/100-alpha-0.2-rerank/result
sl=zh
tl=en
num_files=${#files[@]}

beamsize=100
num_process=16
gpulist="gpu4 gpu5 gpu6 gpu7"

# Generage nbest for each test set
# input: $data/$file.$sl  output: $ndir/$file.trans
if [ $start -le 1 ] && [ $end -ge 1 ];then
    [ ! -s $ndir ] && mkdir -p $ndir
    for((i=0; i<$num_files;i++));do
        pfx=${files[$i]}
        echo "THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn python \
        $bin/nematus/translate-tag.py -m $models/nmt0/model.npz -k $beamsize -n -p $num_process --alpha 0.2 --n-best \
        -i $data/$pfx.$sl -o $ndir/$pfx.nbest --gpu-list "$gpulist" --coverage &> $ndir/$pfx.nbest.log &"
        THEANO_FLAGS=mode=FAST_RUN,floatX=float32,device=$device,on_unused_input=warn python \
        $bin/nematus/translate-tag.py -m $models/nmt0/model.npz -k $beamsize -n -p $num_process --alpha 0.2 --n-best \
        -i $data/$pfx.$sl -o $ndir/$pfx.nbest --gpu-list "$gpulist" --coverage > $ndir/$pfx.nbest.log 2>&1
    done
fi

# Generate features for each test set
if [ $start -le 2 ] && [ $end -ge 2 ]; then
    echo 'STAGE 2: Generate features for each test set' 
    for f in ${files[@]}; do
        # $bin/rescore/nmtnbest2moses.pl -k nmt0 < $ndir/$f.nbest | sed "s/@@ //g" > $ndir/$f.nbest.moses
        $bin/rescore/nmtnbest2moses.pl -k nmt0 coverage < $ndir/$f.nbest | python $bin/utils/remove_bpe.py > $ndir/$f.nbest.moses
        # generate ngram feats
        $bin/rescore/feats.pl -dir $ndir -nbest $f.nbest.moses -src $data/$f.$sl -output $f.nbest.feats \
        -lms $models/lm/news.201[23456].$tl.5gram.bin -lm-orders 5 5 5 5 5 \
        -threads 20 -normalize &> $ndir/$f.feats.log 

        echo "Recase, detoken, and using mt-eval tokenization for $ndir/$f.nbest"
        python $bin/utils/nbest_proc_pre.py $ndir/$f.nbest.feats > $ndir/$f.nbest.translation
        $bin/utils/recase.sh ../models/recaser/model/moses.ini $ndir/$f.nbest.translation $ndir/$f.nbest.translation.rc
        cat $ndir/$f.nbest.translation.rc | $bin/utils/uppercase-bos.pl -l en | $bin/utils/detokenizer.perl -l en > $ndir/$f.nbest.translation.rc.final
        cat $ndir/$f.nbest.translation.rc.final | $bin/utils/escape4mteval.pl | tee $ndir/$f.nbest.escape | $bin/utils/mteval-norm-text.pl -c | python $bin/utils/nbest_proc_post.py $ndir/$f.nbest.feats.info > $ndir/$f.nbest.feats.proc
    done
fi
# adjust nmt weights
if [ $start -le 3 ] && [ $end -ge 3 ]; then
    [ ! -s $mdir ] && mkdir -p $mdir
    # for f in ${files[@]}; do sed -e "s/@@ //g" -i $ndir/$f.nbest.feats; done
    for f in ${files[@]}; do
        # sed -e "s/@@ //g" -i $ndir/$f.nbest.feats;
        cat $ndir/$f.nbest.feats.proc | python $bin/utils/remove_bpe.py > $ndir/$f.nbest.feats.tmp
        mv $ndir/$f.nbest.feats.tmp $ndir/$f.nbest.feats.proc
    done

    # cat $data/$valid.$tl | sed "s/@@ //g" > $mdir/$valid.$tl
    cat $data/$valid.$tl | python $bin/utils/remove_bpe.py > $mdir/$valid.$tl
    echo -e "[weight]\nnmt0= 0.5\ncoverage= 0.5\nt2s.l2r= 0.3\ns2t.r2l= 0.3" > $ndir/moses.ini
    $bin/rescore/kbmira.pl -nbest $ndir/$valid.nbest.feats.proc -refs $mdir/$valid.$tl \
    -ini $ndir/moses.ini -out $mdir/weights -work-dir $mdir -add-feat-names lm.0 lm.1 lm.2 lm.3 lm.4 -add-feat-weights 0.2 0.2 0.2 0.2 0.2 -kbmira-args "--iters 60" &> $mdir/mira.log &
fi
wait

# reranking
if [ $start -le 4 ] && [ $end -ge 4 ]; then
    # post proccess
    for f in ${files[@]}; do 
        cat $data/$f.$tl > $ndir/$f.$tl; 
        # sed -e "s/@@ //g" -i $ndir/$f.nbest.feats
        cat $ndir/$f.nbest.feats.proc | python $bin/utils/remove_bpe.py > $ndir/$f.nbest.feats.tmp
        mv $ndir/$f.nbest.feats.tmp $ndir/$f.nbest.feats.proc
    done
    echo "$bin/rescore/test-and-eval.pl -ini $mdir/weights -trg-lang $tl -tst-nbests $ndir/*.feats -tst-trg-xmls $ndir/*.$tl -out-dir $rdir"
    $bin/rescore/test-and-eval.pl -ini $mdir/weights -trg-lang $tl -tst-nbests $ndir/*.feats -tst-trg-xmls $ndir/*.$tl -out-dir $rdir
    
    # post process
    for f in ${files[@]}; do
        $bin/utils/concat-sent.pl $data/$f.$sl.sntID < $rdir/$f/tst >  $rdir/$f/tst.concat
        $bin/utils/recase.sh ../models/recaser/model/moses.ini $rdir/$f/tst.concat $rdir/$f/tst.concat.rc
        cat $rdir/$f/tst.concat.rc | $bin/utils/uppercase-bos.pl -l en | $bin/utils/detokenizer.perl -l en | $bin/utils/escape4mteval.pl | $bin/utils/plain2xml.pl -ms $data/$f.zh.sgm -sl zh -tl en > $rdir/$f/tst.trans.sgm
        $bin/utils/mteval-v11b.pl -c -s $data/$f.zh.sgm -r $data/$f.en.sgm -t $rdir/$f/tst.trans.sgm > $rdir/$f/sens.bleu 
    done
    head $rdir/*/*.bleu | grep "^NI|^=" -P | tee > $rdir/tc.bleu &
fi
