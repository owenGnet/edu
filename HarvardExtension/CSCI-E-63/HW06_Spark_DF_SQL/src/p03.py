from pyspark import SparkConf, SparkContext, SQLContext, Row
from pyspark.sql import functions as F

spark_root_dir = 'file:///home/cloudera/proj/lec06'

conf = SparkConf().setMaster('local').setAppName('py03') 
sc = SparkContext(conf = conf) 
sqc = SQLContext(sc)

#Import data into an RDD object. 
ebay_data = sc.textFile(spark_root_dir + '/data/ebay.csv') #_short.csv') 
ebay_lines = ebay_data.map(lambda line: line.split(','))
#Transform that RDD into an RDD of Row-s by assign schema (column names and types).
ebay_rows = ebay_lines.map(lambda e: Row(auctionid = e[0], 
                                         bid = float(e[1]), 
                                         bidtime = float(e[2]), 
                                         bidder = e[3], 
                                         bidderrate = int(e[4]), 
                                         openbid = float(e[5]), 
                                         price = float(e[6]), 
                                         item = e[7], 
                                         daystolive = int(e[8])))
# Transform that new RDD into a DataFrame. Call that DataFrame Auction.
auction = sqc.createDataFrame(ebay_rows)
#Show (print) the schema of the DataFrame. 
auction.printSchema()

#Persist your  DataFrame as a Parquet file 
auction.write.parquet('auction_parquet', mode='overwrite')


def as_dataframe(auc):
    print '------------- AS DATAFRAME ------------------------------------'
   
    #How many auctions were held?
    print 'Number of auctions:'
    print auc.select("auctionid").distinct().count()
    
    #How many bids were made per item?
    print 'Number of bids per item (across all auctions):'
    auc.groupBy('item').count().show()
    
    #What's the minimum, maximum, and average bid (price) per item?
    print 'Minimum price/bid per item:'
    auc.groupBy('item').min('bid').show()
    print 'Maximum price/bid per item:'
    auc.groupBy('item').max('bid').show()
    print 'Average price/bid per item:'
    auc.groupBy('item').avg('bid').show()
    
    #What's the minimum, maximum, and average number of bids per item?
    aucGroup1 = auc.groupBy('item','auctionid').count()
    #aucGroup1.show() #debug, to show my initial grouping    
    print 'Minimum number of bids per item:'
    aucGroup2 = aucGroup1.select(aucGroup1['item'],aucGroup1['count']) 
    #aucGroup2.show() #debug
    
    (aucGroup2.groupBy('item').min('count')
        .select('item', F.format_number('min(count)',0)
        .alias('MinPerBid')).show())

    print 'Maximum number of bids per item:'
    (aucGroup2.groupBy('item').max('count')
        .select('item', F.format_number('max(count)',0)
        .alias('MaxPerBid')).show())
#    aucGroup2.groupBy('item').max('count').alias('MaxPerBid').show()

    print 'Average number of bids per item:'
    (aucGroup2.groupBy('item').avg('count')
        .select('item', F.format_number('avg(count)',4)
        .alias('AvgPerBid')).show())

    #Show the bids with price > 100
    print 'Bids with price > 100 (limit = 10)'
    auc.filter(auction.bid > 100).show(10)

def as_table(auc):
    print '------------- AS TABLE ------------------------------------'
    sqc.registerDataFrameAsTable(auc, 'auction')
    
    #How many auctions were held?
    cnt = sqc.sql('SELECT COUNT(DISTINCT auctionid) AS auctionCount FROM auction').collect()[0][0]
    print 'Number of auctions: {0}'.format(cnt)
    #How many bids were made per item?

    print 'Number of bids per item (across all auctions):'
    num_bids_group = sqc.sql('SELECT item, COUNT(bid) AS NumBids FROM auction GROUP BY item')
    num_bids_group.show()

    #What's the minimum, maximum, and average bid (price) per item?
    print 'Minimum/maximum/average price (bid) per item:'
    sqc.sql('''
            SELECT item, MIN(bid) AS MinBid, MAX(bid) AS MaxBid, AVG(bid) AS AvgBid
            FROM auction
            GROUP BY item    
            ''').show()

    #What's the minimum, maximum, and average number of bids per item?
    print 'Minimum/maximum/average number of bids per item:'
    sqc.sql('''
            SELECT A.item, MIN(A.NumBids) AS MinNumBids, MAX(NumBids) AS MaxNumBids,
                AVG(NumBids) AS AvgNumBids
            FROM
                (SELECT item, auctionid, COUNT(bid) AS NumBids
                  FROM auction
                  GROUP BY item, auctionid) A
            GROUP BY A.item
              ''').show()

    #Show the bids with price > 100
    print 'Bids with price > 100'
    sqc.sql('SELECT * FROM auction WHERE bid > 100 LIMIT 10').show()


as_dataframe(auction)
as_table(auction)

print '-----END END END --------------------------------------'

