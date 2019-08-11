#!/bin/bash
# run_wien2k.sh
# F. Iwase
# 2019年  6月 19日 水曜日 11:26:36 JST

NAME="CCl3COI"
CDRE=`basename $(pwd)`
# 原子の移動量（Å）
P_move_s=( "0" "0.1" "0.2" "0.3" "0.4" "0.5" "0.6" )
P_rkmax_s=( "5.5" )
# 分子の回転（degree）どの原子を移動させるかなどは、rotation_template.txtで指定すること
P_angles=( "0" )
# ブリルアンゾーンにおけるk点の数
P_k_s=( "8" )

if [ -e ${CDRE}.sdf ]; then
  echo "sdf file found."
else
  echo "no sdf file. check sdf file! (sdf file name must be same with the directory name)"
  exit 1
fi
for P_k in ${P_k_s[@]}; do
for P_rkmax in ${P_rkmax_s[@]}; do
  PROJECT=${NAME}"_10A_"${P_k}"k_PBE_RKM"${P_rkmax//./_}"_len"
  echo ${PROJECT}

for P_move in ${P_move_s[@]}; do

for P_angle in ${P_angles[@]}; do
  PARANAME=`echo $P_move | sed -e 's/-/m/g' -e 's/\./_/g'`
  CASE=${PROJECT}_${PARANAME}_rot${P_angle}

  MOVE=${P_move}

  mkdir $CASE

# 原子の移動
  python3 ~/WIEN2kdata/moveatom.py ${CDRE}.sdf 7 4 $MOVE ${CASE}/${CASE}.sdf
# 分子原子の回転
# rotation.txtのR_ANGLEを編集
  sed s/R_ANGLE/${P_angle}/ ../rotation_template.txt > rotation.txt
  python3 ~/WIEN2kdata/rotatemol.py ${CASE}/${CASE}.sdf rotation.txt
# sdf→ cif
  python3 ~/WIEN2kdata/sdf2cif.py ${CASE}/${CASE}_r.sdf 10.0 10.0 10.0 ${CASE}/${CASE}.cif

  cp run_wien2k.sh ${CASE}/${CASE}.sh

  cd $CASE

# cifファイルからstructファイルへの変換 ######################################
  cif2struct ${CASE}.cif

# 計算条件の設定 #############################################################
# -b: バッチモード(Fast Mode)
# -red: RMT reduction by X %
# -vxc: VXC option (13: PBE, 5=LDA, 11=WC, 19=PBEsol)
# -ecut: energy seperation between core/valence (default: -6.0 Ry)
# -rkmax: RKMAX (default:7.0), gmax < gminになる場合は小さくする
# increase of RKmax by only 10 % increases the basis set by about 30% and the computing time by about a factor of 2 !!!!
# Proper RKmax values depend on:
# the desired accuracy for a specific property (e.g. geometry optimization of internal parameters does not need such high precision as accurate lattice parameters).
# the available computer power (both cpu-time AND memory).
# The specific atom with the smallest RMT.
# The size of the spheres. Typically the same atom converges faster with RKmax with a larger sphere.
#
# The following rough guideline applies for low-medium convergence (provided you have used the new setrmt_lapw script): 
#
# RKmax    smallest atom 
# 3.0      H
# 4.5      Li
# 5.0      Be, B, Si
# 5.5      C, P
# 6.0      N, S
# 6.5      O, Cl, Na, K, Rb, Cs, Mg, Ca, Sr, Ba, Al
# 7.0      F
# 7.5      Sc-Cr, Ga-Br, Y-Mo
# 8.0      Mn-Zn, Ru-Cd, In-I, La, Ce, Hf-Re
# 8.5       Os-At, Pr-Lu, Ac-Lr
# Note: these values may be different for your specific case. Change them by +/- 10 % to get more accurate / faster calculations. 

# -numk: X k-points in full BZ (defalt: 1000)

#init_lapw -b -red 0 -vxc 13 -ecut -6.0 -rkmax 5 -numk 8
echo P_rkmax:${P_rkmax} P_k:${P_k}
  init_lapw -b -red 0 -vxc 13 -ecut -6.0 -rkmax ${P_rkmax} -numk ${P_k}


# gmax > gmin チェック ########################################################
# ${CASE}.outputdでgmax > gminのチェック（必要かよくわからない）
  grep "gmin" ${CASE}.outputd
  grep "gmax" ${CASE}.outputd
  GMIN=`grep "gmin" ${CASE}.outputd | awk '{print $3}'`
  GMAX=`grep "gmax" ${CASE}.outputd | awk '{print $3}'`
  if [ `echo "$GMIN < $GMAX" | bc` == 1 ]; then
    echo "check gmax > gmin OK"
  else
    echo "gmax < gmin"
    echo "強制終了"
    exit 1
  fi

# scf実行 エネルギー 10**-6 Ry の精度 -ec 0.000001 ###########################
  run_lapw -ec 0.000001

# EFGモードでlapw2を実行 ######################################################
  x lapw2 -efg

# nQの計算 ####################################################################
  python3 ~/WIEN2kdata/scf2nQ.py ${CASE}.scf > ${CASE}.nQ
# total energy を追記  
  grep :ENE ${CASE}.scf | tail -n 1 >> ${CASE}.nQ

# Density of States (DOS)の計算 ###############################################
# まずpartial charges を計算する。qtlファイルが作成される
  x lapw2 -qtl
# .intファイルを作るプログラムを用意する  configure_int_lapwで自動的に作る
  configure_int_lapw -b total 1 tot,s,p,PX,PY,PZ end

# DOS を計算する.
  x tetra
  grep :RKM ${CASE}.scf | tail -n 1 >> ${CASE}.nQ
  grep :KPT ${CASE}.scf | tail -n 1 >> ${CASE}.nQ
  grep :FER ${CASE}.scf | tail -n 1 >> ${CASE}.nQ

# 電荷密度の計算 ############################################
  cp ~/WIEN2kdata/wien2k2venus.py ./
  if [ -e ${CASE}.in1 ]; then
    echo "${CASE}.in1 found."
    python wien2k2venus.py 70 70 70
  elif  [ -e ${CASE}.in1c ]; then
    echo "${CASE}.in1c found. complex option"
    python wien2k2venus.py -c 70 70 70
  else
    echo "no in1 or in1c file"
    exit 1
  fi

  echo ${CASE}"  - END "`date`"   ------------------------"
  cd ..
done
done
done
done
