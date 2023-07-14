import streamlit as st
import openpyxl
import csv
import tempfile
from datetime import date

# Function to handle file processing
def process_file(source_file, template_file, bonus_code, name, platform):
    try:
        # Open the source file and template file
        source_wb = openpyxl.load_workbook(source_file)
        template_wb = openpyxl.load_workbook(template_file)

        # Get the A and B columns from the source file excluding the first row
        source_sheet = source_wb.active
        rows_to_copy = source_sheet.iter_rows(min_row=2, min_col=1, max_col=2, values_only=True)

        # Prepare the CSV file name
        today = date.today()
        output_file_name = f"{bonus_code}_{today.strftime('%d%m%y')}_{name}_{platform}.csv"
        output_file_path = tempfile.gettempdir() + '/' + output_file_name

        with open(output_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Get the information from cells A1 and B1 of the template file
            template_sheet = template_wb.active
            template_info = [template_sheet.cell(row=1, column=1).value, template_sheet.cell(row=1, column=2).value]

            # Write the header row
            csv_writer.writerow(template_info)

            # Write the rows from the source file
            for row in rows_to_copy:
                csv_writer.writerow(row)

        # Close the workbooks
        source_wb.close()
        template_wb.close()

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
template_file = st.file_uploader("Choose a template file", type=['xlsx', 'xls'])
bonus_code = st.text_input('Bonus Code')
name = st.text_input('Name')
platform = st.selectbox('Platform', ['PBULL', 'SBULL'])

if st.button('Process File'):
    if source_file and template_file and bonus_code and name and platform:
        output_file_path = process_file(source_file, template_file, bonus_code, name, platform)
        if output_file_path:
            st.download_button(label="Download Output File", data=output_file_path, file_name='output.csv')
    else:
        st.error("All fields are required.")
