import sys
import socket
import MySQLdb
import chardet
import ssl
import time          
import re          
import os
import string
import sys
import math
import matplotlib.pyplot as plt

def averageWeightInCluster(cluster):
	results = getInClusterData(cluster)
	if None != results:
		for item in results:
			print item

	

def getInClusterData(cluster):
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT start,end,depth FROM wordLink where cluster = "'+cluster+'" and start like "#%"')
        results = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return results
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def getAllCluster():
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT distinct cluster FROM wordLink')
        results = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return results
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

if __name__ == '__main__':
	averageWeightInCluster("1")
