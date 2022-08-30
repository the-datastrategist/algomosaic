# -*- coding: utf-8 -*-
""" algoMosaic dataObject that inputs various types of data inputs
and converts to dataFrame. Accepts these input data types:
    - dataObject
    - Pandas DataFrame
    - CSV file
    - SQL file
    - JSON file

And outputs these data types:
    - Pandas DataFrame
    - CSV
    - Database (BigQuery load)

TO DO:
    - Add new input data formats (eg JSON object)

"""

import hashlib
import pandas as pd
from datetime import datetime

import configs
from algom.utils.client import bqClient


def get_hash_id(obj):
    """Create SHA1 hash ID from any data input

    Args:
        obj (str): String containing input information
            to be translated into an ID.

    Returns:
        str: Containing an ID based on the input data.
    """
    x = str(obj).encode()
    gid = hashlib.sha1(x).hexdigest()
    return gid


def _set_query_params(query, params):
    """ Format a query given a dict of parameters
    """
    if params:
        for k, v in params.items():
            query = query.replace('{' + str(k) + '}', str(v))
    query = query.replace('YYYYMMDD', datetime.now().strftime('%Y%m%d'))
    return query


def load_schema(df):
    """ Create schema template for BigQuery
    """
    def _get_type(v):
        if isinstance(v, str):
            return 'STRING'
        elif isinstance(v, int):
            return 'INT64'
        elif isinstance(v, float):
            return 'FLOAT64'
        elif isinstance(v, pd._libs.tslibs.timestamps.Timestamp):
            return 'DATETIME'
        else:
            return type(v)

    x = []
    for i, r in df[0:1].T.iterrows():
        x.append({
            'name': i,
            'type': _get_type(r[0]),
            'description': '',
        })
    return x


