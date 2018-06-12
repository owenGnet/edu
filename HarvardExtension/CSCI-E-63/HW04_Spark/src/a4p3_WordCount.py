#a4p3_WordCount.py

import re
from pyspark import SparkConf, SparkContext 
 
conf = SparkConf().setMaster('local').setAppName('pyWordCount') 
sc = SparkContext(conf = conf) 

lines = sc.textFile('./ulysses/4300.txt') 
re_clean = re.compile(r'[^A-Za-z0-9 ]')

rdd_split = lines.flatMap(lambda line: line.split(' '))
rdd_count = rdd_split.map(lambda word: (re.sub(re_clean, '', word).lower(), 1))
rdd_summed = rdd_count.reduceByKey(lambda a, b: a +b)

rdd_summed.saveAsTextFile('a4p3_out')

