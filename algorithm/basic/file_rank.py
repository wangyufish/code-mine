#!/usr/bin/python
#coding=utf-8
import MySQLdb
import string
import os
import urllib2
import datetime

conn= MySQLdb.connect(
    host='localhost',
    port = 3306,
    user='root',
    passwd='wangyu',
    db ='code_mine',
)
cur = conn.cursor()

def formatDatetime(time):
  numbers = time.split()
  if len(numbers) != 6:
    return -1
  year = numbers[4]
  month_dict = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
  }
  month = month_dict[numbers[1]]
  day = numbers[2]
  time = numbers[3]
  retTime = year+'-'+month+'-'+day+' '+time
  return retTime



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
      time = formatDatetime(tmps[1].rstrip())
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
      sql = "insert into commits values('"+commit_id+"', '"+name+"', '"+email+"', '"+comment+"', '"+changed_files+"', '"+time+"')"
      print sql
      cur.execute(sql)
      comment = ""
      changed_files = "" 
  gitlog.close()
#insertCommitData()

cur.close()
conn.commit()
conn.close()