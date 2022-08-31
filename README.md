# ges-disc-data-engineering

## Environment Creation:
- create a virtual environment using venv built in module in python
- enter your virtual environment and setup 'requirements.txt' file as follows
    `pip install requirements.txt`
- Download the Cloud Provider connection SDK, in this project we use GCP
    - Install gcloud SDK to enable the gcloud cli in your terminal
    - use `gcloud init` command to initialize the connection
    - use `gcloud auth application-default login` to login into your account and create service account JSON file to be authinticated with the gcloud CLI.

## Data Description:
These datasets are about Air Temperature and it's an multidimensional geographic data.
## Project Structure:
- Use Airflow to execute on the following python callable functions:
    - Create Validation Files and Authenticate users to be able to use ges-disc API
    - Extract the data from ges-disc API.
    - Create png files using matplotlib to show the total air temperature of earth at a specific month
- Use An operator to upload the png files to Google Cloud Storage Bucket.
## Test Use cases:
- Test whether the username and the password is exists in the environment variables or not.
- Test the response of the session is coming back with status 200 or not.
