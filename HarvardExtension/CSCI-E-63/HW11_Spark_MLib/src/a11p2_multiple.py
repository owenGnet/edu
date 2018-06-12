from pyspark import SparkConf, SparkContext 
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.regression import LinearRegressionWithSGD
import numpy as np

def get_mapping(rdd, idx):
    return rdd.map(lambda fields: fields[idx]).distinct().zipWithIndex().collectAsMap()

def extract_features(record):
    cat_vec = np.zeros(cat_len)
    i = 0
    step = 0
    #for field in record[2:9]:
    fields = [record[j] for j in cat_idx]
    for field in fields:
        m = mappings[i]
        idx = m[field]
        cat_vec[idx + step] = 1
        i = i + 1
        step = step + len(m)
    #num_vec = np.array([float(field) for field in record[10:13]]) 
    num_vec = np.array([float(record[j]) for j in num_idx])
    return np.concatenate((cat_vec, num_vec))

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

def evaluate(train, test, iterations, step, regParam,regType,intercept):
    model = LinearRegressionWithSGD.train(train,iterations,step,regParam=regParam, regType=regType, intercept=intercept)
    tp = test.map(lambda p: (p.label, model.predict(p.features)))
    rmsle = np.sqrt(tp.map(lambda (t, p): squared_log_error(t,p)).mean())
    return rmsle

def evaluate_final(description, data):
    data_with_idx = data.zipWithIndex().map(lambda (k, v): (v, k))
    test = data_with_idx.sample(False, 0.13, 63) #.13 WAS working to get 10..., for 10% ..., 63 is the seed
    train = data_with_idx.subtractByKey(test)
    train_data = train.map(lambda (idx, p): p) #train_size = train_data.count()
    test_data = test.map(lambda (idx, p) : p) #test_size = test_data.count()

    #no need to adjust iter & step values for each dependent variable since they shared the same optimal values
    linear_model = LinearRegressionWithSGD.train(train_data, iterations=5, step=0.0000001, intercept=False) 
    true_vs_predicted = test_data.map(lambda p: (p.label, linear_model.predict(p.features)))

    mse = true_vs_predicted.map(lambda (t, p): squared_error(t, p)).mean()
    mae = true_vs_predicted.map(lambda (t, p): abs_error(t, p)).mean()
    rmsle=np.sqrt(true_vs_predicted.map(lambda(t,p):squared_log_error(t,p)).mean())
    
    print '{0} Linear Model - Mean Squared Error: {1:2.4f}'.format(description, mse)   
    print '{0} Linear Model - Root Mean Squared Error: {1:2.4f}'.format(description, np.sqrt(mse))  
    print '{0} Linear Model - Mean Absolute Error: {1:2.4f}'.format(description, mae)
    print '{0} Linear Model - Root Mean Squared Log Error: {1:2.4f}'.format(description, rmsle)


conf = SparkConf().setMaster('local').setAppName('pyAssign11_Multiple') 
sc = SparkContext(conf = conf) 

file_path = 'file:////home/joe/proj/lec11/small_car_data.csv'
raw_data = sc.textFile(file_path)
records = raw_data.map(lambda x: [cell.strip() for cell in x.split(',')])
records.cache()
first = records.first()

cat_idx = [2,5,7,9] #Cylinders, Manufacturer, Model_Year, Origin
num_idx = [3,10] #Displacement, Weight
mappings = [get_mapping(records, i) for i in cat_idx]
cat_len = sum(map(len, mappings))
num_len = sum(len(records.first()[i]) for i in num_idx)
#total_len = num_len + cat_len

print records.first()
print 'Feature vector length for categorical features: %d' % cat_len
print 'Feature vector length for numerical features: %d' % num_len 
#40 numlen = distinct counts for each column: Mfg: 28, Origin: 6, Year: 3, Cylinders: 3 -- 28+6+3+3=40
print 'Total feature vector length: %d' % total_len

data_acc = records.map(lambda r: LabeledPoint(extract_label_acc(r), extract_features(r)))
data_hp = records.map(lambda r: LabeledPoint(extract_label_hp(r), extract_features(r)))

first_point_acc = data_acc.first()
first_point_hp = data_hp.first()
print 'Raw data: ' + str(first)
print 'Acc Label: ' + str(first_point_acc.label)
print 'HP Label: ' + str(first_point_hp.label)
print 'Linear Model feature vector:\n' + str(first_point_acc.features)
print 'Linear Model feature vector length: ' + str(len(first_point_acc.features))

evaluate_final('ACCELERATION',data_acc)
evaluate_final('HORSEPOWER',data_hp)


#--------------------------------------------------------
#coming up with best step/iteration values for each model
#each returns differing rmsle for submitted step/iter values as expected for diff generated models
#but in the end step = 0.0000001 and iterations = 5 seems to work best for both acceleration and horsepower 

## dependent var = horsepower
    #step_params = [0.00000001,0.00000005,0.00000008,0.0000001,0.0000005,0.000001]
    #step_metrics = [evaluate(train_data, test_data, 10, step_param, 0.0, 'l2',False) for step_param in step_params]
    #print step_metrics #[1.1006039362999183, 0.26902311044451516, 0.25271535442823323, 0.25005936125107098, nan, nan]
    ##use step = 0.0000001, same as for acceleration
    
    #iter_params = [1,5,10,20,50,100] #5 good enough, same as with acceleration
    #iter_metrics = [evaluate(train_data, test_data, iter_param, 0.0000001, 0.0, 'l2',False) for iter_param in iter_params]
    #print iter_metrics #[0.25022360622846102, 0.25005936125107098, 0.25005936125107098, 0.25005936125107098, 0.25005936125107098, 0.25005936125107098]

### dependent var = acceleration
    #step_params = [0.00000001,0.00000005,0.00000008,0.0000001,0.0000005,0.000001]
    #step_metrics = [evaluate(train_data, test_data, 10, step_param, 0.0, 'l2',False) for step_param in step_params]
    #print step_metrics #[1.7312475116799362, 0.68034979567703358, 0.46920254015648477, 0.41748612595024526, nan, nan]
    ##use step = 0.0000001
    
    #iter_params = [1,5,10,20,50,100] #5 good enough = 0.41748612595024526
    #iter_metrics = [evaluate(train_data, test_data, iter_param, 0.0000001, 0.0, 'l2',False) for iter_param in iter_params]
    #print iter_metrics #[0.4189442995988179, 0.41748612595024526, 0.41748612595024526, 0.41748612595024526, 0.41748612595024526, 0.41748612595024526]
