
from pyspark import SparkConf, SparkContext 
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.regression import LinearRegressionWithSGD
import numpy as np

def squared_log_error(pred, actual):
    return (np.log(pred + 1) - np.log(actual + 1))**2

def squared_error(actual, pred):
    return (pred - actual)**2

def abs_error(actual, pred):
    return np.abs(pred - actual)

def evaluate(train, test, iterations, step, regParam,regType,intercept):
    model = LinearRegressionWithSGD.train(train,iterations,step,regParam=regParam, regType=regType, intercept=intercept)
    tp = test.map(lambda p: (p.label, model.predict(p.features)))
    rmsle = np.sqrt(tp.map(lambda (t, p): squared_log_error(t,p)).mean())
    return rmsle

conf = SparkConf().setMaster('local').setAppName('pyAssign11_Simple') 
sc = SparkContext(conf = conf) 

file_path = 'file:////home/joe/proj/lec11/small_car_data.csv'
raw_data = sc.textFile(file_path)
records = raw_data.map(lambda x: [cell.strip() for cell in x.split(',')])
first = records.first()
print first
#records_raw = raw_data.map(lambda x: x.split(','))

#data = records.map(lambda r: LabeledPoint(float(r[4]), [r[3]] ))
data = records.map(lambda r: LabeledPoint(float(r[4]), np.array( [float(r[3])] )))
data.cache()
print data.take(5)

data_with_idx = data.zipWithIndex().map(lambda (k, v): (v, k))
test = data_with_idx.sample(False, 0.13, 63) #.13 WAS working to get 10..., for 10% ..., 63 is the seed
train = data_with_idx.subtractByKey(test)
train_data = train.map(lambda (idx, p): p) #train_size = train_data.count() = 90
test_data = test.map(lambda (idx, p) : p) #test_size = test_data.count() = 10

#step_params = [0.0000001,0.000001,0.00001,0.0001,0.0001]
#step_metrics = [evaluate(train_data, test_data, 10, step_param, 0.0, 'l2',False) for step_param in step_params]
#print step_metrics #-> [3.4679800804243932, 1.5228864259213952, 0.28894714450593106, nan, nan]

#iter_params = [1,5,10,20,50,100] #20 good enough = 0.27639320673299744
#iter_metrics = [evaluate(train_data, test_data, iter_param, 0.00001, 0.0, 'l2',False) for iter_param in iter_params]
#print iter_metrics #-> [0.75783871278320125, 0.33747797400340473, 0.28894714450593106, 0.27639320673299744, 0.27639320673299744, 0.27639320673299744]

linear_model = LinearRegressionWithSGD.train(train_data, iterations=20, step=0.00001, intercept=False) #, regType='l1')
true_vs_predicted = test_data.map(lambda p: (p.label, linear_model.predict(p.features)))
tvp_with_input = test_data.map(lambda p: (p.features[0], p.label, linear_model.predict(p.features)))

mse = true_vs_predicted.map(lambda (t, p): squared_error(t, p)).mean()
mae = true_vs_predicted.map(lambda (t, p): abs_error(t, p)).mean()
rmsle=np.sqrt(true_vs_predicted.map(lambda(t,p):squared_log_error(t,p)).mean())
print "Linear Model - Mean Squared Error: %2.4f" % mse
print "Linear Model - Mean Absolute Error: %2.4f" % mae
print "Linear Model - Root Mean Squared Log Error: %2.4f" % rmsle

#print true_vs_predicted.take(2) #[(130.0, 151.90443654598366), (165.0, 173.18095371691948)]
tvp = tvp_with_input.collect()
lec11_p1_csv = 'displacement,actual,predicted\r\n' + '\r\n'.join(['{0},{1},{2:.4f}'.format(tup[0], tup[1], tup[2]) for tup in tvp])
print lec11_p1_csv

print linear_model.weights
