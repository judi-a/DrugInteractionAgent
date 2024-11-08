##Overview

The main task of this AI agent is to facilitate the drug discovery process. Understanding how drug interacts with other proteins and molecules helps developing effective treatments for diseases while minimizing side effects. 

This script utilizes OpenAI's API to extract information from text, including drug and target names, and to predict drug-target interaction (DTI) scores using pretrained models from the DeepPurpose library. Additionally, it fetches amino acid sequences for target proteins and provides general medical information on drugs.

This agent asks the user to input a proposal of the experiment they are working on. 
1. The first step is that it calls two extractor agents; one to extract the drug name and the other to extract the protein name from the experiment proposal.
2. In order to predict interaction, one needs to get the 3D structure of the interacting molecules. For drugs, this is represented by the SMILE sequence. For protein, the amino acid sequence is used. Therefore, two other agents are called to extract the SMILE sequence and the amino acid sequences of both the drug and the protein.
3. Finally, the prediction agent loads a pretrained model, that was already trained on drug protein interaciton data in the other project (DrugInteraction). It then predicts the binding interatction between the given drug and target

4. There is also a medical agent that provides explanation on how the drugs are used

## Demo 
To see it working, you can go to Demo.ipynb and look at the results. 


# How to run the code
To make it work on your machine, you first need to download Docker and create an account on openAI and get your openAI key

This code is packaged into a Docker container. 
To run, download the docker image and run it using this command
clone the repo
build the docker image and run the container
docker build -t predictor-docker:latest .
docker run -it -p 9999:9999 predictor-docker

Inside the docker image, run the conda enviroment using 
conda activate python_env

then export your openAI API key using this command
export OPENAI_API_KEY=XXXXXXXXX

Your main entry point should be drug_extractor_agent.py. Inside it, the function agent_call() is responsible for managing the agents


##Dependencies
This code requires the following libraries:

openai for accessing OpenAI's API.
os for file and directory operations.
zipfile for handling zip file errors.
requests for making HTTP requests to the UniProt API.
DeepPurpose for DTI models, datasets, and utilities.
Custom utils functions, including get_compound_name and get_target_name_from_uniprot, assumed to be defined in utils.py.
Global Variables
SAVE_PATH: Directory path where pretrained model data will be saved. Defaults to "./saved_path".






## How to Use (Docker)
```sh
cd DrugPredictor
docker build -t predictor-docker:latest .
#if you want to make sure Docker is build fresh new no cache
docker build --no-cache  -t predictor-docker:latest .
docker run -it -p 9999:9999 predictor-docker
##this should start the web app

########### no need for this ######
conda activate python_env

sk-proj-XXXXXXXXXXXXX (USE YOUR API KEY)
```

# How to run the code

```sh
cd DrugPredictor
python drug_extractor_agent.py
   # DrugInteractionAgent


####Run with Docker and flask
docker build --no-cache  -t predictor-docker:latest . 
docker run -it -p 9999:9999 predictor-docker /bin/bash
conda activate python_env

python app.py

## Deploying on Heroku
 docker buildx build --provenance=false --platform linux/amd64 -t predictor-docker-linux:latest .
 docker tag predictor-docker-linux registry.heroku.com/drug-predictor1/web
 docker push registry.heroku.com/drug-predictor1/web 
 heroku container:release web -a drug-predictor1


 #to delete all docker containers and clear cache
 docker system prune --all
 