class dataObject:
    """Convert various forms data of data within a single class.

    Input data types:
        - dataObject
        - Pandas DataFrame
        - CSV file
        - SQL file
        - JSON file

    Output data types:
        - Pandas DataFrame
        - CSV
        - Database

    Attributes

    Examples:
        data = dataObject(my_data.csv)
    """
    def __init__(self, data, params=None, table_schema=None, if_exists='replace'):
        client = bqClient()
        self.credentials = client.credentials
        self.df = pd.DataFrame()
        self.params = eval(params) if isinstance(params, str) else params
        self.table_schema = table_schema
        self.if_exists = if_exists
        self.data_type = self._get_data_type(data)
        self.data = self.load_data(data)
        self._get_data_metadata()

    def load_data(self, data):
        """Load input data and convert to dataFrame (all formats):

        Check the inout data format and call the relevant
        function to input the data type.

        Args:
            data (any): Specify the data to input. Format can be
                on of the following:
                - algoMosaic dataObject
                - CSV reference (str)
                - JSON reference (str)
                - SQL file reference (str)
                - SQL query

        Returns:
            None
        """
        if 'dataObject' in str(type(data)):
            self.load_blob(data)
        elif isinstance(data, (list, dict, pd.DataFrame)):
            self.load_df(data)
        elif isinstance(data, str):
            if data.endswith('.csv'):
                self.load_csv_file(data)
            elif data.endswith('.json'):
                self.load_json_file(data)
            elif data.endswith('.sql'):
                self.load_sql_file(data)
            elif 'select' in data.lower() and 'from' in data.lower():
                self.load_sql(data)
        else:
            print("ERROR: This data type is not accepted.")
            # <<< NEED TO COMPLETE DATA INPUTS HERE >>>

            # <<< NEED TO ADD EXCEPTION HANDLING HERE >>>

    """
    Load data (by input type):
        Load one of several data types into the dataObject class, and
        convert data type into a dataFrame.
    """
    def load_blob(self, blob):
        try:
            self.input_type = 'dataObject'
            self.input_file = None
            self.input_code = None
            self.df = blob.df
            print("SUCCESS: Loaded dataObject.")
        except Exception as e:
            print("ERROR: Unable to import dataObject. {}.".format(e))

    def load_df(self, df):
        try:
            self.input_type = 'dataframe'
            self.input_file = None
            self.input_code = None
            self.df = pd.DataFrame(df)
            print("SUCCESS: Loaded DataFrame.")
        except Exception as e:
            print("ERROR: Unable to import DataFrame.\n{}".format(e))

    def load_csv_file(self, csv_file):
        try:
            self.input_type = 'csv file'
            self.input_file = csv_file
            self.input_code = None
            self.df = pd.read_csv(csv_file)
            print("SUCCESS: Loaded CSV file.")
        except Exception as e:
            print("ERROR: Unable to import CSV.\n{}".format(e))

    def load_json_file(self, json_file):
        try:
            self.input_type = 'json file'
            self.input_file = json_file
            self.input_code = None
            self.df = pd.read_json(json_file)
            print("SUCCESS: Loaded JSON file.")
        except Exception as e:
            print("ERROR: Unable to import JSON file.\n{}".format(e))

    def load_sql_file(self, sql_file):
        try:
            with open(sql_file, 'r') as f:
                sql = f.read()
            self.input_type = 'sql file'
            self.input_file = sql_file
            self.input_code = _set_query_params(sql, self.params)

            print("RUNNING: Loading SQL file: {}.".format(sql_file))
            self.df = pd.read_gbq(
                self.input_code,
                credentials=self.credentials,
                )
            print("SUCCESS: Loaded SQL query.")
        except Exception as e:
            print("ERROR: Unable to read SQL file.\n{}".format(e))

    def load_sql(self, sql, params=None, use_cache=True):
        try:
            self.input_type = 'sql'
            self.input_file = None
            self.input_code = _set_query_params(sql, self.params)

            print("RUNNING: Querying SQL script.")
            self.df = pd.read_gbq(
                self.input_code,
                credentials=self.credentials,
                configuration={'query': {'useQueryCache': use_cache}},
                )
            print("SUCCESS: Loaded SQL query.")
        except Exception as e:
            print("ERROR: Unable to run SQL.\n{}".format(e))

    """ OUTPUT DATA
        Output one of several data types from the dataObject class.
    """

    def to_df(self):
        return self.df

    def to_json(self, **kwargs):
        return self.df.to_json(**kwargs)

    def to_csv(self, path, **kwargs):
        return self.df.to_csv(path, **kwargs)

    def to_db(
        self,
        destination_table,
        project_id=None,
        partition=None,
        params=None,
        table_schema=None,
        if_exists=None,
    ):
        """Output dataframe to a database destination table.
        Currently only supports BigQuery.
        """
        def _set_destination_table_ids(destination_table):
            destination_list = destination_table.replace(':', '.').split('.')
            if len(destination_list) == 3:
                self.project_id = destination_list[0]
                self.dataset_id = destination_list[1]
                self.table_id = destination_list[2]
            if len(destination_list) == 2:
                self.project_id = project_id or configs.GOOGLE_PROJECT_ID
                self.dataset_id = destination_list[0]
                self.table_id = destination_list[1]

        # Get parameterized table IDs
        _set_destination_table_ids(destination_table)
        self.destination_table = self.dataset_id + '.' + self.table_id
        self.partition = partition or datetime.now().strftime('%Y%m%d')
        self.params = eval(params) if isinstance(params, str) else params
        self.destination_table_id = self._replace_string_parameters(
            self.destination_table, self.partition, self.params)
        self.full_destination_table_id = self.project_id + '.' + self.destination_table_id

        # Load dataframe to BigQuery via gbq()
        self.df.to_gbq(
            destination_table=self.destination_table_id,
            project_id=self.project_id,
            credentials=self.credentials,
            table_schema=table_schema or self.table_schema,
            if_exists=if_exists or self.if_exists,
        )

    """ METADATA
        Get metadata from data object.
    """
    def _get_data_metadata(self):
        self._get_features()
        self._get_data_id()

    def _get_features(self):
        feature_list = list(self.df)
        feature_list.sort()
        self.feature_list = feature_list

    def _get_data_id(self):
        """Create data_id based on technical_analysis included in data"""
        if len(self.feature_list) > 0:
            self.data_id = get_hash_id(self.feature_list)
        else:
            print(
                'ERROR: Must upload data with valid fields'
                ' to output the data_id.'
            )

    """ HELPER FUNCTIONS
        Functions referenced in the code above.
    """
    def _get_data_type(self, data):
        return type(data)

    def _replace_string_parameters(self, entry, partition=None, params=None):
        """Update a query or table name with today's date (i.e. YYYYMMDD)
        or custom parameters (e.g. {param_name}).
        """
        def _replace_date_partition(entry, partition=None):
            """
            Return table_id with YYYYMMDD notation as a date partition.
            Date partition defaults to today if not specified.
            """
            p = partition or datetime.now().strftime("%Y%m%d")
            return entry.replace("YYYYMMDD", p).replace("{partition}", p)

        def _replace_params(entry, params):
            # Replace all parameters in the destination table name
            return _set_query_params(entry, params)

        # Run function
        entry = _replace_date_partition(entry, partition)
        entry = _replace_params(entry, params)
        return entry
