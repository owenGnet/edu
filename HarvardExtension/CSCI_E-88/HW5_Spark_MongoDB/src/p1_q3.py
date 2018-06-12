
from pyspark import SparkContext

sc = SparkContext("local", "Query 3")
#Query 3: get count of unique (by userId) clicks per URL by hour

p1 = False
p2_single_folder = False
if p1:
    rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
elif p2_single_folder:
    # load only Dataset1
    rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2/')
    # won't make a difference for a single source folder
    rdd = rddA.distinct()
else:
    # use problem 2 files, for testing from local drive
    rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2/')
    rddB = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2_dup/')
    # concatenate the two RDDs and then call .distinct to get rid of any duplicates
    # Query 3 is the only query where there will actually be a difference in the results if .distinct() is/is not used
    rdd = sc.union([rddA, rddB]).distinct()

# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
    # pull out hour and url AND userid as key, the value will simply be the number 1
    .map(lambda row: ((row[-3].split()[1][:2], row[-2], row[-1]), 1) )
    )

# .countByKey(): Count the number of elements for each key, and return the result to the master as a dictionary.
final = rdd1.countByKey()

print('Query 3: get count of unique (by userId) clicks per URL by hour')
for k,v in sorted(final.items()):
    # each key is a tuple of (hour, url, userid)
    print('hour/url/userid combination: {}\tcount of unique (by userId) clicks per URL by hour: {}'.format(
        '/'.join(k), v))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
