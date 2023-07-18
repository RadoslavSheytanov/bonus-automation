import pandas as pd
import streamlit as st
import tempfile
import os
import datetime
import re
import base64

def process_file(source_file, bonus_type, bonus_code, name, platform):
    try:
        df = pd.read_excel(source_file)
        
        # Split the data into VIP and non-VIP rows
        vip_data = df[df.iloc[:, 1].str.contains('VIP\s*\(\d+\)', na=False, regex=True)]
        non_vip_data = df[~df.iloc[:, 1].str.contains('VIP\s*\(\d+\)', na=False, regex=True)]
        
        # Keep only the first two columns
        non_vip_data = non_vip_data.iloc[:, :2]
        
        # Process the non-VIP data according to the bonus type
        if bonus_type == 'Free Bets':
            non_vip_data.columns = ['SBUSERID', 'Bonus Value']
        elif bonus_type == 'Free Spins':
            non_vip_data.columns = [None, None]
        elif bonus_type in ['Casino Bonus', 'Sports Bonus', 'Prize Picker']:
            non_vip_data.columns = ['SBUSERID', 'Bonus Code']
        else:
            non_vip_data.columns = ['', '']

        # Save the non-VIP data to a temporary CSV file
        temp_dir = tempfile.mkdtemp()
        output_file_path = os.path.join(temp_dir, f"{name}_{platform}_{bonus_type.replace(' ', '')}_{bonus_code.replace('ddmmyy', datetime.datetime.now().strftime('%d%m%Y'))}.csv")
        non_vip_data.to_csv(output_file_path, index=False, header=bonus_type != 'Free Spins')

        return output_file_path, vip_data
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None, None

def get_csv_download_link(csv_file):
    # Generate a link to download the CSV file
    with open(csv_file, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="non_vip_data.csv">Download CSV File</a>'
    return href

st.title('Excel Automation')

uploaded_file = st.file_uploader("Choose a file", type=['xls', 'xlsx'])
bonus_type = st.selectbox("Bonus type", ["Free Bets", "Free Spins", "Casino Bonus", "Sports Bonus", "Prize Picker"])
bonus_code = st.text_input("Bonus code", "Bonuscode_ddmmyy")
name = st.text_input("Name")
platform = st.selectbox("Platform", ["PBULL", "SBULL"])

if st.button('Process File'):
    if uploaded_file is not None and bonus_type and bonus_code and name and platform:
        output_file_path, vip_data = process_file(uploaded_file, bonus_type, bonus_code, name, platform)

        # Display the non-VIP data
        if output_file_path is not None:
            st.write(f"Non-VIP data has been saved to {output_file_path}")
            st.markdown(get_csv_download_link(output_file_path), unsafe_allow_html=True)

        # Display the VIP data
        if vip_data is not None and not vip_data.empty:
            st.write("VIP Players (should be credited in a different campaign):")
            for _, row in vip_data.iterrows():
                st.write(f"{row['Sbuserid']} - {row['Sum of FS'].split('(')[1].split(')')[0]} FS")
    else:
        st.error("Please provide all inputs.")
