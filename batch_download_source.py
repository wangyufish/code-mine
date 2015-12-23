#!/usr/bin/python
#coding=utf-8
import MySQLdb
import string
import os

conn= MySQLdb.connect(
    host='localhost',
    port = 3306,
    user='msr14',
    passwd='msr14',
    db ='msr14',
)
cur = conn.cursor()

count = cur.execute("select url from projects where forked_from is null")

codesetDir = "/media/wangyu/My_Device/科研数据/github/codeset"
info = cur.fetchmany(count)
for urls in info:
  url = urls[0].replace("https://api.github.com/repos/", " git@github.com:")
  os.chdir(codesetDir)
  print 'git clone ' + url
  var = os.system('git clone ' + url)
  if var != 0:
    print "error: " + url

cur.close()
conn.commit()
conn.close()
