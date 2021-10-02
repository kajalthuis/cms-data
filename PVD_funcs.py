# -*- coding: utf-8 -*-
"""
Created on Tue May 11 17:52:23 2021

@author: KALT
"""

import pandas as pd
import streamlit as st
import plotly.express as px


def convert(list_, headerlist, wp_calc_method, fixed_nr):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    nums = list(range(len(headerlist)))
    headerdict = dict(zip(nums, headerlist))    
    frame = frame.rename(columns=headerdict)

    frame = frame.sort_values(['date [YYYYMMDD]', 'time [HHMMSS]'])
    
        ## Add date and time columns ##
    frame['date [YYYYMMDD]'] = pd.to_datetime(frame['date [YYYYMMDD]'], format='%Y%m%d').dt.date
    frame['time [HHMMSS]'] = pd.to_datetime(frame['time [HHMMSS]'], format='%H%M%S').dt.time
       
        ## Cable tension + wp thickness ##
    wp_thickness = [100]*len(frame)
    
    for pvd in range(len(frame)):
        
        keys = list(frame)
        force1 = keys.index('Force [kN]')
        force_df = frame.iloc[:, force1:]
        force_pvd =  force_df.loc[pvd,:].values.tolist()
        
        force_pvd = [i for i in force_pvd if i != 0]    #remove zeros
        force_pvd = force_pvd[2:-3]                     #remove first 2 and last 2 values
        
        if len(force_pvd) > 0:
            cable_tension = min(force_pvd)
            if wp_calc_method == 'Lowest force plus fixed number':
                cutoff = cable_tension + fixed_nr
            elif wp_calc_method == 'Manual choice':
                cutoff = fixed_nr
                
            cable_tension_index = force_pvd.index(cable_tension)
            force_pvd = force_pvd[:cable_tension_index]
                    
            wp = (sum(i > cutoff for i in force_pvd) + 2) * frame['Log interval [m]'][pvd]
            wp_thickness[pvd] = wp
    
    wp_frame = frame[['X [m]', 'Y [m]']]
    wp_frame['wp [m]'] = wp_thickness
        
        ## Output on screen ##    
    col1, col2 = st.columns(2)
    col1.metric('Number of drains [-]', len(frame))
    col2.metric('Linear meter [m]', round(frame['Max. depth [m]'].sum(),2))
        
    return frame, wp_frame


def show_preview(frame):
    st.write('**Preview (Installation depth):**')
    fig = px.scatter(data_frame = frame,
                     x=frame['X [m]'],
                     y=frame['Y [m]'],
                     color='Max. depth [m]', 
                     color_continuous_scale='turbo')
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)
    
    
def show_wp(wp_frame):
    st.write('**Working platform thickness:**')
    fig = px.scatter(data_frame = wp_frame,
                     x=wp_frame['X [m]'],
                     y=wp_frame['Y [m]'],
                     color='wp [m]', 
                     color_continuous_scale='turbo',
                     range_color=[0,5])
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)   
    
    
