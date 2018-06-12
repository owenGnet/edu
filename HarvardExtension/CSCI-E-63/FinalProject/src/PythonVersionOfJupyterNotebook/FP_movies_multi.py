
# coding: utf-8

# In[11]:

import h2o
h2o.init()
h2o.remove_all()


# In[15]:

from h2o.estimators.glm import H2OGeneralizedLinearEstimator
import numpy as np

df = h2o.import_file('FP_movies.psv')
print df.shape #(rows,columns)
train, test = df.split_frame([0.8], seed=63)
print len(train), len(test)


# In[16]:

train.head()


# In[13]:

target_simple_Y = 'rtAllCriticsRating'
exp_multi_X = ['year','country','directorName','Actor1','MovieStarPowerWCntry','AudienceRating',
              'Genre1', 'Genre2', 'Genre3', 'Actor1NameEndsInA']

glm_movie_multi = H2OGeneralizedLinearEstimator(
                    model_id='glm_movie_multi',
                    family='gaussian', 
                    solver='IRLSM' 
                    ,lambda_search = True
                )  

glm_movie_multi.train(exp_multi_X, target_simple_Y, training_frame=train)
glm_movie_multi


# In[14]:

print 'RMSE: {0}'.format(np.sqrt(glm_movie_multi.mse()))
glm_movie_multi_pred = glm_movie_multi.predict(test)
print("GLM predictions: ")
test_headers = ['title'] + exp_multi_X[:]
test_headers.append('rtAllCriticsRating')
df_movie_multi = test[test_headers].cbind(glm_movie_multi_pred)

h2o.export_file(frame=df_movie_multi, path='movie_MULTI_out.csv', force=True)

print df_movie_multi.head(5)

