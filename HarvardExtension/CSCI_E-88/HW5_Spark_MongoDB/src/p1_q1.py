from pyspark import SparkContext

sc = SparkContext("local", "Query 1")
# Query 1: get count of unique URLs by hour

p1 = False
p2_single_folder = True
if p1:
    rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
elif p2_single_folder:
    # load only Dataset1
    #rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2/')
    rddA = sc.textFile('s3://owengnet-data/e88/A4/Dataset1')
    # won't make a difference for a single source folder
    rdd = rddA.distinct()
#    rdd = sc.textFile('s3://owengnet-data/e88/A4/Dataset1')
else:
    # use problem 2 files, for testing from local drive
    # rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2/')
    # rddB = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2_dup/')
    rddA = sc.textFile('s3://owengnet-data/e88/A4/Dataset1')
    rddB = sc.textFile('s3://owengnet-data/e88/A4/Dataset2')
    # concatenate the two RDDs and then call .distinct to get rid of any duplicates
    # the .distinct() won't make any difference for Query 1, too many events, only three urls
    rdd = sc.union([rddA, rddB]).distinct()

# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
        # pull out only the two characters representing the hour, along with the 2nd field, i.e. the url
        # use negative indexing on the initial column selection so that same code will work when there are
        # additional columns pre-pended, i.e. when UUID is first column in problem 2
        .map(lambda row: (row[-3][11:13], row[-2]))
        # group by the key, i.e. the hour value, making the value an iterable of urls
        .groupByKey()
        # pull out the hour value, apply set on the iterable to remove dups, and return length of that set as value
        .map(lambda row: (row[0], len(set(row[1]))))
    )
# pull out all the results, sorting by the hour value
final = rdd1.sortByKey().collect()

print('Query 1: get count of unique URLs by hour')
for (hour, count) in final:
    print('- hour: {}\tcount unique urls: {}'.format(hour, count))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
