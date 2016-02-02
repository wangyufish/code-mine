#coding=utf-8
import nltk, re, pprint
import MySQLdb
import sys
from nltk.corpus import brown

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
    sql = "select cluster from commit_cluster group by cluster"
    cur.execute(sql)
    result = cur.fetchall()
    clusterids = []
    if None != result:
        for item in result:
            clusterids.append(item[0])
    print "finish get cluster ids..."
    for clusterid in clusterids:
        text = ""
        sql = "select message from commits, commit_cluster where commits.id = commit_cluster.original_id and cluster = " + str(clusterid)
        cur.execute(sql)
        result = cur.fetchall()
        print "finish get messages..."
        if None != result:
            output.writelines("====================" + str(clusterid) + "====================")
            for message in result:
                setence = message[0].replace("\n", "").replace("_", " ").replace("---", " ")
                #setence = filter(str.isalnum, str(setence))
                #text += setence + "."
                np_extractor = NPExtractor(setence)
                result = np_extractor.extract()
                print "%s" % ", ".join(result)
                #print "This setence is about: %s" % ", ".join(result)
                if len(result) > 0:
                    output.writelines(str(result) + "\n")
        break
    output.close()
    cur.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    buildCommentsForCluster()
    