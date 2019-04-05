# -*- coding: utf-8 -*-
#EFG_OUT2nQ.py
#20190107 F. Iwase

import re
import sys
import math
import codecs

efg_list = []

def usage():
  message = 'usage: python3 EFG_OUT.py file_name'
  print(message)
  sys.exit()

def sort_list(numbers_array):
  return sorted(numbers_array, key=abs, reverse=True)

#def openfile(path):
#  f = codecs.open(path, "r", "utf-8")
#  lines = f.readlines()
#  f.close()
#  return lines

def eigen(path):
  cl_true = False
  eigen_true = False
  f = open(path, 'r', encoding='utf-8')
  for line in f:
    if line.find('Cl') != -1:
      cl_true = True
    if line.find('eigenvalues') != -1:
      eigen_true = True
      continue
    if cl_true == True and eigen_true == True:
      values = re.split(" +", line.strip(" "))
      efg = [float(s) for s in values[0:3]]
      
      cl_true = False
      eigen_true = False
      efg_list.append(sort_list(efg))

  f.close()

def EFG2nQ(efg_list):
  n = 0
  # e [esu]
  ele = 4.80325e-10
  # Planck erg s
  planck = 6.62619e-27
  # 35Cl quadrupole moment (CGS)(cm2)
  # 1 barn = 1e-24 cm2
  Q = -0.08249e-24
  #Qcl = -0.08249e-24
  #Qo = -2.578e-26
  for eigenvalues in efg_list:
    #atomic unit of EFG 9.717362e21 V/m2 = 9.717362e17 V/cm2
    # eq [esu/cm3]
    eq = float(eigenvalues[0]) * ele / ((5.2917715e-9) ** 3)
    Vyy = float(eigenvalues[1]) * ele / ((5.2917715e-9) ** 3)
    Vxx = float(eigenvalues[2]) * ele / ((5.2917715e-9) ** 3)
    eta = (Vxx - Vyy)/eq
    #nu = ele * eq * Qcl / (planck * 1000000)
    # nu [MHz] 1000000はHzをMHzにするため
    # 1 esu2 = 1 erg cm
    # nu [MHz]=eQVzz/2h=1.60217662E-19[C] -0.08249E-24 * 0.00001[m] Vzz [V/m2] /(2 * 6.62619E-34) [m2 kg/s]
    # I=3/2の場合の共鳴周波数
    nu = ele * eq * Q * math.sqrt(1+ (eta ** 2) / 3) / (2 * planck * 1000000)

    print("eta[" + str(n) + "] = " + str(eta))
    print("nuQ[" + str(n) + "] = " + str(nu) + ' MHz')
    print()

    n = n + 1


def main():
  args = sys.argv
  if len(args) > 2:
    usage()
  
  path = args[1] 
#  openfile(path)
  eigen(path)
  EFG2nQ(efg_list)

  
if __name__ == "__main__":
  main()

