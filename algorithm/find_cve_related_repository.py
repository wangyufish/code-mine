#coding=utf-8
import os

def findCVERelatedRepo():
    cveDataFile = open("../data/cve/allitems.txt")
    repoFile = open("../data/cve/githubrepo", "w")
    repo_list = list()
    for line in cveDataFile:
        if line.find("github.com/") != -1:
            tmprepo = line[line.find("github.com/") + 11 : len(line)]
            index = tmprepo.find("/")
            index2 = tmprepo.find("/", index + 1)
            repo = tmprepo[0 : index2]
            git_repo = "git@github.com:" + repo + ".git"
            if git_repo not in repo_list:
                repo_list.append(git_repo)
    for repo in repo_list:
        repoFile.write(repo + '\n')
    cveDataFile.close()
    repoFile.close()
    return repo_list

def batchDownloadRepo(repo_list):
    codesetDir = "/media/wangyu/My_Device/科研数据/github/codeset"
    os.chdir(codesetDir)
    for repo in repo_list:
        print 'git clone ' + repo
        var = os.system('git clone ' + repo)
        if var != 0:
            print "error: " + repo

#repo_list = findCVERelatedRepo()
#batchDownloadRepo(repo_list)