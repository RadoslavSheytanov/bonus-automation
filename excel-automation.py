import streamlit as st
import openpyxl
import csv
import tempfile
from datetime import date
import pandas as pd
import os

def process_file(source_file, bonus_type, bonus_code, name, platform):
    try:
        # Open the source file
        source_wb = openpyxl.load_workbook(source_file)
        source_sheet = source_wb.active

        # Get the A and B columns from the source file excluding the first row
        rows_to_copy = list(source_sheet.iter_rows(min_row=2, min_col=1, max_col=2, values_only=True))

        # Prepare the CSV file name
        today = date.today()
        output_file_name = f"{bonus_code}_{today.strftime('%d%m%y')}_{name}_{platform}.csv"
        output_file_path = tempfile.gettempdir() + '/' + output_file_name

        # Set the header based on the bonus type
        if bonus_type == 'Free Bets' or bonus_type == 'Casino Bonus' or bonus_type == 'Sports Bonus':
            header = ['SBUSERID', 'Bonus Value']
        elif bonus_type == 'Free Spins (Daily Lucky Spins)':
            header = ['(insert SbPin)', '(insert amount)']
        else:
            header = ['', '']

        # Create a pandas DataFrame from the rows_to_copy
        df = pd.DataFrame(rows_to_copy, columns=header)

        # Save the DataFrame to a csv file
        df.to_csv(output_file_path, index=False)

        # Close the workbook
        source_wb.close()

        # Print completion message
        st.success(f"File processing completed successfully")

        return output_file_path

    except Exception as e:
        # Print error message
        st.error(f"Error processing file. Error message: {str(e)}")

        return None

# Streamlit UI
st.title('File Processor')

# Input widgets
source_file = st.file_uploader("Choose a source file", type=['xlsx', 'xls'])
bonus_type = st.selectbox('Bonus Type', ['Free Bets', 'Free Spins', 'Free Spins (Daily Lucky Spins)', 'Casino Bonus', 'Sports Bonus'])
bonus_code = st.text_input('Bonus Code')
name = st.text_input('Name')
platform = st.selectbox('Platform', ['PBULL', 'SBULL'])

if st.button('Process File'):
    if source_file and bonus_type and bonus_code and name and platform:
        output_file_path = process_file(source_file, bonus_type, bonus_code, name, platform)
        if output_file_path:
            st.download_button(label="Download Output File", data=output_file_path, file_name='output.csv')
    else:
        st.error("All fields are required.")
