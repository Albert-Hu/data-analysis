from __future__ import print_function

import os, json, sqlite3
from urllib import request

SQL_CREATE_TOPIC = '''CREATE TABLE `topic` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL,
  `name_slug`	TEXT NOT NULL
);
'''

SQL_CREATE_QUESTION = '''CREATE TABLE `question` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `leetcode_id`	INTEGER NOT NULL,
  `difficulty`	TEXT NOT NULL,
  `title`	TEXT NOT NULL,
	`title_slug`	TEXT NOT NULL,
  `accepted`	INTEGER NOT NULL,
  `submitted`	INTEGER NOT NULL
);
'''

SQL_CREATE_TOPIC_QUESTION = '''CREATE TABLE `topic_question` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`topic_id`	INTEGER NOT NULL,
  `question_id`	INTEGER NOT NULL
);
'''

SQL_INSERT_TOPIC = '''INSERT INTO `topic` (
  `name`,
  `name_slug`
) VALUES (
  "{}","{}");'''

SQL_INSERT_QUESTION = '''INSERT INTO `question` (
  `leetcode_id`,
  `difficulty`,
  `title`,
  `title_slug`,
  `accepted`,
  `submitted`
) VALUES (
  "{}", "{}", "{}", "{}", "{}", "{}");
'''

SQL_INSERT_TOPIC_QUESTION = '''INSERT INTO `topic_question` (
  `topic_id`,
  `question_id`
) VALUES (
  "{}","{}");'''

SQL_QUERY_LAST_ID = 'select last_insert_rowid();'

def download_tags(db):
  cursor = db.cursor()
  cursor.execute(SQL_CREATE_TOPIC)
  topic_questions = {}
  url = 'https://leetcode.com/problems/api/tags'
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
  target = request.Request(url, headers=headers)
  with request.urlopen(target) as content:
    tags = json.loads(content.read().decode('utf8'))
    for topic in tags['topics']:
      name = topic['name']
      name_slug = topic['slug']
      cursor.execute(SQL_INSERT_TOPIC.format(name, name_slug))
      cursor.execute(SQL_QUERY_LAST_ID)
      last_id = cursor.fetchone()[0]
      topic_questions[last_id] = topic['questions'] # leetcode id
  db.commit()
  return topic_questions

def download_questions(db):
  level = {1: 'easy', 2: 'medium', 3: 'hard'}
  cursor = db.cursor()
  cursor.execute(SQL_CREATE_QUESTION)
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
      cursor.execute(SQL_INSERT_QUESTION.format(leetcode_id, difficulty, title, title_slug, accepted, submitted))
      cursor.execute(SQL_QUERY_LAST_ID)
      questions[leetcode_id] = cursor.fetchone()[0]
  db.commit()
  return questions

def associate(topic, questions):
  cursor = db.cursor()
  cursor.execute(SQL_CREATE_TOPIC_QUESTION)
  for topic_id in topic.keys():
    for leetcode_id in topic[topic_id]:
      if leetcode_id not in questions: continue
      cursor.execute(SQL_INSERT_TOPIC_QUESTION.format(topic_id, questions[leetcode_id]))
  db.commit()

if __name__ == '__main__':
  db_name = 'leetcode.db'
  if os.path.isfile(db_name):
    os.remove(db_name)
  db = sqlite3.connect(db_name)
  # start to download tags and questions
  topic = download_tags(db)
  questions = download_questions(db)
  associate(topic, questions)
  # close the database
  db.close()
