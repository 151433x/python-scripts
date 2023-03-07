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
    concat_data=pd.concat(all_files,ignore_index=True,axis=0)
    print(concat_data)
    return concat_data

def clean(all_data):
    """puts concated raw data in excel as 'raw', cleans data and returns it """
    # with pd.ExcelWriter('OBS impressions MMM pull.xlsx',mode='w')as writer:
    #     all_data.to_excel(writer,sheet_name='raw',index=False)
    ctv=[]
    olv=[]
    dis=[]
    aud=[]
    social=[]
    search=[]  
    df=pd.DataFrame(all_data)
    df=df.dropna(axis=1,) # gets rid of rows with NA's in them
    df['Date']=pd.to_datetime(df['Date']) # converts date collumn to date time format, this is so we can easily use this as an index and group by week
    df=df.drop(labels=['Clicks','Click Rate','Active View: Viewable Impressions','Active View: Measurable Impressions','Active View: Eligible Impressions','Total Conversions'],axis=1)    
    print(df.head())
    # for i in df:
    #     if df['Placement'].str.contains('CTV'):
    #         ctv.append(df[i])
    #     elif df['Placement'].str.contains('OLV'):
    #         olv.append(df[i])
    #     elif df['Placement'].str.contains('DIS'):
    #         dis.append(df[i])
    #     elif df['Placement'].str.contains('AUD'):
    #         aud.append(df[i])
    #     elif df['Placement'].str.contains('Social'):
    #         social.append(df[i])
    #     elif df['Placement'].str.contains('Search'):
    #         search.append(df[i])    



if __name__ == "__main__":
    os.chdir("C:\Desktop\python_scripts/raw_data/mmm") # YOU MUST CHANGE THE ROOT DIRECTORY FOR THE CODE TO WORK, GLOB.GLOB USES THE ROOT DIRECTORY FOR THE LOCATION TO SEARCH, THIS LINE CHANGES IT.
data_prep('CIG')

#need to build a mmm pull automater as well, i can import the data from dcm but the excel work should be automated, concats, globs, and some filtering, with finding the starting day of the week,

# step 1: we download csv's from the dcm data, or social/search UI's, we pull the data based on p periods, seperated by brand: " CIG,OBS,BFG "
# Step 2: 