import pandas as pd
from acestor.read import s3_helper
from pathlib import Path
import os
import shutil
import boto3
from tqdm import tqdm

if not os.path.exists("tmp/"):
    os.makedirs("tmp/")

summaries_URI = "s3://artpark-1health-hh-live-data/state-karnataka/summaries_daily_v2/\
combined_daily_reports_till_2023-09-15.csv"
path = s3_helper.download(summaries_URI, download_dir="tmp/")
summaries = pd.read_csv(path, low_memory=False)

district_codes_path = Path(__file__).parent / "Daily Summary v2 Format - ordered_districts.csv"
i = 1
for each_date in tqdm(summaries["record.date"].unique(), total=len(summaries["record.date"].unique())):

    district_codes = pd.read_csv(district_codes_path)
    daily_summary = summaries[summaries["record.date"] == each_date].reset_index(drop=True)
    daily_summary = pd.merge(daily_summary, district_codes, how="right", on="regionID")
    daily_summary["record.date"].fillna(each_date, inplace=True)
    daily_summary.fillna(0, inplace=True)
    daily_summary = daily_summary[["record.date", "regionID", "regionName", "daily.suspected", "daily.tested",
                                   "daily.igm_positives", "daily.ns1_positives", "daily.total_positives",
                                   "daily.deaths", "cumulative.suspected", "cumulative.tested",
                                   "cumulative.igm_positives", "cumulative.ns1_positives",
                                   "cumulative.total_positives", "cumulative.deaths"]]

    target_file_name = str(each_date) + ".csv"
    daily_summary.to_csv("tmp/" + target_file_name, index=False)

    dest_key = "state-karnataka/summaries_daily_v2/" + target_file_name
    s3 = boto3.client('s3')
    s3.upload_file(
                    "tmp/" + target_file_name,
                    "artpark-1health-hh-live-data",
                    dest_key,
                )

shutil.rmtree("tmp/")
