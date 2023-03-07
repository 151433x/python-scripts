import pandas as pd
import glob
import os 
#THIS WILL ONLY WORK WITH CSV FILES, IT WILL NOT WORK WITH XLS FILES FOR THE RAW DATA, IT MUST TAKE IN CSV FILES FOR THE INITIAL DATA.

def data_prep(name): 
    """finds raw data that matches name and then cocats them into the same dataframe"""
    all_files=[]   
    raw_files=glob.glob(f'{name}*.csv') #THIS WILL ONLY WORK WITH CSV FILES, IT WILL NOT WORK WITH XLS FILES FOR THE RAW DATA
    #glob finds all csv files where it finds name(the brand we give it) and saves it in raw files
    for file in raw_files:
        print(f"found this file matching your request: {file}") #this tells the user which files it found
        df=pd.read_csv(file,index_col=0,header=0)
        all_files.append(df)
    concat_data=pd.concat(all_files,ignore_index=True,axis=0)
    return concat_data

def poster(df,file,sheet_name,index=False):
    """
    so this posts the output of different functions as sheets to excel, it takes in the dataframe, the name of the file, and the sheet name,and if index exists. 
    """
    with pd.ExcelWriter(f'{file} Completed Mapping.xlsx',mode='a')as writer:
        df.to_excel(writer,sheet_name=f'{sheet_name}',index=index)
    print(f'{sheet_name} posted to sheet named "{sheet_name}" ')

def clean(raw):
    """
    puts concated raw data in excel as 'raw data', from there cleans data and returns it 
    """
    all_data=raw[~raw["Placement status"].str.contains('Archived',na=False)] #gets rid of all archived in placement status, from the raw data.
    df=pd.DataFrame(all_data)
    df=df[["Placement ID","Placement Name"]] #only keeps placement Id's and placement names in clean data
    df=df.dropna() #drops all rows values with na in the placement ID or Placement name
    df=df[~df["Placement Name"].str.contains('Package')] #gets rid of all rows with 'package' in placement name
    df["Placement Name"]=df["Placement Name"].str.title() # upercase first letter lowercase after
    df['Placement Name']=df['Placement Name'].str.replace('Aud',"Audio",regex=True) # gets rid of AUD and turns them into Audio
    df['Placement Name']=df['Placement Name'].str.replace('Audioio',"Audio",regex=True) # gets rid of mistakes made by line 32
    df=df.drop_duplicates() #drops all duplicates in the data set
    return df

def text_to_column(df):
    """
    creates a text to column with pre assigned names and saves as excel sheet, receives clean data as a input, requires placement name to create the text-to-collumn
    """
    placement_holderv2=df['Placement Name'].str.split('_', expand=True) # this is the text to collumn function
    for i in placement_holderv2.iloc:#this is a small cleaning process since we can index this new text-to-collumn collumns
        if i[11] == 'Audio' and i[6] =='Matterkind': # matterkind does not run any audio for us, there is a probem in the original string where the real partner is located in partner detail which is one delimter after this so this fixes that 
                i[6]=i[7]
        elif i[11]=='Display' and i[6]=='Spotify': # spotify does not run any display campaigns for us but there are problems with the string so this fixes that 
                i[11]=i[10]
    ultimate_dataframe=pd.concat(objs=[df,placement_holderv2],axis=1)
    return ultimate_dataframe

def pivot_table_1(pivot_input):
    """
    This function will take in clean data from either text to collumn or clean concat and create a pivot table with that data and append a pivot table in the OBS Completed Mapping excel sheet with the name as 'pivot' 
    """
    pivot_input=pd.DataFrame(pivot_input) # this makes the data into a dataframe format so that we can edit it
    pivot_table_data=pd.pivot_table(data=pivot_input,columns=pivot_input.iloc[:,[4,13,8,11,10]],values=[0],aggfunc=pd.Series.count).T #this creates the pivot table with as well as gives the count of the brand which is also the count of the overall placment created which allows us to QA the data later.
    return pivot_table_data  

def placement_generator(df,brand,quarter,year):
    """
    creates Placement from data frame as well ads in placement name and placement ID into one list and posts it to excel
    """
    dashboard_name=f'{brand} {quarter} {year}' # This creates the dashboard name for the report based off the name quarter and year.
    window=str(year)[2:4]+quarter #this creates a window which we use to create the report names
    placement_holder={'Foursquare Dashboard Name':[],'Foursquare Report Name':[],'Placement ID':[],'Placements to Include':[]} #this creates the different lists that will be placed into the excel writer later
    for i in df.iloc:
        Objective=i[2]
        channel=i[11]
        partner=i[6]
        targeting_type=i[9]
        targeting_detail=i[8]
        local_holder=   [f'{brand}|{window}|{Objective}|{channel}|{partner}|{targeting_type}|All', 
                        f'{brand}|{window}|{Objective}|{channel}|{partner}|All|All',
                        f'{brand}|{window}|{Objective}|{channel}|All|All|All']
                        
                        #so the list 'local holder' is the mandatory placments that are created for every single placement name, this creates them and then we add local holder in lines below 
        if i[2]=='Visits' and i[11]=='Display': # we want to analyze store visits on targeting detail level so this allows us to only generate the placement names for display visits
            local_holder.append(f'{brand}|{window}|{Objective}|{channel}|{partner}|{targeting_type}|{targeting_detail}')
        placement_holder['Foursquare Report Name']+=local_holder # this add each placement into the list
        placement_name=i['Placement Name'] # this saves the current placement name, so that we save it later in line 81
        Placement_ID=i['Placement ID']# this saves the current placement id, so that we save it later in line 82
        for i in local_holder:            
            placement_holder['Placements to Include'].append(placement_name)
            placement_holder['Placement ID'].append(Placement_ID)
            placement_holder['Foursquare Dashboard Name'].append(dashboard_name)
    final=pd.DataFrame(data=placement_holder)
    return final

def final(name,quarter,year):
    """ 
        The function final takes in name(the brand or that you would like to search for), quarter(the quarter of the data we are compiling) and year (the year of the data).
        it runs all functions in the order that is required to get the final product, it allows for the user to have as little input as possible.
    """
    file_name = data_prep(name)
    
    with pd.ExcelWriter(F'{name} Completed Mapping.xlsx',mode='w')as writer: #creates the excel sheet and writes in raw data as the first sheet named raw
        file_name.to_excel(writer,sheet_name='raw',index=False)
        print('raw data is posted to sheet named "raw" ')

    input=clean(file_name)
    poster(input,name,'cleaned data')

    df=text_to_column(input)
    poster(df,name,'text-to-collumn')

    pivot=pivot_table_1(df)
    poster(pivot,name,'pivot-table',True)

    placement=placement_generator(df,name,quarter,year)
    poster(placement,name,'final')

    print('program complete!')
       
if __name__ == "__main__":
    os.chdir("C:\Desktop\python_scripts/raw_data/archive") # YOU MUST CHANGE THE ROOT DIRECTORY FOR THE CODE TO WORK, GLOB.GLOB(line 7) USES THE ROOT DIRECTORY FOR THE LOCATION TO SEARCH, THIS LINE CHANGES IT.
    final('OBS','Q1','2023') # when the program prints 'program complete!', the excel sheet will be posted in hte directory above, it will be posted as an excel sheet,
    final('CIG','Q1','2023')
    final('BFG','Q1','2023')


#need to build a mmm pull automater as well, i can import the data from dcm but this excel processes should be automated, concats, globs, and some filtering, with finding the starting day of the week,

# bfg sometimes uses materkind or matterkind
