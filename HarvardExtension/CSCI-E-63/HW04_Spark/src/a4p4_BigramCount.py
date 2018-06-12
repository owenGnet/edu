#a4p4_BigramCount.py

import re, os, shutil
from pyspark import SparkConf, SparkContext 

re_clean = re.compile(r'[^A-Za-z0-9 ]')
re_sentence = re.compile(r'\. |! |\? ')

def clean(word):
	return re.sub(re_clean, '', word).lower()

def bigramify(line):
	bigrams = []
	sentence_parts = re.split(re_sentence, line)
	for s in sentence_parts:
		parts = [clean(word) for word in s.split()]
		bigrams.extend([(parts[i],parts[i+1]) for i,part in enumerate(parts) if i < len(parts)-1 ])
	return bigrams
	

output_dir = '/home/joe/bigram_out'
if os.path.exists(output_dir):
	shutil.rmtree(output_dir)

conf = SparkConf().setMaster('local').setAppName('pyBigramCount') 
sc = SparkContext(conf = conf) 

#lines = sc.textFile('./ulysses/4300.txt') 
lines = sc.textFile('file:///home/joe/4300.txt')
#lines = sc.textFile('file:///home/joe/bigram.txt')	#test input file

rdd_split = lines.flatMap(bigramify).filter(lambda word_pair: len(word_pair) > 0)
rdd_count = rdd_split.map(lambda word_pair: (word_pair, 1))
rdd_summed = rdd_count.reduceByKey(lambda a, b: a +b)

rdd_summed.saveAsTextFile('file://' + output_dir) 
print 'TOTAL BIGRAM COUNT: {0}'.format(rdd_summed.count())
 
rdd_twenty = rdd_summed.take(20)
f = open(output_dir + '/twenty.txt', 'w')
f.writelines([str(bigram) + '\n' for bigram in rdd_twenty])
f.close()

#rdd_heaven = rdd_summed.map(lambda bigram: (bigram[0], bigram[1]))
rdd_heaven = rdd_summed.filter(lambda result: result[0][0] == u'heaven' or result[0][1] == u'heaven').collect()
f = open(output_dir + '/heaven.txt', 'w')
f.writelines([str(bigram) + '\n' for bigram in rdd_heaven])
f.close()

 
