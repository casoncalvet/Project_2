#!/usr/bin/env python
# coding: utf-8

# In[2]:


#def import_all(): 
    
def import_all(): 
    import requests
    import pandas as pd
    import requests
    import re
    from pandas import json_normalize
    import json
    import os
    from dotenv import load_dotenv 
    import tweepy
    import seaborn as sns 
    import matplotlib.pyplot as plt
    import squarify 
    import numpy as np 
    import geopandas as gpd
    import plotly.express as px 
import_all()


# In[2]:


## Connect to API 

def connect(link): 
    to_transform= requests.get(link)
    json= to_transform.json()
    return json

nobels= connect("http://api.nobelprize.org/2.1/laureates?limit=1000&csvLang=en")


# In[ ]:


# separate laureates and place into df 

laureates= nobels['laureates']
df= pd.DataFrame(laureates)
df1= df[['gender','nobelPrizes', 'fullName']]

#Now, begin unravelling nobel prizes dictionary 
dict_nobels= df1['nobelPrizes']
dict_nobels

## get year and category from dict_nobels
def get_year(x,y): 
    years= []
    for i in range(len(dict_nobels)):
        years.append(dict_nobels[i][0][y]) 
    df1[x]  = years 
    return df1[x]
get_year('Year', 'awardYear')

# Get category 
def get_cat(rename,ogcol): 
    categories= []
    for i in range(len(dict_nobels)):
        categories.append(dict_nobels[i][0][ogcol]['en']) 
    df1[rename]  = categories 
    return df1[rename]

get_cat('Category','category')
df1


# In[884]:


## Drop na to avoid endless errors in for loop 
df1 = df1.dropna()
df1 = df1.reset_index()


# In[885]:


## Get Names from API 

namedict= df1['fullName']

def get_name(newcol):
    names= []
    for i in range(len(df1)):
        names.append(df1['fullName'][i]['en'])
    df1[newcol]= names
    return df1[newcol]
get_name('Name')


# In[997]:


# Extract countries
dfcuntt= pd.DataFrame(laureates)
dfcuntt= dfcuntt[['birth', 'id']]
dfcuntt= dfcuntt.dropna(inplace=True)
birth_dict= dfcuntt['birth']


# In[1037]:


#birth_dict[0][3]['birth']['en']
def get_country(newcolu):
    countries= [] 
    for i in range(len(birth_dict)):
        try: 
            countries.append(birth_dict[i]['place']['country']['en'])
        except KeyError: 
            countries.append("NaN")
        except ValueError:
            countries.append("NaN")
        except TypeError: 
            countries.append("NaN")
    dfcuntt[newcolu]= countries 
    return dfcuntt[newcolu]
get_country('Country')


# In[1261]:


def clean_countries(dfcuntt):
    countries= dfcuntt['Country']
    countries= pd.DataFrame(countries)
    cleancountries= countries[countries['Country']!= "NaN"]
    cleancountries['Country']= cleancountries['Country'].str.replace('Austrian Empire','Austria')
    cleancountries['Country'] = cleancountries['Country'].str.replace('Austria-Hungary','Austria')
    cleancountries['Country'] = cleancountries['Country'].str.replace('British Protectorate of Palestine','British Mandate of Palestine')
    cleancountries['Country'] = cleancountries['Country'].str.replace('Faroe Islands (Denmark)','Denmark')
    cleancountries['Country'] = cleancountries['Country'].str.replace('German-occupied Poland','Poland')
    cleancountries['Country'] = cleancountries['Country'].str.replace('Russian Empire','Russia')
    country_counts= pd.DataFrame(cleancountries.value_counts())
    country_counts= pd.DataFrame(cleancountries.value_counts())   
    country_counts=country_counts.rename(columns= {0: 'Count'})
    top10= country_counts[:10]
    return top10


# In[888]:


def Sort_year(df1):
    # Sort df by year 
    df1= df1.sort_values(by= ['Year'])
    df1 = df1.reset_index(drop= True)
    df1.rename(columns= {'gender':'Gender'}, inplace=True)
    df1= df1[['Year','Name','Category','Gender']]
    return df1


# In[155]:


