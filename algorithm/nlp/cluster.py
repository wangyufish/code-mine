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
from sklearn.externals import joblib
import numpy
import string
from string import punctuation  
import re
import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords

commitDict = {}

def clusterKMeans():
    X,commitkeyList,commitmessList = getTFIDFMatrix()
    clf = KMeans(n_clusters=600)  
    s = clf.fit(X)
    #clf.plot()
    print s

    #9个中心
    print '中心',clf.cluster_centers_

    #每个样本所属的簇
    print '每个样本所属的簇',clf.labels_,type(clf.labels_)

    #用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数
    print clf.inertia_
    saveClusterResult(commitkeyList,commitmessList,clf.labels_)

    #进行预测
    #print clf.predict(feature)

    #保存模型
    #joblib.dump(clf , '/home/happy/model/km.pkl')

    #载入保存的模型
    #clf = joblib.load('/home/happy/model/km.pkl')

    #用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数
    #for i in range(5,30,1):
    #clf = KMeans(n_clusters=i)
    #s = clf.fit(feature)
    #print i , clf.inertia_


def saveClusterResult(commitkeyList,commitmessList,labels):
    global commitDict
    #for i in range(len(commitkeyList)):
        #print commitidList[i],commitDict[commitidList[i]][0],
        #clusterList.append((commitkeyList[i].split('_')[0],commitkeyList[i].split('_')[1],commitDict[commitkeyList[i]][1],commitmessList[i].decode('utf-8','ignore').encode('utf-8'),labels[i]))
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        cur.execute('truncate table commit_cluster_600')
        for i in range(len(commitkeyList)):
            clusterList = (commitkeyList[i].split('_')[0],commitkeyList[i].split('_')[1],commitDict[commitkeyList[i]][1],commitmessList[i].decode('utf-8','ignore').encode('utf-8'),labels[i])
            sqli='insert into commit_cluster_600 (original_id,repository_id,sha,message_stem,cluster) values (%s,%s,%s,%s,%s);'
            cur.execute(sqli,clusterList)
            conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def getTFIDFMatrix():
    contentDict = getCommitMessListByReposId()
    print "commits count: ", len(contentDict)
    commitkeyList = contentDict.keys()
    commitmessList = contentDict.values()
    transformer=TfidfTransformer()
    vectorizer=CountVectorizer()
    tfidf=transformer.fit_transform(vectorizer.fit_transform(commitmessList))*10000000
    word=vectorizer.get_feature_names()
    print "feature维度：",len(word)
    #weight=tfidf.toarray()
    return tfidf,commitkeyList,commitmessList



def getCommitMessListByReposId():
    global commitDict
    contentDict = {}
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT id,repository_id,sha,message FROM commits where repository_id in (457, 274, 288, 256, 249, 135, 207, 460, 452, 1);')
        #linux, qemu, git, postgres, openssl, httpd, torque, lxc, libuv, abrt
        result = cur.fetchall()
        if None != result:
            for item in result:
                contentDict[str(item[0])+'_'+str(item[1])] = getStem(removePunctuationNum(item[3]))
                commitDict[str(item[0])+'_'+str(item[1])] = (item[1],item[2])
        conn.commit()
        cur.close()
        conn.close()
        return contentDict
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def removePunctuationNum(text):
    text = re.sub(r'[{}]+'.format('!"$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\n'),' ',text.decode('utf-8','ignore').encode('utf-8'))
    return text

def getStem(text):
    text = unicode( text , errors='ignore')
    st = nltk.LancasterStemmer()
    wordList = text.split(' ')
    stemList = []
    for word in wordList:
        word = filter(str.isalnum, str(word))
        temp_word = st.stem(word)
        if not temp_word in stopwords.words('english'):
            stemList.append(temp_word)
    return ' '.join(stemList)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    clusterKMeans()


