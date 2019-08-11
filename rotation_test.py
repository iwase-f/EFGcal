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
  #R = (np.linalg.inv(Rx)).dot(np.linalg.inv(Ry)).dot(Rz).dot(Ry).dot(Rx)
  #R = (np.linalg.inv(Rx)).dot(np.linalg.inv(Ry)).dot(Ry).dot(Rx)
  #.dot(Rz).dot(Ry).dot(Rx)
  #R = Rx
  #R = Ry
  #R = Ry.dot(Rx)
  #R = Rz.dot(Ry).dot(Rx)
  #R = (np.linalg.inv(Ry)).dot(Rz).dot(Ry).dot(Rx)
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
  print(atom_positions)
  atom_positions = displacement(atom_positions, r_origin)
  print(atom_positions)
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

  print(new_position_list)
  return new_position_list

def get_angle(r_vector, r_angle):
  x, y, z = r_vector
  x, y, z = float(x), float(y), float(z)
  theta_x = math.degrees(math.atan2(y,z))
  theta_y = math.degrees(math.atan2(x,math.sqrt(y**2+z**2)))
  
  r_angle =float(r_angle)
  #print(type(theta_x), theta_y, type(r_angle))
  angle = [theta_x, theta_y, r_angle]

  return angle

def get_theta_y(r_vector):
  x, y, z = r_vector
  x, y, z = float(x), float(y), float(z)
  theta_y = math.degrees(math.atan2(x,z))
  return theta_y

def get_theta_x(r_vector):
  x, y, z = r_vector
  x, y, z = float(x), float(y), float(z)
  theta_x = math.degrees(math.atan2(y,z))
  return theta_x


r_vector = [0.001, 1, 0.00001]

r_axis = get_angle(r_vector, 90)


R = rot_matrix(r_axis)
atom_posi=[1,1,0]
atom_posi_array = np.array(atom_posi)
#atom_posi_array = np.array(r_vector)
print('position=',atom_posi)
print('vector=',r_vector)
print('angle=',r_axis)
new_position = np.dot(R, atom_posi_array)
print('new_position=',new_position)