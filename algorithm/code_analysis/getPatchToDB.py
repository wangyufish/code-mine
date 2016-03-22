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
import re
import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
reposNameDict = {}
reposNameDict[457]='linux'
reposNameDict[274]='qemu'
reposNameDict[288]='git'
reposNameDict[256]='postgres'
reposNameDict[249]='openssl'
reposNameDict[135]='httpd'
reposNameDict[207]='torque'
reposNameDict[460]='lxc'
reposNameDict[452]='libuv'
reposNameDict[1]='abrt'

patchList = []

hubpathprefix = '/home/happy/git_vccfinder/project/'

def getPatchDB():
    global hubpathprefix
    global reposNameDict
    for reposId in [1,452,460,207,135,249,256,288,274,457]:
        results = getCommitMessListByReposId(reposId)
        count = 0;
        flag = 0;
        if(None != results):
            for item in results:
                id = item[0]
                repository_id = item[1]
                sha = item[2]
                if flag ==0:
                    projectName = reposNameDict[int(repository_id)]
                    allPath = hubpathprefix + projectName + '/'
                    os.chdir(allPath)
                patch = getPatchBySha(id,repository_id,sha)
                count = count + 1
                if(count>10):
                    count = 0
                    savePatchToDB()
        savePatchToDB()

def getPatchBySha(id,repository_id,sha):
    cmd = 'git show '+sha+' --pretty=format:\"\"'
    code = execCmd(cmd)
    patchList.append((id,repository_id,sha,code))  


def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return trimstr(text)


def trimstr(zstr):
    ystr=zstr.lstrip()
    ystr=ystr.rstrip()
    ystr=ystr.strip()
    return ystr

def savePatchToDB():
    global patchList
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        sqli='insert into commit_patch (id,repository_id,sha,code) values (%s,%s,%s,%s);'
        cur.executemany(sqli,patchList)
        patchList = []
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def getCommitMessListByReposId(reposId):
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT id,repository_id,sha FROM commits_words where repository_id=%s;'%reposId)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    getPatchDB()

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
