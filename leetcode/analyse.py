from __future__ import print_function

import os, json
import pandas
from urllib import request

ROOT_PATH = 'raw_data'

def get_file_path(name):
  return os.path.join(ROOT_PATH, name)

def download(url, name):
  file_path = get_file_path(name)
  if not os.path.exists(ROOT_PATH):
    os.mkdir(ROOT_PATH)
  if not os.path.exists(file_path):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
    req = request.Request(url, headers=headers)
    with request.urlopen(req) as content:
      with open(file_path, 'w') as file:
        file.write(content.read().decode('utf8'))

def load_json(file_path):
  with open(file_path, 'r') as file:
    return json.loads(file.read())

def analyse():
  difficulty = ['easy', 'medium', 'hard']
  topics_json = load_json(get_file_path('topics.json'))
  questions_json = load_json(get_file_path('questions.json'))
  # generate the statistics of the topics
  topics = topics_json['topics']
  # generate the statistics of the questions
  questions = {}
  for q in questions_json['stat_status_pairs']:
    qid = q['stat']['frontend_question_id']
    questions[qid] = {
      'title': q['stat']['question__title'],
      'title_slug': q['stat']['question__title_slug'],
      'accepted': q['stat']['total_acs'],
      'submissions': q['stat']['total_submitted'],
      'difficulty': difficulty[q['difficulty']['level'] - 1],
      'topics': set([t['slug'] for t in filter(lambda x: qid in x['questions'], topics)])
    }
  # update the statistics of the topics
  for i in range(len(topics)):
    topics[i]['questions'] = list(filter(lambda qid: qid in questions.keys(), topics[i]['questions']))
    topics[i]['difficulties'] = {
      d: list(filter(lambda qid: questions[qid]['difficulty'] == d, topics[i]['questions']))
      for _, d in enumerate(difficulty)}
  topics = list(filter(lambda t: len(t['questions']) > 0, topics_json['topics']))
  # add similarity to each of questions
  for i in questions.keys():
    questions[i]['similarities'] = {}
    for j in questions.keys():
      if i == j: continue
      t1 = questions[i]['topics']
      t2 = questions[j]['topics']
      intersection = t1.intersection(t2)
      if len(intersection) > 1:
        questions[i]['similarities'][j] = intersection
  return topics, questions

def to_markdown(topics, questions):
  # write to topics.md
  with open(get_file_path('topics.md'), 'w') as md:
    topic_data = {
      'Name': ['[{}](#{})'.format(t['name'], t['slug']) for t in topics],
      'Total': [len(t['questions']) for t in topics],
      'Easy': [len(t['difficulties']['easy']) for t in topics],
      'Medium': [len(t['difficulties']['medium']) for t in topics],
      'Hard': [len(t['difficulties']['hard']) for t in topics]
    }
    topic_table = pandas.DataFrame.from_dict(topic_data)
    topic_table = topic_table.sort_values(by=['Total'], ascending=False)
    md.write('# Topics\n\n')
    md.write(topic_table.to_markdown(index=False))
    md.write('\n\n')
    for t in topics:
      md.write('# {}\n\n'.format(t['name']))
      level = {'easy': 0, 'medium': 1, 'hard': 2}
      question_data = {
        'Level': [level[questions[qid]['difficulty']] for qid in t['questions']],
        'ID': [qid for qid in t['questions']],
        'Title': ['[{}](https://leetcode.com/problems/{})'.format(questions[qid]['title'], questions[qid]['title_slug']) for qid in t['questions']],
        'Difficulty': [questions[qid]['difficulty'].capitalize() for qid in t['questions']],
        'Accepted': ['{:,}'.format(questions[qid]['accepted']) for qid in t['questions']],
        'Submissions': ['{:,}'.format(questions[qid]['submissions']) for qid in t['questions']],
        'Acceptance': ['{:.0f}%'.format(100. * questions[qid]['accepted'] / questions[qid]['submissions']) for qid in t['questions']]
      }
      question_table = pandas.DataFrame.from_dict(question_data)
      question_table = question_table.sort_values(by=['Level', 'ID'])
      md.write(question_table.iloc[:,1:].to_markdown(index=False))
      md.write('\n\n')

if __name__ == '__main__':
  download('https://leetcode.com/problems/api/tags', 'topics.json')
  download('https://leetcode.com/api/problems/all', 'questions.json')
  topics, questions = analyse()
  to_markdown(topics, questions)
