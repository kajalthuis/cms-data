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


def convert(list_, headerlist):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    nums = list(range(len(headerlist)))
    headerdict = dict(zip(nums, headerlist))    
    frame = frame.rename(columns=headerdict)

    frame = frame.sort_values(['date [YYYYMMDD]', 'time [HHMMSS]'])
    
        ## Add date and time columns ##
    frame['date [YYYYMMDD]'] = pd.to_datetime(frame['date [YYYYMMDD]'], format='%Y%m%d').dt.date
    frame['time [HHMMSS]'] = pd.to_datetime(frame['time [HHMMSS]'], format='%H%M%S').dt.time
        
        ## Output on screen ##    
    col1, col2 = st.columns(2)
    col1.metric('Number of drains [-]', len(frame))
    col2.metric('Linear meter [m]', round(frame['Max. depth [m]'].sum(),2))
    
    
    
    return frame


def show_preview(frame):
    st.write('**Preview:**')
    fig = px.scatter(data_frame = frame,
                     x=frame['X [m]'],
                     y=frame['Y [m]'],
                     color='Max. depth [m]', 
                     color_continuous_scale='turbo')
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)