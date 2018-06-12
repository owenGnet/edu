
# coding: utf-8

# In[2]:

import h2o
h2o.init()            #uses all cores by default
h2o.remove_all()      #clean slate, in case cluster was already running


# In[3]:

from h2o.estimators.glm import H2OGeneralizedLinearEstimator
import numpy as np

df = h2o.import_file('small_car.csv')
#help(h2o.import_file)
train, test = df.split_frame([0.8], seed=63)
print len(train), len(test)


# In[4]:

target_simple_Y = 'Horsepower'
exp_simple_X = 'Displacement'

target_multi_Y = 'Horsepower'
exp_multi_X = ['Cylinders', 'Displacement', 'Manufacturer', 'Model_Year', 'Origin', 'Weight']


# In[5]:

glm_simple_cars = H2OGeneralizedLinearEstimator(
                    model_id='glm_simple_cars',  #will appear in Flow by this name
                    family='gaussian', 
                    solver='IRLSM' #'L_BFGS' is the other GLM solveraka
                    ,lambda_search = True
                )  

glm_multi_cars = H2OGeneralizedLinearEstimator(
                    model_id='glm_multi_cars', 
                    family='gaussian', 
                    solver='IRLSM' 
                    ,lambda_search = True
                )  


# In[6]:

glm_simple_cars.train(exp_simple_X, target_simple_Y, training_frame=train) #, validation_frame=valid)
glm_multi_cars.train(exp_multi_X, target_multi_Y, training_frame=train) #, validation_frame=valid)


# In[7]:

glm_simple_cars


# In[8]:

#SIMPLE: target = horsepower, explanatory = displacement

#the test set used for lecture 11, a hack since some of these are likely in the training set here
test_simple = h2o.import_file('lec11_test.csv')

print '#my homework had MSE = 602.31 -> RMSE = 24.54'
print 'RMSE: {0}'.format(np.sqrt(glm_simple_cars.mse())) 
glm_simple_pred = glm_simple_cars.predict(test_simple)
#print 'pred object dimensions: {0}'.format(glm_simple_pred.dim)

print("GLM predictions: ")
df_simple = test_simple[['Displacement','Horsepower']].cbind(glm_simple_pred)
print df_simple.head()
py_df_simple = df_simple.as_data_frame(use_pandas=False)
print py_df_simple[:10]
h2o.export_file(frame=df_simple, path='car_SIMPLE.csv', force=True)


# In[ ]:

glm_multi_cars


# In[9]:

#MULTI: target = hp, explanatory = #cylinders, displacement, manufacturer, model_year, origin and weight 
#Lec11 spark MLLIB: 38.65 RMSE for mutliple -> predict hp 
#SIMPLE above gave an RMSE = 17.4
print 'RMSE: {0}'.format(np.sqrt(glm_multi_cars.mse())) 
glm_multi_pred = glm_multi_cars.predict(test)
print("GLM predictions: ")

df_multi = test[['Displacement','Horsepower']].cbind(glm_multi_pred)
print df_multi.head().apply(fun=lambda row : row) #playing around with
h2o.export_file(frame=df_multi, path='car_MULTI.csv', force=True)

