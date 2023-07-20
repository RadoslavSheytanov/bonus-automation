# Import necessary libraries
import pandas as pd  # For data manipulation
import streamlit as st  # For creating the web app
import tempfile  # For creating temporary folders to store the processed files
import os  # For file path manipulations
import datetime  # For handling date related functions
import base64  # For encoding the file for download
import traceback  # For detailed error handling

# This function handles processing the uploaded file based on the provided parameters
def process_file(source_file, bonus_type, bonus_code, name, platform, selected_date):
    try:
        # Read the uploaded Excel file into a pandas DataFrame
        df = pd.read_excel(source_file)
        
        # Handle the 'Casino Calendar' bonus type separately
        if bonus_type == 'Casino Bonus (Casino Calendar)':
            # Keep only the second and third columns and set the headers
            df = df.iloc[:, 1:3]
            df.columns = ['SBUSERID', 'Bonus Value']
        else:
            # Convert second column to string type to handle potential non-string values
            df.iloc[:, 1] = df.iloc[:, 1].astype(str)
            
            # Identify the VIP rows using a regular expression pattern
            vip_data = df[df.iloc[:, 1].str.contains('VIP\s*\(\d+\)', na=False, regex=True)]
            
            # The remaining rows are the non-VIP rows
            non_vip_data = df[~df.iloc[:, 1].str.contains('VIP\s*\(\d+\)', na=False, regex=True)]
            
            # Keep only the first two columns of the non-VIP data
            non_vip_data = non_vip_data.iloc[:, :2]
            
            # Set the column headers based on the bonus type
            if bonus_type == 'Free Bets':
                non_vip_data.columns = ['SBUSERID', 'Bonus Value']
            elif bonus_type == 'Free Spins':
                non_vip_data.columns = [None, None]
            elif bonus_type in ['Casino Bonus', 'Sports Bonus', 'Prize Picker']:
                non_vip_data.columns = ['SBUSERID', 'Bonus Value']
            else:
                non_vip_data.columns = ['', '']

            # Replace the original DataFrame with the processed non-VIP data
            df = non_vip_data

        # Create a temporary directory to store the output CSV file
        temp_dir = tempfile.mkdtemp()
        
        # Construct the output file name based on the provided parameters
        if selected_date:
            selected_date_str = selected_date.strftime('%Y-%m-%d')  # Format the date in 'YYYY-MM-DD' format
            file_name = f"{bonus_code}_{selected_date_str}_{name}_{platform}.csv"
        else:
            today_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Use today's date if no date is selected
            file_name = f"{bonus_code}_{today_date}_{name}_{platform}.csv"
        
        # Combine the directory path and file name to get the full path of the output file
        output_file_path = os.path.join(temp_dir, file_name)
        
        # Save the DataFrame to a CSV file
        df.to_csv(output_file_path, index=False, header=(bonus_type != 'Free Spins'))

        # Return the path of the output file and the VIP data (if any)
        return output_file_path, vip_data if bonus_type != 'Casino Bonus (Casino Calendar)' else None
    except Exception as e:
        # If there's an error during the processing, show the error message and detailed traceback
        st.error(f"An error occurred while processing the file: {str(e)}")
        st.error(traceback.format_exc())
        return None, None

# This function creates a download link for the processed CSV file
def get_csv_download_link(csv_file):
    with open(csv_file, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()  # Encode the file to base64
        # Construct the download link
        href = f'<a href="data:file/csv;base64,{b64}" download="{csv_file.split("/")[-1]}" style="display: inline-block; padding: 0.5em 1em; color: #ffffff; background-color: #007bff; border-radius: 0.25em; text-decoration: none;">Download CSV File</a>'
    return href

# Set the title of the Streamlit app
st.title('Bonus Templating System')

# Create file uploader, dropdowns, text inputs, and date input for user to provide necessary information
uploaded_file = st.file_uploader("Choose a file", type=['xls', 'xlsx'])
bonus_type = st.selectbox("Bonus Type:", ["------", "Free Bets", "Free Spins", "Casino Bonus", "Sports Bonus", "Prize Picker", "Casino Bonus (Casino Calendar)"])
bonus_code = st.text_input("Bonus Code:", "")
selected_date = st.date_input("Select Date:")
name = st.text_input("Agent's Name:")
platform = st.selectbox("Platform:", ["------", "PBULL", "SBULL"])

# When the user clicks the 'Process File' button, process the uploaded file
if st.button('Process File'):
    if uploaded_file is not None and bonus_type != "------" and bonus_code and name and platform:
        # Process the uploaded file
        output_file_path, vip_data = process_file(uploaded_file, bonus_type, bonus_code, name, platform, selected_date)

        # If the output file was successfully created, provide a download link
        if output_file_path is not None:
            st.markdown(get_csv_download_link(output_file_path), unsafe_allow_html=True)

        # If there are any VIP rows, display them separately
        if vip_data is not None and not vip_data.empty:
            st.markdown("**ATTENTION: This file consists of VIP Player/s and they should be credited in a different campaign:**", unsafe_allow_html=True)
            st.dataframe(vip_data)
        else:
            st.success("This file doesn't contain any special VIP Players Bonuses. Click -Download CSV file- button above and credit the bonus as normal.")
    else:
        st.error("Please provide all inputs.")

# Add hyperlinks to LinkedIn, GitHub, and email for contacting the developer
linkedin_url = "https://ie.linkedin.com/in/radoslav-sheytanov-771a43260"
github_url = "https://github.com/radoslavSheytanov/"
email = "radoslav@programmer.net"
st.markdown(f"Development and Support - [LinkedIn]({linkedin_url}) and [GitHub]({github_url})")
st.markdown(f"Questions? Feel free to [message the developer directly.](mailto:{email})")
