import logging
import os
import sys
import argparse
import time
import pprint

from dotenv import find_dotenv, load_dotenv
import pandas as pd
from requests import RequestException

from d3b_utils.requests_retry import Session

DOTENV_PATH = find_dotenv()
if DOTENV_PATH:
    load_dotenv(DOTENV_PATH)

API_VERSION = "v2"
X_SBG_Auth_Token = os.getenv("X_SBG_Auth_Token")

DATASET_ID = os.getenv("DATASET_ID")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

pp = pprint.PrettyPrinter(indent=4)


class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"\nerror: {message}\n\n")
        if not isinstance(sys.exc_info()[1], argparse.ArgumentError):
            self.print_help()
        sys.exit(2)


# Instantiate a parser
parser = CustomParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Required arguments
parser.add_argument("source_file_path", help="Source tabluar file")
parser.add_argument("target_file_path", help="Target tabluar file")

# Optional arguments
parser.add_argument(
    "--sep",
    default="t",
    choices=["t", "c"],
    required=False,
    help="Delimiter to use; t (for tsv) or c (for csv)",
)
parser.add_argument(
    "--cavatica_drs_api_url",
    default="https://cavatica-api.sbgenomics.com/",
    required=False,
    help="CAVATICA DRS API URL",
)
parser.add_argument(
    "--hash_types",
    nargs="+",
    default=["ETag", "MD5", "SHA-1"],
    choices=["ETag", "MD5", "SHA-1"],
    required=False,
    help="Hash types",
)

# Parse arguments
args = parser.parse_args()

source_file_path = args.source_file_path
target_file_path = args.target_file_path
sep = "\t" if args.target_file_path == "t" else ","
cavatica_drs_api_url = args.cavatica_drs_api_url
hash_types = args.hash_types

# Import in source file
source_df = pd.read_csv(source_file_path, sep=sep)
target_df = source_df.copy()
expects, success = source_df.shape[0], 0

logging.info(f"🚀 Start registering {expects} files to {cavatica_drs_api_url}!")
start = time.time()


# Index DRS objects
access_url_list = []
for i, row in source_df.iterrows():
    # Build data
    data = {
        "datasetId": DATASET_ID,
        "name": row["Key"].split("/")[-1],
        "size": row["Size"],
        "checksums": [
            {"type": hash_type, "checksum": row[hash_type]} for hash_type in hash_types
        ],
        "locationUrls": [f"s3://{row['Bucket']}/{row['Key']}"],
    }

    # Send a POST request
    resp = Session().post(
        f"{cavatica_drs_api_url.rstrip('/')}/{API_VERSION}/drs-internal/objects/index/",
        headers={
            "X-SBG-Auth-Token": X_SBG_Auth_Token,
            "X-SBG-Advance-Access": "advance",
            "Content-Type": "application/json",
        },
        json=data,
    )

    # Cache generated DRS URI
    try:
        resp.raise_for_status()
        drs_uri = resp.json().get("drsUri")
        access_url_list.append(drs_uri)
        success += 1
        pp.pprint(f"  🍱 Registered {data}; Access URL: {drs_uri}")
    except RequestException as e:
        pp.pprint(f"  ❌ Failed to register {data}: {e.response.text}")

# Export to target file
target_df["Access URL"] = access_url_list
target_df.to_csv(target_file_path, sep=sep, index=False)


# Time the process
end = time.time()
timedelta = end - start
m, s = divmod(timedelta, 60)
h, m = divmod(m, 60)
logging.info(f"✅ Time elapsed: {h} hours {m} minutes {s} seconds")

logging.info(f"🎉 {success} files have been registered to {cavatica_drs_api_url}!")
