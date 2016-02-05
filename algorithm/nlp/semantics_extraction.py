#coding=utf-8
from __future__ import print_function
import nltk, re, pprint
import MySQLdb
import sys
from nltk.corpus import brown
from time import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

n_samples = 2000
n_features = 1000
n_topics = 20
n_top_words = 20

brown_train = brown.tagged_sents(categories='news')
regexp_tagger = nltk.RegexpTagger(
    [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
     (r'(-|:|;)$', ':'),
     (r'\'*$', 'MD'),
     (r'(The|the|A|a|An|an)$', 'AT'),
     (r'.*able$', 'JJ'),
     (r'^[A-Z].*$', 'NNP'),
     (r'.*ness$', 'NN'),
     (r'.*ly$', 'RB'),
     (r'.*s$', 'NNS'),
     (r'.*ing$', 'VBG'),
     (r'.*ed$', 'VBD'),
     (r'.*', 'NN')
])
unigram_tagger = nltk.UnigramTagger(brown_train, backoff=regexp_tagger)
bigram_tagger = nltk.BigramTagger(brown_train, backoff=unigram_tagger)

cfg = {}
cfg["NNP+NNP"] = "NNP"
cfg["NN+NN"] = "NNI"
cfg["NNI+NN"] = "NNI"
cfg["JJ+JJ"] = "JJ"
cfg["JJ+NN"] = "NNI"

class NPExtractor(object):
 
    def __init__(self, sentence):
        self.sentence = sentence

    def tokenize_sentence(self, sentence):
        sentence = unicode( sentence , errors='ignore')
        tokens = nltk.word_tokenize(sentence)
        return tokens

    def normalize_tags(self, tagged):
        n_tagged = []
        for t in tagged:
            if t[1] == "NP-TL" or t[1] == "NP":
                n_tagged.append((t[0], "NNP"))
                continue
            if t[1].endswith("-TL"):
                n_tagged.append((t[0], t[1][:-3]))
                continue
            if t[1].endswith("S"):
                n_tagged.append((t[0], t[1][:-1]))
                continue
            n_tagged.append((t[0], t[1]))
        return n_tagged
 
    def extract(self):
        tokens = self.tokenize_sentence(self.sentence)
        tags = self.normalize_tags(bigram_tagger.tag(tokens)) 
        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break
        matches = []
        for t in tags:
            if t[1] == "NNP" or t[1] == "NNI":
                matches.append(t[0])
        return matches

def buildCommentsForCluster():
    output = open("../../result/tmp_gitlog", "wr")
    conn= MySQLdb.connect(host='localhost', port = 3306, user='root', passwd='wangyu', db ='vccfinder')
    cur = conn.cursor()
    sql = "select cluster from commit_cluster_100 group by cluster"
    cur.execute(sql)
    result = cur.fetchall()
    clusterids = []
    if None != result:
        for item in result:
            clusterids.append(item[0])
    print("finish get cluster ids...")
    for clusterid in clusterids:
        text = ""
        sql = "select message from commits, commit_cluster_100 where commits.id = commit_cluster_100.original_id and cluster = " + str(clusterid)
        cur.execute(sql)
        result = cur.fetchall()
        print("finish get messages...")
        if None != result:
            output.writelines("====================" + str(clusterid) + "====================")
            for message in result:
                setence = message[0].replace("\n", " ").replace("_", " ").replace("---", " ")
                filtered_setence = ""
                words = setence.split()
                for word in words:
                    word = filter(str.isalnum, str(word))
                    if word != "":
                        filtered_setence += word + " "
                filtered_setence = filtered_setence.rstrip()
                filtered_setence += "."
                text += filtered_setence
        np_extractor = NPExtractor(text)
        result = np_extractor.extract()
        print("%s" % ", ".join(result))
        if len(result) > 0:
            output.writelines(str(result) + "\n")
        break
    output.close()
    cur.close()
    conn.commit()
    conn.close()

def print_top_words(model, feature_names, n_top_words, outputfile):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        outputfile.writelines("\nTopic #%d:\n" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        outputfile.writelines(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()

def topicExtractionLDA():
    output = open("../../result/topic_extraction", "wr")
    conn= MySQLdb.connect(host='localhost', port = 3306, user='root', passwd='wangyu', db ='vccfinder')
    cur = conn.cursor()
    sql = "select cluster from commit_cluster_100 group by cluster"
    cur.execute(sql)
    result = cur.fetchall()
    clusterids = []
    if None != result:
        for item in result:
            clusterids.append(item[0])
    print("finish get cluster ids...")
    for clusterid in clusterids:
        text = []
        sql = "select message from commits, commit_cluster_100 where commits.id = commit_cluster_100.original_id and cluster = " + str(clusterid)
        cur.execute(sql)
        result = cur.fetchall()
        print("finish get messages...")
        if None != result:
            output.writelines("\n====================start " + str(clusterid) + "====================")
            for message in result:
                setence = message[0].replace("\n", "").replace("_", " ").replace("---", " ")
                filtered_setence = ""
                words = setence.split()
                for word in words:
                    word = filter(str.isalnum, str(word))
                    if word != "":
                        filtered_setence += word + " "
                filtered_setence = filtered_setence.rstrip()
                filtered_setence += "."
                #print(filtered_setence)
                text.append(filtered_setence)
        print("finish build text array... then extracting tf features for LDA...")
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features, stop_words='english')
        tf = tf_vectorizer.fit_transform(text)
        print("Fitting LDA models with tf features, n_samples=%d and n_features=%d..." % (n_samples, n_features))
        lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5, learning_method='online', learning_offset=50.,
                                                                    random_state=0)
        lda.fit(tf)
        tf_feature_names = tf_vectorizer.get_feature_names()
        print_top_words(lda, tf_feature_names, n_top_words, output)
    output.close()
    cur.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    #buildCommentsForCluster()
    topicExtractionLDA()
    