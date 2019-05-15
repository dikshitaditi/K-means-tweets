# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sys
import re,string
import json
#import numpy as np
from nltk.corpus import stopwords
regex = re.compile('[%s]' % re.escape(string.punctuation))
stop_words_list = set(stopwords.words('english'))

def clusterTweets(k,seeds_arg,tweets_arg, maxiters):
        tweets = dict()
        with open(tweets_arg,'r') as tweet_File:           
            for tweet in tweet_File:
                line_read = json.loads(tweet)
                tweets[line_read['id']] = line_read
        seeds = list()
        with open(seeds_arg, 'r') as seeds_file:
            for seed in seeds_file:
                line = int(seed.rstrip(',\n'))
                seeds.append(line)
        clusters = {}                            #store id of tweets per cluster
        id_clusters = {}                         #storing the cluster number for each id
       
        for tweet in tweets:                     #assign no cluster to all tweets
            id_clusters[tweet] = -1
        
                                                # initialize clusters with seeds
        for i in range(k):
            clusters[i] = {seeds[i]}
            id_clusters[seeds[i]] = i
            
        DistanceMatrix = calculateJaccardDistance(tweets)      #storing Jaccard distances of tweets
        clustersNew, id_clustersNew = buildNewClusters(tweets, clusters, id_clusters, k, DistanceMatrix)
        clusters = clustersNew
        id_clusters = id_clustersNew
        
        iteration = 1
        
        while iteration < maxiters:                #recluster k times
            clustersNew, id_clustersNew = buildNewClusters(tweets, clusters, id_clusters, k, DistanceMatrix)
            if id_clusters == clustersNew:
                break
            iteration+=1
            clusters = clustersNew
            id_clusters = id_clustersNew
        with open('out.txt', 'w') as output:
            for cluster in clusters:
                print(str(cluster)+"   "+','.join(map(str, clusters[cluster])) +'\n')
                output.write(str(cluster)+"   "+','.join(map(str, clusters[cluster])) +'\n')
def calculateJaccardDistance(tweets):
        DistanceMatrix = {}
        for i in tweets:
            DistanceMatrix[i] = {}
            set1 = preProcess(tweets[i]['text'])
            for j in tweets:
                if j not in DistanceMatrix:
                    DistanceMatrix[j] = {}
                set2 = preProcess(tweets[j]['text'])
                dist = jaccardDistance(set1,set2)
                DistanceMatrix[i][j] = dist
                DistanceMatrix[j][i] = dist
        return DistanceMatrix
def buildNewClusters(tweets, clusters, id_clusters, k, DistanceMatrix):
        clustersNew = {}
        id_clustersNew = {}
        for i in range(k):
            clustersNew[i] = set()
        for i in tweets:
            min_dist = float("inf")
            min_cluster = id_clusters[i]
            
            for j in clusters:
                dist = 0
                count = len(clusters[j])
                for l in clusters[j]:
                    dist+= DistanceMatrix[i][l]
                if count>0 and (dist/float(count)) < min_dist:
                    min_dist = dist/float(count)
                    min_cluster = j
            clustersNew[min_cluster].add(i)
            id_clustersNew[i] = min_cluster
        return clustersNew, id_clustersNew 
def preProcess(line):
        words = line.lower().strip().split(' ')
        to_return = set()
        for word in words:
            word = word.rstrip().lstrip()
            # print(word)
            # if not (re.match(r'^https?:\/\/.*[\r\n]*', word)) and not (re.match('^@.*', word)) and
            # not (re.match('\s', word)) and word not in (stopWordsList) and (word != 'rt') and (word != ''):
            if (not (re.match(r'^https?://.*[\r\n]*', word))) and \
                    (not (re.match('^@.*', word))) and word not in stop_words_list and not (re.match('rt', word)):
                to_return.add(regex.sub('', word))
        return to_return  
def jaccardDistance(A, B):
        try:
            return 1 - float(len(A.intersection(B))) / float(len(A.union(B)))
        except ZeroDivisionError:
            print("ERROR")         
            
if __name__ == "__main__":
        if len(sys.argv) < 3:
            print (" invalid ip")
        else:
            k = int(sys.argv[1])
            seeds_arg = sys.argv[2] 
            tweets_arg = sys.argv[3] 
            clusterTweets(k,tweets_arg,seeds_arg,1000)