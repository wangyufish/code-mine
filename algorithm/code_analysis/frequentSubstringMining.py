#coding=utf-8
import sys
import MySQLdb

def substringList(word, k):
    if len(k) > len(word):
        return -1
    substrings = []
    for i in range(k, len(word)):
        for j in range(0, len(word) - i):
            substring = word[j: j + i]
            substrings.append(substring)
    return substrings

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    substrings = substringList('wangyushiwenguo', 4)
    print substrings