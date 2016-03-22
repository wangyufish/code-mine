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
from collections import Counter

project_path = "/home/happy/code_vccfinder/project/"
worddictlist=[]
worddictlist_length = 10000
file_count=0

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = [(457,'linux'),(274,'qemu'),(288,'git'),(256,'postgres'),(249,'openssl'),(135,'httpd'),(207,'torque'),(460,'lxc'),(452,'libuv'),(1,'abrt')]

def getAllDict(repos_list):
    for repos_id,repos_name in repos_list:
        getWordDict(repos_id,repos_name)
        
def getWordDict(repos_id,repos_name):
    count =1
    repos_path = project_path + repos_name + "/"
    write_path = project_path + "word_count/" + repos_name +"/" + repos_name
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
            elif file.endswith(".png"):
                continue
            elif file.endswith(".jpg"):
                continue
            elif file.endswith(".svg"): 
                continue
            elif file.endswith(".pyc"): 
                continue
            elif file.endswith(".ico"): 
                continue
            elif file.endswith(".icns"):
                continue
            elif file.endswith(".tar"):
                continue
            elif file.endswith(".zip"): 
                continue
            elif file.endswith(".ico"): 
                continue
            elif file.endswith(".vbs"): 
                continue
            elif file.endswith(".gif"): 
                continue
            elif file.endswith(".ps"):
                continue
            elif file.endswith(".fig"):
                continue
            elif file.endswith(".bmp"): 
                continue
            elif file.endswith(".svg"): 
                continue
            elif file.endswith(".pem"):
                continue
            elif file.endswith(".crl"):
                continue
            else:
                print root + "/" + file,count
                count = count + 1
                file_read = open(file_path,"r")
                original_content = file_read.read()
                file_read.close()
                d = getDict(removePunctuationNum(original_content))
                file_content = str(d)
                item = (repos_id,file_path,file_content,d)
                worddictlist.append(item)
                tryToSaveDict(write_path)
    insertWordDictIntoFile(write_path)
    print count

def tryToSaveDict(write_path):
    if (len(worddictlist)>worddictlist_length):
        insertWordDictIntoFile(write_path)


def insertWordDictIntoFile(write_path):
    global worddictlist
    global file_count
    print 'insert',len(worddictlist)
    file_write =file(write_path+str(file_count),"a+")
    for item in worddictlist:
        worddict = item[3]
        c = Counter(worddict)
        del c['']
        l = list(c.elements())
        file_write.writelines(' '.join(l).decode('utf-8','ignore').encode('utf-8') + ' ')
    file_write.close()
    worddictlist=[]
    file_count = file_count + 1
    print "clear worddictlist"
    
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
