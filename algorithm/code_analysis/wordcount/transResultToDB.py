#coding=utf-8 
import urllib2  
import os
import sys
import socket
import MySQLdb
import chardet
import ssl


recordlist = []
recordlist_length = 10000
project_path = "/home/happy/code_vccfinder/project/"
#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = [(457,'linux'),(274,'qemu'),(288,'git'),(256,'postgres'),(249,'openssl'),(135,'httpd'),(207,'torque'),(460,'lxc'),(452,'libuv'),(1,'abrt')]

def getAllToDB(repos_list):
    for repos_id,repos_name in repos_list:
        getDataFromFile(repos_id,repos_name)
        
def getDataFromFile(repos_id,repos_name):
    file_path = project_path + "word_count/" + repos_name + "/part-r-00000"
    file_read = open(file_path,"r")
    for text in file_read.readlines():
        word = text.split('\t')[0]
        count = text.split('\t')[1]
        item = (repos_id,word,count)
        recordlist.append(item)
        tryToSaveDict()
    file_read.close()
    insertDataIntoDB()

def tryToSaveDict():
    if (len(recordlist)>recordlist_length):
        insertDataIntoDB()


def insertDataIntoDB():
    global recordlist
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sqli='insert into repos_count (repository_id,word,count) values (%s,%s,%s);'
        cur.executemany(sqli,recordlist)
        recordlist=[]
        print "clear recordlist"
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    getAllToDB(repos_list)
