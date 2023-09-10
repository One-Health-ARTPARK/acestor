import pandas as pd
import json
import numpy as np
import os
import re
import tempfile
import boto3


def read_linelist(linelist_paths: str = None, metadata_path: str = None,
                  year: int = 2021, source="local") -> pd.DataFrame:
    """_summary_

    Args:
        linelist_paths (str, optional): _description_. Defaults to None.
        metadata_path (str, optional): _description_. Defaults to None.
        year (int, optional): _description_. Defaults to 2021.
        source (str, optional): _description_. Defaults to "local".

    Returns:
        pd.DataFrame: _description_
    """

    with open(metadata_path, 'r') as f:
        metadata_list = json.load(f)

    linelists = [None] * len(metadata_path)

    headers = ['symptom_onset_date_dayfirst', 'year', 'age', 'sex', 'state_name',
               'district_name', 'sub_district_name', 'village_name', 'zone_name',
               'locality_name', 'ward_code', 'phc', 'sub_center', 'sample_collection_center',
               'initial_symptom_date', 'sample_date', 'result_date', 'testing_lab', 'test_method',
               'address', 'bbmp_Ulb']

    for i in range(len(metadata_list)):
        linelists[i] = preprocess(metadata_list[i], headers, year)

    linelist = pd.concat(linelists, ignore_index=True)

    return linelist


def standardise(linelist):

    return linelist


def preprocess(metadata, headers, year):

    tmp = tempfile.TemporaryDirectory()

    s3_session = boto3.session.Session().resource('s3')

    bucket = s3_session.Bucket('artpark-1health-data-dumps')
    file_key = 'mohfw_gok/line-lists/'

    s3_client = boto3.client('s3')

    keys = []
    for s3_file in bucket.objects.filter(Prefix=file_key):
        if s3_file.key.endswith('/'):
            continue
        keys.append(s3_file.key)

    keys = [file_name for file_name in keys if str(year) in file_name]

    for elem in keys:
        if year == 2018:
            file_name = 'LINE LIST OF DEN & CHIK.18.xlsx'
        else:
            file_name = elem.split('/')[-1]
        temp_file_path = os.path.join(tmp.name, file_name)
        s3_client.download_file(bucket.name, elem, temp_file_path)

    path = tmp.name
    print(metadata['file_name'])
    file_name = metadata['file_name']
    file_name = os.path.join(path, file_name)
    tab_name = metadata['tab_name']
    row_start = metadata['row_start']
    col_start = metadata['col_start']
    test_method_values = metadata['test_method_values']
    column_mapping = metadata['column_mapping']

    df = pd.read_excel(file_name, sheet_name=tab_name)
    if "row_end" in metadata:
        df_temp = df.iloc[row_start:metadata['row_end'], col_start:]
    else:
        df_temp = df.iloc[row_start:, col_start:]
    column_mapping = {
        df_temp.columns[int(k)]: v for k, v in metadata['column_mapping'].items()}
    df_temp.rename(columns=column_mapping, inplace=True)
    df_temp["district_name"] = metadata['district']
    df_temp["state_name"] = metadata['state']
    df_temp["year"] = metadata['year']

    if 'symptom_onset_date_dayfirst' in metadata and metadata['symptom_onset_date_dayfirst']:
        symptom_onset_date_dayfirst = True
    else:
        symptom_onset_date_dayfirst = False
    df_temp["symptom_onset_date_dayfirst"] = symptom_onset_date_dayfirst

    if "ffill_reqd" in metadata and metadata["ffill_reqd"]:
        columns_to_fill = ["sub_district_name"]
        for column in columns_to_fill:
            df_temp[column] = df_temp[column].replace('"', np.nan)
            df_temp[column].fillna(method='ffill', inplace=True)

    # For chikkaballapura and Haveri 2021
    if "ffill_reqd_na" in metadata and metadata["ffill_reqd_na"]:
        columns_to_fill = ["sub_district_name"]
        for column in columns_to_fill:
            df_temp[column] = df_temp[column].replace({'unknown': ''}).ffill().replace({'': np.nan})

    if "combined_result" in df_temp.columns:
        df_temp['test_method'] = df_temp['combined_result'].apply(
            check_test_result)
    elif "report_igm" in df_temp.columns and "report_ns1" in df_temp.columns:
        df_temp['test_method'] = np.where(df_temp['report_igm'].isin(test_method_values['IgM_positive']), 'IgM',
                                          np.where(df_temp['report_ns1'].isin(test_method_values['NS1_positive']),
                                                   'NS1', None))
    elif "report_igm" in df_temp.columns:
        df_temp['test_method'] = np.where(df_temp['report_igm'].isin(
            test_method_values['IgM_positive']), 'IgM', None)
    elif "report_ns1" in df_temp.columns:
        df_temp['test_method'] = np.where(df_temp['report_ns1'].isin(
            test_method_values['NS1_positive']), 'NS1', None)
    if 'age' in df_temp and 'sex' not in df_temp:
        try:
            df_temp[['age', 'sex']] = df_temp['age'].str.extract(
                r'^(\d+\.?[yrs|Yrs|mnth|Mnths|months|Months|years|Years]*)(?:\/([MF]))?$')
        except:
            df_temp["age"] = df_temp["age"]
    if 'sex' in df_temp and 'age' not in df_temp:
        df_temp['sex'] = df_temp['sex']
    df_temp = df_temp.reindex(columns=headers)

    return df_temp


def check_test_result(s):
    """ Standardise the test_method column
    """

    igm_pattern = re.compile(r"\bI\s*g\s*M\b", re.IGNORECASE)
    ns1_pattern = re.compile(r"\bN\s*S\s*1\b", re.IGNORECASE)
    try:
        if re.search(igm_pattern, s):
            return "IgM"
        elif re.search(ns1_pattern, s):
            return "NS1"
        else:
            return np.nan
    except:
        return np.nan


if __name__ == "__main__":
    df = read_linelist(metadata_path="/Users/saisneha/Documents/acestor/src/acestor/tmpdir/linelist_metadata_2021.json")
    df.to_csv("temp2021.csv")
