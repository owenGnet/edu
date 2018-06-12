from pyspark import SparkConf, SparkContext 
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree
import numpy as np

def get_mapping(rdd, idx):
    return rdd.map(lambda fields: fields[idx]).distinct().zipWithIndex().collectAsMap()

def extract_features_dt(record):
    cat_lst = []
    fields = [record[j] for j in cat_idx]
    for idx,field in enumerate(fields):
        cat_lst.append(mappings[idx][field])
    #cat_vec = np.array([float(j) for j in cat_lst]) #don't need it, np.concatenate takes raw lst
    
    num_idx = [3,10]
    num_vec = np.array([float(record[j]) for j in num_idx])

    return np.concatenate((cat_lst, num_vec))
    

def extract_label_acc(record):
    return float(record[1])
    
def extract_label_hp(record):
    return float(record[4])

def squared_log_error(pred, actual):
    return (np.log(pred + 1) - np.log(actual + 1))**2

def squared_error(actual, pred):
    return (pred - actual)**2

def abs_error(actual, pred):
    return np.abs(pred - actual)

def evaluate_final(description, data, maxDepth, maxBins):
    data_with_idx = data.zipWithIndex().map(lambda (k, v): (v, k))
    test = data_with_idx.sample(False, 0.13, 63) #.13 WAS working to get 10..., for 10% ..., 63 is the seed
    train = data_with_idx.subtractByKey(test)
    train_data = train.map(lambda (idx, p): p) #train_size = train_data.count()
    test_data = test.map(lambda (idx, p) : p) #test_size = test_data.count()

    dt_model = DecisionTree.trainRegressor(train_data,{}, maxDepth=maxDepth, maxBins=maxBins)
    preds = dt_model.predict(test_data.map(lambda p: p.features))
    actual = test_data.map(lambda p: p.label)
    true_vs_predicted_dt = actual.zip(preds)

    print '\r\n-------- ' + description + ' ---------'
    print "Decision Tree predictions: " + str(true_vs_predicted_dt.take(5))
    print "Decision Tree depth: " + str(dt_model.depth())
    print "Decision Tree number of nodes: " + str(dt_model.numNodes())
    
    mse_dt = true_vs_predicted_dt.map(lambda (t, p): squared_error(t, p)).mean()
    mae_dt = true_vs_predicted_dt.map(lambda (t, p): abs_error(t, p)).mean()
    rmsle_dt = np.sqrt(true_vs_predicted_dt.map(lambda (t, p): squared_log_error(t, p)).mean())
    
    print 'Decision Tree -Mean Squared Error: {0:2.4f}'.format(mse_dt)   
    print 'Decision Tree -Root Mean Squared Error: {0:2.4f}'.format(np.sqrt(mse_dt))  
    print 'Decision Tree -Mean Absolute Error: {0:2.4f}'.format(mae_dt)
    print 'Decision Tree -Root Mean Squared Log Error: {0:2.4f}'.format(rmsle_dt)
    
    
conf = SparkConf().setMaster('local').setAppName('pyAssign11_Multiple') 
sc = SparkContext(conf = conf) 

file_path = 'file:////home/joe/proj/lec11/small_car_data.csv'
raw_data = sc.textFile(file_path)
records = raw_data.map(lambda x: [cell.strip() for cell in x.split(',')])
records.cache()
first = records.first()

cat_idx = [2,5,7,9] #Cylinders, Displacement, Manufacturer, Model_Year, Origin
num_idx = [3,10] #Displacement, Weight

mappings = [get_mapping(records, i) for i in cat_idx]
print 'mappings: ' + str(mappings)

data_dt_acc = records.map(lambda r: LabeledPoint(extract_label_acc(r),extract_features_dt(r)))
data_dt_hp = records.map(lambda r: LabeledPoint(extract_label_hp(r),extract_features_dt(r)))

first_point_dt = data_dt_acc.first()
print "Decision Tree feature vector: " + str(first_point_dt.features)
print "Decision Tree feature vector length: " + str(len(first_point_dt.features))

#def evaluate_final(description, data, maxDepth, maxBins):
evaluate_final('ACCELERATION', data_dt_acc, maxDepth=5, maxBins=32)
evaluate_final('HORSEPOWER', data_dt_hp, maxDepth=3, maxBins=8)



#===============================================================================
# #######################
# #Acceleration, depth = 5
# train_data_dt, test_data_dt = create_train_test(data_dt_acc)
# depth_params = [1, 2, 3, 4, 5, 10, 20]
# metrics = [evaluate_dt(train_data_dt, test_data_dt, param, 32) for param in depth_params]
# 
# %matplotlib inline
# import matplotlib
# from pylab import plot
# print metrics #[0.092841717862485865, 0.089265498562083476, 0.11480498057663967, 0.10559226478908185, 0.088691632155098635, 0.13995172893623051, 0.13995172893623051]
# plot(depth_params, metrics)
# fig = matplotlib.pyplot.gcf()
# 
# #######################
# #Horsepower, depth = 3 
# train_data_dt, test_data_dt = create_train_test(data_dt_hp)
# depth_params = [1, 2, 3, 4, 5, 10, 20]
# metrics = [evaluate_dt(train_data_dt, test_data_dt, param, 32) for param in depth_params]
# 
# %matplotlib inline
# import matplotlib
# from pylab import plot
# print metrics #[0.23444495934071619, 0.17013551304201496, 0.14229474701127939, 0.16098453079652439, 0.17897035995486035, 0.18641182106302645, 0.18603726827029393]
# plot(depth_params, metrics)
# fig = matplotlib.pyplot.gcf()
# 
# #######################
# #Acceleration, bins = 32
# train_data_dt, test_data_dt = create_train_test(data_dt_acc)
# bin_params = [2, 4, 8, 16, 32, 64, 100]
# metrics = [evaluate_dt(train_data_dt, test_data_dt, 5, param) for param in bin_params]
# print metrics #[0.089726588821365555, 0.16188926584413466, 0.10092368423911695, 0.101790771551064, 0.088691632155098635, 0.1326161778087083, 0.1326161778087083]
# 
# %matplotlib inline
# import matplotlib
# from pylab import plot
# plot(bin_params, metrics)
# fig = matplotlib.pyplot.gcf()
# 
# #######################
# #Horsepower, bins = 8
# train_data_dt, test_data_dt = create_train_test(data_dt_hp)
# bin_params = [2, 4, 8, 16, 32, 64, 100]
# metrics = [evaluate_dt(train_data_dt, test_data_dt, 5, param) for param in bin_params]
# print metrics 
# 
# %matplotlib inline
# import matplotlib
# from pylab import plot
# plot(bin_params, metrics)
# fig = matplotlib.pyplot.gcf()
#===============================================================================
