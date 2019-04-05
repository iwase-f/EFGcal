# -*- coding: utf-8 -*-
#scf2nQ.py
# Wien2kの case.scfから電場勾配情報を抽出し、共鳴周波数を計算する。
# 
# 参考
# ここで1番目の原子のEFGを抽出している。
# grep -A16 ':EFG001' case.scf | tail -n 17 | awk 'NR==8{print $4};NR==9{print $5};NR==10{print $6}'
#20190329 F. Iwase

import re
import sys
import math
import codecs
import numpy as np

def usage():
  message = 'usage: python3 scf2nQ.py [sfc_file]'
  print(message)
  sys.exit()

#def sort_list(numbers_array):
#  return sorted(numbers_array, key=abs, reverse=True)

def sort_V(numbers_array):
  return numbers_array.sort(key=lambda x:x[0], reverse=True)
  #return sorted(numbers_array, reverse=True)

#def eigen(a,b,c):
#  values = [a,b,c]
#  efg = [float(s) for s in values[0:3]]
# return sort_list(efg)

def EFG2nQ(efg_list):
  # WIEN2kでは 電場勾配は V / m**2 の単位で与えられる。
  # e [C]
#  ele = 1.60217662e-19
  # Planck m2 kg /C
#  planck = 6.62619e-34
  # 35Cl quadrupole moment (SI)(m2)
  # 1 barn = 1e-24 cm2
#  Q = -0.08249e-28
  # eQ/2hの値（10^-21は省略。MHzに変換済み)
  eQh = -0.9972816157083
  #for eigenvalues in efg_list:
    #atomic unit of EFG 9.717362e21 V/m2 = 9.717362e17 V/cm2
    # eq [esu/cm3]
    #Vzz = float(eigenvalues[0]) #* ele / ((5.2917715e-9) ** 3)
    #Vyy = float(eigenvalues[1]) #* ele / ((5.2917715e-9) ** 3)
    #Vxx = float(eigenvalues[2]) #* ele / ((5.2917715e-9) ** 3)
  Vzz = efg_list[0] 
  Vyy = efg_list[1] 
  Vxx = efg_list[2]
  eta = abs(round((Vxx - Vyy)/Vzz,6))
    #nu = ele * eq * Qcl / (planck * 1000000)
    # nu [MHz] 1000000はHzをMHzにするため
    # 1 esu2 = 1 erg cm
    # nu [MHz]=eQVzz/2h=1.60217662E-19[C] -0.08249E-24 * 0.00001[m] Vzz [V/m2] /(2 * 6.62619E-34) [m2 kg/s]
    # I=3/2の場合の共鳴周波数
  nu = abs(round(eQh * Vzz * math.sqrt(1+ (eta ** 2) / 3), 6)) #/ (2 * planck * 1000000)

  #print("nuQ = " + str(nu) + ' MHz')
  #print("eta = " + str(eta))
  #print()

  return str(nu), str(eta)

def openfile(path):
  efgline=[]
  atom = []
  keta = []
  V = []
  Vxyz = ['','','']
  Vdirection = []
  count = 0
  atomn = 0
  f = codecs.open(path, 'r', 'utf-8')
  for line in f.readlines():
    word = line.strip().split()
   
    if 'ATOMNUMBER=' in line:
      atomn = int(word[1]) -1 
      if atom[atomn:atomn+1]:
        atom[atomn] = word[2]
      else:
        atom.append(word[4])
    if ':EFG' in line:

      if efgline[atomn:atomn+1]:
        efgline[atomn] = line
        keta[atomn] = word[4][-2:]
      else:
        efgline.append(line)
        keta.append(word[4][-2:])
        
      count = 1
      continue

    if count > 0 and count < 15:
      efgline[atomn] = efgline[atomn] + line
      if count == 7:
  # リストに対して要素ごとに代入するとVにも同時に反映されてしまうので、一旦Vxyz_0などにいれておく。
        Vxyz_0 = word[3]
      elif count == 8:
        Vxyz_1 = word[4]
      elif count == 9:
        Vxyz_2 = word[5]
      elif count == 11:
        direction_0 = [ word[5], word[6], word[7] ]
      elif count == 12:
        direction_1 = [ word[0], word[1], word[2] ]
      elif count == 13:
        direction_2 = [ word[0], word[1], word[2] ]
      
      count = count + 1
      continue
   
    if count == 15:
      Vxyz=[Vxyz_0,Vxyz_1,Vxyz_2]
      direction=[direction_0, direction_1, direction_2]
    
      arr_dire = np.array(direction).T.tolist()
    
      if V[atomn:atomn+1]:
        V[atomn] = Vxyz
        Vdirection[atomn] = arr_dire 
      else:
        V.append(Vxyz)
        Vdirection.append(arr_dire)

      count = 0
  f.close()
  return atomn, atom, keta, V, Vdirection

def main():
  args = sys.argv
  if len(args) != 2:
    usage()
  path = args[1]
 
  atomn, atom, keta, V, Vdirection = openfile(path)
  #print('######## EFG tensor & nuQ #############')
  print('No atom |Vzz| |Vyy| |Vxx| keta nQ[MHz] eta vec_xx_x vec_xx_y vec_xx_z vec_yy_x vec_yy_y vec_yy_z vec_zz_x vec_zz_y vec_zz_z')
  
  index = 0
  for atomb in range(atomn+1):
    Va_tmp = [abs(float(V[index][0])), Vdirection[index][0]]
    Vb_tmp = [abs(float(V[index][1])), Vdirection[index][1]]
    Vc_tmp = [abs(float(V[index][2])), Vdirection[index][2]]
    
    V_ex = [Va_tmp, Vb_tmp, Vc_tmp]

    sort_V(V_ex)

    efg_list = [V_ex[0][0], V_ex[1][0],V_ex[2][0]]
    nuQ, eta = EFG2nQ(efg_list)

    print(str(atomb+1), atom[index], V_ex[0][0], V_ex[1][0],V_ex[2][0],keta[index], nuQ, eta, V_ex[0][1][0], V_ex[0][1][1], V_ex[0][1][2],V_ex[1][1][0],V_ex[1][1][1],V_ex[1][1][2],V_ex[2][1][0],V_ex[2][1][1],V_ex[2][1][2])
    index = index + 1
  
if __name__ == "__main__":
  main()

