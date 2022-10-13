#!/usr/bin/env python
# coding: utf-8

# # The Category 2 airlines automator for the World Bank Airline Advisory System.
# The Airline Advisory Safety System (AAS) is an evaluation tool for the assessment of the risks associated with air travel by Bank staff since FY 2008
# All carriers in the Airline Advisory Safety System are classified into the following five categories: 
# Category 1: IATA IOSA (International Air Transport Association Operational Safety Audit) Certification registered carriers;
# Category 2:  FAA IASA (Federal Aviation Administration International Aviation Safety Assessment) Rating Category 1 licensed carriers;
# Category 3:  Carriers outside Category 1 and 2. Category 3 airlines need further invastigation to take into consideration four risk-increasing factors and to have an appropriate sub-category associated with each carrier.
# ### The program creates the list of Category 2 and Category 3 carriers. It launches the list of IASA countries from FAA portal and associates its country rating with the whole potential Category 2 & Category 3 carriers based on country names. The list of potential category 2 and category 3 carriers is taken from the latest offline verion of AAS, sheets: 'CAT 2' and 'CAT 3' carriers.

# ### Variables discription:
# df: IASA countries database
# 
# result: cleaned and ready-to-work IASA database
# 
# df_main: list of countries from the latest version of offline AAS
# 
# df_result: df_main list supplemented by country rating from result database.
# 
# cat2_list: the list of all potential CAT 2 airlines.
# 
# cat2_result: cat2_list with associated IASA rating
# 
# cat2: CAT 2 airlines which is obtained from cat2_result taking only FAA IASA category 1 countries
# 
# cat3: CAT 3 airlines which is obtained from cat2_result taking all the remaining countries.
# 

# ## STEP 1. 
# Launching the latest list of IASA countries from FAA portal. Normalize the list for further work. 

# In[4]:


import urllib
outfilename = "IASA_countries.xlsx"
url_of_file = "https://www.faa.gov/sites/faa.gov/files/2022-07/IASA_Progam_Results_0.xlsx"
urllib.request.urlretrieve(url_of_file, outfilename) 


# In[5]:


#download data from the excel file into workbook:
import pandas as pd
from pandas import read_excel
df = read_excel("IASA_Countries.xlsx")
#df.iloc[:,[1,2,5,6]]


# In[6]:


#keeping only necessary dataset:
df = df.rename(columns={'FAA  Flight Standards Service': 'Country_list', 'Unnamed: 2': 'Category_list','Unnamed: 5':'Country_list', 'Unnamed: 6': 'Category_list'})
df.iloc[:,[1,2,5,6]]
list1=df.iloc[:,[1,2]]
list2=df.iloc[:,[5,6]]
list1=list1.loc[list1['Category_list'].notnull()]
list2=list2.loc[list2['Category_list'].notnull()]


# In[7]:


#Now we have the whole list of countries and its categories:
frames = [list1, list2]
result = pd.concat(frames)
new_header = result.iloc[0]
result = result[1:] #take the data less the header row
result.columns = new_header
result['CATEGORY'] = result['CATEGORY'].astype(str)
result=result.loc[result['CATEGORY'].isin(['1','2'])]
result.rename({'COUNTRY': 'Country', 'CATEGORY': 'Category'}, axis=1, inplace=True)
#add US:
add_US = {'Country': 'United States of America', 'Category': '1'}
result = result.append(add_US, ignore_index = True)
#delete space at the end i.e. Serbia:
result['Country']=result['Country'].str.rstrip()

result


# ## STEP 2
# 
# Matching IASA list of countries with our own list.
# ### 2.1. Create our own list of countries based on current offline AAS:
# 
# 

# In[8]:


#take all the countries from all three categories and creating the aggregating list:
import xlwings as xw
workbook = xw.Book('/Users/dianatolstyga/Documents/WORLD BANK/AIR TRANSPORT/AAS/Airline Advisory Database 15June2022.xlsx')
worksheet1=workbook.sheets['CAT 1'].used_range.value
worksheet2=workbook.sheets['CAT 2'].used_range.value
worksheet3=workbook.sheets['CAT 3'].used_range.value
df_main1=pd.DataFrame(worksheet1)
df_main2=pd.DataFrame(worksheet2)
df_main3=pd.DataFrame(worksheet3)
main1_header = df_main1.iloc[0] 
df_main1 = df_main1[1:] 
df_main1.columns = main1_header
main2_header = df_main2.iloc[0] 
df_main2 = df_main2[1:] 
df_main2.columns = main2_header
main3_header = df_main3.iloc[0] 
df_main3 = df_main3[1:] 
df_main3.columns = main3_header

