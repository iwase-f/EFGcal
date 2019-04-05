# -*- coding: utf-8 -*-
#EFG_OUT2nQ_WIEN2k.py
# WIEN2kのEFGデータを使って電場勾配を計算する。
# !!!基本的にこのプログラムは使用しない!!!
# !!!scf2nQ.pyを使うこと!!!
# Wien2kの case.scfから電場勾配情報を抽出するコマンドは以下。
# ここで1番目の原子のEFGを抽出している。
# grep -A16 ':EFG001' case.scf | tail -n 17 | awk 'NR==8{print $4};NR==9{print $5};NR==10{print $6}'
#20190322 F. Iwase

import re
import sys
import math
import codecs

efg_list = []

def usage():
  message = 'usage: python3 EFG_OUT2nQ_WIEN2k.py Vzz Vyy Vxx'
  print(message)
  sys.exit()

def sort_list(numbers_array):
  return sorted(numbers_array, key=abs, reverse=True)

def eigen(a,b,c):
#  cl_true = False
#  eigen_true = False
#  f = open(path, 'r', encoding='utf-8')

  #for line in f:
  #  if line.find('Cl') != -1:
  #    cl_true = True
  #  if line.find('eigenvalues') != -1:
  #    eigen_true = True
  #    continue
  #  if cl_true == True and eigen_true == True:
  #    values = re.split(" +", line.strip(" "))
  values = [a,b,c]
  efg = [float(s) for s in values[0:3]]
  
  #cl_true = False
  #eigen_true = False
  efg_list.append(sort_list(efg))

#  f.close()
  
def EFG2nQ(efg_list):
  n = 0
  # e [C]
#  ele = 1.60217662e-19
  # Planck m2 kg /C
#  planck = 6.62619e-34
  # 35Cl quadrupole moment (SI)(m2)
  # 1 barn = 1e-24 cm2
#  Q = -0.08249e-28
  # eQ/2hの値（10^-21は省略。MHzに変換済み)
  eQh = -0.9972816157083
  for eigenvalues in efg_list:
    #atomic unit of EFG 9.717362e21 V/m2 = 9.717362e17 V/cm2
    # eq [esu/cm3]
    Vzz = float(eigenvalues[0]) #* ele / ((5.2917715e-9) ** 3)
    Vyy = float(eigenvalues[1]) #* ele / ((5.2917715e-9) ** 3)
    Vxx = float(eigenvalues[2]) #* ele / ((5.2917715e-9) ** 3)
    eta = (Vxx - Vyy)/Vzz
    #nu = ele * eq * Qcl / (planck * 1000000)
    # nu [MHz] 1000000はHzをMHzにするため
    # 1 esu2 = 1 erg cm
    # nu [MHz]=eQVzz/2h=1.60217662E-19[C] -0.08249E-24 * 0.00001[m] Vzz [V/m2] /(2 * 6.62619E-34) [m2 kg/s]
    # I=3/2の場合の共鳴周波数
    nu = eQh * Vzz * math.sqrt(1+ (eta ** 2) / 3) #/ (2 * planck * 1000000)

    print("eta[" + str(n) + "] = " + str(eta))
    print("nuQ[" + str(n) + "] = " + str(nu) + ' MHz')
    print()

    n = n + 1


def main():
  args = sys.argv
  if len(args) > 5:
    usage()
  
  a = args[1]
  b = args[2]
  c = args[3] 
#  openfile(path)
  eigen(a,b,c)
  EFG2nQ(efg_list)

  
if __name__ == "__main__":
  main()

