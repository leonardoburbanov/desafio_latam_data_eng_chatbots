import streamlit as st
import pandas as pd
import time
import os

# Function to read messages from file
def read_messages_from_file(file_path):
    try:
        df = pd.read_json(file_path, lines=True)
        return df
    except FileNotFoundError:
        st.error(f"{file_path} file not found. Please ensure it exists.")
        return None

# Main Streamlit code
def main():
    
    file_path = "messages.txt"

    
    # Initialize an empty placeholder for the table
    table_placeholder = st.empty()
    
    while True:
        # Read messages from file
        df = read_messages_from_file(file_path)
        
        # Update the table in the placeholder
        if df is not None:
            table_placeholder.table(df)
        
        # Wait for 2 seconds before updating again
        time.sleep(2)

if __name__ == "__main__":
    main()
