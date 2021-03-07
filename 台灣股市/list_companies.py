# -*- coding: utf8 -*-
from __future__ import print_function

import argparse, os
import pandas

def run(f):
  if not os.path.isfile(f):
    raise Exception('{} is not a file.'.format(f))
  csv = pandas.read_csv(f)
  data = csv.loc[:, ['公司名稱', '公司代號', '產業別']]
  for _, row in data.iterrows():
    print('{}: {}'.format(row['公司名稱'], row['公司代號']))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--file', type=str, required=True, help='Path to csv file.')
  args = parser.parse_args()
  run(args.file)
