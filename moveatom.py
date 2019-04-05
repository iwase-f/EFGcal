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

def usage():
  message = u'usage: python3 moveatom.py sdf_file_name atom_origin atom_moving length[ang] [output_cif_file]'
  print(message)
  sys.exit()

def sdfatom(path):
  fout = codecs.open(outpath, 'w', 'utf-8')

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
  atom_o = args[2]
  atom_m = args[3]
  length = args[4]
  root, ext = os.path.splitext(path)
  if len(args) == 6:
    outpath = args[5]
  else:
    outpath = root + '_m.sdf'
  print(outpath)
  
  sdfatom(path, outpath, atom_0, atom_m, length)
  
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


