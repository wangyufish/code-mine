#coding=utf-8
import os
import MySQLdb
import urllib2
from bs4 import BeautifulSoup
import socket
import chardet
import sys
import ssl
from file_rank import formatDatetime

conn= MySQLdb.connect(
    host='localhost',
    port = 3306,
    user='root',
    passwd='wangyu',
    db ='vccfinder',
)
cur = conn.cursor()

codesetsDir = "/media/wangyu/My_Device/科研数据/github/codeset/"

def buildRepoTable():
    cur.execute("truncate table repositories")
    names = os.listdir(codesetsDir)
    #print names
    tmpfile = "/home/wangyu/tmp"
    sqlfile = open("../result/insert_sql_list", 'wr')
    id = 1
    for name in names:
        #print id
        #print name
        os.chdir(codesetsDir + name)
        os.system('git log --pretty=format:"%ae, %cd" > ' + tmpfile)
        tmp = open(tmpfile)
        lists = list()
        authors = list()
        count = 0
        for line in tmp:
            count += 1
            pairs = line.split(',')
            if pairs[0] not in authors:
                authors.append(pairs[0])
            lists.append(pairs[1])
        created_at = formatDatetime(lists[len(lists) - 1].lstrip().rstrip())
        #print created_at
        updated_at = formatDatetime(lists[0].rstrip().lstrip())
        #print updated_at
        distinct_authors_count = len(authors)
        #print authors
        #print distinct_authors_count
        commits_count = count
        #print commits_count

        os.chdir(codesetsDir)
        tmp.close()
        os.system('du -s ' + name + ' > ' + tmpfile)
        tmp = open(tmpfile)
        size = -1
        for line in tmp:
            words = line.split()
            size = words[0]
            break
        #print size

        configFile = open(codesetsDir + name + '/.git/config')
        default_branch = ''
        git_url = ''
        for line in configFile:
            if line.find('[branch') != -1:
                words = line.split('"')
                default_branch = words[1]
            if line.find('url = ') != -1:
                words = line.split()
                git_url = words[2]
        #print default_branch
        #print git_url
        configFile.close()
 
        tmp.close()
        #print[id, name, created_at, updated_at, size, default_branch, git_url, distinct_authors_count, commits_count]
        web_url = git_url[0 : len(git_url) - 4].replace('git@github.com:', 'https://github.com/')
        print "\n" + web_url
        response = urllib2.urlopen(web_url,timeout = 30)
        html = response.read()
        tmp = open(tmpfile, 'wr')
        tmp.writelines(html)
        tmp.close()
        soup = BeautifulSoup(open(tmpfile))
        soup1=soup.find("span", class_ = "repository-meta-content")
        span = str(soup1)
        raw_span = span[span.index('<span class="repository-meta-content">') + len('<span class="repository-meta-content">') : span.index('</span>')]
        description = raw_span.lstrip().rstrip().replace("'", " ").replace("…", " ").replace("™", "").replace("’", " ")
        #print description
        soup1 = soup.find_all("a", class_ = "social-count")
        stargazers_count = -1
        watchers_count = -1
        forks_count = -1
        for child in soup1:
            #print child.get("href")
            if child.get("href").find("watchers") != -1:
                watchers_count = child.get_text().rstrip().lstrip().replace(',', '')
                #print watchers_count
            if child.get("href").find("stargazers") != -1:
                stargazers_count = child.get_text().rstrip().lstrip().replace(',', '')
                #print stargazers_count
            if child.get("href").find("network") != -1:
                forks_count = child.get_text().rstrip().lstrip().replace(',', '')
                #print forks_count
        soup1 = soup.find_all("span", class_ = "counter")
        if len(soup1) == 2:
            open_issues_count = soup1[0].get_text().rstrip().lstrip().replace(',', '')
            pull_request_count = soup1[1].get_text().rstrip().lstrip().replace(',', '')
        else:
            if len(soup1) == 1:
                open_issues_count = 0
                pull_request_count = soup1[0].get_text().rstrip().lstrip().replace(',', '')
            else:
                open_issues_count = 0
                pull_request_count = 0
        #print open_issues_count
        #print pull_request_count

        soup1 = soup.find("div", class_ = "repository-lang-stats")
        soup2 = soup1.find("li").find("span", class_ = "lang")
        language = soup2.get_text().rstrip().lstrip()
        #print language

        sql = "insert into repositories values ("+str(id)+", '"+name+"', '"+description+"', null, '"+created_at+"', '"+updated_at+"', "+forks_count+", "
        sql += str(stargazers_count)+", "+str(watchers_count)+", null, "+str(open_issues_count)+", "+str(pull_request_count)+", "+str(size)+", '"+language+"', '"
        sql += default_branch+"', '"+git_url+"', "+str(distinct_authors_count)+", "+str(commits_count)  +")"
        print sql
        sqlfile.writelines(sql+"\n")
        cur.execute(sql)
        id += 1
    sqlfile.close()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    buildRepoTable()
    cur.close()
    conn.commit()
    conn.close()
