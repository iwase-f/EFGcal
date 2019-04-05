#!/bin/bash

CASE="10426"
mkdir $CASE
cd $CASE
cp ../${CASE}.sdf .

python3 ~/WIEN2kdata/sdf2cif.py ${CASE}.sdf 10 10 10 ${CASE}.cif

cif2struct ${CASE}.cif

#The following rough guideline applies for low-medium convergence (provided you have used the new setrmt_lapw script): 
#RKmax    smallest atom 
#3.0      H
#4.5      Li
#5.0      Be, B, Si
#5.5      C, P
#6.0      N, S
#6.5      O, Cl, Na, K, Rb, Cs, Mg, Ca, Sr, Ba, Al
#7.0      F
#7.5      Sc-Cr, Ga-Br, Y-Mo
#8.0      Mn-Zn, Ru-Cd, In-I, La, Ce, Hf-Re
#8.5       Os-At, Pr-Lu, Ac-Lr

# -b: バッチモード(Fast Mode)
# -red: RMT reduction by X %
# -vxc: VXC option (13: PBE)
# -ecut: energy seperation between core/valence (default: -6.0 Ry)
# -rkmax: RKMAX (default:7.0), gmax < gminになる場合は小さくする
# -numk: X k-points in full BZ (defalt: 1000)
init_lapw -b -red 0 -vxc 13 -ecut -6.0 -rkmax 5 -numk 5

# ${CASE}.outputdでgmax > gminのチェック（必要かよくわからない）
GMIN=`grep "gmin" ${CASE}.outputd | awk '{print $3}'`
GMAX=`grep "gmax" ${CASE}.outputd | awk '{print $3}'`
if [ `echo "$GMIN < $GMAX" | bc` == 1 ]; then
  echo "check gmax > gmin OK"
else
  echo "gmax < gmin"
  echo "強制終了"
  exit 1
fi

# scf実行 エネルギー 10**-6 Ry の精度
run_lapw -ec 0.000001

# EFGモードでlapw2を実行
x lapw2 -efg

# nQの計算
python3 ~/WIEN2kdata/scf2nQ.py ${CASE}.scf > nQ.txt
