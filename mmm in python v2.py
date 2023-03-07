import pprint as pp
import pandas as pd
import glob
import os
def data_prep(name): 
    """finds raw data that matches name and then cocats them into the same dataframe"""
    all_files=[]   
    raw_files=glob.glob(f'*{name}*.csv') #glob finds all csv files where it finds name(the brand we give it) and saves it in raw files
    for file in raw_files:
        print(f"found this file matching your request: {file}") #this tells the user which files it found
        df=pd.read_csv(file,index_col=0,header=12,skip_blank_lines=False,dtype={'Campaign ID':str,'Site (CM360)':str}) # because of the format of out put from dcm, we need to explicitly tell it what row to start at and wether or not to skip blank rows.
        df=df[:-1] # this limits the length of the file to the 2nd to last row, since we have a grand total collumn in the output from DCM, this gets rid of that row
        all_files.append(df)
    concat_data=pd.concat(all_files,ignore_index=False,axis=0)
    return concat_data

def clean(all_data):
    """puts concated raw data in excel as 'raw', cleans data and returns it seperated as impresssions and spend dataframes"""
    df=pd.DataFrame(all_data)    
    df=df.drop(labels=['Clicks','Click Rate','Active View: Viewable Impressions','Active View: Measurable Impressions','Active View: Eligible Impressions','Total Conversions'],axis=1) # this drops colllumns that we dont use for analysis
    df=df.dropna(axis=1) # gets rid of rows with NA's in them
    df=df[(df!=0).all(1)] # returns only the rows that dont have 0 in them.
    df['Date']=pd.to_datetime(df['Date']) # converts date collumn to date time format, this is so we can easily use this as an index and group by week later in the script.
    df['Week Start']=df['Date'] - pd.to_timedelta(df['Date'].dt.dayofweek, unit='d') # convert date to week start data
    df.rename(columns={'Site (CM360)':'Partner','Designated Market Area (DMA)':'DMA'},inplace=1) # rename 'site (CM360)' to Partner and 'designated market area (DMA)' to DMA 
    impressions=df.drop(labels='Media Cost',axis=1) # creates the impressions clean file 
    Spend=df.drop(labels='Impressions',axis=1) # creates the media cost clean file
    impressions_agg=impressions.groupby(['Week Start','Partner','DMA','Placement','Campaign'],as_index=False)['Impressions'].sum()
    Spend_agg=Spend.groupby(['Week Start','Partner','DMA','Placement','Campaign'],as_index=False)['Media Cost'].sum()
    return impressions_agg,Spend_agg
def channel_seperator(impressions,spend):
    group_of_chanels=['CTV','OLV','Display','AUD','Social','Search']
    new_imps={}
    new_spend={}
    for i in group_of_chanels:
        new_imps[i]=new_imps.get(i,impressions[impressions['Placement'].str.contains(i)]) #creates the spreadsheets for impressions
        new_spend[i]=new_spend.get(i,spend[spend['Placement'].str.contains(i)]) #creates the spreadsheets for spend
    # if new_imps.keys =='AUD':
    #         new_imps['AUD']=new_imps['AUD'].groupby('Week Start','Partner','Placement','Campaign',as_index=False)['Impressions'].sum()
    # if new_spend.keys =='AUD':
    #         new_spend['AUD']=new_spend['AUD'].groupby('Week Start','Partner','Placement','Campaign',as_index=False)['Media Cost'].sum()
    print(new_imps)
    # for i in new_imps:

    return new_imps,new_spend

# def group_by(impressions,spend): 
#     impressions=pd.DataFrame(impressions)
#     for i in impressions:
#         impressions=pd.DataFrame.groupby(impressions['Week'].dt.date,as_index=1).sum()
#     print(impressions)
#     return




    
    


if __name__ == "__main__":
    os.chdir("C:\Desktop\python_scripts/raw_data/mmm") # YOU MUST CHANGE THE ROOT DIRECTORY FOR THE CODE TO WORK, GLOB.GLOB USES THE ROOT DIRECTORY FOR THE LOCATION TO SEARCH, THIS LINE CHANGES IT.
    raw=data_prep('CIG')
    impressions,spend=clean(raw)
    impressions,spend=channel_seperator(impressions,spend)
#need to build a mmm pull automater as well, i can import the data from dcm but the excel work should be automated, concats, globs, and some filtering, with finding the starting day of the week,

# Step 3: 