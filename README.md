# INCLUDE DRS Registration Application

The INCLUDE DRS Registration Application registers file metadata to the CAVATICA DRS server.

## 1. Prerequisites

Before starting the file registration process, get familiar with the [CAVATICA DRS API](https://docs.cavatica.org/reference/drs-api-overview).

1. Sign up for [CAVATICA](https://www.cavatica.org/) if you haven't done so yet. Obtain an [authentication token](https://docs.cavatica.org/docs/get-your-authentication-token). All API requests need to have this as the HTTP header `X-SBG-Auth-Token` later in the registration process.

2. Contact the D3b DevOps team to obtain `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` that allow `Read` and `Write` aceess to objects in the S3 bucket where files to be registered are stored.

## 2. Source File Manifest Preparation

Prepare a source file manifest including the following columns (**Note**: Hashes can very, but usually include `ETag`, `MD5`, and `SHA-1`):

| ... | Bucket                                  | Key                                    | Size | ETag                             | ... |
| --- | --------------------------------------- | -------------------------------------- | ---- | -------------------------------- | --- |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0001B_MSD.tsv.gz | 906  | 19515517bfacc0b2ac2fc755b7c6440d |     |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0003A_MSD.tsv.gz | 917  | 6eb5846285c464762d074240b491171a |     |
|     | include-study-us-east-1-prd-sd-7ydc1w4h | source/other-omics/HTP0005A_MSD.tsv.gz | 917  | 818978bfa381a29ff772b4218ccd2b91 |     |

## 3. Dataset Creation and Storage Attachment

Before registering files to the CAVATICA DRS server, there are two steps requiring interactions with the API: 1) dataset creation and 2) storage attachment. The rest of the steps assumes the following URL as a `BASE_URL` of the API: `https://cavatica-api.sbgenomics.com/v2/drs-internal`

### 3.1 Dataset Creation

This step creates a dataset in the CAVATICA DRS server. Send a HTTP POST request to `<BASE_URL>/datasets` with the following data:

```json
{
  "name": "include-study-us-east-1-prd-sd-7ydc1w4h-registered",
  "version": "0.1.0",
  "access": {
    "privacy": "PRIVATE",
    "privateType": "REGISTERED",
    "authorizationEntity": "SBG"
  }
}
```

Note that we pick `"name"` and `"version"` while the rest is preset. Conventionally,

- The value of `"name"` suffixes the bucket name with "-registered" because files with a registered tier are indexed into the CAVATICA DRS server.
- For the initial, pre-release of data and software across D3b, `"0.1.0"` is used. This versioning may need to be re-visited later in the future.

Once successful, the above HTTP POST request will result in a response as follows:

```json
{
  "id": "61285b65-031f-414d-b501-d41599423e07",
  "createdBy": "meenchulkim",
  "dateCreated": "2022-03-07 14:10:09+0000",
  "dateModified": "2022-03-07 14:10:09+0000",
  "name": "include-study-us-east-1-prd-sd-7ydc1w4h-registered",
  "version": "0.1.0",
  "visible": false,
  "access": {
    "privacy": "PRIVATE",
    "privateType": "REGISTERED",
    "authorizationEntity": "SBG"
  }
}
```

Store the value of `"id"`, _i.e._, `DATASET_ID`; it is used for the rest of the registration process.

### 3.2 Storage Attachment

This step attaches a storage to the dataset created above. Send a HTTP POST request to `<BASE_URL>/storages` with the following data:

```json
{
  "name": "include-study-us-east-1-prd-sd-7ydc1w4h-registered",
  "datasetId": "61285b65-031f-414d-b501-d41599423e07",
  "cloudProvider": "AWS",
  "region": "us-east-1",
  "bucketName": "include-study-us-east-1-prd-sd-7ydc1w4h",
  "storageCredentials": {
    "type": "aws_user",
    "accessKeyId": <AWS_ACCESS_KEY_ID>,
    "secretAccessKey": <AWS_SECRET_ACCESS_KEY>
  }
}
```

Note that we pick the followings while the rest is preset:

- `"name"`: Use the same name used for dataset creation.
- `"datasetId"`: Use the `DATASET_ID` obtained as a result of dataset creation.
- `"bucketName"`: Use the bucket name.
- `"storageCredentials"`: Use the AWS credentials obtained from the D3b DevOps team.

Once successful, the above HTTP POST request will result in a response as follows:

```json
{
  "id": "ace3fa62-a430-438c-86b3-989941a2adb9",
  "createdBy": "meenchulkim",
  "dateCreated": "2022-03-07 14:12:11+0000",
  "dateModified": "2022-03-07 14:12:11+0000",
  "datasetId": "61285b65-031f-414d-b501-d41599423e07",
  "name": "include-study-us-east-1-prd-sd-7ydc1w4h-registered",
  "cloudProvider": "AWS",
  "bucketName": "include-study-us-east-1-prd-sd-7ydc1w4h",
  "region": "us-east-1",
  "active": true
}
```

## 4. DRS Registration

1. Make sure Python (>=3.7) is installed on your local machine or remote server where the application is deployed.

2. Clone this repository:

```bash
$ git  clone  https://github.com/include-dcc/include-app-drs-registration.git
$ cd  include-app-drs-registration
```

3. Create and activate a virtual environment:

```bash
$ python3  -m  venv  venv
$ source  venv/bin/activate
```

4. Create a `.env` file in the root directory:

```bash
# AWS credentials
AWS_ACCESS_KEY_ID=<PUT-AWS-ACCESS-KEY-ID>
AWS_SECRET_ACCESS_KEY=<PUT-AWS-SECRET-ACCESS-KEY>

# Dataset ID
DATASET_ID=<PUT-DATASET-ID>

# SBG Authentication token
X_SBG_Auth_Token=<PUT-X-SBG-AUTH-TOKEN>
```

5. Install dependencies:

```bash
(venv) $ pip install --upgrade pip && pip install  -r  requirements.txt
```

6. Get familiar with required and optional arguments:

```bash
(venv) python entrypoint.py -h
```

```
usage: entrypoint.py [-h] [--sep {t,c}]
                     [--cavatica_drs_api_url CAVATICA_DRS_API_URL]
                     [--hash_types {ETag,MD5,SHA-1} [{ETag,MD5,SHA-1} ...]]
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
  --hash_types {ETag,MD5,SHA-1} [{ETag,MD5,SHA-1} ...]
                        Hash types (default: ['ETag', 'MD5', 'SHA-1'])
```

7. Run the following command:

```bash
(venv) python entrypoint.py <source_file_path>  <target_file_path>

# e.g., >> python entrypoint.py source_file.csv target_file.csv --sep c --hash_types ETag SHA-1
```

## 5. Dataset Publication

The final step publishes the dataset. Send a HTTP POST request to `<BASE_URL>/<DATASET_ID>/publish`. Once successful, this HTTP POST request will result in a response as follows:

```json
{
  "id": "61285b65-031f-414d-b501-d41599423e07",
  "createdBy": "meenchulkim",
  "modifiedBy": "meenchulkim",
  "dateCreated": "2022-03-07 14:10:09+0000",
  "dateModified": "2022-03-10 16:07:00+0000",
  "name": "include-study-us-east-1-prd-sd-7ydc1w4h-registered",
  "version": "0.1.0",
  "visible": true,
  "access": {
    "privacy": "PRIVATE",
    "privateType": "REGISTERED",
    "authorizationEntity": "SBG"
  }
}
```

Corresponding CURL command for publishing: 

	curl --location -g --request PATCH ‘https://cavatica-api.sbgenomics.com/v2/drs-internal/datasets/<dataset_id>/publish' 
	--header 'X-SBG-Auth-Token: <token>' 
	--header 'X-SBG-Advance-Access: advance'


🎉 Tada! Now, the files are registed to the CAVATICA DRS server!
