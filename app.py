# -*- coding: utf-8 -*-
"""
Created on Tue May 11 17:47:49 2021

@author: KALT
"""
import pandas as pd
import streamlit as st
from PIL import Image
import CDC_funcs
import CRC_funcs
import PVD_funcs

#st.markdown('<style>body{background-color: #D1D1D1;}</style>',unsafe_allow_html=True)

header1, header2 = st.beta_columns([1,5])
image1 = Image.open('BOS_Cofra_Logo_RGB.png')
header1.image(image1, width=100)

def main():
    
    technique = st.sidebar.radio("""Choose technique""", ['CDC', 'CRC', 'PVD'])
    
    #####CDC#####
    if technique == 'CDC':
        header2.title("""CDC data import""")
        col1, col2 = st.beta_columns(2)
        radio1 = col1.radio('Remove points with less than 3 blows?', ['yes','no'])
        radio2 = col2.radio('Save as?', ['Excel file','CSV file'])        
        
        uploads = st.sidebar.file_uploader('Upload log files', 
                                           accept_multiple_files=True, 
                                           type='log')
        
        if len(uploads) == 1:
            st.write(f' **{len(uploads)}** file imported')
        else:
            st.write(f' **{len(uploads)}** files imported')
        
        if len(uploads) > 0:
            list_ = []
            for file_ in uploads:
                ##### only for new file type
                headers = [0,1]
                df = pd.read_csv(file_, skiprows=headers, index_col=False, usecols=(range(76)), header=None)
                #####
                list_.append(df)
                
            new_name = uploads[0].name
            new_name=new_name.split('_')
            new_name=new_name[0]
            
            col1, col2 = st.beta_columns([2,4])
            start_button = col1.button('Process .log files', key='1')
            
            if start_button:
                with st.spinner(text='In progress...'):
                    frame = CDC_funcs.convert(list_, radio1, radio2, new_name)    
                
                if radio2 == 'CSV file':
                    tmp_download_link = CDC_funcs.download_link_csv(frame, 
                                                                    f'{new_name}.csv', 
                                                                    'Click here to download CSV file!')
                elif radio2 == 'Excel file':
                    tmp_download_link = CDC_funcs.download_link_excel(frame, 
                                                                      f'{new_name}.xlsx', 
                                                                      'Click here to download excel file!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)                    
                
                st.success('Done!')
                CDC_funcs.show_preview(frame)
    
    #####CRC#####
    elif technique == 'CRC':
        header2.title("""CRC data import""")
        col1, col2 = st.beta_columns(2)
        radio1 = col1.radio('Save as?', ['Excel file','CSV file'])
        
        uploads_ext = st.sidebar.file_uploader('Upload pos files', 
                                               accept_multiple_files=True, 
                                               type='ext')
        uploads_log = st.sidebar.file_uploader('Upload log files', 
                                               accept_multiple_files=True, 
                                               type='log')
        uploads_pos = []
        uploads_acc = []

        if len(uploads_ext) > 0:
            for ext_file in uploads_ext:
                if 'pos' in ext_file.name:
                    uploads_pos.append(ext_file)
                elif 'acc' in ext_file.name:
                    uploads_acc.append(ext_file)
                    
        if len(uploads_pos) == 1:
            st.write(f' **{len(uploads_pos)}** pos file imported')
        else:
            st.write(f' **{len(uploads_pos)}** pos files imported')
        if len(uploads_acc) == 1:
            st.write(f' **{len(uploads_acc)}** acc file imported')
        else:
            st.write(f' **{len(uploads_acc)}** acc files imported')                
        if len(uploads_log) == 1:
            st.write(f' **{len(uploads_log)}** log file imported')
        else:
            st.write(f' **{len(uploads_log)}** log files imported')        
        
        if len(uploads_ext) > 0:
            
            if len(uploads_pos) < len(uploads_acc):
                num_missing = len(uploads_acc) - len(uploads_pos)
                st.warning(f'**WARNING: You are missing {num_missing} pos files, number of pos and acc files should be equal**')
            elif len(uploads_acc) < len(uploads_pos):
                num_missing = len(uploads_pos) - len(uploads_acc)
                st.warning(f'**WARNING: You are missing {num_missing} acc files, number of pos and acc files should be equal**')
            
            select_headers = st.multiselect('Add/remove columns', 
                                             ['Date', 'Time','Acceleration','Direction [deg]', 'X','Y', 'Pass', 'Speed [km/h]'], 
                                             ['Date', 'Time','Acceleration','Direction [deg]', 'X','Y', 'Pass', 'Speed [km/h]'])    
            
            log_ = []
            pos_ = []
            acc_ = []
            
            if len(uploads_log) > 0:
                log_present = True
            else:
                log_present = False
                st.warning('**WARNING: no log files uploaded, driving speed cannot be calculated**')
            
            if len(uploads_acc) > 0:
                acc_present = True
            else:
                acc_present = False

            if log_present:
                for log_file in uploads_log:
                    df = pd.read_csv(log_file, skiprows=[0], index_col=False)
                    log_.append(df)
            for pos_file in uploads_pos:
                df = pd.read_csv(pos_file, skiprows=[0], index_col=False)
                pos_.append(df)
            if acc_present:
                for acc_file in uploads_acc:
                    df = pd.read_csv(acc_file, skiprows=[0,1], index_col=False, header=None)
                    acc_.append(df)
            
            start_button = st.button('Process files', key='1')
            if start_button:
                with st.spinner(text='In progress...'):
                    output = CRC_funcs.convert(pos_, acc_, log_, log_present, acc_present, select_headers)[0]
                    pos = CRC_funcs.convert(pos_, acc_, log_, log_present, acc_present, select_headers)[1]
                    acc = CRC_funcs.convert(pos_, acc_, log_, log_present, acc_present, select_headers)[2]
                    log = CRC_funcs.convert(pos_, acc_, log_, log_present, acc_present, select_headers)[3]
                    
                    if radio1 == 'CSV file':
                        download_link_proc = CDC_funcs.download_link_csv(output, 
                                                                          'CRC_data_processed.csv', 
                                                                          'Click here to download processed data')
                        download_link_pos = CDC_funcs.download_link_csv(pos, 
                                                                          'CRC_data_pos.csv', 
                                                                          'Click here to download raw pos data')
                        download_link_acc = CDC_funcs.download_link_csv(acc, 
                                                                          'CRC_data_acc.csv', 
                                                                          'Click here to download raw acc data')
                        download_link_log = CDC_funcs.download_link_csv(log, 
                                                                          'CRC_data_log.csv', 
                                                                          'Click here to download raw log data')                        
                    elif radio1 == 'Excel file':
                        download_link_proc = CDC_funcs.download_link_excel(output, 
                                                                          'CRC_data_processed.xlsx', 
                                                                          'Click here to download processed data!')
                        download_link_pos = CDC_funcs.download_link_excel(pos, 
                                                                          'CRC_data_pos.xlsx', 
                                                                          'Click here to download raw pos data')
                        download_link_acc = CDC_funcs.download_link_excel(acc, 
                                                                          'CRC_data_acc.xlsx', 
                                                                          'Click here to download raw acc data')

                        download_link_log = CDC_funcs.download_link_excel(log, 
                                                                          'CRC_data_log.xlsx', 
                                                                          'Click here to download raw log data')                        
                        
                    st.write('**Processed data:**')
                    st.markdown(download_link_proc, unsafe_allow_html=True)                    
                    st.write('**Raw data:**')     
                    st.markdown(download_link_pos, unsafe_allow_html=True)
                    st.markdown(download_link_acc, unsafe_allow_html=True)
                    if log_present:
                        st.markdown(download_link_log, unsafe_allow_html=True)
                     
                st.success('Done!')
                CRC_funcs.show_preview(output)
    
    #####PVD#####
    elif technique == 'PVD':
        header2.title("""PVD data import""")
        col1, col2 = st.beta_columns(2)
        radio1 = col1.radio('Save as?', ['Excel file','CSV file'])
        
        uploads = st.sidebar.file_uploader('Upload log files', 
                                           accept_multiple_files=True, 
                                           type='ext')        
        if len(uploads) == 1:
            st.write(f' **{len(uploads)}** file imported')
        else:
            st.write(f' **{len(uploads)}** files imported')
            
        if len(uploads) > 0:
            select1 = st.sidebar.multiselect('test', ['ja', 'nee','weetnie','depth', 'taota','pullbahc', 'force', 'vertical'], ['ja', 'nee','weetnie','depth', 'taota','pullbahc', 'force', 'vertical'])
            list_ = []
             
            for file_ in uploads:
                for headerline in file_:
                    headerline = str(headerline)
                    if '#date' in headerline:
                        break
                headerline = headerline[:-3]
                headerlist = headerline.replace("b'#", "").split(',')  
                
                
                if ' [ok' in headerlist:
                    headerlist.remove(' [ok')
                    headerlist.remove('new roll')
                    for index, item in enumerate(headerlist):
                        if 'canceled]' in item:
                            item = ' '
                            headerlist[index] = item
                
                headers = [0, 1]
                df = pd.read_csv(file_, index_col=False, header=None)
                #####
                list_.append(df)
            
            #header_list = pd.read_csv(uploads[0], skiprows=[0], nrows=3, index_col=False, header=2, names=list(range(250)))
            
            #st.write(header_list)   
            
            col1, col2 = st.beta_columns([2,4])
            start_button = col1.button('Process .ext files', key='1')

            if start_button:
                with st.spinner(text='In progress...'):
                    frame = PVD_funcs.convert(list_, headerlist)    

                if radio1 == 'CSV file':
                    tmp_download_link = CDC_funcs.download_link_csv(frame, 
                                                                    'PVD_data_processed.csv', 
                                                                    'Click here to download CSV file!')
                elif radio1 == 'Excel file':
                    tmp_download_link = CDC_funcs.download_link_excel(frame, 
                                                                      'PVD_data_processed.xlsx', 
                                                                      'Click here to download excel file!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)                  
                
                ## Download button ##
                @st.cache
                def convert_df(df):
                    # Cache the conversion to prevent computation on every rerun
                    
                    return df.to_csv().encode('utf-8')
                
                csv = convert_df(frame)
                st.download_button(
                    label="Press to Download",
                    data=csv,
                    file_name='PVD_data_processed.csv',
                    mime='text/csv',
                    )
                
                
                
                st.success('Done!')
                PVD_funcs.show_preview(frame)                    
            
if __name__ == "__main__":
    main()
    
## Export to a .csv file per pass ##
#Passes = list(set(frame.Level))
#for i in Passes:
#    pass_frame = frame[frame.Level == i]
#    pass_name = allFiles[0]
#    pass_name = pass_name.split('_')
#    pass_name = pass_name[0] + '_' + i
#    pass_frame.to_excel(f'{pass_name}.xlsx')
