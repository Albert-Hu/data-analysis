from __future__ import print_function

import argparse, os
import pandas

def run(d):
  if not os.path.isdir(d):
    raise Exception('{} is not a directory.'.format(d))
  table = []
  for file in filter(lambda f: f.lower().endswith('.csv'), os.listdir(d)):
    csv = pandas.read_csv(os.path.join(d, file))
    columns = set(csv.columns)
    for c in table:
      if columns == c: break
    else:
      table.append(columns)
  for columns in table:
    for c in columns:
      print(c, end=',')
    print('')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--directory', type=str, required=True, help='Directory to raw data.')
  args = parser.parse_args()
  run(args.directory)
