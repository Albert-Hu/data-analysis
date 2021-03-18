from __future__ import print_function

import os, json
from urllib import request

def download_tags():
  topics = {}
  url = 'https://leetcode.com/problems/api/tags'
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
  target = request.Request(url, headers=headers)
  with request.urlopen(target) as content:
    tags = json.loads(content.read().decode('utf8'))
    for t in tags['topics']:
      questions = t['questions']
      name = t['name']
      name_slug = t['slug']
      topics[name_slug] = {'name': name, 'questions': questions}
  return topics

def download_questions():
  level = {1: 'easy', 2: 'medium', 3: 'hard'}
  questions = {}
  url = 'https://leetcode.com/api/problems/all'
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
  target = request.Request(url, headers=headers)
  with request.urlopen(target) as content:
    data = json.loads(content.read().decode('utf8'))
    for problem in data['stat_status_pairs']:
      leetcode_id = problem['stat']['frontend_question_id']
      difficulty = level[problem['difficulty']['level']]
      title = problem['stat']['question__title']
      title_slug = problem['stat']['question__title_slug']
      accepted = problem['stat']['total_acs']
      submitted = problem['stat']['total_submitted']
      questions[title_slug] = {
        'id': leetcode_id,
        'difficulty': difficulty,
        'title': title,
        'accepted': accepted,
        'submitted': submitted,
        'topics': []
      }
  return questions

def associate(topics, questions):
  for name in topics.keys():
    for title in questions.keys():
      if questions[title]['id'] in topics[name]['questions']:
        questions[title]['topics'].append(name)

if __name__ == '__main__':
  topics = download_tags()
  questions = download_questions()
  associate(topics, questions)
  # show all the topics
  print('{} Topics({}) {}'.format('=' * 10, len(topics.keys()), '=' * 10))
  for name in topics.keys():
    print('{:25}: {}'.format(name, len(topics[name]['questions'])))
  # show all the questions
  print('{} Questions({}) {}'.format('=' * 10, len(questions.keys()), '=' * 10))
  for title in questions.keys():
    print('{}\n  {}'.format(title, '\n  '.join(questions[title]['topics'])))
