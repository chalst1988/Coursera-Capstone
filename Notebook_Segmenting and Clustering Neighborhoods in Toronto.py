#!/usr/bin/env python
# coding: utf-8

# # Notebook- "Segmenting and Clustering Neighborhoods in Toronto"

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


# Installing beautifulsoup package, lxml parser and requests
import sys
#!conda install --yes --prefix {sys.prefix} beautifulsoup4
#!conda install --yes --prefix {sys.prefix} lxml
#!conda install --yes --prefix {sys.prefix} requests


# Use the Notebook to build the code to scrape the following Wikipedia page, https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M, in order to obtain the data that is in the table of postal codes and to transform the data into a pandas dataframe
# 

# In[3]:


import requests
website_url = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text


# In[4]:


from bs4 import BeautifulSoup
soup = BeautifulSoup(website_url,'lxml')
print(soup.prettify())


# # By observation we can see that the tabular data is availabe in table and belongs to class="wikitable sortable"So let's extract only table¶

# In[5]:


My_table = soup.find('table',{'class':'wikitable sortable'})
My_table


# In[6]:


print(My_table.tr.text)


# In[7]:


headers="Postcode,Borough,Neighbourhood"


# # Geting all values in tr and seperating each td within by ","

# In[8]:


table1=""
for tr in My_table.find_all('tr'):
    row1=""
    for tds in tr.find_all('td'):
        row1=row1+","+tds.text
    table1=table1+row1[1:]
print(table1)


# # Writing table data into .csv file for further usage

# In[9]:


file=open("toronto.csv","wb")
#file.write(bytes(headers,encoding="ascii",errors="ignore"))
file.write(bytes(table1,encoding="ascii",errors="ignore"))


# ------------------------------------------------------------------------------------------------------------
# # Part- I
# ------------------------------------------------------------------------------------------------------------

# # 1. Create a dataframe consists of three columns: PostalCode, Borough, and Neighborhood

# In[10]:


df = pd.read_csv('toronto.csv',header=None)
df.columns=["Postalcode","Borough","Neighbourhood"]


# In[11]:


df.head(10)


# # 2. Only process the cells that have an assigned borough. Ignore cells with a borough that is Not assigned.

# In[12]:


# Get names of indexes for which column Borough has value "Not assigned"
indexNames = df[ df['Borough'] =='Not assigned'].index

# Delete these row indexes from dataFrame
df.drop(indexNames , inplace=True)


# In[13]:


df.head(10)


# # 3. If a cell has a borough but a Not assigned neighborhood, then the neighborhood will be the same as the borough

# In[14]:


df.loc[df['Neighbourhood'] =='Not assigned' , 'Neighbourhood'] = df['Borough']
df.head(10)


# # 4. More than one neighborhood can exist in one postal code area. For example, in the table on the Wikipedia page, you will notice that M6A is listed twice and has two neighborhoods: Harbourfront and Regent Park. These two rows will be combined into one row with the neighborhoods separated with a comma

# In[15]:


result = df.groupby(['Postalcode','Borough'], sort=False).agg( ', '.join)
df_new=result.reset_index()
df_new.head(15)


# # 5. In the last cell of your notebook, use the .shape method to print the number of rows of your dataframe.

# In[16]:


df_new.shape


# -----------------------------------------------------------------------------------------------------------------
# # Part- II
# -----------------------------------------------------------------------------------------------------------------

# # Use the Geocoder package or the csv file to create dataframe with longitude and latitude values
# We will be using a csv file that has the geographical coordinates of each postal code: http://cocl.us/Geospatial_data

# In[17]:


get_ipython().system("wget -q -O 'Torronto_geospatial_data.csv'  http://cocl.us/Geospatial_data")
df_lon_lat = pd.read_csv('Torronto_geospatial_data.csv')
df_lon_lat.head()


# In[18]:


df_lon_lat.rename(columns = {'Postal Code': 'Postalcode'}, inplace = True)
df_lon_lat.head()


# In[19]:


df_new.shape, df_lon_lat.shape


# In[20]:


Toronto_df = pd.merge(df_new,
                 df_lon_lat[['Postalcode','Latitude', 'Longitude']],
                 on='Postalcode')
Toronto_df.head(10)


# -------------------------------------------------------------------------------------------------------------------------------
# # Part- III
# ---------------------------------------------------------------------------------------------------------------------------------

