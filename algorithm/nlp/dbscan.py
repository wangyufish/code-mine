#coding=utf-8 
import urllib2  
import os
import sys
import socket
import MySQLdb
import ssl
import time          
import re          
import os
import string
import sys
import math
import nltk
import sklearn
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import random
from sklearn.cluster import KMeans 
from sklearn.cluster import MiniBatchKMeans 
from sklearn.externals import joblib
from sklearn.cluster import DBSCAN
import numpy
import string
from string import punctuation

commitDict = {}

def dbscan():
    X,commitkeyList,commitmessList = getTFIDFMatrix()
    X=X.todense()
    clf = DBSCAN(eps=0.1, min_samples=20).fit(X)
    s = clf.fit(X)
    print s

    print '每个样本所属的簇',clf.labels_,type(clf.labels_)

    print '核心点的索引',clf.core_sample_indices_
    print '中心样本',clf.components_
    print 'endTime',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #saveClusterResult(commitkeyList,commitmessList,clf.labels_)
    saveLabelResult(clf.labels_)
    print 'saveTime',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def saveLabelResult(labels):
    clusterDict = {}
    for i in range(len(labels)):
        if labels[i] in clusterDict.keys():
            clusterDict[labels[i]] = clusterDict[labels[i]] + 1
        else:
            clusterDict[labels[i]] = 1
    for key in clusterDict.keys():
        print key,clusterDict[key]

def saveClusterResult(commitkeyList,commitmessList,labels):
    global commitDict
    length = len(commitkeyList)/10000 + 1
    for i in range(length):
        if (i*10000 + 9999) > len(commitkeyList) - 1:
            temp_commitkeyList = commitkeyList[(i*10000):(len(commitkeyList) - 1)]
        else:
            temp_commitkeyList = commitkeyList[(i*10000):(i*10000 + 9999)]
        clusterList = []
        for i in range(len(temp_commitkeyList)):
            clusterList.append((temp_commitkeyList[i].split('_')[0],temp_commitkeyList[i].split('_')[1],commitDict[temp_commitkeyList[i]][1],commitDict[temp_commitkeyList[i]][2],labels[i],commitDict[temp_commitkeyList[i]][3],commitDict[temp_commitkeyList[i]][4],commitDict[temp_commitkeyList[i]][5],commitDict[temp_commitkeyList[i]][6],commitDict[temp_commitkeyList[i]][7]))
        saveClusterToDB(clusterList)



def saveClusterToDB(clusterList):
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        sqli='insert into commit_cluster_dbscan (original_id,repository_id,sha,message,cluster,is_bug_fixed,author_email,committer_email,additions,deletions) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        cur.executemany(sqli,clusterList)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def getTFIDFMatrix():
    print 'getTime',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    contentDict = getCommitMessListByReposId()
    print 'len(contentDict.keys())',len(contentDict.keys())
    print 'end-getTime',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    for item in contentDict.keys():
        try:
            contentDict[item] = contentDict[item].decode('utf-8').encode('utf-8')
        except:
            del contentDict[item]
    commitkeyList = contentDict.keys()
    commitmessList = contentDict.values()
    transformer=TfidfTransformer()
    vectorizer=CountVectorizer()
    tfidf=transformer.fit_transform(vectorizer.fit_transform(commitmessList))
    word=vectorizer.get_feature_names()
    print "feature维度：",len(word)
    print 'startTime',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #weight=tfidf.toarray()
    return tfidf,commitkeyList,commitmessList



def getCommitMessListByReposId():
    global commitDict
    contentDict = {}
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        #count=cur.execute('SELECT id,repository_id,sha,message,is_bug_fixed,author_email,committer_email,additions,deletions FROM commits_words where repository_id=457 or repository_id=274 or repository_id=288 or repository_id=256 or repository_id=249 or repository_id=135 or repository_id=207 or repository_id=460 or repository_id=452 or repository_id=1;')
        count=cur.execute('SELECT id,repository_id,sha,message,is_bug_fixed,author_email,committer_email,additions,deletions FROM commits_words where repository_id=207 or repository_id=460 or repository_id=452 or repository_id=1;')
        result = cur.fetchall()
        if None != result:
            for item in result:
                contentDict[str(item[0])+'_'+str(item[1])] = item[3]
                commitDict[str(item[0])+'_'+str(item[1])] = (item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8])
        conn.commit()
        cur.close()
        conn.close()
        return contentDict
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    dbscan()

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