df_frames = [df_main1['Country'], df_main2['Country'], df_main3['Country'] ]
df_main = pd.concat(df_frames)
df_main=df_main.drop_duplicates()
df_main = df_main.to_frame().reset_index()
df_main




# ### 2.2.  Match AAS country names with those from IASA list 

# In[9]:


#creating a separate 'translation' column for proper matching for some dependent territories and ambivalent country names:

def territories (row):
   if row['Country'] == 'Denmark' : #our name
      return 'Denmark incl. Faroe Islands' #is renamed on IASA name
   if row['Country'] == 'Greenland' :
      return 'Denmark incl. Faroe Islands'
   if row['Country'] == 'Faroe Islands' :
      return 'Denmark incl. Faroe Islands'
   if row['Country'] == 'France' :
      return 'France   incl.  Guadeloupe,  French Polynesia'
   if row['Country'] == 'Guadeloupe' :
      return 'France   incl.  Guadeloupe,  French Polynesia'
   if row['Country'] == 'French Polynesia' :
      return 'France   incl.  Guadeloupe,  French Polynesia'
   if row['Country'] == 'French Guiana' :
      return 'France   incl.  Guadeloupe,  French Polynesia' 
   if row['Country'] == 'Netherlands' :
      return 'Netherlands incl. Bonaire, Saba, St.Eustatius'
   if row['Country'] == 'Bonaire' :
      return 'Netherlands incl. Bonaire, Saba, St.Eustatius'
   if row['Country'] == 'Saba':
      return 'Netherlands incl. Bonaire, Saba, St.Eustatius'
   if row['Country']  == 'St.Eustatius':
      return 'Netherlands incl. Bonaire, Saba, St.Eustatius'
   if row['Country'] == 'Sint Maarten (Dutch part)':
      return 'Netherlands incl. Bonaire, Saba, St.Eustatius'
   if row['Country'] == 'United Kingdom':
      return 'United Kingdom  incl. Anguilla,  British Virgin Islands,   Montserrat,  Turks and Caicos'
   if row['Country'] == 'Anguilla':
      return 'United Kingdom  incl. Anguilla,  British Virgin Islands,   Montserrat,  Turks and Caicos'
   if row['Country'] == 'British Virgin Islands':
      return 'United Kingdom  incl. Anguilla,  British Virgin Islands,   Montserrat,  Turks and Caicos'
   if row['Country'] == 'Montserrat':
      return 'United Kingdom  incl. Anguilla,  British Virgin Islands,   Montserrat,  Turks and Caicos'
   if row['Country'] == 'Turks and Caicos Islands':
      return 'United Kingdom  incl. Anguilla,  British Virgin Islands,   Montserrat,  Turks and Caicos'
   if row['Country'] == 'Antigua And Barbuda':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'Dominica':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'Grenada':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'St. Lucia':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'St. Vincent and The Grenadines':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'St. Kitts and Nevis':
      return 'Organization of Eastern Caribbean States - Eastern Caribbean Civil Aviation Authority members : Antigua & Barbuda, Dominica, Grenada, St. Lucia, St. Vincent and The Grenadines,  St. Kitts and Nevis'
   if row['Country'] == 'Virgin Islands':
      return 'United States of America'
   if row['Country'] == 'Northern Mariana Islands':
      return 'United States of America'
   if row['Country'] == 'Puerto Rico':
      return 'United States of America'
   if row['Country'] == 'Virgin Islands (U.S.)':
      return 'United States of America'
   if row['Country'] == 'Macao':
      return 'China'
   if row['Country'] == 'Hong Kong (SAR), China':
      return 'Hong Kong'
   if row['Country'] == 'Macao (SAR), China':
      return 'China'
   if row['Country'] == 'China (People\'s Republic of)':
      return 'China'
   if row['Country'] == 'Chinese Taipei':
      return 'Taiwan' 
   if row['Country'] == 'Korea, Democratic People\'s Republic of':
      return 'Republic of Korea'
   if row['Country'] == 'Korea, Republic of':
      return 'Republic of Korea'
   if row['Country'] == 'Trinidad and Tobago':
      return 'Trinidad & Tobago'
   if row['Country'] == 'Russian Federation':
      return 'Russia'
   if row['Country'] == 'Cape Verde':
      return 'Cabo Verde'
   if row['Country'] == 'Moldova, Republic of':
      return 'Moldova'
   if row['Country'] == 'Iran, Islamic Republic of':
      return 'Iran'
   if row['Country'] == 'Tanzania, United Republic of':
      return 'Tanzania'
   if row['Country'] ==  'Lao People\'s Democratic Republic':
      return 'Laos'
   if row['Country'] ==  'Congo, Democratic Republic of the':
      return'Congo, Democratic Republic of'   

   return row['Country']

