from algom.utils.data_object import dataObject
from pathlib import Path
import os


def get_inputs():
    return {
        'sql': '''SELECT
        place_id,
        place_name,
        FROM `bigquery-public-data.geo_us_census_places.places_new_york`
        LIMIT 10
        '''
    }


def get_data():
    inputs = get_inputs()
    sql = inputs.get('sql')
    return dataObject(sql)
    

def test_sql_load():
    # Load publicly available table from BigQuery
    # Ensure SQL file loads properly
    inputs = get_inputs()
    sql = inputs.get('sql')
    data = dataObject(sql)
    assert len(data.df) == 10
    assert len(data.feature_list) == 2
    assert len(data.data_id) > 1


def test_sql_file_load():
    # Load publicly available table from BigQuery
    # Ensure SQL file loads properly
    def _write_sql():
        inputs = get_inputs()
        f = open("test_file.sql", "a")
        f.write(inputs.get('sql'))
        f.close()

    _write_sql()
    data = dataObject('test_file.sql')
    os.remove('test_file.sql')
    assert len(data.df) == 10
    assert len(data.feature_list) == 2
    assert len(data.data_id) > 1


def test_csv_load():
    # Ensure CSV loads properly
    data = get_data()
    data.df.to_csv('test_file.csv')
    data = dataObject('test_file.csv')
    os.remove('test_file.csv')
    assert len(data.df) == 10


def test_json_load():
    # Ensure JSON loads properly
    data = get_data()
    data.df.to_json('test_data.json')
    data = dataObject('test_data.json')
    os.remove('test_data.json')
    assert len(data.df) == 10


def test_df_load():
    # Ensure dataFrame loads properly
    data = get_data()
    data = dataObject(data.df)
    assert len(data.df) == 10


def test_data_load():
    # Ensure dataObject loads properly
    data_obj = get_data()
    data = dataObject(data_obj)
    assert len(data.df) > 1
