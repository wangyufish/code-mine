#coding=utf-8
import MySQLdb
import string
import os
import urllib2
import datetime
from sklearn import svm

conn= MySQLdb.connect(
    host='localhost',
    port = 3306,
    user='root',
    passwd='wangyu',
    db ='code_mine',
)
cur = conn.cursor()

S = list()

def bagOfWords():
    sql = "select comment from commits"
    count = cur.execute(sql)
    info = cur.fetchmany(count)
    for comment in info:
        words = comment[0].split()
        for word in words:
            if word not in S:
                S.append(word)
    return S

def buildTrainVector(S):
    sql = "select commit_id, comment from commits where time < '2014-01-01 00:00:00'"
    count = cur.execute(sql)
    info = cur.fetchmany(count)
    X = [0 for i in range(len(info))]
    i = 0
    for record in info:
        X[i] = [0 for j in range(len(S))]
        words = record[1].split()
        for word in words:
            position = S.index(word)
            X[i][position] = 1
        i += 1
    return X

def buildTestVector(S):
    sql = "select commit_id, comment from commits where time >= '2014-01-01 00:00:00'"
    count = cur.execute(sql)
    info = cur.fetchmany(count)
    Z = dict()
    for record in info:
        commit_id = record[0]
        comment = record[1]
        words = record[1].split()
        feature = [0 for i in range(len(S))]
        for word in words:
            position = S.index(word)
            feature[position] = 1
        Z[commit_id] = feature
    return Z


def linearSVM(X, Z):
    n = len(X) / 2
    if len(X) % 2 == 0:
        m = 0
    else:
        m = 1
    y = [0] * n + [1] * n + [1] * m
    lin_svc = svm.LinearSVC(C=1.0).fit(X, y)
    for commit_id in Z:
        K = lin_svc.predict(Z.values())
        print K
        break

S = bagOfWords()
#print len(S)
X = buildTrainVector(S)
print len(X)
Z = buildTestVector(S)
linearSVM(X, Z)
