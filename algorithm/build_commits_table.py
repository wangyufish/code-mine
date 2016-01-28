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

codesetsDir = "/media/wangyu/My_Device/research_data/github/codeset/"
codewarehouseDir = "/media/wangyu/My_Device/research_data/github/codewarehouse/"

def buildCommitsTable():
    cur = conn.cursor()
    cur.execute("truncate table commits")
    os.system("rm -rf " + codewarehouseDir + "/*")
    names = os.listdir(codesetsDir)
    #print names
    gitlogfile = "/home/wangyu/code-mine/result/tmp_gitlog"
    repository_id = 1
    for name in names:
        cur = conn.cursor()
        os.system("mkdir " + codewarehouseDir + name)
        patchDir = codewarehouseDir+name
        os.chdir(codesetsDir + name)
        os.system('rm ' + gitlogfile)
        os.system('git log --pretty=format:"%H || %an || %ae || %ad  || %cn || %ce || %cd || %cn || %s" --stat -U1 -w > ' + gitlogfile)
        gitlog = open(gitlogfile)
        id = 0
        is_bug_fixed = 0 #1 for bug fix commit, 0 for non-bug-fix commit
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
        patch_count = -1
        patch = ""
        files_changed = ""

        is_changed_file = 1

        for line in gitlog:
            if line == '\n':
                continue
            if line.count(' || ') == 8:
                strings = line.split(' || ')
                if strings[2].find("@") == -1 or strings[5].find("@") == -1 or formatDatetime(strings[3]) == -1 or formatDatetime(strings[6]) == -1:
                    continue
                print line
                patch_count = 0
                is_changed_file = 1
                if id > 0:
                    #print id
                    #print repository_id
                    #print is_bug_fixed
                    #print sha #url
                    #print author_email
                    #print author_name
                    #print author_when
                    #print committer_email
                    #print committer_name
                    #print committer_when
                    #print additions
                    #print deletions
                    #print total_changes
                    #print message
                    #print patch #cve
                    #print files_changed
                    if patch == "":
                        patchfile = "null"
                    else:
                        patchfile = patchDir + "/" + sha
                        os.system("touch " + patchfile)
                        output = open(patchfile, 'wr')
                        output.write(patch)
                        output.close()
                    if files_changed == "":
                        files_changed = "null"
                    sql = "insert into commits values ("+str(id)+", '"+str(repository_id)+"', '"+str(is_bug_fixed)+"', '"+sha+"', null, '"+author_email+"', '"
                    sql += author_name+"', '"+author_when+"', '"+committer_email+"', '"+committer_name+"', '"+committer_when+"', "+str(additions)+", "+str(deletions)+", "
                    sql += str(total_changes)+", '"+message+"', '"+patchfile+"', null, '"+files_changed +"')"
                    print sql
                    print "=================================\n"
                    cur.execute(sql)

                patch = ""
                files_changed = ""
                is_bug_fixed = 0
                text = strings[8].lower()
                all = text.count("error") + text.count("bug") + text.count("fix") + text.count("issue") + text.count("mistake") + text.count("incorrect") + text.count("fault") + text.count("defect") + text.count("flaw")
                if all > 0:
                    is_bug_fixed = 1
                sha = strings[0]
                author_email = strings[2].replace("'", "")
                author_name = strings[1].replace("'", " ").replace('\"', '').replace('\\', '')
                author_when = formatDatetime(strings[3])
                committer_email = strings[5].replace("'", "")
                committer_name = strings[4].replace("'", " ").replace('\"', '').replace('\\', '')
                committer_when = formatDatetime(strings[6])
                message = text.replace("'", "")
                id += 1
                continue

            if line.find("file changed,") != -1 or line.find("files changed,") != -1:
                if line.find("(+)") == -1 and line.find("(-)") == -1:
                    continue
                if line.count('%d') > 0:
                    continue
                print line
                is_changed_file = 0
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
                patch = line
                continue

            if patch_count == 1:
                patch += line

            if line.count(' | ') == 1 and is_changed_file == 1:
                print line
                strings = line.split(' | ')
                files_changed += strings[0].rstrip().lstrip().replace("'", "") + " "
        repository_id += 1
        gitlog.close()
        cur.close()
        conn.commit()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    buildCommitsTable()
    conn.close()
