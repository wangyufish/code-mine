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

def getLinks(filepath):
	clusterDict = readLDAResult(filepath)
	for item in clusterDict.keys():
		print item
		getGraph(item,clusterDict[item])
		insertWordLinkToDB()

def getEdge(clusterFlag,word,word2,beforeName,laterName):
	global wordlinklist
	entitySynset = wn.synset('entity.n.01')
	synsetSet = set()
	synsetList1 = wn.synsets(word)
	synsetList2 = wn.synsets(word2)
	tempwordlinklist = []
	tempdepth = 0
	for synset1 in synsetList1:
		for synset2 in synsetList2:
			synsetList3 = synset1.lowest_common_hypernyms(synset2)
			if len(synsetList3) == 0:
				pass
			else:
				for synset3 in synsetList3:
					if (synset3 != entitySynset) and (synset3 not in synsetSet):
						synsetSet.add(synset3)
						depth = synset3.min_depth()
						if depth > tempdepth:
							tempdepth = depth
							if synset1 == synset3:
								tempwordlinklist = [(clusterFlag,beforeName,laterName,beforeName + ":" + word + "-->" + laterName + ":" + word2,depth)]
							elif synset2 == synset3:
								tempwordlinklist = [(clusterFlag,laterName,beforeName,laterName + ":" + word2 + "-->" + beforeName + ":" + word,depth)]
							else:
								pass
								#tempwordlinklist = [(clusterFlag,synset3.name(),beforeName,synset3.name() + "-->" + beforeName + ":" + word,depth),(clusterFlag,synset3.name(),laterName,synset3.name() + "-->" + laterName + ":" + word2,depth)]
#如word与word2有共同上位词的情况不需要处理，可不存入数据库
	wordlinklist.extend(tempwordlinklist)

	
def getGraph(clusterFlag,keyList):
	for i in range(len(keyList)):
		beforeItem = keyList[i]
		for j in range(i+1,len(keyList)):
			laterItem = keyList[j]
			for word in beforeItem[1]:
				for word2 in laterItem[1]:
					getEdge(clusterFlag,word,word2,beforeItem[0],laterItem[0])

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
        sqli='insert into wordLink (cluster,start,end,edge,depth) values (%s,%s,%s,%s,%s);'
        cur.executemany(sqli,wordlinklist)
        wordlinklist=[]
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def trimstr(zstr):
    ystr=zstr.lstrip()
    ystr=ystr.rstrip()
    ystr=ystr.strip()
    return ystr

if __name__ == '__main__':
	getLinks('../../result/topic_extraction_100')