# Explore and cluster the neighborhoods in Toronto. You can decide to work with only boroughs that contain the word Toronto and then replicate the same analysis we did to the New York City data. It is up to you.
# 
# Just make sure:
# 
# 1. to add enough Markdown cells to explain what you decided to do and to report any observations you make.
# 
# 2. to generate maps to visualize your neighborhoods and how they cluster together.

# # Use geopy library to get the latitude and longitude values of New York City.

# In[24]:


from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported successfully..')


# In[25]:


address = 'Toronto, ON'

geolocator = Nominatim(user_agent="Toronto")
location = geolocator.geocode(address)
latitude_toronto = location.latitude
longitude_toronto = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude_toronto, longitude_toronto))


# In[26]:


map_toronto = folium.Map(location=[latitude_toronto, longitude_toronto], zoom_start=10)

# add markers to map
for lat, lng, borough, Neighbourhood in zip(Toronto_df['Latitude'], Toronto_df['Longitude'], Toronto_df['Borough'], Toronto_df['Neighbourhood']):
    label = '{}, {}'.format(Neighbourhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='seagreen',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# # Define Foursquare credentials and version

# In[27]:


CLIENT_ID = 'VNWUPMJJ2PQDRXITPENQP1AUGWWWQ2ZDDOECVNX40WXAMVIQ' # your Foursquare ID
CLIENT_SECRET = '2O25YPJ0TYWEAMQS4GEAZ0IG0R2VP0CNRRRACYTJKAQVBDW2' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 100
radius = 500
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[28]:



def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighbourhood', 
                  'Neighbourhood Latitude', 
                  'Neighbourhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[29]:


toronto_venues = getNearbyVenues(names=Toronto_df['Neighbourhood'],
                                   latitudes=Toronto_df['Latitude'],
                                   longitudes=Toronto_df['Longitude']
                                  )


# # Checking the venues and size of dataframe

# In[30]:


toronto_venues.head(10)


# In[31]:


toronto_venues.shape


# In[32]:


toronto_venues.groupby('Neighbourhood').count()


# # Analyzing each neighborhood and with venues

# 1. Converting Venue category to numeric ie., one hot encoding

# In[33]:


toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighbourhood'] = toronto_venues['Neighbourhood'] 

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot.head()


# In[34]:


toronto_onehot.shape


# 2. Grouping rows by neighborhood and by taking the mean of the frequency of occurrence of each category

# In[35]:


toronto_grouped = toronto_onehot.groupby('Neighbourhood').mean().reset_index()
toronto_grouped


# # Print each neighborhood along with the top 5 most common venues

# In[36]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# # Top 10 venues for each neigborhood

# In[37]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighbourhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighbourhoods_venues_sorted = pd.DataFrame(columns=columns)
neighbourhoods_venues_sorted['Neighbourhood'] = toronto_grouped['Neighbourhood']

for ind in np.arange(toronto_grouped.shape[0]):
    neighbourhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

neighbourhoods_venues_sorted.head(10)


# # Clustering Neighborhoods

# Run k-means to cluster the neighborhood into 5 clusters.

# In[38]:


# set number of clusters
kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighbourhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_ 
# to change use .astype()


# In[39]:


# add clustering labels
neighbourhoods_venues_sorted.insert(0, 'Cluster_Labels', kmeans.labels_)

toronto_merged = Toronto_df

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
toronto_merged = toronto_merged.join(neighbourhoods_venues_sorted.set_index('Neighbourhood'), on='Neighbourhood')

toronto_merged.head() # check the last columns!


# In[40]:


toronto_merged=toronto_merged.dropna()


# # Examine Clusters one by one

# # Cluster 1

# In[41]:


toronto_merged.loc[toronto_merged['Cluster_Labels'] == 0, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# # Cluster 2

# In[42]:


toronto_merged.loc[toronto_merged['Cluster_Labels'] == 1, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# # Cluster 3

# In[43]:


toronto_merged.loc[toronto_merged['Cluster_Labels'] == 2, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# # Cluster 4

# In[44]:


toronto_merged.loc[toronto_merged['Cluster_Labels'] == 3, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# # Cluster 5

# In[45]:


toronto_merged.loc[toronto_merged['Cluster_Labels'] == 4, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[46]:


# create map
map_clusters = folium.Map(location=[latitude_toronto, longitude_toronto], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Neighbourhood'], toronto_merged['Cluster_Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[int(cluster)-1],
        fill=True,
        fill_color=rainbow[int(cluster)-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:




