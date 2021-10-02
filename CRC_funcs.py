# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 14:41:59 2020

@author: KALT
"""

import pandas as pd
import math
import plotly.express as px
import streamlit as st

    
def convert(pos_, acc_, log_, log_present, acc_present, select_headers):
    ## log ## 
    
    if log_present:
        log = pd.concat(log_)
        
        temp = [0]*len(log)
        for i in range(1, len(log)-1):
            dt = log['time [HHMMSS.SSS]'].iloc[i+1] - log['time [HHMMSS.SSS]'].iloc[i-1]
            dx = log['Crane Easting [m]'].iloc[i+1] - log['Crane Easting [m]'].iloc[i-1]
            dy = log['Crane Northing [m]'].iloc[i+1] - log['Crane Northing [m]'].iloc[i-1]
            speed = 3.6 * (math.sqrt(dx ** 2 + dy ** 2))/dt
            temp[i] = speed
            
        log['Speed [km/h]'] = temp
        log = log.sort_values(by=['#date [YYYYMMDD]', 'time [HHMMSS.SSS]'])
        
    else:
        log = pd.DataFrame()
        
    ## pos ##
    pos = pd.concat(pos_)
    pos_result = pos.groupby(['Impact # [-]']).mean()
    pos_result = pos_result.rename(columns={' X [m]' : 'X_average [m]',
                                            ' Y [m]' : 'Y_average [m]'})
    pos_result = pos_result.drop(' Pass # [-]', axis=1)
    pos_first = pos.groupby(['Impact # [-]']).first()
    pos_last = pos.groupby(['Impact # [-]']).last()
    
    list_direction = [0]*len(pos_result)
    list_X_left = [0]*len(pos_result)
    list_Y_left = [0]*len(pos_result)
    list_X_right = [0]*len(pos_result)
    list_Y_right = [0]*len(pos_result)
    Pass_left = [0]*len(pos_result)
    Pass_right = [0]*len(pos_result)
    Impact_left = [0]*len(pos_result)
    Impact_right = [0]*len(pos_result)
    Speed = [0]*len(pos_result)
    
    wheel_dist = 1.03
    
    for i in range(1, len(pos_result)-1):
        X_plus = pos_result['X_average [m]'].iloc[i+1]
        X_min = pos_result['X_average [m]'].iloc[i-1]
        Y_plus = pos_result['Y_average [m]'].iloc[i+1]
        Y_min = pos_result['Y_average [m]'].iloc[i-1]
        dx = abs(X_plus - X_min)
        dy = abs(Y_plus - Y_min)
        if dx == 0:
            alpha = 0.5 * math.pi
        else:
            alpha = math.atan(dy/dx)
        beta = (0.5 * math.pi) - alpha
        if X_plus >= X_min and Y_plus >= Y_min:
            dx_left = -wheel_dist * math.cos(beta)
            dy_left = wheel_dist * math.sin(beta)
            direction = beta
        elif X_plus < X_min and Y_plus > Y_min:
            dx_left = -wheel_dist * math.cos(beta)
            dy_left = -wheel_dist * math.sin(beta)
            direction = (2 * math.pi) - beta
        elif X_plus > X_min and Y_plus < Y_min:
            dx_left = wheel_dist * math.cos(beta)
            dy_left = wheel_dist * math.sin(beta)
            direction = (1 * math.pi) - beta
        elif X_plus < X_min and Y_plus < Y_min:
            dx_left = wheel_dist * math.cos(beta)
            dy_left = -wheel_dist * math.sin(beta)
            direction = beta + math.pi
        
        list_X_left[i] = pos_result['X_average [m]'].iloc[i] + dx_left
        list_Y_left[i] = pos_result['Y_average [m]'].iloc[i] + dy_left
        list_X_right[i] = pos_result['X_average [m]'].iloc[i] - dx_left
        list_Y_right[i] = pos_result['Y_average [m]'].iloc[i] - dy_left
        Pass_left[i] = pos_first[' Pass # [-]'].iloc[i]
        Pass_right[i] = pos_last[' Pass # [-]'].iloc[i]
        list_direction[i] = math.degrees(direction)
        
        impact_left = str(pos_result.index[i]) + 'L'
        impact_right = str(pos_result.index[i]) + 'R'
            
        Impact_left[i] = impact_left
        Impact_right[i] = impact_right        
        
        if log_present:
            logtemp = log[['time [HHMMSS.SSS]', 'Speed [km/h]']].copy()
            logtemp['time [HHMMSS.SSS]'] = abs(logtemp['time [HHMMSS.SSS]']-pos_result['time [HHMMSS]'].iloc[i])
            logtemp = logtemp.sort_values(by='time [HHMMSS.SSS]')
            Speed[i] = logtemp['Speed [km/h]'].iloc[0]
                        
    for i in [0, -1]:
        Impact_left[i] = str(pos_result.index[i]) + 'L'
        Impact_right[i] = str(pos_result.index[i]) + 'R'
        list_X_left[i] = pos_result['X_average [m]'].iloc[i]
        list_Y_left[i] = pos_result['Y_average [m]'].iloc[i]
        list_X_right[i] = pos_result['X_average [m]'].iloc[i]
        list_Y_right[i] = pos_result['Y_average [m]'].iloc[i]
        Pass_left[i] = pos_first[' Pass # [-]'].iloc[i]
        Pass_right[i] = pos_last[' Pass # [-]'].iloc[i]
        
    pos_result['#date [YYYYMMDD]'] = pd.to_datetime(pos_result['#date [YYYYMMDD]'], 
                                                    format='%Y%m%d').dt.date
    pos_result['time [HHMMSS]'] = pd.to_datetime(pos_result['time [HHMMSS]'], 
                                                    format='%H%M%S').dt.time
    
    dict_left = {'Impact #' : Impact_left,
            'Date' : list(pos_result['#date [YYYYMMDD]']),
            'Time' : list(pos_result['time [HHMMSS]']),
            'Acceleration' : list(pos_result[' Acceleration [m/s2]']),
            'Direction [deg]' : list_direction,
            'X' : list_X_left,
            'Y' : list_Y_left,
            'Pass' : Pass_left,
            'Speed [km/h]' : Speed}
    
    dict_right = {'Impact #' : Impact_right,
                  'Date' : list(pos_result['#date [YYYYMMDD]']),
            'Time' : list(pos_result['time [HHMMSS]']),
            'Acceleration' : list(pos_result[' Acceleration [m/s2]']),
            'Direction [deg]' : list_direction,
            'X' : list_X_right,
            'Y' : list_Y_right,
            'Pass' : Pass_right,
            'Speed [km/h]' : Speed}
    
    df_left = pd.DataFrame(dict_left)
    df_right = pd.DataFrame(dict_right)
    output = df_left.append(df_right)
    output = output.sort_values(by=['Date', 'Time', 'Impact #'])
    output = output.set_index('Impact #')
    
    for header in list(output):
        if header not in select_headers:
            output = output.drop(header, axis=1)
    
    pos = pos.sort_values(by=['#date [YYYYMMDD]', 'time [HHMMSS]'])
    
    ## acc ##
    if acc_present:
        acc = pd.concat(acc_)
        acc = acc.rename(columns={0 : '#date [YYYYMMDD]',
                            1 : 'time [HHMMSS]',
                            2 : 'Impact # [-]',
                            3 : 'Heave acceleration [m/s2]'})
        acc = acc.sort_values(by=['#date [YYYYMMDD]', 'time [HHMMSS]'])
    else:
        acc = pd.DataFrame()
    
    col1, col2 = st.columns(2)
    col1.metric('Number of impacts [-]', len(output))
    #col2.metric('Linear meter [m]', round(frame['Max. depth [m]'].sum(),2))    
    
    ## file name ##
    #date = output['Date'].iloc[0]
    #name_proc = 'CRC data_processed_' + str(date)
    #name_raw = 'CRC data_raw_' + str(date)
    
    return output, pos, acc, log


def show_preview(output):
    st.write('**Preview:**')
    for col in ['X', 'Y', 'Pass']:
        if col not in list(output):
            st.warning('Please add the X, Y and Pass columns')
            return
    fig = px.scatter(data_frame = output,
                     x=output['X'],
                     y=output['Y'],
                     color='Pass', 
                     color_continuous_scale='turbo')
                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)
