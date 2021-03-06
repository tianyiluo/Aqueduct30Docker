
# coding: utf-8

# ### Spatially Join FAO Names to hydrobasins level 6
# 
# * Purpose of script: Spatially join FAO Names hydrobasins to the official HydroBasins level 6 polygons
# * Author: Rutger Hofste
# * Kernel used: python35
# * Date created: 20170825

# In[1]:

S3_INPUT_PATH_FAO = "s3://wri-projects/Aqueduct30/processData/Y2017M08D23_RH_Buffer_FAONames_V01/output/"
S3_INPUT_PATH_HYBAS = "s3://wri-projects/Aqueduct30/processData/Y2017M08D02_RH_Merge_HydroBasins_V01/output/"
S3_OUTPUT_PATH = "s3://wri-projects/Aqueduct30/processData/Y2017M08D25_RH_spatial_join_FAONames_V01/output/"
EC2_INPUT_PATH = "/volumes/data/Y2017M08D25_RH_spatial_join_FAONames_V01/input/"
EC2_OUTPUT_PATH = "/volumes/data/Y2017M08D25_RH_spatial_join_FAONames_V01/output/"
INPUT_FILE_NAME_FAO = "hydrobasins_fao_fiona_merged_buffered_v01.shp"
INPUT_FILE_NAME_HYBAS = "hybas_lev06_v1c_merged_fiona_V01.shp"
OUTPUT_FILE_NAME = "hybas_lev06_v1c_merged_fiona_withFAO_V01.csv"


# In[2]:

get_ipython().system('rm -r {EC2_INPUT_PATH}')
get_ipython().system('rm -r {EC2_OUTPUT_PATH}')

get_ipython().system('mkdir -p {EC2_INPUT_PATH}')
get_ipython().system('mkdir -p {EC2_OUTPUT_PATH}')


# In[7]:

get_ipython().system('aws s3 cp {S3_INPUT_PATH_FAO} {EC2_INPUT_PATH} --recursive ')


# In[4]:

get_ipython().system('aws s3 cp {S3_INPUT_PATH_HYBAS} {EC2_INPUT_PATH} --recursive --exclude *.tif')


# In[5]:

import os
if 'GDAL_DATA' not in os.environ:
    os.environ['GDAL_DATA'] = r'/usr/share/gdal/2.1'
from osgeo import gdal,ogr,osr
'GDAL_DATA' in os.environ
# If false, the GDAL_DATA variable is set incorrectly. You need this variable to obtain the spatial reference
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import time
get_ipython().magic('matplotlib notebook')


# In[8]:

gdfFAO = gpd.read_file(os.path.join(EC2_INPUT_PATH,INPUT_FILE_NAME_FAO))


# In[9]:

list(gdfFAO)


# In[10]:

gdfHybas = gpd.read_file(os.path.join(EC2_INPUT_PATH,INPUT_FILE_NAME_HYBAS))


# In[11]:

list(gdfHybas)


# In[12]:

gdfHybas.dtypes


# In[13]:

gdfFAO.dtypes


# In[14]:

gdfFAO['index1_copy'] = gdfFAO['index1']


# In[15]:

gdfFAO = gdfFAO.set_index('index1')


# In[16]:

gdfFAO.index.name


# A spatial join was performed on the data. However the FAO polygons were stored as polygons and not as multi-polygons. The data also lacked a unique Identifier. The identifier consists of a combination of MAJ_BAS and SUB_BASE. The maximum length of MAJ_BAS is 4 and 6 for SUB_BAS (279252). We will store the identifier as a string with the format: MAJ_BASxxxxSUB_BASExxxxxx

# In[17]:

gdfFAO['FAOid'] = gdfFAO.apply(lambda x:'MAJ_BAS_%0.4d_SUB_BASE_%0.7d' % (x['MAJ_BAS'],x['SUB_BAS']),axis=1)


# In[18]:

gdfFAO.index.name


# In[20]:

dfFAO = gdfFAO.drop('geometry',1)


# In[21]:

dfFAO.head()


# In[22]:

gdfFAO['FAOid_copy'] = gdfFAO['FAOid']


# In[25]:

gdfFAO.index.name


# In[23]:

list(gdfFAO)


# In[24]:

gdfFAO = gdfFAO.dissolve(by='FAOid')


# In[ ]:

list(gdfFAO)


# In[ ]:

dfFAO = gdfFAO.drop('geometry',1)


# In[ ]:

dfFAO.head()


# In[ ]:

gdfFAOTest = gdfFAO.loc[100:200]


# In[ ]:

validGeom = gdfFAO.geometry.is_valid


# In[27]:

gdfFAO.crs = {'init': u'epsg:4326'}


# In[29]:

gdfFAO = gdfFAO.set_index('index1_copy')


# In[30]:

gdfJoined = gpd.sjoin(gdfHybas, gdfFAO ,how="left", op='intersects')


# In[31]:

list(gdfJoined)


# In[33]:

gdfJoined.shape


# In[37]:

series = gdfJoined.groupby('PFAF_ID')['SUB_NAME'].apply(list)
series2 = gdfJoined.groupby('PFAF_ID')['MAJ_NAME'].apply(list)
series3 = gdfJoined.groupby('PFAF_ID')['FAOid_copy'].apply(list)


# In[38]:

df_new1 = series.to_frame()
df_new2 = series2.to_frame()
df_new3 = series3.to_frame()


# In[36]:

df_new1.head()


# In[45]:

df_out = df_new1.merge(right = df_new2, how = "outer", left_index = True, right_index = True )


# In[46]:

df_out = df_out.merge(right = df_new3, how = "outer", left_index = True, right_index = True )


# In[47]:

df_out.dtypes


# In[48]:

df_out.to_csv(os.path.join(EC2_OUTPUT_PATH,OUTPUT_FILE_NAME),encoding="UTF-8")


# In[49]:

get_ipython().system('aws s3 cp {EC2_OUTPUT_PATH} {S3_OUTPUT_PATH} --recursive')

