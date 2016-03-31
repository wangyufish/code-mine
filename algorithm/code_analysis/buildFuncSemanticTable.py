#coding=utf-8 
import urllib2  
import os
from bs4 import BeautifulSoup
import sys
import socket
import MySQLdb
import chardet
import ssl
import string
from string import punctuation  
import re
import sys

project_path = "/media/wangyu/My_Device1/research_data/github/codeset_10/"
functionList = []
functionList_length = 10000

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = [(457,'linux'),(274,'qemu'),(288,'git'),(256,'postgres'),(249,'openssl'),(135,'httpd'),(207,'torque'),(460,'lxc'),(452,'libuv'),(1,'abrt')]

def genTagsFile():
    for repos_id, repos_name in repos_list:
        repos_path = project_path + repos_name + "/"
        tagsfile = repos_path + "tags"
        if not os.path.exists(tagsfile):
            os.chdir(repos_path)
            os.system("ctags -R *")
    for repos_id, repos_name in repos_list:
        repos_path = project_path + repos_name + "/"
        tagsfile = repos_path + "tags"
        if not os.path.exists(tagsfile):
            return False
    return True

def extractFunctionName():
    for repos_id, repos_name in repos_list:
        repos_path = project_path + repos_name + "/"
        print repos_path
        tagsfile = open(repos_path + "tags", "r")
        for line in tagsfile:
            if line.find("\tf\tfile:") != -1:
                words = line.split("\t")
                item = (words[0], repos_id)
                functionList.append(item)
                tryToSaveDict(False)
        tryToSaveDict(True)
        tagsfile.close()

def tryToSaveDict(isEnd):
    if (len(functionList)>functionList_length) or isEnd == True:
        insertFuncDictIntoDB()

def insertFuncDictIntoDB():
    global functionList
    print len(functionList)
    try:
        conn=MySQLdb.connect(host='192.168.162.122',user='wangyu',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sqli='insert into func_semantic (func_name, repos_id) values (%s,%s);'
        cur.executemany(sqli,functionList)
        functionList=[]
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" ) 
    is_tagfile = genTagsFile()
    if not is_tagfile:
        print "Some projects don't have tags file!"
        exit()
    extractFunctionName()