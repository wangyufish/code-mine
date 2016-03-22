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
taglist=[]
taglist_length = 10000

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = [(457,'linux'),(274,'qemu'),(288,'git'),(256,'postgres'),(249,'openssl'),(135,'httpd'),(207,'torque'),(460,'lxc'),(452,'libuv'),(1,'abrt')]


def getAllTag(repos_list):
    for repos_id,repos_name in repos_list:
        getReposTag(repos_id,repos_name)

def getReposTag(repos_id,repos_name):
    count = 0
    repos_tag_path = project_path + repos_name + "/tags"
    file_read = open(repos_tag_path,"r")
    for text in file_read.readlines():
        count = count + 1
        text = text.strip()
        flag = 1
        other = ""
        field = ""
        if "/^" in text:
            splits = text.split('\t')
            name = splits[0]
            file = splits[1]
            start = text.find("/^")
            end = text.find('$/;\"',start)
            address = text[start:end+4]
            splits1 = text[end+4:len(text)].split('\t')
            if len(splits1) == 2:
                kind = splits1[1]
            elif len(splits1) == 3:
                kind = splits1[1]
                if splits1[2].endswith(':'):
                    field = splits1[2]
                else:
                    other = splits1[2]
            elif len(splits1) == 4:
                kind = splits1[1]
                if splits1[3].endswith(':'):
                    other = splits1[2]
                    field = splits1[3]
                else:
                    other = splits1[2] + '\t' + splits1[3]
            elif len(splits1) == 5:
                kind = splits1[1]
                if splits1[4].endswith(':'):
                    other = splits1[2] + '\t' + splits1[3]
                    field = splits1[4]
                else:
                    print 'type0',splits1,len(splits1),count
                    flag = 0
            else:
                print 'type1',splits1,len(splits1),count
                flag = 0
        else:
            splits = text.split('\t')
            if len(splits) == 4:
                name,file,address,kind = text.split('\t')
            elif len(splits) == 5:
                if splits[4].endswith(':'):
                    name,file,address,kind,field = text.split('\t')
                else:
                    name,file,address,kind,other = text.split('\t')
            elif len(splits) == 6:
                name,file,address,kind,other,field = text.split('\t')
            else:
                print 'type2',splits,len(splits),count
                flag = 0
        if 1 == flag:
            item = (repos_id,name,file,address,kind,other,field)
            taglist.append(item)
        tryToSaveTag()
    file_read.close()
    insertTagIntoDB()

def tryToSaveTag():
    if (len(taglist)>taglist_length):
        insertTagIntoDB()


def insertTagIntoDB():
    global taglist
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sqli='insert into tag_content (repository_id,tagname,tagfile,tagaddress,kind,tagother,field) values (%s,%s,%s,%s,%s,%s,%s);'
        cur.executemany(sqli,taglist)
        taglist=[]
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    getAllTag(repos_list)