df_main['Country_translation'] = df_main.apply (lambda row: territories(row), axis=1)
df_main


# In[10]:


#Assign two tables:
df_main.rename(columns={'Country': 'Country_initial_list', 'Country_translation': 'Country'}, inplace=True)

df_main


# In[11]:


df_result=pd.merge(df_main, result, how='outer', on='Country')


# In[12]:


#create an excel file of AAS countries with IASA countries' rating
with pd.ExcelWriter('df_main.xlsx') as writer:
    df_main.to_excel(writer, sheet_name='Our list')
    result.to_excel(writer, sheet_name='IASA list')
    df_result.to_excel(writer, sheet_name='Combined list')


# ## STEP 3. 
# After we have all our countries categorized based on the latest IASA list, we can create the list of Category 2 airlines i.e. the FAA IASA Category 1 licensed carriers.

# ### 3.1. Gathering the list of all potential category 2 airlines: we take all the carierrs from CAT 2 and CAT 3 sheets of the latest offline AAS database:

# In[13]:


cat2_list1=pd.DataFrame(worksheet2)
cat2_list1=cat2_list1.iloc[:,[0,1,2,4]]
cat2_list2=pd.DataFrame(worksheet3)
cat2_list2=cat2_list2.iloc[:,[0,1,2,3]]
list1_header = cat2_list1.iloc[0] 
cat2_list1 = cat2_list1[1:] 
cat2_list1.columns = list1_header 
list2_header = cat2_list2.iloc[0] 
cat2_list2 = cat2_list2[1:] 
cat2_list2.columns = list2_header

cat2_frames = [cat2_list1, cat2_list2]
cat2_list = pd.concat(cat2_frames)
cat2_list.rename(columns={'Country': 'Country_initial_list'}, inplace=True)

cat2_list


# ### 3.2. Keeping only FAA IASA Cat1 carriers as cat 2 carriers, and all the remaining carriers go to cat 3 list:
# 
# 

# In[14]:


#But first lets add country rating country rating:
cat2_result=pd.merge(cat2_list, df_result, on='Country_initial_list', how="left")
cat2_result = cat2_result[cat2_result['Airline Callsign'].notna()]

cat2 = cat2_result[cat2_result['Category'] == '1']
cat3 = cat2_result[cat2_result['Category'] != '1']
cat2 = cat2.iloc[:,[0,1,2,3,5,6]]
cat3 = cat3.iloc[:,[0,1,2,3,5,6]]

cat2_result


# In[15]:


#saving the result to excel file:
with pd.ExcelWriter('Cat2&3_airlines.xlsx') as writer:
    cat2_result.to_excel(writer, sheet_name='Cat2&3_total')
    cat2.to_excel(writer, sheet_name='CAT 2')
    cat3.to_excel(writer, sheet_name='CAT 3')


# ### Next steps:
#     1.As a next step, a category 1 carriers list can be created. An automator will tale the latest version of IATA IOSA registered carriers from IATA website and read 'comments' column to check the registration status.
#     2. Then we can supplement the list of potential cat 2 carriers: former CAT 1 list + new IATA IOSA list - cleaned new IATA IOSA list) 
#     3. We could check if online and offline versions of AAS are properly matched

# In[ ]:




