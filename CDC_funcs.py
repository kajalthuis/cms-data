# -*- coding: utf-8 -*-
"""
Created on Tue May 11 17:52:23 2021

@author: KALT
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import io
import base64
import numpy as np


def convert(list_, radio1, radio2, new_name):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    frame = frame.rename(columns={0: 'Date',
                                  1: 'Time',
                                  2: 'Vessel_name',
                                  3: 'Level/Pattern',
                                  4: 'Location',
                                  5: 'Easting',
                                  6: 'Northing',
                                  7: 'Total_settlement',
                                  8: 'Total_time',
                                  9: 'Total_energy',
                                  10: 'Average_velocity',
                                  11: 'Manual_velocity',
                                  12: 'Foot_diameter',
                                  13: 'Stop_criterion',
                                  14: 'Num_blows',
                                  15: 'Set_1'})
    for i in range(16, 76):
        frame = frame.rename(columns={i:f'Set_{i-14}'})    
    #####
    
    frame = frame.sort_values(['Date', 'Time'])
    frame = frame.drop(frame.columns[[-1,]], axis=1)
    del frame['Average_velocity']
    del frame['Manual_velocity']
    frame = frame[frame.Date != 'yyyymmdd']
    
        ## Add date and time columns ##
    frame['Date'] = pd.to_datetime(frame['Date'], format='%Y%m%d').dt.date
    
    frame['Time'] = frame['Time'].astype(str)
    frame['Time'] = frame['Time'].str.split('.', expand=True)[0]
    frame['Time'] = frame['Time'].astype(int)
    for point in frame.index:
        if len(str(frame.loc[point, 'Time'])) < 6:
            frame.loc[point, 'Time'] = (6 - len(str(frame.loc[point, 'Time']))) * '0' + str(frame.loc[point, 'Time'])    
    frame['Time'] = pd.to_datetime(frame['Time'], format='%H%M%S').dt.time
    
        ## Split Level/Pattern column ##
    frame.insert(3, 'Level', 0)
    frame.insert(4, 'Pattern', 0)
    frame.Level, frame.Pattern = frame['Level/Pattern'].str.split('/').str
    
    try:
        frame.Pattern = frame.Pattern.astype(float)
    except:
        pass
    del frame['Level/Pattern']
    

    frame_drop = frame.dropna()
    Nan_rows=frame[~frame.index.isin(frame_drop.index)]
    frame = frame.dropna()
        
        ## Convert columns to float ##
    frame.Num_blows = frame.Num_blows.astype(int)
    frame.Location = frame.Location.astype(int)
    frame.Easting = frame.Easting.astype(float)
    frame.Northing = frame.Northing.astype(float)
    frame.Total_settlement = frame.Total_settlement.astype(float)
    frame.Total_time = frame.Total_time.astype(float)
    frame.Total_energy = frame.Total_energy.astype(float)
    frame.Foot_diameter = frame.Foot_diameter.astype(float)
    frame.Stop_criterion = frame.Stop_criterion.astype(float)
    frame.Set_1 = frame.Set_1.astype(float)
    
        ## Print info and warnings ##
    
    blows60 = frame.Num_blows[frame.Num_blows > 60].count()
    if blows60 > 1:
        st.write(f'WARNING: {blows60} points with more than 60 blows. This will result in a wrong induced settlement for those points')
    elif blows60 == 1:
        st.write(f'WARNING: {blows60} point with more than 60 blows. This will result in a wrong induced settlement for that point')
    
    # if empty > 1:
    #     st.write(empty, 'files are empty')
    # elif empty == 1:
    #     st.write(empty, 'file is empty')
    
    if len(Nan_rows) > 1:
        st.write('Removed', len(Nan_rows), 'lines with Nan values')
    elif len(Nan_rows) == 1:
        st.write('Removed', len(Nan_rows), 'line with Nan values')
    
        ## Remove line with less than 3 blows ## (can be adjusted)
    if radio1 == 'yes':
        noblows = frame.Num_blows[frame.Num_blows <= 2].count()
        if noblows > 1:
            st.write(f'Removed **{noblows}** points with less than 3 blows')
        elif noblows ==1:
            st.write(f'Removed **{noblows}** point with less than 3 blows')
        
        frame = frame[frame.Num_blows > 2]
        
        if frame.Total_settlement.mean() < 0:
            frame.Total_settlement = frame.Total_settlement * -1
            for i in range(1, 61):
                frame[f'Set_{i}'] = frame[f'Set_{i}'] * -1
    
        ## Calculate induced settlement per blow and put it in a new column ##
    for i in range(4,61):
        frame[f'ind_{i}'] = ((frame[f'Set_{i-2}'] - frame[f'Set_{i-3}']) + (frame[f'Set_{i-1}'] - frame[f'Set_{i-2}']) + (frame[f'Set_{i}'] - frame[f'Set_{i-1}']))/3
    
        ## Remove minus values resulting from calculation of induced settlement ##
    keys = list(frame)
    start = keys.index('ind_4')
    end = keys.index('ind_60')+1
    for i in range(start,end):
        for j in range(0,len(frame.ind_4)):
            if frame.iloc[j,i] < 0:
                frame.iloc[j,i] = 0
    
        ## change to 60 blows if more than 60 blows ## (can be adjusted, but not taken into account for induced. Only 60 blows are imported)       
    Num_blows_index = keys.index('Num_blows')            
    for i in range(0, len(frame.Num_blows)):
        if frame.iloc[i, Num_blows_index] > 60:
            frame.iloc[i, Num_blows_index] = 60             
           
        ## Add a column with induced settlement ##
    frame['Total_induced'] = 0
    keys = list(frame)
    Total_induced_index = keys.index('Total_induced')
    
    for i in range(len(frame['Total_induced'])):
        Blows = frame.iloc[i, Num_blows_index]
        if Blows > 4:        
            ind_index = keys.index(f'ind_{Blows}')
            frame.iloc[i, Total_induced_index] = frame.iloc[i, ind_index-1]
    
        ## Add column with cumulative count of points ##
    #frame = frame.sort_values(by=['Date', 'Time'])
    #frame.loc[:, 'Point nr.'] = np.arange(1,len(frame)+1)
    #frame = frame.set_index('Point nr.')
    
    Cranes = list(set(frame.Vessel_name))
    for i in  Cranes:
        crane = list(frame.Vessel_name)
        points_per_crane = crane.count(i)
        st.write('  * Points compacted by', i,':', points_per_crane)
    
    st.write("  * Total points compacted: ", len(frame))
    
    try:
        st.write('  * Total square meter covered:', sum(frame.Pattern * frame.Pattern))
    except:
        st.write('  * Square meter not possible, no grid entered in cms')
      
    #Preview    
    
    return frame


def download_link_csv(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=True)
    
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def download_link_excel(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        towrite = io.BytesIO()
        object_to_download = object_to_download.to_excel(towrite, index=True)
        towrite.seek(0)
    
    b64 = base64.b64encode(towrite.read()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def show_preview(frame):
    st.write('**Preview:**')
    fig = px.scatter(data_frame = frame,
                     x=frame['Easting'],
                     y=frame['Northing'],
                     color='Num_blows', 
                     color_continuous_scale='turbo')
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)
