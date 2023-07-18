import pandas as pd
import streamlit as st
import tempfile
import os
import datetime
import re
import base64
import traceback
import streamlit.components.v1 as components

def process_file(source_file, bonus_type, bonus_code, name, platform, selected_date):
    try:
        df = pd.read_excel(source_file)
        
        # Convert columns to string type
        df.iloc[:, 1] = df.iloc[:, 1].astype(str)
        
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
        if selected_date:
            selected_date_str = selected_date.strftime('%Y-%m-%d')  # changed date format
            file_name = f"{bonus_code}_{selected_date_str}_{name}_{platform}.csv"
        else:
            today_date = datetime.datetime.now().strftime('%Y-%m-%d')  # changed date format
            file_name = f"{bonus_code}_{today_date}_{name}_{platform}.csv"
        output_file_path = os.path.join(temp_dir, file_name)
        non_vip_data.to_csv(output_file_path, index=False, header=bonus_type != 'Free Spins')

        return output_file_path, vip_data
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        st.error(traceback.format_exc())
        return None, None

def get_csv_download_link(csv_file):
    # Generate a link to download the CSV file
    with open(csv_file, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{csv_file.split("/")[-1]}" style="display: inline-block; padding: 0.5em 1em; color: #ffffff; background-color: #007bff; border-radius: 0.25em; text-decoration: none;">Download CSV File</a>'
    return href

st.title('Bonus Templating System')

uploaded_file = st.file_uploader("Choose a file", type=['xls', 'xlsx'])
bonus_type = st.selectbox("Bonus Type:", ["------", "Free Bets", "Free Spins", "Casino Bonus", "Sports Bonus", "Prize Picker"])
bonus_code = st.text_input("Bonus Code:", "")

selected_date = st.date_input("Select Date:")

name = st.text_input("Agent's Name:")
platform = st.selectbox("Platform:", ["------", "PBULL", "SBULL"])

if st.button('Process File'):
    if uploaded_file is not None and bonus_type != "------" and bonus_code and name and platform:
        output_file_path, vip_data = process_file(uploaded_file, bonus_type, bonus_code, name, platform, selected_date)

        # Display the non-VIP data
        if output_file_path is not None:
            st.markdown(get_csv_download_link(output_file_path), unsafe_allow_html=True)

        # Display the VIP data
        if vip_data is not None and not vip_data.empty:
            st.markdown("**ATTENTION: This file consists of VIP Player/s and they should be credited in a different campaign:**", unsafe_allow_html=True)
            st.dataframe(vip_data)
        else:
            st.success("This file doesn't contain any special VIP Players Bonuses. Click -Download CSV file- button above and credit the bonus as normal.")
    else:
        st.error("Please provide all inputs.")



# Add hyperlinks to LinkedIn and GitHub
linkedin_url = "https://ie.linkedin.com/in/radoslav-sheytanov-771a43260"
github_url = "https://github.com/radoslavSheytanov/"
st.markdown(f"Development and Support - [LinkedIn]({linkedin_url}) and [GitHub]({github_url})")

# Add email link
email = "radoslav@programmer.net"
st.markdown(f"Questions? Feel free to [message the developer directly](mailto:{email})")


