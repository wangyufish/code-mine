#coding=utf-8 
from nltk.corpus import wordnet as wn
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

wordlinklist=[]

def getLinks(start,end,filepath):
	clusterDict = readLDAResult(filepath)
	results = getClusterPair(start,end)
	if None != results:
		for item in results:
			beforeCluster = item[0]
			laterCluster = item[1]
			location = item[2]
			print "cluster-two:",beforeCluster,laterCluster
			for topic1 in clusterDict[beforeCluster]:
				for topic2 in clusterDict[laterCluster]:
					getGraphBetweenCluster(beforeCluster,laterCluster,topic1,topic2,location)
			insertWordLinkToDB()

def getEdge(clusterFlag1,clusterFlag2,word,word2,beforeName,laterName,location):
	global wordlinklist
	entitySynset = wn.synset('entity.n.01')
	synsetSet = set()
	synsetList1 = wn.synsets(word)
	synsetList2 = wn.synsets(word2)
	tempwordlinklist = []
	tempdepth = 0
	for synset1 in synsetList1:
		for synset2 in synsetList2:
			sim = synset1.path_similarity(synset2)
			synsetList3 = synset1.lowest_common_hypernyms(synset2)
			if len(synsetList3) == 0:
				pass
			else:
				for synset3 in synsetList3:
					if (synset3 != entitySynset) and (synset3 not in synsetSet):
						synsetSet.add(synset3)
						depth = synset3.min_depth()
						if depth > tempdepth:#默认为当父结点层数越深表示关系越密切
							tempdepth = depth
							if synset1 == synset3:
								tempwordlinklist = [(clusterFlag1,clusterFlag2,clusterFlag1,clusterFlag2,location,beforeName,laterName,clusterFlag1 + beforeName + ":" + word + "-->" + clusterFlag2 + laterName + ":" + word2,depth,synset2.min_depth(),synset1.name(),synset2.name(),synset1.path_similarity(synset2))]
							elif synset2 == synset3:
								tempwordlinklist = [(clusterFlag2,clusterFlag1,clusterFlag1,clusterFlag2,location,laterName,beforeName,clusterFlag2 + laterName + ":" + word2 + "-->" + clusterFlag1 + beforeName + ":" + word,depth,synset1.min_depth(),synset2.name(),synset1.name(),synset2.path_similarity(synset1))]
							else:
								pass
	wordlinklist.extend(tempwordlinklist)

def getGraphBetweenCluster(beforeCluster,laterCluster,topicTuple1,topicTuple2,location):
	beforeName = topicTuple1[0]
	laterName = topicTuple2[0]
	for word in topicTuple1[1]:
		for word2 in topicTuple2[1]:
			getEdge(beforeCluster,laterCluster,word,word2,topicTuple1[0],topicTuple2[0],location)

def readLDAResult(filepath):
	clusterDict = {}
	file_read = open(filepath,"r")
	clusterFlag = ""
	topicFlag = ""
	tempClusterList = []
	flag = 0
	for text in file_read.readlines():
		if text.startswith("====================") and flag == 0:
			clusterFlag = text[26:-21]
			flag = 1
		elif text.startswith("====================") and flag == 1:
			clusterDict[clusterFlag] = tempClusterList
			clusterFlag = text[26:-21]
			tempClusterList = []
		elif text.startswith("Topic"):
			topicFlag = text[6:-2]
		else:
			keyList = trimstr(text).split(" ")
			tempClusterList.append((topicFlag,keyList))
	return clusterDict

def insertWordLinkToDB():
    global wordlinklist
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        sqli='insert into BCWordLinkSub (cluster1,cluster2,original_cluster1,original_cluster2,location,start,end,edge,depth1,depth2,synset1,synset2,path_sim) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        cur.executemany(sqli,wordlinklist)
        wordlinklist=[]
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def getClusterPair(start,end):
    report = ""
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT cluster1,cluster2,location FROM BClusterPair where id >= %s and id <= %s'%(start,end))
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def trimstr(zstr):
    ystr=zstr.lstrip()
    ystr=ystr.rstrip()
    ystr=ystr.strip()
    return ystr

if __name__ == '__main__':
	if(len(sys.argv)==3):
		start = sys.argv[1]
		end = sys.argv[2]
		getLinks(start,end,'../../result/topic_extraction_100')
