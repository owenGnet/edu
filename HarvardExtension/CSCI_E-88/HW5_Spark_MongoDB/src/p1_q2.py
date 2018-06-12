
from pyspark import SparkContext

sc = SparkContext("local", "Query 2")
#Query 2: get count of unique visitors per URL by hour

p1 = False
p2_single_folder = False
if p1:
    rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
elif p2_single_folder:
    # load only Dataset1
    rddA = sc.textFile('s3://owengnet-data/e88/A4/Dataset1')
    # won't make a difference for a single source folder
    rdd = rddA.distinct()
else:
    # use problem 2 files, for testing from local drive
    rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2/')
    rddB = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_output2_dup/')
    # concatenate the two RDDs and then call .distinct to get rid of any duplicates
    rdd = sc.union([rddA, rddB]).distinct()


# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
    # pull out hour and url as key, playing w/slightly different slicing vs. query1, reutrn userid as value
    .map(lambda row: ((row[-3].split()[1][:2], row[-2]), row[-1]))
    # groupBy the key = hour+url combo, value becomes iterable of userids
    .groupByKey()
    # like query 1, but now getting the number of unique userids for each hour+url combo
    .map(lambda row: (row[0], len(set(row[1]))))
    )

# pull out all the results, sorting by the hour value
final = rdd1.sortByKey().collect()

print('Query 2: get count of unique visitors per URL by hour')
for (hour_url, count) in final:
    print('hour/url combination: {}/{}\tcount of unique visitors per URL unique urls: {}'.format(
        hour_url[0], hour_url[1], count))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
