import pandas as pd
from pathlib import Path
import boto3
import os
from datetime import datetime as dt
import shutil


START_DATE = dt.strptime("2023-09-12", "%Y-%m-%d")


def generate_daily_summary(xls_URI: str) -> pd.DataFrame:
    """Generates Daily Summary in standard format

    Args:
        xls_URI (str): _description_

    Returns:
        pd.DataFrame: _description_
    """

    path = download(xls_URI)

    # Based on 2023 Format
    row_indices = list(range(4, 35)) + [37]
    col_indices = [0, 1, 2] + list(range(7, 19))

    district_codes_path = Path(__file__).parent / "Daily Summary v2 Format - ordered_districts.csv"

    district_codes = pd.read_csv(district_codes_path)

    summary = pd.read_excel(path).iloc[row_indices, col_indices].reset_index(drop=True)

    summary.columns = ["record.date", "regionID", "regionName", "daily.suspected", "daily.tested",
                       "daily.igm_positives", "daily.ns1_positives", "daily.total_positives",
                       "daily.deaths", "cumulative.suspected", "cumulative.tested",
                       "cumulative.igm_positives", "cumulative.ns1_positives",
                       "cumulative.total_positives", "cumulative.deaths"]

    summary["regionID"] = district_codes["regionID"]
    summary["regionName"] = district_codes["regionName"]
    _, key = xls_URI.replace("s3://", "").split("/", 1)
    date = key.split("/")[-1].replace(".xlsx", "")
    summary["record.date"] = date
    summary.fillna(0, inplace=True)
    # summary.drop("regionName", axis="columns", inplace=True)

    return summary


def download(URIS: [str, dict], download_dir: str = None, access="implicit") -> [str, dict]:
    """Download the files from S3 for the URIs provided

    Args:
        URIS (str, dict]): _description_
        download_dir (str, optional): Directory to Download the file(s) to. Defaults to None.
            Function uses "/tmp" when set to None, will be deprecated in favour of python's tempfile.TemporaryFile()
        access (str, optional): _description_. Defaults to "implicit".

    Raises:
        ValueError: _description_

    Returns:
        [str, dict]: the path (or dictionary of paths) of the downloaded files
    """

    if download_dir is None:
        download_dir = "tmp/"

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    if isinstance(URIS, str):
        if access == "implicit":
            client = boto3.client('s3')

            if URIS.endswith("/") or "/" not in URIS or not URIS.startswith("s3://"):
                raise ValueError("Enter a Valid URI for a file")

            bucket, key = URIS.replace("s3://", "").split("/", 1)
            path = download_dir + key.split("/")[-1]

            client.download_file(bucket, key, path)

        return path


if __name__ == "__main__":

    s3 = boto3.client('s3')

    source_objects = s3.list_objects_v2(Bucket="artpark-1health-data-dumps",
                                        Prefix="mohfw_gok/daily_reports/2023-")
    source_keys = [obj["Key"] for obj in source_objects.get("Contents", []) if obj["Size"] > 0]

    dest_objects = s3.list_objects_v2(Bucket="artpark-1health-hh-live-data",
                                      Prefix="state-karnataka/summaries_daily_v2/2023-")
    dest_keys = [obj["Key"] for obj in dest_objects.get("Contents", []) if obj["Size"] > 0]

    if not os.path.exists("tmp/"):
        os.makedirs("tmp/")

    for key in source_keys:
        filename = key.split("/")[-1]
        target_filename = filename.replace(".xlsx", ".csv")

        file_date = dt.strptime(filename.replace(".xlsx", ""), "%Y-%m-%d")

        if file_date >= START_DATE:
            dest_key = "state-karnataka/summaries_daily_v2/" + target_filename

            if dest_key not in dest_keys:
                s3.download_file(
                    Bucket="artpark-1health-data-dumps",
                    Key=key,
                    Filename="tmp/" + filename
                )

            if dest_key not in dest_keys:
                source_URI = "s3://artpark-1health-data-dumps/" + key
                summary = generate_daily_summary(source_URI)
                summary.to_csv("tmp/" + target_filename, index=False)
                # print("UPLOADING:", dest_key)
                s3.upload_file(
                    "tmp/" + target_filename,
                    "artpark-1health-hh-live-data",
                    dest_key,
                )

    shutil.rmtree("tmp/")
