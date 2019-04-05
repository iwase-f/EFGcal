# -*- coding: utf-8 -*-
# sdf_parse.py
# sdfファイルをパースする。
# 試験的に作成
# 20190307 F. Iwase

import re
import sys
import math
import codecs

#efg_list = []

def usage():
  message = u'usage: python3 sdf_parse.py file_name'
  print(message)
  sys.exit()

def sdfparse(path):
  atomx=[]
  atomy=[]
  atomz=[]
  atom=[]
  bondmatrix=[]
  f = codecs.open(path, 'r', 'utf-8')
  i = 0
  j = 1
  for line in f:
    # CID
    if i == 0:
      cid = line.strip()
      print(cid)
    # プログラム名(-OEChem-)、作成日時、次元(3D)など
    elif i == 1:
      line = line.strip()
      print(line)
    # コメント
    elif i == 2:
      comment = line
    # 原子数、結合数、
    elif i == 3:
      linelist = line.strip().split()
      atomn = linelist[0]
      bondn = linelist[1]
      print(atomn)
    # x, y, z, 元素記号、
    elif (i - 4) < int(atomn):
      linelist = line.strip().split()
      atomx.append(linelist[0])
      atomy.append(linelist[1])
      atomz.append(linelist[2])
      lin = [s for s in atom if linelist[3] == re.sub('[0-9]','',s)]
      atom.append(linelist[3]+str(len(lin)+1))
      print(atomx[i-4], atomy[i-4], atomz[i-4], atom[i-4])
    # 原子1, 原子2, 結合次数, 
    elif (i - 4 - int(atomn)) < int(bondn):
      linelist = line.strip().split()
      bondmatrix.append(linelist[:3])
      print(bondmatrix[i-4-int(atomn)])
    elif line.strip() == "M  END":
      print("end")
      break
    i = i+1
  f.close()

def main():
  args = sys.argv
  if len(args) > 2:
    usage()
  
  path = args[1] 
  sdfparse(path)

  
if __name__ == "__main__":
  main()

