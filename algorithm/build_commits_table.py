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

def buildCommitsTable():
    cur.execute("truncate table commits")
    names = os.listdir(codesetsDir)
    #print names
    gitlogfile = "/home/wangyu/code-mine/result/tmp_gitlog"
    sqlfile = open("../result/insert_commits_list", 'wr')
    repository_id = 1
    for name in names:
        os.chdir(codesetsDir + name)
        #os.system('rm ' + gitlogfile)
        #os.system('git log --pretty=format:"%H || %an || %ae || %ad  || %cn || %ce || %cd || %cn || %s" --stat -U1 -w > ' + gitlogfile)
        gitlog = open(gitlogfile)
        id = 0
        patch_count = -1
        patch = ""
        label = 1
        for line in gitlog:
            if line == '\n':
                continue
            type = 0 #1 for bug fix commit, 0 for non-bug-fix commit
            sha = ''
            author_email = ''
            author_name = ''
            author_when = ''
            committer_email = ''
            committer_name = ''
            committer_when = ''
            additions = 0
            deletions = 0
            total_changes = 0
            message = ''

            if line.count(' || ') == 8:
                if label == 0:
                    continue
                if label == 1:
                    label = 0
                id += 1
                patch_count = 0
                print "============================"
                print id
                print patch
                if id > 5:
                    break
                patch = ""
                strings = line.split(' || ')
                text = strings[8].lower()
                all = text.count("error") + text.count("bug") + text.count("fix") + text.count("issue") + text.count("mistake") + text.count("incorrect") + text.count("fault") + text.count("defect") + text.count("flaw")
                if all > 0:
                    type = 1
                #print type
                sha = strings[0]
                author_email = strings[2]
                author_name = strings[1]
                author_when = formatDatetime(strings[3])
                committer_email = strings[5]
                committer_name = strings[4]
                committer_when = formatDatetime(strings[6])
                message = text
                continue

            if line.find("file changed,") != -1 or line.find("files changed,") != -1:
                label = 1
                strings = line.split(', ')
                if len(strings) == 3:
                    insertion = strings[1]
                    additions = insertion.split()[0]
                    deletions = strings[2].split()[0]
                if len(strings) == 2:
                    if strings[1].find("insertion") != -1:
                        additions = strings[1].split()[0]
                    if strings[1].find("deletion") != -1:
                        deletions = strings[1].split()[0]
                total_changes = int(additions) + int(deletions)
                continue

            if line.find("diff --git") != -1 and patch_count == 0:
                patch_count = 1
                patch += line
                continue

            if patch_count == 1:
                patch += line
                #print patch
        #sql = "insert into repositories values ("+str(id)+", '"+name+"', '"+description+"', null, '"+created_at+"', '"+updated_at+"', "+forks_count+", "
        #sql += str(stargazers_count)+", "+str(watchers_count)+", null, "+str(open_issues_count)+", "+str(pull_request_count)+", "+str(size)+", '"+language+"', '"
        #sql += default_branch+"', '"+git_url+"', "+str(distinct_authors_count)+", "+str(commits_count)  +")"
        #print sql
        #sqlfile.writelines(sql+"\n")
        #cur.execute(sql)
        repository_id += 1
        gitlog.close()
        break
    sqlfile.close()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    buildCommitsTable()
    cur.close()
    conn.commit()
    conn.close()
