# -*- coding: utf-8 -*-
# rotatemol.py
# pubchemからダウンロードしたsdfファイルで、
# 分子全体を回転させる。
# python3 rotatemol.py sdf_file_name inputfile [output_sdf_file]
# output_sdf_file default (sdf_file_name)_r.sdf 
# 20190417 F. Iwase

import re
import os
import sys
import math
import codecs
import numpy as np

def usage():
  message = 'usage: python3 rotatemol.py sdf_file_name inputfile [output_sdf_file]\n'\
            'input file format:\n'\
            'origin\n'\
            'axis (x or y or z or vector or atom1 atom2)\n'\
            'angle (deg)\n'\
            '[atom number]\n'\
            'example:\n\n'\
            '0 0 0\n'\
            'x\n'\
            '10\n'\
            '1\n'
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

def str2nparray(atom_zahyou):
  float_atom = []
  for atom in atom_zahyou:
    float_number = []  
    for number in atom:
      float_number.append(float(number))
    float_atom.append(float_number)
  return np.array(float_atom)

# 回転の行列を計算する
def rot_matrix(axis):
  theta_x = np.radians(axis[0])
  theta_y = np.radians(axis[1])
  theta_z = np.radians(axis[2])
  Rx = np.array([
    [1, 0, 0],
    [0, np.cos(theta_x), -np.sin(theta_x)],
    [0, np.sin(theta_x), np.cos(theta_x)]
  ])
  Ry = np.array([
    [np.cos(theta_y), 0, -np.sin(theta_y)],
    [0, 1, 0],
    [np.sin(theta_y), 0, np.cos(theta_y)]
  ])
  Rz = np.array([
    [np.cos(theta_z), -np.sin(theta_z), 0],
    [np.sin(theta_z), np.cos(theta_z), 0],
    [0, 0, 1],
  ])
  # 回転行列
  R = (np.linalg.inv(Rx)).dot(np.linalg.inv(Ry)).dot(Rz).dot(Ry).dot(Rx)

  return R

def displacement(atom_positions, r_origin):
  new_position_list = []
  for atom_posi in atom_positions:
    #print(atom_posi, 'r_origin= ', r_origin)
    atom_posi_array = np.array(atom_posi)
    r_origin_array = np.array(r_origin)
    new_position = atom_posi_array - r_origin_array
    new_position_list.append(new_position.tolist())
  
  return new_position_list

def moveatoms(atom_positions, r_origin, r_axis, r_atoms):
  #new_position = np.empty((0,3), float)
  new_position_list = []
  #print(atom_positions)
  atom_positions = displacement(atom_positions, r_origin)
  #print(atom_positions)
  R = rot_matrix(r_axis)

  index = 1
  index2 = 0
  for atom_posi in atom_positions:
    #print(atom_posi)
    atom_posi_array = np.array(atom_posi)
    new_position = np.array(atom_posi)
    if r_atoms[0] == 'all':
        #atom_position_array = atom_posi_array[index2]
      new_position = np.dot(R, atom_posi_array)
    elif len(r_atoms) > index2:
      if int(r_atoms[index2]) == index:
        #atom_position_array = atom_posi_array[index2]
        new_position = np.dot(R, atom_posi_array)
        index2 = index2 + 1

    new_position_list.append(new_position.tolist())
    index = index + 1

  r_origin_n = [(-1) * i for i in r_origin]
  new_position_list = displacement(new_position_list, r_origin_n)

  #print(new_position_list)
  return new_position_list
  
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

def input_file(path):
  r_atoms = []
  fin = codecs.open(path, 'r', 'utf-8')
  index = 0
  for line in fin:
    if line[0] == '#':
      continue
    
    line = line.strip().split()
    # 回転の原点
    if index == 0:
      r_origin = line
      print('r_origin = ', r_origin)
    # 回転の軸
    if index == 1:
      r_vector = line
      if r_vector[0] == 'x':
        r_vector = ['1', '0', '0']
      elif r_vector[0] == 'y':
        r_vector = ['0', '1', '0']
      elif r_vector[0] == 'z':
        r_vector = ['0', '0', '1']
      print('r_vector= ', r_vector)
    # 回転の角度
    if index == 2:
      r_angle = line
      if len(r_angle) > 1:
        print('input file error')
        sys.exit()
      else:
        r_angle=r_angle[0]
      print('r_angle(deg)= ', r_angle)
    # 回転する原子の指定
    if index > 2:
      r_atoms = line
      #if r_atom[0] == 'all':
      #  print('r_atoms= ', r_atoms)
      #  fin.close()
      #  return r_origin, r_vector, r_angle, r_atoms
      #else:
      #  r_atoms.append(r_atom)
      print('r_atoms= ', r_atoms)
    index = index + 1
  fin.close()
  return r_origin, r_vector, r_angle, r_atoms

def get_angle(r_vector, r_angle, atom_zahyou):
  if len(r_vector) == 2:
    origin_atom = np.array(atom_zahyou[int(r_vector[0])-1])
    head_atom   = np.array(atom_zahyou[int(r_vector[1])-1])
    direction = head_atom - origin_atom
    x, y, z = direction.tolist()
  else:
    x, y, z = r_vector

  x, y, z = float(x), float(y), float(z)
  theta_x = math.degrees(math.atan2(y,z))
  theta_y = math.degrees(math.atan2(x,math.sqrt(y**2+z**2)))
  
  r_angle =float(r_angle)
  #print(type(theta_x), theta_y, type(r_angle))
  angle = [theta_x, theta_y, r_angle]

  return angle

def get_origin(r_origin, atom_zahyou):
  if len(r_origin) > 2:
    r_origin = [float(r_origin[0]), float(r_origin[1]), float(r_origin[2])]
  else:
    r_origin = atom_zahyou[int(r_origin[0])-1]

  return r_origin

def main():
  args = sys.argv
  if len(args) < 2 or len(args) > 4:
    usage()
  sdf_path = args[1]
  input_path = args[2]
  r_origin, r_vector, r_angle, r_atoms = input_file(input_path)
  
  root, ext = os.path.splitext(sdf_path)
  if len(args) == 4:
    outpath = args[3]
  else:
    outpath = root + '_r.sdf'
  print(outpath)
  
  before, atom_zahyou, atom_syurui, after = readsdf(sdf_path)
  
  # atom_zahyouには全部の原子の座標が入っている
  #print(atom_zahyou)
  atom_zahyou = str2float(atom_zahyou)
  #print(atom_zahyou)
  
  #print(r_origin)
  #r_origin = str2float(r_origin)
  r_origin = get_origin(r_origin, atom_zahyou)

  #print(r_origin)
  r_axis = get_angle(r_vector, r_angle, atom_zahyou)
  new_position = moveatoms(atom_zahyou, r_origin, r_axis, r_atoms)
  
  sdfout(outpath, before, new_position, atom_syurui, after)
  
if __name__ == "__main__":
  main()


