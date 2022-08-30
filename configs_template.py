"""configs.py

Configurations for the algoMosaic project.

"""

# GOOGLE CLOUD PLATFORM

# Below are details need to connect algoMosaic to your Google Cloud Platform.
GOOGLE_PROJECT_ID = 'my-project-name'

# GCP Storage bucket where models will be saved
GOOGLE_STORAGE_BUCKET = 'my_storage_bucket'

# Location of the GCP service account key
GOOGLE_APPLICATION_CREDENTIALS = 'my-project-name-xxxxxxxxxxxx.json'

# KUBEFLOW
# Specify your Kubeflow host
KFP_CLIENT_HOST = 'https://XXXXXXXXXXXXXXXX-dot-us-central1.pipelines.googleusercontent.com'

# MODEL STORAGE
# The information below specifies where to store models
# on Google Cloud Storage. When you store models, they
# will be stored to this location.
MODEL_STORAGE_DIRECTORY = 'models/'
MODEL_LOCAL_DIRECTORY = '/home/jovyan/algomosaic/data/models/'

# SLACK
# Add a Slack Bot token below to enable messaging between algom and Slack
SLACK_BOT_TOKEN = 'XXXXXXX'
