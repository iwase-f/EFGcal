#!/usr/bin/gawk
# split a sdf file containing many molecular data into each sdf files
#
# awk -f splitsdf.awk sdf_file
#

{
  if(before~/\$\$\$\$/) file=$0
  print $0 >> file ".sdf" 
  before=$0
}