def GenderCategorynGraph(df1): 
    males= df1[df1['Gender']== 'male']
    labelsm = males.groupby('Category').sum().index.get_level_values(0).tolist()
    m= males.groupby('Category').count()
    sizem= m['Year']
    #females 
    females = df1[df1['Gender']== 'female'] 
    labelsf = females.groupby('Category').sum().index.get_level_values(0).tolist()
    f= females.groupby('Category').count() 
    sizef= f['Year']
    # Male tree map  
    sns.set_style()
    fig, ax= plt.subplots(1,2, figsize= (15,5))
    plt.sca(ax[0])
    squarify.plot(sizes=sizem,label=labelsm, alpha=.8 )
    plt.set_cmap('YlOrRd')
    plt.xlabel("Male Laureates")
    plt.xticks([])
    plt.yticks([])
    #Female Treemap 
    plt.sca(ax[1])
    plt.set_cmap('YlOrRd')
    squarify.plot(sizes=sizef,label=labelsf, alpha=.9)
    plt.xlabel("Female Laureates")
    plt.xticks([])
    plt.yticks([])
    #plt.savefig('../images/MvsFLaureateCategories.png', bbox_inches='tight')
    return plt.show()


# In[110]:


## Interactive Tree map of Woman Winners 

fem= females[['Category', 'Year', 'Name']]

def TreeMapFemale(): 
    fig= px.treemap(fem, path= fem.columns ,width=1000, height=600)
    colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c'] 
    fig.update_layout(
    treemapcolorway = colors, #defines the colors in the treemap
    margin = dict(t=50, l=25, r=25, b=25))
    #fig.write_html("/Users/casonberkenstock/Project-2/images/FemaleLaureates.html")
    return fig.show()


# In[109]:


## Interactive Tree map of Men Winners 
def TreeMapMale(): 
    males= df1[df1['Gender']== 'male']
    male= males[['Category', 'Year', 'Name']]
    fig= px.treemap(male, path= male.columns ,width=1000, height=600)
    colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c'] #color palette
    fig.update_layout(
    treemapcolorway = colors, #defines the colors in the treemap
    margin = dict(t=50, l=25, r=25, b=25))
    #fig.write_html("/Users/casonberkenstock/Project-2/images/MaleLaureates.html")
    return fig.show()


# In[368]:


def NobelLineGraph(females, males): 
    FperYr= females.groupby('Year').size()
    MperYr= males.groupby('Year').size()
    plt.figure(figsize=(10, 5))
    plt.plot(MperYr)
    plt.plot(FperYr)
    plt.xticks(np.arange(0, 126, 5))
    plt.xticks(rotation = 45)
    ax= plt.gca()
    ax.legend(['Male', 'Female'])
    plt.title('Nobel Prizes Awarded Each Year ')
    #plt.savefig('../images/NobelPrizesYears.png', dpi= 100)


# In[1262]:


def BarPlotNobel(males, females): 
    plt.figure(figsize=(10, 5))
    men= males.groupby('Category').size()
    bar1 = sns.barplot(x= men.index,y= men[:], data=males, color='orange')
    fen= females.groupby('Category').size()
    bar2 = sns.barplot(x= fen.index,y= fen[:], data=females, color='lightblue')
    plt.legend(['Males', 'Females'])
    ax = plt.gca()
    leg = ax.get_legend()
    leg.legendHandles[0].set_color('orange')
    leg.legendHandles[1].set_color('lightblue')
    plt.xlabel('Prize Category')
    plt.title('Nobel Prize Winners')
    #plt.savefig('../images/Barplot.png', bbox_inches='tight')
    return plt.show()


# In[376]:


## Read csv for GDI/ GNI 
GDIdf= pd.read_csv('../datasets/GDI.csv')
GDIdf.head()


# In[697]:


#Explore if women rewarded less than men for years of school 

GDIdfextract= GDIdf[['GDI_Value', 'HDI_Female', 'HDI_Male', 'GDI_Group', 'Lif_Expec_Female','Lif_Excep_Male', 'Mean_Yrs_Schooling_Female', 'Mean_Yrs_Schooling_Male', 'GNI_PC_Female', 'GNI_PC_Male']]

