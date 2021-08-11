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


def convert(list_):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    frame = frame.rename(columns={0: 'Date',
                                  1: 'Time',
                                  2: 'Easting [m]',
                                  3: 'Northing [m]',
                                  4: 'Height [m]',
                                  5: 'Drain nr. [-]',
                                  6: 'Job nr. [-]',
                                  7: 'Base unit [-]',
                                  8: 'Operator [-]',
                                  9: 'Stitcher type [-]',
                                  10: 'Stitcher length [m]',
                                  11: 'Stitcher ballast [ton]',
                                  12: 'Drain type [-]',
                                  13: 'Anchoring [-]',
                                  14: 'Pattern type [0=square/1=triang.]',
                                  15: 'Pattern distance',
                                  16: 'Pattern heading [deg]',
                                  17: 'Pattern X-position [m]',
                                  18: 'Pattern Y-position [m]',
                                  19: 'Prescribed depth [m]',
                                  20: 'Max. depth [m]',
                                  21: 'Duration [s]',
                                  22: 'Max. force [kN]',
                                  23: 'Stitcher angle [deg]',
                                  24: 'Remarks',
                                  25: '',
                                  26: '',
                                  27: 'Log interval [m]',
                                  28: 'Data nr [-]',
                                  29: 'Force [kN]'})
    #####
    frame = frame.sort_values(['Date', 'Time'])
    
        ## Add date and time columns ##
    frame['Date'] = pd.to_datetime(frame['Date'], format='%Y%m%d').dt.date
    frame['Time'] = pd.to_datetime(frame['Time'], format='%H%M%S').dt.time
        
        ## Convert columns to float ##
    # frame.Num_blows = frame.Num_blows.astype(int)
    # frame.Location = frame.Location.astype(int)
    # frame.Easting = frame.Easting.astype(float)
    # frame.Northing = frame.Northing.astype(float)
    # frame.Total_settlement = frame.Total_settlement.astype(float)
    # frame.Total_time = frame.Total_time.astype(float)
    # frame.Total_energy = frame.Total_energy.astype(float)
    # frame.Foot_diameter = frame.Foot_diameter.astype(float)
    # frame.Stop_criterion = frame.Stop_criterion.astype(float)
    # frame.Set_1 = frame.Set_1.astype(float)
    
    st.write("  * Number of drains installed: ", len(frame))
    st.write("  * Linear meter installed: ", round(frame['Max. depth [m]'].sum(),2))
    
    return frame


def show_preview(frame):
    st.write('**Preview:**')
    fig = px.scatter(data_frame = frame,
                     x=frame['Easting [m]'],
                     y=frame['Northing [m]'],
                     color='Max. depth [m]', 
                     color_continuous_scale='turbo')
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)