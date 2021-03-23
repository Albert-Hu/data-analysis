from __future__ import print_function

import os, json
import pandas
from datetime import date
from urllib import request
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style

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
  # add similarity to each questions
  topic_intersections = {}
  for i in questions.keys():
    questions[i]['similarities'] = {}
    for j in questions.keys():
      if i == j: continue
      t1 = questions[i]['topics']
      t2 = questions[j]['topics']
      intersection = t1.intersection(t2)
      if len(intersection) > 1:
        questions[i]['similarities'][j] = intersection
        group = ', '.join(sorted(intersection))
        if not group in topic_intersections.keys():
          topic_intersections[group] = set()
        topic_intersections[group].add(i)
        topic_intersections[group].add(j)
  return topics, questions, topic_intersections

def topic_difficulty_list(topics, difficulty):
  return [len(t['difficulties'][difficulty]) for t in topics]

def group_difficulty_list(group, questions, difficulty):
  return len(list(filter(lambda qid: questions[qid]['difficulty'] == difficulty, group)))

def to_markdown(topics, questions, topic_intersections):
  timestamp = 'latest updated at {}'.format(date.today().strftime("%Y/%m/%d"))
  # write to topics.md
  file_name = get_file_path('topics.md')
  with open(file_name, 'w') as md:
    name = '[{}]({}.md)'
    topic_data = {
      'Name': [name.format(t['name'], t['slug']) for t in topics],
      'Total': [len(t['questions']) for t in topics],
      'Easy': topic_difficulty_list(topics, 'easy'),
      'Medium': topic_difficulty_list(topics, 'medium'),
      'Hard': topic_difficulty_list(topics, 'hard')
    }
    topic_table = pandas.DataFrame.from_dict(topic_data)
    topic_table = topic_table.sort_values(by=['Total'], ascending=False)
    md.write('# Topics\n\n')
    md.write('**Total {} topics, {}.**\n\n'.format(len(topics), timestamp))
    writer = MarkdownTableWriter()
    writer.from_dataframe(topic_table)
    writer.column_styles = [
        Style(align="left"),
        Style(align="right"),
        Style(align="right"),
        Style(align="right"),
        Style(align="right")
    ]
    md.write(writer.dumps())
    md.write('\n\n')
    print('Created {}.'.format(file_name))
  # write to each topics
  for t in topics:
    file_name = get_file_path(t['slug'] + '.md')
    with open(file_name, 'w') as md:
      level = {'easy': 0, 'medium': 1, 'hard': 2}
      title = '[{}](https://leetcode.com/problems/{})'
      question_data = {
        'Level': [level[questions[qid]['difficulty']] for qid in t['questions']],
        'ID': [qid for qid in t['questions']],
        'Title': [title.format(questions[qid]['title'], questions[qid]['title_slug']) for qid in t['questions']],
        'Difficulty': [questions[qid]['difficulty'] for qid in t['questions']],
        'Accepted': ['{:,}'.format(questions[qid]['accepted']) for qid in t['questions']],
        'Submissions': ['{:,}'.format(questions[qid]['submissions']) for qid in t['questions']],
        'Acceptance': ['{:.0f}%'.format(100. * questions[qid]['accepted'] / questions[qid]['submissions']) for qid in t['questions']]
      }
      question_table = pandas.DataFrame.from_dict(question_data)
      question_table = question_table.sort_values(by=['ID', 'Level'])
      md.write('# {}\n\n'.format(t['name']))
      md.write('**Total {} questions, {}.**\n\n'.format(len(question_data['ID']), timestamp))
      writer = MarkdownTableWriter()
      writer.from_dataframe(question_table.iloc[:,1:])
      writer.column_styles = [
          Style(align="right"),
          Style(align="left"),
          Style(align="center"),
          Style(align="right"),
          Style(align="right"),
          Style(align="right")
      ]
      md.write(writer.dumps())
      md.write('\n\n')
      print('Created {}.'.format(file_name))
  # write to similarities.md
  file_name = get_file_path('similarities.md')
  with open(file_name, 'w') as md:
    md.write('# Similarity Questions\n\n')
    md.write('**Total {} similarities, {}.**\n\n'.format(len(topic_intersections.keys()), timestamp))
    similarities_data = {
      'Group': [],
      'Total': [],
      'Easy': [],
      'Medium': [],
      'Hard': []
    }
    group_title = '[{}](#{})'
    for group in sorted(topic_intersections.keys()):
      similarities_data['Group'].append(group_title.format(group, '-'.join(group.split(', '))))
      similarities_data['Total'].append(len(topic_intersections[group]))
      similarities_data['Easy'].append(group_difficulty_list(topic_intersections[group], questions, 'easy'))
      similarities_data['Medium'].append(group_difficulty_list(topic_intersections[group], questions, 'medium'))
      similarities_data['Hard'].append(group_difficulty_list(topic_intersections[group], questions, 'hard'))
    similarities_table = pandas.DataFrame.from_dict(similarities_data)
    writer = MarkdownTableWriter()
    writer.from_dataframe(similarities_table)
    writer.column_styles = [
        Style(align="left"),
        Style(align="right"),
        Style(align="right"),
        Style(align="right"),
        Style(align="right")
    ]
    md.write(writer.dumps())
    md.write('\n\n')
    title = '[{}](https://leetcode.com/problems/{})'
    for group in sorted(topic_intersections.keys()):
      md.write('## {}\n\n'.format(group))
      group_data = {
        'ID': [],
        'Question': [],
        'Difficulty': [],
        'Accepted': [],
        'Submissions': [],
        'Acceptance': []
      }
      for qid in topic_intersections[group]:
        group_data['ID'].append(qid)
        group_data['Question'].append(title.format(questions[qid]['title'], questions[qid]['title_slug']))
        group_data['Difficulty'].append(questions[qid]['difficulty'])
        group_data['Accepted'].append('{:,}'.format(questions[qid]['accepted']))
        group_data['Submissions'].append('{:,}'.format(questions[qid]['submissions']))
        group_data['Acceptance'].append('{:.0f}%'.format(100. * questions[qid]['accepted'] / questions[qid]['submissions']))
      group_table = pandas.DataFrame.from_dict(group_data)
      group_table = group_table.sort_values(by=['ID'])
      writer = MarkdownTableWriter()
      writer.from_dataframe(group_table)
      writer.column_styles = [
          Style(align="right"),
          Style(align="left"),
          Style(align="center"),
          Style(align="right"),
          Style(align="right"),
          Style(align="right")
      ]
      md.write(writer.dumps())
      md.write('\n\n')
    print('Created {}.'.format(file_name))

if __name__ == '__main__':
  download('https://leetcode.com/problems/api/tags', 'topics.json')
  download('https://leetcode.com/api/problems/all', 'questions.json')
  topics, questions, topic_intersections = analyse()
  to_markdown(topics, questions, topic_intersections)
