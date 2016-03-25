#coding=utf-8
import sys
import MySQLdb
from nltk.stem.lancaster import LancasterStemmer

def getWordList():
    try:
        conn = MySQLdb.connect(host='192.168.162.122',user='wangyu',passwd='123456',port=3306)
        cur = conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sql = "select id, word from repos_count_after_filter"
        count = cur.execute(sql)
        info = cur.fetchmany(count)
        st = LancasterStemmer()
        for id, word in info:
            etyma = st.stem(word)
            print id
            sql = "update repos_count_after_filter set etyma = '"+etyma+"' where id = '"+str(id)+"'"
            print sql
            cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        return info
    except MySQLdb.Error, e:
        print e
        raise

def buildRootWordDic():
    rootword_dic = {}
    info = getWordList()
    st = LancasterStemmer()
    for id, word in info:
        text = st.stem(word)
        if text not in rootword_dic:
            rootword_dic[text] = [word]
        else:
            rootword_dic[text].append(word)
    output = open("../../result/similar_word_combine_results", "wr")
    for rootword in rootword_dic:
        if len(rootword_dic[rootword]) > 1:
            #print rootword + ":" + str(rootword_dic[rootword])
            output.writelines(rootword + ":" + str(rootword_dic[rootword]) + "\n")
    return rootword_dic

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    buildRootWordDic()