#!/usr/bin/python
#coding=utf-8
import MySQLdb
import string
import os

conn= MySQLdb.connect(
    host='localhost',
    port = 3306,
    user='root',
    passwd='wangyu',
    db ='code_mine',
)
cur = conn.cursor()

def insertCommitData():
  cur.execute("truncate table commits")
  commit_id = ""
  name = ""
  email = ""
  time = ""
  comment = ""
  changed_files = ""
  gitlog = open("../data/node_gitlog")
  for line in gitlog:
    if line[0: 7] == 'commit ':
      commit_id = line[7: len(line)].rstrip();
      #print commit_id
    if line[0: 8] == 'Author: ':
      tmps = line[8: len(line) - 2].split('<')
      name = tmps[0].rstrip().replace("'", " ").replace('"', ' ')
      email = tmps[1].rstrip().replace("'", " ").replace('"', ' ')
      #print name
      #print email
    if line[0: 8] == 'Date:   ':
      tmps = line.split('   ')
      time = tmps[1].rstrip()
      #print time
    if line[0: 4] == "    " and line[4] != " ":
      comment += line[4: len(line)].rstrip().replace("'", " ").replace('"', ' ')
      comment += " "
      #print comment
    if line.find(" | ") != -1 and line[0] == " ":
      tmps = line.split(" | ")
      changed_files += tmps[0].rstrip().lstrip().replace("'", " ").replace('"', ' ')
      changed_files += " "
      #print changed_files
    if line.find("file changed,") != -1 or line.find("files changed,") != -1:
      sql = "insert into commits values('"+commit_id+"', '"+name+"', '"+email+"', '"+time+"', '"+comment+"', '"+changed_files+"')"
      print sql
      cur.execute(sql)
      comment = ""
      changed_files = "" 

  gitlog.close()

insertCommitData()

cur.close()
conn.commit()
conn.close()