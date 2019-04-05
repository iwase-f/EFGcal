# -*- coding: utf-8 -*-
# pubchem.py
#20190308 F. Iwase

import re
import sys
import math
import codecs
import pubchempy as pcp

def usage():
  message = u'usage: python3 pubchem.py name'
  print(message)
  sys.exit()

def main():
  args = sys.argv
  if len(args) > 2:
    usage()
  
  name = args[1] 
  aa = pcp.get_compounds(name,'name')
  #aa = pcp.get_compounds(name, searchtype='similarity', listkey_cound=3)
  for i in aa:
    cid = i.cid
    print('CID: {}\tName: {}\tFormula: {}'.format(i.cid, i.iupac_name,i.molecular_formula))
#    pcp.download('SDF',str(cid)+'.sdf', cid, 'cid')

 # sids = pcp.get_sids(name, 'name')

  #for sid in sids:
   # print(Substance.from_sid(sid))

if __name__ == "__main__":
  main()