## Clean Mean Years Schooling Female, GNI Female, and GDI Group Columns of NA
def CleanSchGNIGDIF(GDIdfextract): 
    myrs= GDIdfextract[['Mean_Yrs_Schooling_Female', 'GNI_PC_Female', 'GDI_Group']]
    myrs= myrs.loc[1:]
    myrs.replace('...', 'NaN', inplace= True)
    myrs.replace('..', 'NaN', inplace= True)
    myrs.drop(myrs.index[myrs['Mean_Yrs_Schooling_Female'] == 'NaN'], inplace = True)
    myrs.drop(myrs.index[myrs['GNI_PC_Female'] == 'NaN'], inplace = True)
    myrs.drop(myrs.index[myrs['GDI_Group'] == 'NaN'], inplace = True)
    #myrs['GNI_PC_Female'] = myrs['GNI_PC_Female'].str.replace(r",", "", regex=True)
    #myrs['GNI_PC_Female']= myrs['GNI_PC_Female'].astype('int')
    return myrs
CleanSchGNIGDIF(GDIdfextract)


# In[1265]:


#Scatter plot of mean yrs schooling 

def ScatterGNIF(myrs): 
    '''
    Must run after CleanSchGNIGDIF function to plot result of cleaning df to myrs.
    Plots female schooling years vs GNI 
    '''
    fig, ax = plt.subplots(1,1)
    g= sns.scatterplot(x=myrs["GNI_PC_Female"], y=myrs["Mean_Yrs_Schooling_Female"])
    xtick_spacing = 10
    ytick_spacing= 10
    ax.xaxis.set_major_locator(ticker.MultipleLocator(xtick_spacing))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(ytick_spacing))
    plt.xticks(rotation=45) 
    g.invert_xaxis()
    return plt.show()
ScatterGNIF(myrs)


# In[1267]:



def CleanSchGNIGDIM(GDIdfextract): 
 '''
 Clean School/GNI/GDI Males df for graphing 
 '''
 GNI= GDIdfextract[['GNI_PC_Male', 'Mean_Yrs_Schooling_Male', 'GDI_Group']]
 GNI= GNI[1:]
 GNI.replace('...', 'NaN', inplace= True)
 GNI.replace('..', 'NaN', inplace= True)
 GNI.drop(GNI.index[GNI['Mean_Yrs_Schooling_Male'] == 'NaN'], inplace = True)
 GNI.drop(GNI.index[GNI['GNI_PC_Male'] == 'NaN'], inplace = True)
 GNI.drop(GNI.index[GNI['GDI_Group'] == 'NaN'], inplace = True)
 #GNI['GNI_PC_Male'] = GNI['GNI_PC_Male'].str.replace(r",", "", regex=True)
 #GNI['GNI_PC_Male']= GNI['GNI_PC_Male'].astype('int')
 return GNI

def ScatterGNIM(GNI): 
 '''
 Must run after CleanSchGNIGDIM function to plot result of cleaning df with GNI
 Plots male schooling years vs GNI 
 '''
 fig, ax = plt.subplots(1,1)
 g= sns.scatterplot(x=GNI["GNI_PC_Male"], y=GNI["Mean_Yrs_Schooling_Male"])
 xtick_spacing = 10
 ytick_spacing= 10
 ax.xaxis.set_major_locator(ticker.MultipleLocator(xtick_spacing))
 ax.yaxis.set_major_locator(ticker.MultipleLocator(ytick_spacing))
 plt.xticks(rotation=45) 
 g.invert_xaxis()
 return plt.show()
ScatterGNIM(GDIdfextract)

## No significant difference in male vs female reward on education, except that men simply get paid more, 
# which can be shown through other plots 


# In[669]:


# Clean DF to plot F vs M income, grouped by GDI Group (1-5)
def clean_FvsMgdigni(GDIdfextract): 
    GNIvsGDI= GDIdfextract[['GNI_PC_Female', 'GNI_PC_Male', 'GDI_Group']]
    GNIvsGDI= GNIvsGDI[1:]
    GNIvsGDI.replace('...', 'NaN', inplace= True)
    GNIvsGDI.replace('..', 'NaN', inplace= True)
    GNIvsGDI.drop(GNIvsGDI.index[GNIvsGDI['GNI_PC_Female'] == 'NaN'], inplace = True)
    GNIvsGDI.drop(GNIvsGDI.index[GNIvsGDI['GNI_PC_Male'] == 'NaN'], inplace = True)
    GNIvsGDI.drop(GNIvsGDI.index[GNIvsGDI['GDI_Group'] == 'NaN'], inplace = True)   


