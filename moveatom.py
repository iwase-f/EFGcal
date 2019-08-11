# -*- coding: utf-8 -*-
# moveatom.py
# pubchemからダウンロードしたsdfファイルで、
# 特定の原子を移動させる。
# プログラムの実行の際に、格子定数を設定する。
# 20190402 F. Iwase


import re
import os
import sys
import math
import codecs
import numpy as np

def usage():
  message = u'usage: python3 moveatom.py sdf_file_name atom_origin atom_moving length[ang] [output_cif_file]'
  print(message)
  sys.exit()

def readsdf(path):
  f = codecs.open(path, 'r', 'utf-8')
  i = 0
  j = 0
  k = 0
  before = []
  atom_zahyou = []
  atom_syurui = []
  after = []
  for line in f:
    # CID
    if i == 0:
      line = line.strip()
      before.append(line + " edited by F. Iwase\n")
      j = j + 1
    elif i == 1:
      before.append(line)
      j = j + 1
      #line = line.strip()
      #print(line)
    # コメント
    elif i == 2:
      before.append(line)
      j = j + 1
      #comment = line
    # 原子数、結合数、
    elif i == 3:
      before.append(line)
      linelist = line.strip().split()
      atomn = linelist[0]
      bondn = linelist[1]
      j = j + 1
    # x, y, z, 元素記号、
    elif (i - 4) < int(atomn):
      linelist = line.strip().split()
      x = linelist[0]
      y = linelist[1]
      z = linelist[2]
      atom = linelist[3]
      atom_zahyou.append([x, y, z])
      atom_syurui.append(atom)
      #atomy.append(linelist[1])
      #atomz.append(linelist[2])
      #atom.append(linelist[3])
      #lin = [s for s in atom if linelist[3] == re.sub('[0-9]','',s)]
      #atom.append(linelist[3]+str(len(lin)+1))
      #print(atom[i-4],j,' ', atom[i-4],' ', atomx[i-4],' ', atomy[i-4],' ', atomz[i-4], sep='')
      #j = j + 1
    # 原子1, 原子2, 結合次数, 
    #elif (i - 4 - int(atomn)) < int(bondn):
    #  linelist = line.strip().split()
    #  bondmatrix.append(linelist[:3])
    #  print(bondmatrix[i-4-int(atomn)])
    else:
      after.append(line)
      k = k + 1
    #if line.strip() == "M  END":
      #print("end")
    #  break
    i = i + 1
  f.close()

  return before, atom_zahyou, atom_syurui, after

def str2float(atom_zahyou):
  float_atom = []
  for atom in atom_zahyou:
    float_number = []  
    for number in atom:
      float_number.append(float(number))
    float_atom.append(float_number)
  return float_atom
  

def moveatoms(atom_zahyou, atom_o, atom_m, length):
  new_atom = [0,0,0]
  origin_atom = np.array(atom_zahyou[int(atom_o)-1])
  move_atom = np.array(atom_zahyou[int(atom_m)-1])
  vector = move_atom - origin_atom
  #print(origin_atom)
  #print(move_atom)
  u = np.linalg.norm(vector)
  float_length = float(length)
  print(float_length)
  new_atom[0] = move_atom[0] + float_length * vector[0] / u 
  new_atom[1] = move_atom[1] + float_length * vector[1] / u
  new_atom[2] = move_atom[2] + float_length * vector[2] / u
  atom_zahyou[int(atom_m)-1]=[new_atom[0],new_atom[1],new_atom[2]]
  return atom_zahyou
  
def sdfout(outpath, before, atom_zahyou, atom_syurui, after):
  fout = codecs.open(outpath, 'w', 'utf-8')
  for line in before:
    fout.write(line)
  index = 0
  for line in atom_zahyou:
    fout.write(str(round(line[0],4)).rjust(10) + str(round(line[1],4)).rjust(10) + str(round(line[2],4)).rjust(10) + " " + atom_syurui[index].ljust(2) + "  0  0  0  0  0  0  0  0  0  0  0  0\n")
    index = index + 1
  for line in after:
    fout.write(line)
    
  
  fout.close()

def main():
  args = sys.argv
  if len(args) < 5 or len(args) > 6:
    usage()

  path = args[1]
  atom_o = args[2]
  atom_m = args[3]
  length = args[4]
  root, ext = os.path.splitext(path)
  if len(args) == 6:
    outpath = args[5]
  else:
    outpath = root + '_m.sdf'
  print(outpath)
  
  before, atom_zahyou, atom_syurui, after = readsdf(path)
  atom_zahyou = str2float(atom_zahyou)
  atom_zahyou = moveatoms(atom_zahyou, atom_o, atom_m, length)
  sdfout(outpath, before, atom_zahyou, atom_syurui, after)
  

if __name__ == "__main__":
  main()


