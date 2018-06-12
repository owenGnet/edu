import os
from pyspark import SparkConf, SparkContext, SQLContext, Row

spark_root_dir = 'file:///home/cloudera/proj/lec06'
file_root_dir = '/home/cloudera/proj/lec06'
output_dir = file_root_dir + '/out'

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

conf = SparkConf().setMaster('local').setAppName('py02') 
sc = SparkContext(conf = conf) 
sqc = SQLContext(sc)

#1)Create RDD emps by importing that file into Spark. 
emps = sc.textFile(spark_root_dir + '/data/emps.txt') 
#2)Next create a new RDD emps_fields by transforming the content of every line in RDD emps into 
#    a tuple with three individual elements by splitting the lines on commas. 
emps_fields = emps.map(lambda line: line.split(',')).map(lambda row: tuple(row))
#emps_fields = emps.map(lambda line: line.split(','))

#3)You need to apply "constructor" Row to every tuple in RDD emps_fields
employees = emps_fields.map(lambda e: Row(name = e[0], age = int(e[1]), salary = float(e[2])))

#You generate a DataFrame by passing an RDD of Row elements to the method createDataFrame() of class SQLContext. 
df = sqc.createDataFrame(employees)
#Show the content of new DataFrame. 
df.show()

tmp_table_name = 'tmp_employees'
#Transform this DataFrame into a Temporary Table 
df.registerTempTable(tmp_table_name)
#select names of all employees who have a salary greater than 3500
sqc.sql('SELECT * FROM {0} WHERE salary > 3500'.format(tmp_table_name)).show()

#print emps_fields.collect()
#print type(emps_fields.take(1)[0])
#print employees.take(1)

#paragraphA = linesA.flatMap(lambda line: line.split(' ')).map(lambda word: clean(word))
