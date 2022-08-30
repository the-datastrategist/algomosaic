###### BETA

# algoMosaic

#### algoMosaic is an open-source data science automation framework.

Automating data science can be complicated. algoMosaic makes it seamless by 
combining these commonly used open-source platforms:

- Jupyter Lab
- Kubeflow
- Docker
- Google Cloud Platform
- MLflow (future version)

algoMosaic allows data scientists to **move easily between ad hoc analysis**
(in Jupyter) **and scheduled processes** (with Kubeflow). It uses GCP Service
Accounts to connect to BigQuery and Storage, allowing for scalable and
decentralized data science pipelines.

<br>

## Setup for Ad Hoc Analysis using Jupyter Notebook

### 1. Clone the template repository from Github.

```
mkdir my-repo
cd my-repo
git clone https://github.com/algomosaic/algom.git
```

### 2A. Launching algoM with Bash

```
cd algom
docker run -it gcr.io/the-data-strategist/algomosaic:latest /bin/bash
```

### 2B. Launching algoM with Jupyter Lab (ad hoc analysis)

```
cd algom
docker-compose -f docker-compose-jupyter.yaml up --build
```

You terminal will launch the standard Jupyter Lab setup. Copy
and paste the URL provided into your browser. 


<br><br>

## Setup for Scheduled/Production using Kubeflow

Before running algoMosaic, we must set up Google Cloud Platform to properly
interact with it. However, you can still run algoM locally without setting
up GCP. If you with to do this, skip to Step 5.1 in the setup.

<br>

### 1. Clone a template project

1.1. Clone the template repository from Github.

```
git clone https://github.com/algomosaic/algom.git
```

<br>

### 2. Set up Google Cloud Platform infrastructure

algoMosaic connects with a set of GCP infrastructure. We must setup this
infrastructure before initializing our algoMosaic project.

2.1. **Set up a [Cloud SQL](https://cloud.google.com/sql/) database**. Follow 
these instructions to 
[setup a new Cloud SQL instance](https://cloud.google.com/sql/docs/mysql/create-instance).

2.2. **Set up Google [Storage](https://cloud.google.com/storage)**. Next, we will  
[setup a Storage instance](https://cloud.google.com/storage/docs/quickstart-console). 
We will store models here when using algoMosaic.

2.3. **Create a new bucket**. 
Create a [Storage bucket](https://cloud.google.com/storage/docs/creating-buckets). 
We'll configure this bucket shortly.

<br>

### 3. Set up GCP Service Account 

Service accounts allow us to connect to BigQuery without user-level authentication.
This account will be used for both ad hoc and scheduled analysis.


3.1. **Create a GCP Service Account**. Follow these instructions to 
[create a Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts#iam-service-accounts-create-console).
    - Add the Role "BigQuery Data Owner"
    - Add the Role "Storage Object Admin"
    - Optionally, grant users access through this service account

3.2. **Create a GCP Service Account Key**. Follow these 
instructions to create a Service Account key.
    - In the Admin Console, select the Service Account you
    just created.
    - Select the "Keys" in the top header.
    - Click "Add Key" button and select the JSON option.

3.3. Download the Service Account Key and add to the `algom`
directory.

<br>

### 4. Update configs.py

Open `algom/configs.py` and update the variables to fit your project. Specifically, we
will add parameters for:
    
    - _algoMosaic ecosystem._ Information related to your algoM instance, i.e. the
    project's 'ecosystem.'
     
    - _Google Cloud Platform._ Includes the GCP project you will use, as well as
    the location you will store your models. 
    
    - _algoMosaic analytics database._ These tables track information about saved
    and executed models.

<br>

### 5. Launch algomosaic

Once you've updated the parameters for the algomosaic ecosystem, we can launch the platform
There are two ways we can launch algoMosaic -- **ad hoc analysis** or **scheduled analysis**.


#### 5.1. __Launching algoM with Bash__

```
docker run -it gcr.io/the-data-strategist/algomosaic:latest /bin/bash
```

<br>

#### 5.2. __Launching algoM with Jupyter Lab (ad hoc analysis)__

```
docker-compose -f docker-compose-jupyter.yaml up --build
```

You terminal will launch the standard Jupyter Lab setup. Copy
and paste the URL provided into your browser. 

<br>


#### 5.3. __algoM with Airflow + Jupyter Lab (scheduled analysis or processes)__

<< TO DO: Update this section >>

```
docker-compose -f docker-compose-airflow.yaml up --build
```

We can connect to each services connect via the ports below:

- Jupyter Lab: `http://localhost:8888` (secure connection required)
- Airflow: `http://localhost:8080`
- MLflow: `http://localhost:5000`   

<br><br>


# How to use

algoMosaic is built with the following ML lifecycle in mind. Our 
[documentation](https://github.com/algomosaic/algomosaic/tree/master/docs) 
provides details on how to complete each step in this lifecycle. 

1. Data extraction
2. Feature engineering
3. Model training and storage
4. Model prediction
5. Python process tracking

We streamline and/or automate aspects of this lifecycle. See the
[example notebooks](https://github.com/algomosaic/algomosaic/tree/master/notebooks/examples) 
for more details.

<br><br>


# Features 

Key features of algoMosaic include:

- **Decentralized modeling.** In a single project, users can independently train, evaluate, 
and predict models stored in a central GCP Storage bucket. Users can access and store data 
in a central BigQuery database. 

- **Python process automation.** Users can add Python files to the src file and reference
them in Airflow DAGs. This is a great way to automate aspects of your analysis. 

- **ML tracking.** algoMosaic tracks and stores information through the entire machine 
learning lifecycle. Users can save models to storage and get them with a `model_id`.

###### _Note: some of this functionality has not been created yet._

<br><br>


# Playbooks

We have created a series of 
[Playbooks](https://github.com/gordonsilvera/algom-trading/tree/master/notebooks/playbooks)
that walk through how to complete each phase of the Lifecycle. Each step is parameterized, 
so it's easy to customize the workflow.

We have included the following Playbooks:

- `playbook_00_all_steps.ipynb` (WIP): end-to-end walk through of each step of the ML lifecyle
- `playbook_01_etl.ipynb`: run an ETL/ELT and feature generation process
- `playbook_02_train.ipynb`: train, evaludate, and store a model
- `playbook_03_predict.ipynb`: predict new data using a stored model
- `playbook_04_process.ipynb`: run any of these processes via a YAML configuration

<br>


# Examples 

What can you do with algoMosaic? Here are a couple sample projects. 

### Stock Prediction

We have used stock/cryptocurrency market prediction and trading as our preliminary use case. 
We have done this for the following reasons:

+ Training data are small, free, and easily accessible
+ Challenging and meritocratic use case (if you can succeed here, then you can anywhere)
+ Allows for easy scaling as we expand the framework. We can scale within a domain (by predicting multiple tickers) 
or across domains (by adding new asset classes or data sources).
+ Tests predictions as well as the actions that are taken from predictions.

<br>

### RSS Sentiment Analysis

We have used stock/cryptocurrency market prediction and trading as our preliminary use case. 

<br>


# Notes

+ In Development
+ Built with Python 3
+ Currently built for Scikit Learn and GCP
+ See [docs](https://github.com/gordonsilvera/algom-trading/tree/master/docs) for more details 

<br>

# To Do

This project is still in development. The 
[projects](https://github.com/orgs/algomosaic/projects/1) tab tracks the
planned updates. 

# FAQ

##### 1. What should I do if I receive the following error message when building the Docker image?
    
    Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
 
You must enable [Google Container Registry API](https://console.cloud.google.com/marketplace/product/google/containerregistry.googleapis.com).  

