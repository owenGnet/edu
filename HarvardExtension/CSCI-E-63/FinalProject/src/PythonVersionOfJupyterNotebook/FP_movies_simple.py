
# coding: utf-8

# In[65]:

import h2o
h2o.init()            #uses all cores by default
h2o.remove_all()      #clean slate, in case cluster was already running


# In[66]:

from h2o.estimators.glm import H2OGeneralizedLinearEstimator
import numpy as np

df = h2o.import_file('FP_movies.psv')
print df.shape #(rows,columns)
train, test = df.split_frame([0.8], seed=63)
print len(train), len(test)


# In[67]:

get_ipython().magic(u'matplotlib inline')
from pylab import hist
import matplotlib


#print test.head(5)
py_df =  df['rtAllCriticsRating'].as_data_frame(use_pandas=False)
#print py_df[:]
py_df = py_df[1:3000]
#print len(py_df[2])
ratings = [float(row[0]) for row in py_df[1:]]
hist(ratings, bins=30, color='lightblue', normed=True)
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(8, 5)


# In[68]:

train.head(5)


# In[69]:

test.head(5)


# In[70]:

target_simple_Y = 'rtAllCriticsRating'
#exp_simple_X = 'MovieStarPower'
#exp_simple_X = 'MovieStarPowerWCntry'
exp_simple_X = 'StarAud'

glm_movie_simple = H2OGeneralizedLinearEstimator(
                    model_id='glm_movie_simple',
                    family='gaussian', 
                    solver='IRLSM' 
                    ,lambda_search = True
                )  

glm_movie_simple.train(exp_simple_X, target_simple_Y, training_frame=train)
glm_movie_simple


# In[71]:

print 'RMSE: {0}'.format(np.sqrt(glm_movie_simple.mse())) 
glm_movie_simple_pred = glm_movie_simple.predict(test)

df_movie_simple_out = test[['title','StarAud','rtAllCriticsRating']].cbind(glm_movie_simple_pred)
print("GLM predictions: ")
print df_movie_simple_out.head(5)

h2o.export_file(frame=df_movie_simple_out, path='movie_SIMPLE_out.csv', force=True)


# In[72]:

output, remainder = df_movie_simple_out.split_frame([0.1], seed=63)
print len(output)
h2o.export_file(frame=output, path='movie_SIMPLE_out_SHORT.csv', force=True)

