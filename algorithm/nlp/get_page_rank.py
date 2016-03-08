import networkx as nx
import sys
import socket
import MySQLdb
import chardet
import ssl
import time          
import re          
import os
import string
import sys
import math
import matplotlib.pyplot as plt

def drawAllGraph():
	clusterResults = getAllCluster()
	if None != clusterResults:
		for item in clusterResults:
			drawGraph(item[0])
			plt.close('all')

def drawGraph(cluster):
	print 'cluster',cluster
	results = getGraphData(cluster)
	ig = nx.DiGraph()
	if None != results:
		ig.add_weighted_edges_from(results)
		layout = nx.spring_layout(ig)
		pos = layout
		pr=nx.pagerank(ig,alpha=0.85)
		for node, pageRankValue in pr.items():
			print("%s,%.4f" %(node,pageRankValue))
		plt.figure(1)
		nx.draw(ig, pos=layout, node_size=[x * 6000 for x in pr.values()],node_color='m',with_labels=True)
        plt.savefig("./graph/graph_pagerank_"+cluster+".png")

def transToSingle(results):
	edgeList = []
	edgedict = {}
	for item in results:
		key = item[0] + '-' + item[1]
		if key in edgedict.keys():
			edgedict[key] = edgedict[key] + 1
		else:
			edgedict[key] = 1
	for item in edgedict.keys():
		keyList = item.split('-')
		edgeList.append((keyList[0],keyList[1],edgedict[item]))
	return edgeList

def getGraphData(cluster):
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT start,end,count FROM tempTopicLink where cluster = "'+cluster+'" and start like "#%"')
        results = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return results
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def getAllCluster():
    try:
        conn=MySQLdb.connect(host='localhost',user='root',passwd='wangyu',port=3306)
        cur=conn.cursor()
        conn.select_db('vccfinder')
        count=cur.execute('SELECT distinct cluster FROM wordLink')
        results = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return results
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

if __name__ == '__main__':
	#drawAllGraph()
	drawGraph('20')
