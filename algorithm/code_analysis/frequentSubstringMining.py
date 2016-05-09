#coding=utf-8
import os
import sys
sys.path.append("..")
import MySQLdb
import nlp.semantics_extraction
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

hadoop_output = "/home/wangyu/hadoop/output/part-r-00000"
output_path = "/home/wangyu/code-mine/result/frequent_word_mining"
code_dir = "/media/wangyu/My_Device1/research_data/github/codeset_10"

#linux 457,qemu 274,git 288,postgres 256,openssl 249,httpd 135,torque 207,lxc 460,libuv 452,abrt 1
repos_list = {457: 'linux', 274: 'qemu', 288: 'git', 256: 'postgres', 249: 'openssl', 135: 'httpd', 207: 'torque', 460: 'lxc', 452: 'libuv', 1: 'abrt'}

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

        '''if last_word != "" and count >= last_count and sub_word.find(last_word) != -1:
            last_count = count
            last_word = sub_word
        else:
            basic_words.append(last_word)
            #print sub_word + " " + str(count)
            outputfile.writelines(last_word + " " + str(last_count) + "\n")
            last_count = count
            last_word = sub_word'''
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

def buildFuncFileDic():
    func_file_dic = dict()
    try:
        conn=MySQLdb.connect(host='192.168.162.122',user='wangyu',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        sql='select func_id, func_name, file_path from func_semantic;'
        count = cur.execute(sql)
        info = cur.fetchmany(count)
        for id, name, file in info:
            if name in func_file_dic:
                func_file_dic[name].append(file)
            else:
                func_file_dic[name] = [file]
        conn.close()
        return func_file_dic
    except MySQLdb.Error,e:
        print e
        raise
    print "finish function-file dictionary building..."


def buildFileMessageDic():
    file_message_dic = dict()
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        sql="select files_changed, message from commits where repository_id in (457, 274, 288, 256, 249, 135, 207, 460, 452, 1) and files_changed != 'null';"
        count = cur.execute(sql)
        info = cur.fetchmany(count)
        for filestr, message in info:
            if filestr == "null":
                continue
            filter_message = filterMessage(message)
            files = filestr.split()
            for file in files:
                if file in file_message_dic:
                    file_message_dic[file] += " " + filter_message
                else:
                    file_message_dic[file] = filter_message
        print "finish file-message dictionary building..."
        cur.close()
        conn.close()
        return file_message_dic
    except MySQLdb.Error,e:
        print e
        raise


def buildFuncMessageDicViaFile():
    func_message_dic = dict()
    try:
        for function in func_file_dic:
            files = func_file_dic[function]
            for file in files:
                for message_file in file_message_dic:
                    filtered_file = message_file.replace(".../", "")
                    if file.find(filtered_file) != -1:
                        if function in func_message_dic:
                            func_message_dic[function] += " " + file_message_dic[message_file]
                        else:
                            func_message_dic[function] = file_message_dic[message_file]
        print len(func_message_dic)
        print "finish function-message dictionary building..."
        return func_message_dic
    except MySQLdb.Error,e:
        print e
        raise

def buildShaDic():
    sha_message_dic = dict()
    sha_repo_dic = dict()
    file_shas_dic = dict()
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('vccfinder')
        sql="select sha, message, repository_id, files_changed from commits where repository_id in (457, 274, 288, 256, 249, 135, 207, 460, 452, 1) and files_changed != 'null';"
        count = cur.execute(sql)
        info = cur.fetchmany(count)
        for sha, message , repository_id, files_changed in info:
            filter_message = filterMessage(message)
            if sha not in sha_message_dic:
                sha_message_dic[sha] = filter_message
            else:
                print "sha error"
                return False
            if sha not in sha_repo_dic:
                sha_repo_dic[sha] = repository_id
            else:
                print "sha error!"
                return False
            files = files_changed.replace(".../", "").split()
            for file in files:
                if file not in file_shas_dic:
                    file_shas_dic[file] = [sha]
                else:
                    file_shas_dic[file].append(file)
        return [sha_message_dic, sha_repo_dic, file_shas_dic]
    except MySQLdb.Error,e:
        print e
        raise

n_samples = 2000
n_features = 1000
n_topics = 1
n_top_words = 10

def buildFuncMessageDicViaPatch():
    func_message_dic = dict()
    try:
        [sha_message_dic, sha_repo_dic, file_shas_dic] = buildShaDic()
        if len(sha_message_dic) == 0 or len(sha_repo_dic) ==0 or len(file_shas_dic) == 0:
            print "sha_message_dic or sha_repo_dic or file_shas_dic is null!"
            return False
        func_file_dic = buildFuncFileDic()
        if len(func_file_dic) == 0:
            print "func_file_dic is null!"
            return False
        file_message_dic = buildFileMessageDic()
        if len(file_message_dic) == 0:
            print "file_message_dic is null!"
            return False
        for func in func_file_dic:
            for file in func_file_dic[func]:
                if file not in file_shas_dic:
                    continue
                for sha in file_shas_dic[file]:
                    if sha not in sha_repo_dic:
                        continue
                    repo_id = sha_repo_dic[sha]
                    repo_dir = code_dir + '/' + repos_list[repo_id]
                    os.chdir(repo_dir)
                    log = os.popen("git show " + sha).read()
                    if log.find(func) != -1:
                        if func not in func_message_dic:
                            func_message_dic[func] = sha_message_dic[sha]
                        else:
                            func_message_dic[func] += " " + sha_message_dic[sha]
        return func_message_dic
    except MySQLdb.Error,e:
        print e
        raise

def extractTopicLDA(func_message_dic, store_cloumn):
    if len(func_message_dic) == 0:
        print "func_message_dic is null"
        return False
    try:
        conn=MySQLdb.connect(host='192.168.162.122',user='wangyu',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('set names utf8mb4')
        conn.select_db('codeAnalysis')
        for function in func_message_dic:
            message = func_message_dic[function]
            np_extractor = nlp.semantics_extraction.NPExtractor(message)
            text = np_extractor.extract()
            if len(text) == 0:
                continue
            tf_vectorizer = CountVectorizer(max_df=1.0, min_df=1, max_features=n_features, stop_words='english')
            tf = tf_vectorizer.fit_transform(text)
            print("Fitting LDA models with tf features, n_samples=%d and n_features=%d..." % (n_samples, n_features))
            lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5, learning_method='online', learning_offset=50.,
                                                                    random_state=0)
            lda.fit(tf)
            tf_feature_names = tf_vectorizer.get_feature_names()
            seprator = " "
            for topic_idx, topic in enumerate(lda.components_):
                keywords = seprator.join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
            sql = "update func_semantic set "+store_cloumn+" = '"+keywords+"' where func_name = '"+function+"'"
            print sql
            cur.execute(sql)
            conn.commit()
        cur.close()
        conn.close()
        return True
    except MySQLdb.Error,e:
        print e
        raise

def filterMessage(message):
    setence = message.replace("\n", "").replace("_", " ").replace("---", " ")
    filtered_setence = ""
    words = setence.split()
    for word in words:
        word = filter(str.isalnum, str(word))
        if word != "":
            filtered_setence += word + " "
    filtered_setence = filtered_setence.rstrip()
    filtered_setence += "."
    return filtered_setence

def executeSequence():
    func_message_dic = buildFuncMessageDicViaPatch()
    extractTopicLDA(func_message_dic, "semantic_func")

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    executeSequence()
    