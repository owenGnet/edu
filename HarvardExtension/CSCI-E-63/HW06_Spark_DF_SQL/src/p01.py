
import re, os, shutil
from pyspark import SparkConf, SparkContext 

spark_root_dir = 'file:///home/cloudera/proj/lec06'
file_root_dir = '/home/cloudera/proj/lec06'
output_dir = file_root_dir + '/out'
re_clean = re.compile(r'[^A-Za-z0-9 ]')

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

def clean(word):
    return re.sub(re_clean, '', word).lower()


conf = SparkConf().setMaster('local').setAppName('py01') 
sc = SparkContext(conf = conf) 

linesA = sc.textFile(spark_root_dir + '/data/L06_paraA.txt') 
linesB = sc.textFile(spark_root_dir + '/data/L06_paraB.txt') 

#2)    Use Spark transformation functions to transform those initial RDD-s into RDD-s that contain only words. 
paragraphA = linesA.flatMap(lambda line: line.split(' ')).map(lambda word: clean(word))
paragraphB = linesB.flatMap(lambda line: line.split(' ')).map(lambda word: clean(word))

#3)    Subsequently create RDD-s that contain only unique words in each of paragraphs.
uniqueA = paragraphA.distinct()
uniqueB = paragraphB.distinct()

#4)    Then create an RDD that contains only words that are present in paragraphA but not in paragraphB.
wordsInANotB = uniqueA.subtract(uniqueB)
#5)    Finally create an RDD that contains only the words common to two paragraphs.
wordsInAAndAlsoInB = uniqueA.intersection(uniqueB)

with open(output_dir + '/Problem01_output.txt', 'w') as f:
    #a.    List for us the first 10 words in each RDD. 
    f.write('#10 from paragraphA\n')
    f.writelines([str(word) + '\n' for word in paragraphA.take(10)])
    f.write('\n#10 from paragraphB\n')
    f.writelines([str(word) + '\n' for word in paragraphB.take(10)])

    f.write('\n#unique in paragraphA\n')
    f.writelines([str(word) + '\n' for word in uniqueA.collect()])
    f.write('\n#unique in paragraphB\n')
    f.writelines([str(word) + '\n' for word in uniqueB.collect()])

    f.write('\n#words in paragraphB but not paragraphA\n')
    f.writelines([str(word) + '\n' for word in wordsInANotB.collect()])

    f.write('\n#words in paragraphA and also in paragraphB\n')
    f.writelines([str(word) + '\n' for word in wordsInAAndAlsoInB.collect()])


print 'paragraphA.take(10)'
print paragraphA.take(10)
print 'paragraphB.take(10)'
print paragraphB.take(10)
print 'uniqueA.take(10)'
print uniqueA.take(10)
print 'uniqueB.take(10)'
print uniqueB.take(10)
print 'wordsInANotB.take(10)'
print wordsInANotB.take(10)
print 'wordsInAAndAlsoInB.take(10)'
print wordsInAAndAlsoInB.take(10)

