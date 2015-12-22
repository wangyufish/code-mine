#!/usr/bin/python
#coding=utf-8
import MySQLdb

conn= MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='msr14',
        passwd='msr14',
        db ='msr14',
        )
cur = conn.cursor()

count = cur.execute("select count(*) from projects")

info = cur.fetchmany(count)
print info

cur.close()
conn.commit()
conn.close()
