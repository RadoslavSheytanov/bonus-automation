import streamlit as st
import pandas as pd
import csv
import tempfile
from datetime import date
import os

def process_file(source_file, bonus_type, bonus_code, name, platform):
    try:
        # Load the source file using pandas
        df = pd.read_excel(source_file)

        # Determine the header based on the bonus type
        if bonus_type == 'Free Bets' or bonus_type == 'Casino Bonus' or bonus_type == 'Sports Bonus' or bonus_type == 'Prize Picker':
            header = ['SBUSERID', 'Bonus Value']
        elif bonus_type == 'Free Spins':
            df = df.iloc[:, :2]  # Keep only the first two columns
            header = None  # No header for Free Spins
        else:
            header = [''] * df.shape[1]
            df.columns = header

        # Prepare the CSV file name
        today = date.today()
        output_file_name = f"{bonus_code.replace('ddmmy', today.strftime('%d%m%y'))}_{name}_{platform}.csv"

        # Create a temporary directory for the output files
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file_path = os.path.join(temp_dir, output_file_name)

            # Save the DataFrame to a CSV file
            df.to_csv(output_file_path, index=False, header=header)

            # Print completion message
            st.success("File processing completed successfully")

            return output_file_path

    except Exception as e:
        # Print error message
        st.error(f"Error processing file. Error message: {str(e)}")

        return None

# Streamlit UI
st.title('Bonus Templating System')

# Input widgets
source_file = st.file_uploader("Choose a source file", type=['xlsx', 'xls'])
bonus_type = st.selectbox('Bonus Type', ['Free Bets', 'Free Spins', 'Casino Bonus', 'Sports Bonus', 'Prize Picker'])
bonus_code = st.text_input('Bonus Code')
name = st.text_input('Name')
platform = st.selectbox('Platform', ['PBULL', 'SBULL'])

if st.button('Process File'):
    if source_file is None:
        st.error("Please select a source file.")
    elif bonus_type and bonus_code and name and platform:
        output_file_path = process_file(source_file, bonus_type, bonus_code, name, platform)
        if output_file_path:
            with open(output_file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button(
                label="Download Output File",
                data=file_bytes,
                file_name=output_file_path.split('/')[-1]
            )
    else:
        st.error("All fields are required.")

# Add hyperlinks to LinkedIn and GitHub
linkedin_url = "https://ie.linkedin.com/in/radoslav-sheytanov-771a43260"
github_url = "https://github.com/radoslavSheytanov/"
st.markdown(f"Development and Support - [LinkedIn]({linkedin_url}) and [GitHub]({github_url})")
