import os
import boto3


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
    print(download("s3://artpark-1health-data-dumps/mohfw_gok/daily_reports/2023-09-11.xlsx"))
