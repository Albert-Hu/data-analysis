from __future__ import print_function

from urllib import request

import os, json, argparse

LEETCODE_API = {
  'tags': 'https://leetcode.com/problems/api/tags',
  'all': 'https://leetcode.com/api/problems/all'
}

LEVELS = {
  1: 'Easy',
  2: 'Medium',
  3: 'Hard'
}

def download(to, override=True):
  if not os.path.exists(to):
    os.mkdir(to)
  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
  for name, url in LEETCODE_API.items():
    file_path = os.path.join(to, name + '.json')
    if os.path.exists(file_path) and not override:
      continue
    req = request.Request(url, headers=headers)
    with request.urlopen(req) as content:
      with open(file_path, 'w') as file:
        file.write(content.read().decode('utf8'))

def similarity_tree_insert(root, qid, topics):
  if len(topics) == 0:
    root['questions'].add(qid)
  else:
    if not topics[0] in root['topics']:
      root['topics'][topics[0]] = {'topics': {}, 'questions': set()}
    similarity_tree_insert(root['topics'][topics[0]], qid, topics[1:])

def load(directory):
  data = {}
  for name, _ in LEETCODE_API.items():
    file_path = os.path.join(directory, name + '.json')
    with open(file_path, 'r') as file:
      data[name] = json.loads(file.read())
  # convert the List to the Set for the performance of the search
  for topic in data['tags']['topics']:
    topic['questions'] = set(topic['questions'])
  questions = {}
  similarity_tree = {'topics': {}}
  for q in data['all']['stat_status_pairs']:
    qid = q['stat']['frontend_question_id']
    releated_topics = filter(lambda t: qid in t['questions'], data['tags']['topics'])
    releated_topics = sorted(set([t['slug'] for t in releated_topics]))
    # add the quetion if the it is not locked
    if len(releated_topics) > 0:
      questions[qid] = {
        'title': q['stat']['question__title'],
        'title_slug': q['stat']['question__title_slug'],
        'accepted': q['stat']['total_acs'],
        'submissions': q['stat']['total_submitted'],
        'level': q['difficulty']['level'],
        'topics': releated_topics
      }
      if not releated_topics[0] in similarity_tree['topics']:
        similarity_tree['topics'][releated_topics[0]] = {'topics': {}, 'questions': set()}
      similarity_tree_insert(similarity_tree['topics'][releated_topics[0]], qid, releated_topics[1:])
  topics = {}
  return topics, questions, similarity_tree

def dump(root, hierarchy=0):
  for name, topic in root['topics'].items():
    print('{}{}: {}'.format(' ' * (hierarchy * 3), name, len(topic['questions'])))
    dump(topic, hierarchy + 1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output-dir',
    required=True,
    help='That the path of the output directory.')
  parser.add_argument('-u', '--update',
    action='store_true',
    help='Update the data from LeetCode.')
  parser.add_argument('-t', '--type',
    nargs='*',
    choices=['md', 'csv', 'ods'],
    help='That the type of output files that supports Markdown(md), Comma-Separated Values(csv), and Operational Data Store(ods).')
  args = parser.parse_args()
  print(args)
  # download data from LeetCode if need
  download(args.output_dir, args.update)
  # load the data
  topics, questions, similarity_tree = load(args.output_dir)
  dump(similarity_tree)