# In[712]:


GNIvsGDI['GNI_PC_Female'] = GNIvsGDI['GNI_PC_Female'].str.replace(r",", "", regex=True)
GNIvsGDI['GNI_PC_Male'] = GNIvsGDI['GNI_PC_Male'].str.replace(r",", "", regex=True)
GNIvsGDIfixed= GNIvsGDI[['GNI_PC_Female', 'GNI_PC_Male' ]].astype('int')
GNIvsGDIfixed['GDI_Group']= GNIvsGDI['GDI_Group']
GNIvsGDImixed=GNIvsGDIfixed.melt(id_vars=['GDI_Group'], value_vars= ['GNI_PC_Female', 'GNI_PC_Male'])
GNIvsGDImixed=GNIvsGDImixed.rename(columns= {'variable': 'Sex', 'value': 'GNI_PC'})


# In[731]:


import matplotlib.patches as mpatches


# In[1231]:


def GNIGDIbar(GNIvsGDIfixed):
    sns.set(style="darkgrid")
    plt.figure(figsize=(8, 6))
    sns.barplot(y='GNI_PC_Male', x='GDI_Group', data=GNIvsGDIfixed, color= 'darkblue', order= ['1', '2', '3', '4', '5']) 
    sns.barplot(y='GNI_PC_Female', x='GDI_Group', data=GNIvsGDIfixed, color= 'lightblue', ci= None, order= ['1', '2', '3', '4', '5'])
    top_bar = mpatches.Patch(color='darkblue', label='Male')
    bottom_bar = mpatches.Patch(color='lightblue', label='Female')
    plt.legend(handles=[top_bar, bottom_bar])
    plt.ylabel('USD ($)')
    plt.xlabel('Gender Development Index Group')
    plt.title('Gross National Income (Per Capita) Among GDI Groups')
    #plt.savefig('../images/BarplotGDI.png', bbox_inches='tight')
    return plt.show()


# In[1236]:


# Table Depicting Wage Gap by GDI Group # 
def FMRatio(GNIvsGDIfixed): 
    GNIgrouped= GNIvsGDIfixed.groupby('GDI_Group').mean()
    GNIgrouped= GNIgrouped[['GNI_PC_Female','GNI_PC_Male']].round()
    GNIgrouped['Total']= GNIgrouped.sum(axis=1)
    GNIgrouped['Ratio F:M Pay']= (GNIgrouped['GNI_PC_Female']/GNIgrouped['Total']).round(2)
    GNIgrouped= GNIgrouped.drop('Total', axis=1)
    #dfi.export(GNIgrouped, 'df.png', table_conversion="matplotlib")
    return GNIgrouped


# In[1237]:


FMRatio(GNIvsGDIfixed)


# In[1235]:


#GNIgrouped.drop('Total', axis=1)


# In[854]:





# In[1239]:


cuntries= GDIdf[['Country', 'GDI_Group']]
cuntries= cuntries[1:]
cuntries= cuntries.dropna()
cuntries[cuntries['Country']== 'Norway']
#cuntycount=cuntycount.rename(columns= {0:'Count'})
#cuntycount= cuntycount.sort_values(by= 'Count')


# In[1238]:


def top10bar(top10): 
    top10['GDIs']= [1, 2, 2, 1, 1, 2, 1, 1,1, 2]
    #top10= top10.reset_index()
    fig, ax = plt.subplots(figsize=(5,5))
    sns.barplot(x= 'Count', y='Country', data=top10, orient = 'h', hue= 'GDIs', palette= 'mako')
    plt.xlabel('Nobels Awarded')
    plt.title('each has a GDI less than 3')
    plt.suptitle('Top 10 Nobel Winning Countries')
    #plt.savefig('../images/Top10.png', bbox_inches='tight')
    return plt.show


# In[1214]:





# In[1260]:



palette_color = sns.color_palette('icefire')
plt.pie([60,894], labels = ['Women', 'Men'], colors= palette_color)
plt.title('Laureates')
plt.savefig('../images/piee.png', bbox_inches='tight')


# In[ ]:




