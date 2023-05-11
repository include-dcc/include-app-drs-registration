# INCLUDE DRS Registration Application

The INCLUDE DRS Registration Application registers file metadata to the CAVATICA DRS server.

## Prerequisites

1. TBD
2. TBD
3. Prepare a source file manifest including the following columns (**Note**: Hashes can very, but usually include `ETag`, `MD5`, and `SHA-1`):

| ... | Bucket                                  | Key                                    | Size | ETag                             | ... |
| --- | --------------------------------------- | -------------------------------------- | ---- | -------------------------------- | --- |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0001B_MSD.tsv.gz | 906  | 19515517bfacc0b2ac2fc755b7c6440d |     |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0003A_MSD.tsv.gz | 917  | 6eb5846285c464762d074240b491171a |     |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0005A_MSD.tsv.gz | 917  | 818978bfa381a29ff772b4218ccd2b91 |     |

## Quickstart

1. Make sure Python (>=3.7) is installed on your local machine or remote server where the application is deployed.

2. Clone this repository:

```bash
$ git clone https://github.com/include-dcc/include-app-drs-registration.git
$ cd include-app-drs-registration
```

3. Create and activate a virtual environment:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

4. Create a `.env` file in the root directory:

```bash
# SBG Authentication token
X_SBG_Auth_Token=<PUT-X-SBG-AUTH-TOKEN>

# Dataset ID
DATASET_ID=<PUT-DATASET-ID>

# AWS credentials
AWS_ACCESS_KEY_ID=<PUT-AWS-ACCESS-KEY-ID>
AWS_SECRET_ACCESS_KEY=<PUT-AWS-SECRET-ACCESS-KEY>
```

5. Install dependencies:

```bash
(venv) $ pip install --upgrade pip && pip install -r requirements.txt
```

6. Get familiar with required and optional arguments:

```bash
(venv) python entrypoint.py -h
```

```
usage: entrypoint.py [-h] [--sep {t,c}]
                     [--cavatica_drs_api_url CAVATICA_DRS_API_URL]
                     [--hashe_types {ETag,MD5,SHA-1} [{ETag,MD5,SHA-1} ...]]
                     source_file_path target_file_path

positional arguments:
  source_file_path      Source tabluar file
  target_file_path      Target tabluar file

optional arguments:
  -h, --help            show this help message and exit
  --sep {t,c}           Delimiter to use; t (for tsv) or c (for csv) (default:
                        t)
  --cavatica_drs_api_url CAVATICA_DRS_API_URL
                        CAVATICA DRS API URL (default: https://cavatica-
                        api.sbgenomics.com/)
  --hashe_types {ETag,MD5,SHA-1} [{ETag,MD5,SHA-1} ...]
                        Hash types (default: ['ETag', 'MD5', 'SHA-1'])
```

7. Run the following command:

```bash
(venv) python entrypoint.py <source_file_path> <target_file_path>

# e.g., >> python entrypoint.py source_file.csv target_file.csv --sep c --hashe_types ETag SHA-1
```
