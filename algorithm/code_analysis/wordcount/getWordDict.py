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

project_path = "/home/happy/code_vccfinder/project/"
worddictlist=[]
worddictlist_length = 10000

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = [(457,'linux'),(274,'qemu'),(288,'git'),(256,'postgres'),(249,'openssl'),(135,'httpd'),(207,'torque'),(460,'lxc'),(452,'libuv'),(1,'abrt')]

def getAllDict(repos_list):
    for repos_id,repos_name in repos_list:
        getWordDict(repos_id,repos_name)
        
def getWordDict(repos_id,repos_name):
    count =1
    repos_path = project_path + repos_name + "/"
    for root, dirs, files in os.walk(repos_path):
        for file in files:
            file_path = root + "/" + file
            if ".git" in file_path: 
                continue
            elif "tags"==file: 
                continue
            elif "/tags"==file: 
                continue
            elif file.endswith(".pdf"): 
                continue
            else:
                print root + "/" + file,count
                count = count + 1
                file_read = open(file_path,"r")
                original_content = file_read.read()
                file_read.close()
                file_content = str(getDict(removePunctuationNum(original_content)))
                item = (repos_id,file_path,file_content)
                worddictlist.append(item)
                tryToSaveDict()
    insertWordDictIntoDB()
    print count

def tryToSaveDict():
    if (len(worddictlist)>worddictlist_length):
        insertWordDictIntoDB()


def insertWordDictIntoDB():
    global worddictlist
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sqli='insert into word_dict (repository_id,file_path,file_content) values (%s,%s,%s);'
        cur.executemany(sqli,worddictlist)
        worddictlist=[]
        print "clear worddictlist"
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

def removePunctuationNum(text):
    text = text.strip().lower()
    text = re.sub(r'[{}]+'.format(string.punctuation),' ',text.decode('utf-8','ignore').encode('utf-8'))
    table = string.maketrans("1234567890\\\n\t\r","              ")  
    text = text.translate(table) 
    return text

def getDict(str):
    dict = {}
    strlist = str.split(' ')
    for text in strlist:
        if text in dict.keys():
            dict[text] += 1
        else:
            dict[text] = 1
    return dict


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" ) 
    getAllDict(repos_list)
