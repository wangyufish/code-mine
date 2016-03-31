#coding=utf-8
import sys
import MySQLdb

hadoop_output = "/home/wangyu/hadoop/output/part-r-00000"
output_path = "/home/wangyu/code-mine/result/frequent_word_mining"

def substringList(word, k):
    if len(k) > len(word):
        return -1
    substrings = []
    for i in range(k, len(word)):
        for j in range(0, len(word) - i):
            substring = word[j: j + i]
            substrings.append(substring)
    return substrings

def frequentWordMining():
    basic_words = []
    inputfile = open(hadoop_output)
    outputfile = open(output_path, "wr")
    last_word = ""
    last_count = 0

    max_word = ""
    max_count = 0
    for line in inputfile:
        tmpArray = line.split()
        sub_word = tmpArray[0].replace("_", " ")
        count = int(tmpArray[1])
        if count < 5:
            continue
        if max_word != "" and max_count != 0:
            if sub_word.find(last_word) != -1:
                if max_count <= count:
                    max_count = count
                    max_word = sub_word
            else:
                basic_words.append(max_word)
                outputfile.writelines(max_word + " " + str(max_count) + "\n")
                max_word = ""
                max_count = 0
        else:
            max_word = sub_word
            max_count = count
        last_word = sub_word
        last_count = count

        #if last_word != "" and count >= last_count and sub_word.find(last_word) != -1:
        #    last_count = count
        #    last_word = sub_word
        #else:
        #    basic_words.append(last_word)
            #print sub_word + " " + str(count)
        #    outputfile.writelines(last_word + " " + str(last_count) + "\n")
        #    last_count = count
        #    last_word = sub_word
    return basic_words

def writeBasicWordsToDB():
    basic_words = frequentWordMining()
    try:
        conn=MySQLdb.connect(host='192.168.162.122',user='wangyu',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sql='select func_id, func_name from func_semantic;'
        count = cur.execute(sql)
        info = cur.fetchmany(count)
        for id, name in info:
            current_basic = ""
            for basic_word in basic_words:
                if name.find(basic_word) != -1:
                    current_basic += basic_word + ' '
            if current_basic != "":
                sql = "update func_semantic set basic_words = '"+current_basic+"' where func_id = '"+str(id)+"'"
                print sql
                cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print e
        raise

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    writeBasicWordsToDB()
    