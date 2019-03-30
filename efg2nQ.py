# -*- coding: utf-8 -*-
# efg2nQ.py
# EFG(電場勾配テンソル)から共鳴周波数を計算する。
# 永年方程式(secular equation)を解く
# オプションはVzz Vyy Vxx 核種
# python3 efg2nQ.py Vzz Vyy Vxx nucleus
#20190327 F. Iwase
#
# secular equation 
# T. P. Das and E. L. Hahn, Nuclear Quadrupole Resonance Spectroscopy, academic press inc., (1958) p. 13.

import sympy as sp

# 四重極モーメントQ [10**-28 m2]
Qdict = {'35Cl':['3half', -8.249e-2],'37Cl':['3half',-6.5e-2],'63Cu':['3half',-0.211],'65Cu':['3half',-0.195]}

def Abefore(atom):
  # e [10**-19 C]
  ele = 1.60217662
  # Planck constant [10**-34 m2 kg /C]
  planck = 6.62619
  # ele,Q, planckで10**-13になっている。
  # Vzzが、VzzE21の桁で与えられるとし、さらにMHzの単位(10**-6)にする
  # 残りの10**2だけ補正をかけておけば計算が楽
  eQh = 100 * ele*Qdict[atom][1]/planck
  spin = Qdict[atom][0]
  # 以下の値にVzzをかければAになる
  A_before = eQh/(4*float(spin)*(2*float(spin)-1))
  #print(ele*Qdict['35Cl']/(2*planck))
  #print(eQ2h)
  
  return A_before
  # eQ/2hの値（10^-21は省略。MHzに変換済み)
  #eQ2h = -0.9972816157083

  #Ah=e*Vzz*Q/(4*spin*(2*spin -1))
  #return A

def solve_ene(spin, eta):
  E = sp.Symbol('x')
  # I = 3/2 (unit A)
  if spin == '3half':
    ene_list = [-3*(1+(eta**2)/3)**0.5, 3*(1+(eta**2)/3)**0.5]
    ene_diff = [ene_list[1] - ene_list[0]]
  # I = 5/2 (unit 2A)
  elif spin == '5half':
    ene_list = sp.solve(E**3 -7*(3+ eta**2)*E -20*(1-eta**2), E)
    ene_diff = [ene_list[2] - ene_list[1], ene_list[1] - ene_list[0]]
  # I = 7/2 (unit 3A)
  elif spin == '7half':
    ene_list = sp.solve(E**4 -42*(1+ (eta**2) / 3)*E**2 - 64 *(1-eta**2) * E + 105*(1+(eta**2)/3)**2, E)
    ene_diff = [ene_list[3] - ene_list[2], ene_list[2] - ene_list[1], ene_list[1] - ene_list[0]]
  # I = 9/2 (unit 6A)
  elif spin == '9half':
    ene_list = sp.solve(E**5 -11*(3+ (eta**2))*E**3 - 44*(1-eta**2) * E**2 + (44/3)*(3+eta**2)**2 * E + 48*(3+eta**2)*(1-eta**2), E)
    ene_diff = [ene_list[4] - ene_list[3], ene_list[3] - ene_list[2], ene_list[2] - ene_list[1], ene_list[1] - ene_list[0]]
  return [float(str(ene).split(" ")[0]) for ene in ene_diff]

def main():
  eta = 0.1
  spin = '9half'

  freqbase_list = solve_ene(spin, eta)

  print(freqbase_list)
  val = Qdict["35Cl"]
  print(val)
  print(Qdict)
  A_before = Abefore('35Cl')
  print(A_before)
if __name__ == "__main__":
  main()
