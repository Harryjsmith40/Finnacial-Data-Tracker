import os
import pandas as pd
import logging

class FinancialTracker:
    """A finnacial tracker designed to help make inform make data based decisions"""    
    # Defines the dtypes of the master record
    schema = {
        'dtypes': {'Amount': float, 'Balance': float, 'Desc': str},
        'date_columns': ['Date'],
        'date_format' : '%d/%m/%Y'
        }

    def __init__(self):
        """Initialises the master record and uploads a new file"""
        # Creates a instance variable with the file path
        self.origin_path = os.getcwd()
        self.data_folder = os.path.join(self.origin_path, 'data')
        self.master_record_path = os.path.join(self.data_folder, 'master_record.csv')

        # Checking if the master file exists
        # Currently assumes ./Data/ exists if the user doesn't have ./Data/master_record.csv 
        if os.path.exists(self.master_record_path):
            # Checks structure of file is correct
            master_record = pd.read_csv(self.master_record_path)
            if master_record.columns.tolist() == ['Date', 'Amount', 'Desc', 'Balance']:
                logging.debug('master_record initialised correctly')
            else:
                raise ValueError('master_record exists with incorrect headers')
            
        # Creates it if it doesn't exist
        else:
            master_record = pd.DataFrame(columns=['Date', 'Amount', 'Desc', 'Balance'])
            if os.path.exists(self.data_folder):
                master_record.to_csv(self.master_record_path, index=False)
            else:
                os.mkdir(self.data_folder)
                master_record.to_csv(self.master_record_path, index=False)

        self.upload_file()
    
    def read_master(self):
        """Reads the master file"""
        master_record = pd.read_csv(self.master_record_path, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)
        return master_record

    def read_and_clean(self, file_path):
        """Reads CSV files, formates dates and data types, removes null data and adds an index"""
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)

        # Sort by date to maintain chronological order
        df.sort_values(by=['Date'], inplace=True, ascending=True)

        # Drops na values if the amount or date is missing
        df.dropna(subset=['Date','Amount'], inplace=True)

        return df
    
    def deduplicate(self, file_path):
        """ Checks for and removes duplicates""" 
        master_record = self.read_master()
        df = self.read_and_clean(file_path)
        merged_df = df.merge(master_record, how='left', on=['Date', 'Amount', 'Desc', 'Balance'], indicator=True)
        merged_df = merged_df[merged_df['_merge'] == 'left_only']
        merged_df = merged_df.drop(labels='_merge' , axis='columns')

        self.to_master(merged_df)

    def to_master(self, df):
        """Updates master_record.csv to include new data"""
        # Appends to master_record.csv the new data
        df.to_csv(self.master_record_path, mode='a', header=False, index=False, date_format=self.schema['date_format'])
    
    def upload_file(self):
        """Asks the user to input a file name and checks if it exists, if it does it is uploaded and deduplicated, if not the user is asked to input a file name again"""
        self.file_path = input("Please ensure the CSV file is in the data folder and provide the file name would like to upload: ")
        self.file_path = os.path.join(self.data_folder, self.file_path)

        if os.path.exists(self.file_path):
            self.deduplicate(self.file_path)
            logging.debug('file_path exists correctly')
        else:
            print("Failed file doesn't exist") 
            self.upload_file()

tracker = FinancialTracker()