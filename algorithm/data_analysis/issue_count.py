#coding=utf-8 
import urllib2  
import os
from bs4 import BeautifulSoup
import sys
import socket
import MySQLdb
import chardet
import ssl

localissuepath = '../data/allissues/issues/'
localissuepagepath = '../data/allissues/issuepages/'
localissuelistpath = '../data/allissues/issuelists/'
localurl = 'https://github.com'
addurl = '/nodejs/node/issues'
basefilename = "issues_result.html"
allissueurl = "issues_url.txt"
file_start = "issues_result_page_"
file_end = ".html"
issueinfo_start = "issues_info_"
issueinfo_end = ".txt"
issuelist = []
issuelist_length = 100

# get local issue page
def getLocalIssue(url,filename):
    print "url:%s"%url  
    print "filename:%s"%filename
    try:   
        #if file not exists
        filepath = localissuelistpath + filename
        if not os.path.exists(filepath):
            response = urllib2.urlopen(url,timeout = 10)
            html = response.read() 
            file_write =file(filepath,"a+")
            file_write.writelines(html)
            file_write.close() 
    #2.6  
    except urllib2.URLError, e:  
        print "error 2.6"
        print e.__class__
        getLocalIssue(url,filename)
    #2.7
    except socket.timeout, e:
        print "error 2.7"
        print e.__class__
        getLocalIssue(url,filename)
    except ssl.SSLError, e:
        print e.__class__
        getLocalIssue(url,filename)
    except Exception, e:
        print e.__class__
        getLocalIssue(url,filename)
        raise
    
# get btn-link pages(open and closed)
def getBtnLink(filename):
    soup = BeautifulSoup(open(filename))
    soup1=soup.find_all("a",class_="btn-link")
    for child in soup1:
        print "btn-link-href:%s"%child.get("href")
        str = child.get("href")
        getNextPage(str)

# get next page and save the issue page urls to file
def getNextPage(addurl1):
    print 'NowPage:%s'%addurl1
    file_middles = addurl1.split('/')
    file_middle = file_middles[len(file_middles)-1]
    filename = file_start + file_middle + file_end
    getLocalIssue(localurl+addurl1,filename)
    getIssuePagesUrl(localissuelistpath+filename)
    soup = BeautifulSoup(open(localissuelistpath+filename))
    soup1=soup.find("div",class_="paginate-container")
    str1 = ['next']
    nextpage = soup1.find("a",class_="next_page")
    if nextpage:
        href = nextpage.get("href")
        print 'NextPage:%s'%href
        getNextPage(href)

# get issue page url
def getIssuePagesUrl(filename):
    soup = BeautifulSoup(open(filename))
    soup1=soup.find("ul",class_="table-list table-list-bordered table-list-issues js-navigation-container js-active-navigation-container")
    file_write =file(allissueurl,"a+")
    for child in soup1.find_all("div",class_="table-list-cell issue-title"):
        file_write.writelines(child.find("a").get("href") + "\n")
    file_write.close()



# get issue pages from the urls
def getIssuePages():
    file_read = open(allissueurl,"r")
    for addurl1 in file_read.readlines():
        strs = addurl1.split('/')
        issue_id = trimstr(strs[len(strs)-1])
        url = localurl+trimstr(addurl1)
        filename = issueinfo_start + issue_id + issueinfo_end
        parseIssuePageInfor(url,filename)
    insertIssueInforIntoDB()
    file_read.close()

# parse issue pages
def parseIssuePageInfor(url,filename):
    try:  
        print "url:%s"%url  
        print "filename:%s"%filename
        filepath = localissuepagepath + filename
        if not os.path.exists(filepath):
            response = urllib2.urlopen(url,timeout = 10)
            html = response.read() 
            file_write =file(filepath,"a+")
            file_write.writelines(html)
            file_write.close() 
            insertIssueInforIntoFile(html,filename) 
    #2.6  
    except urllib2.URLError, e:  
        print "error 2.6"
        print e.__class__
        insertIssueInforIntoDB()
        parseIssuePageInfor(url,filename)
    #2.7
    except socket.timeout, e:
        print "error 2.7"
        print e.__class__
        insertIssueInforIntoDB()
        parseIssuePageInfor(url,filename)
    except ssl.SSLError, e:
        insertIssueInforIntoDB()
        print e.__class__
        parseIssuePageInfor(url,filename)
    except Exception, e:
        insertIssueInforIntoDB()
        print e.__class__
        raise

# save issue information
def insertIssueInforIntoFile(html,filename):
    global issuelist
    global issuelist_length
    file_write =file(localissuepath + filename,"a+")
    soup = BeautifulSoup(html)
    soup1=soup.find("span",class_="js-issue-title")
    title=soup1.string
    soup2=soup.find("span",class_="gh-header-number")
    issue_id=soup2.string.split('#')[1]
    print issue_id
    soup4=soup.find("div",class_="labels css-truncate")
    tag=""
    for child in soup4.find_all("a"):
        tag=tag + "|" + child.string
    if tag.startswith("|"):
        tag=tag[1:len(tag)]
    try:
        soup3=soup.find("div",class_="js-discussion js-socket-channel")
        for child in soup3.find_all("div",class_="timeline-comment-wrapper js-comment-container"):
            print "find issue"
            contents=child.find("div",class_="edit-comment-hide")
            content=""
            for child1 in contents.strings:
                content=content + child1
            content = trimstr(content)
            name=child.find("a",class_="author").string
            time_temp=child.find("time").get("datetime")
            time=time_temp.split('T')[0]+' '+(time_temp.split('T')[1]).split('Z')[0]
            content = content.decode('utf-8','ignore').encode('utf-8')
            file_write.writelines("issue_id:%s,title:%s,name:%s,time:%s,content:%s,project:%s,tag:%s" % (issue_id,title,name,time,content,"node",tag) +"\n")
            temp_issue = (issue_id,title,name,time,content,tag,"node")
            issuelist.append(temp_issue)
        print "before insert:%d"%len(issuelist)
        if (len(issuelist)>issuelist_length):
            insertIssueInforIntoDB()
            print "insert"
        else:
            print "no insert"
    except Exception,e:
        print e
        insertIssueInforIntoDB()
    finally:
        file_write.close()

# save issue information to db
def insertIssueInforIntoDB():
    global issuelist
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('code_mine')
        sqli='insert into issues (issue_id,title,name,time,content,tag,project) values (%s,%s,%s,%s,%s,%s,%s);'
        cur.executemany(sqli,issuelist)
        issuelist=[]
        print "clear issuelist"
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

# trim str
def trimstr(zstr):
    ystr=zstr.lstrip()
    ystr=ystr.rstrip()
    ystr=ystr.strip()
    return ystr

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    getLocalIssue(localurl+addurl,basefilename)
    getBtnLink(localissuelistpath + basefilename)
    getIssuePages()


