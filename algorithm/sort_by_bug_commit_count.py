#!/usr/bin/python
import os

def getBugCommitCount():
    file_read = open("../data/node_gitlog","r")
    file_write =file("../result/commit_bug_result","a+")
    dict_result = {}
    file_list = []
    desc = ""
    flag = 0
    #error, bug, fix, issue, mistake, incorrect, fault, defect and flaw.
    for text in file_read.readlines():
        if flag==0:
            flag = 1
        elif text.startswith("commit"):
            text = desc.lower()
            all = text.count("error") + text.count("bug") + text.count("fix") + text.count("issue") + text.count("mistake") + text.count("incorrect") + text.count("fault") + text.count("defect") + text.count("flaw")
            if(all > 0):
		for file_name in file_list:
                    if file_name in dict_result:
                        dict_result[file_name] = dict_result[file_name] + 1
                    else:
                        dict_result[file_name] = 1
            desc = ""
            file_list = []
        else:
            if("|" not in text):
                desc = desc + text
            else:
                file_log = text.split('|')
                file_name = file_log[0]
                file_list.append(trimstr(file_name))
    text = desc.lower()
    all = text.count("error") + text.count("bug") + text.count("fix") + text.count("issue") + text.count("mistake") + text.count("incorrect") + text.count("fault") + text.count("defect") + text.count("flaw")
    if(all > 0):
        for file_name in file_list:
            if file_name in dict_result:
                dict_result[file_name] = dict_result[file_name] + 1
            else:
                dict_result[file_name] = 1
    str = sorted(dict_result.items(), key=lambda dict_result:dict_result[1],reverse=1)
    for str1 in str:
        file_write.writelines("file:%s,count:%d" % (str1[0],str1[1]) +"\n")

    file_read.close()
    file_write.close()

def trimstr(zstr):
    ystr=zstr.lstrip()
    ystr=ystr.rstrip()
    ystr=ystr.strip()
    return ystr

if __name__ == '__main__':
    getBugCommitCount()



