#coding=utf-8 
from get_BC_word_link_by_input import readLDAResult

def sortKeywords(clusterDict):
	keywordDict = {}
	for clusterId, clusterItems in clusterDict.items():
		for topic in clusterItems:
			for topicId in topic:
				if len(topicId) != 20:
					continue
				for keyword in topicId:
					if keyword not in keywordDict:
						keywordDict[keyword] = 1
					else:
						keywordDict[keyword] += 1
	result = sorted(keywordDict.items(), key = lambda d : d[1], reverse = True)
	print result

if __name__ == '__main__':
	clusterDict = readLDAResult("../../result/topic_extraction_100")
	sortKeywords(clusterDict)