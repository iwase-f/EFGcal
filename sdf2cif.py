# -*- coding: utf-8 -*-
# sdf2cif.py
# pubchemからダウンロードしたsdfファイルをWIEN2kで使うためにcifファイルに変換する。
# 分子はユニットセルの中心に配置される。
# プログラムの実行の際に、格子定数を設定する。
#20190325 F. Iwase

import re
import os
import sys
import math
import codecs

def usage():
  message = u'usage: python3 sdf2cif.py sdf_file_name a_x a_y a_z [output_cif_file]'
  print(message)
  sys.exit()

def sdfparse(path):
  atomx=[]
  atomy=[]
  atomz=[]
  atom=[]
  #bondmatrix=[]
  f = codecs.open(path, 'r', 'utf-8')
  i = 0
  for line in f:
    # CID
    if i == 0:
      cid = line.strip()
      #print("_chemical_name_common '" + cid + "'")
    # プログラム名(-OEChem-)、作成日時、次元(3D)など
    elif i == 1:
      line = line.strip()
      #print(line)
    # コメント
    elif i == 2:
      comment = line
    # 原子数、結合数、
    elif i == 3:
      linelist = line.strip().split()
      atomn = linelist[0]
      bondn = linelist[1]
    # x, y, z, 元素記号、
    elif (i - 4) < int(atomn):
      linelist = line.strip().split()
      atomx.append(linelist[0])
      atomy.append(linelist[1])
      atomz.append(linelist[2])
      atom.append(linelist[3])
      #lin = [s for s in atom if linelist[3] == re.sub('[0-9]','',s)]
      #atom.append(linelist[3]+str(len(lin)+1))
      #print(atom[i-4],j,' ', atom[i-4],' ', atomx[i-4],' ', atomy[i-4],' ', atomz[i-4], sep='')
      #j = j + 1
    # 原子1, 原子2, 結合次数, 
    #elif (i - 4 - int(atomn)) < int(bondn):
    #  linelist = line.strip().split()
    #  bondmatrix.append(linelist[:3])
    #  print(bondmatrix[i-4-int(atomn)])
    elif line.strip() == "M  END":
      #print("end")
      break
    i = i+1
  f.close()
  return cid, atom, atomx, atomy, atomz

def main():
  args = sys.argv
  if len(args) < 6 or len(args) > 7:
    usage()

  path = args[1]
  lattice_x = args[2]
  lattice_y = args[3]
  lattice_z = args[4]
  root, ext = os.path.splitext(path)
  if len(args) == 6:
    outpath = args[5]
  else:
    outpath = root + '.cif'
  print(outpath)
  fout = codecs.open(outpath, 'w', 'utf-8')

  text="_space_group_name_H-M_alt       'P 1'\n\
_space_group_crystal_system cubic\n\
_space_group_symop_operation_xyz  'x, y, z'\n\
_cell_length_a    LENGTH!CHANGE_x\n\
_cell_length_b    LENGTH!CHANGE_y\n\
_cell_length_c    LENGTH!CHANGE_z\n\
_cell_angle_alpha 90\n\
_cell_angle_beta  90\n\
_cell_angle_gamma 90\n\
loop_\n\
    _atom_site_label\n\
    _atom_site_type_symbol\n\
    _atom_site_fract_x\n\
    _atom_site_fract_y\n\
    _atom_site_fract_z"
  
  text = text.replace('LENGTH!CHANGE_x', lattice_x).replace('LENGTH!CHANGE_y', lattice_y).replace('LENGTH!CHANGE_z', lattice_z)
  cid, atom, atomx, atomy, atomz = sdfparse(path)
  #print("_chemical_name_common '" + cid + "'")
  #print(text)
  fout.write("data_\n")
  fout.write("_chemical_name_common '" + cid + "'\n")
  fout.write(text + '\n')
  index = 0
  for item in atom:
    #print(atom[index],index,' ', atom[index],' ', round(float(atomx[index])/float(lattice),6)+0.5,' ', round(float(atomy[index])/float(lattice),7)+0.5,' ', round(float(atomz[index])/float(lattice),6)+0.5, sep='')
    write_text = str(atom[index]) + str(index) + ' ' + str(atom[index]) + ' ' + str(round(float(atomx[index])/float(lattice_x)+ 0.50,6)) + ' ' + str(round(float(atomy[index])/float(lattice_y)+0.50, 6)) + ' ' + str(round(float(atomz[index])/float(lattice_z)+0.50, 6)) + '\n'
    fout.write(write_text)
    index = index + 1

  fout.close()

if __name__ == "__main__":
  main()

