from openai import OpenAI
import os
import zipfile

import requests
from DeepPurpose import DTI as models
from DeepPurpose.dataset import *
from DeepPurpose.utils import *
from utils import get_compound_name, get_target_name_from_uniprot

SAVE_PATH = "./saved_path"


client = OpenAI()
"""
Extracts drug names from the input text.

Parameters:
text (str): A string containing text from which drug names need to be extracted.
Returns:
A string containing the extracted drug names.
"""
def drug_names_extractor_agent(text):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are an assistant that extracts drug names from text."
              },
              {
                  "role": "user",
                  "content": f"Extract the drug names only, not the enzymes or proteins that the drugs bind to, from this text: {text}. Return just the drug names without appending any text"
              }
      ]

    )
  drug_names = response.choices[0].message.content
  return drug_names

"""
Extracts target protein names from the input text.

Parameters:
text: Input text containing potential target names.
Returns: A string of target names extracted from the text.
"""

def target_names_extractor_agent(text):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are an assistant that extracts targets that drugs bind to from text."
              },
              {
                  "role": "user",
                  "content": f"Extract the target names that drugs bind to from this text: {text}. Return just the target names without appending any text"
              }
      ]

    )
  target_names = response.choices[0].message.content
  return target_names
  
"""
Predicts DTI score between a single drug and a target.

Parameters:
drug: Drug name or SMILES string.
target: Target protein name.
is_smiles: If True, drug is treated as a SMILES string.
is_sequence: If True, target is treated as an amino acid sequence.
Returns: DTI score (float). Returns 0 if an error occurs.

"""

def prediction_agent(drug: str, target: str, is_smiles=False, is_sequence=False) -> float:
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    if not is_sequence:
        try:
            target_sequence = get_target_sequence(target)
        except ValueError:
            print(
                f"Logging: Returning 0 because target sequence for '{target}' was not found."
            )
            return 0

    else:
        target_sequence = target

    try:
        net = models.model_pretrained(model="MPNN_CNN_BindingDB")
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid zip file.")
        return 0

    #Use the broad data to get the drug SMILE 
    X_repurpose, drug_name, drug_cid = load_broad_repurposing_hub(SAVE_PATH)
    if is_smiles:
        idx = X_repurpose == drug
    else:
        idx = drug_name == drug
    if not any(idx):
        print(f"Logging: Returning 0 because drug '{drug}' was not found.")
        return 0
    print(f"\n The drug SMILE sequence is {X_repurpose[idx]}")
    res = models.virtual_screening(
        X_repurpose[idx], [target_sequence], net, drug_name[idx], [target]
    )
    return res[0]

"""
Fetches the amino acid sequence for a given target protein from UniProt API.

Parameters:
target: Target protein name.
Returns: Amino acid sequence (string) of the target protein.
Raises: RuntimeError if the API request fails.
"""
def get_target_sequence(target: str) -> str:
    print ("\n Getting the amino acod sequence of the target")
    base_url = "https://rest.uniprot.org/uniprotkb/search"

    params = {
        "query": f"gene:{target} AND organism_id:9606",
        "format": "json",
        "fields": "sequence",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data["results"]:
            raise ValueError(f"No sequence found for target '{target}'")

        sequence = data["results"][0]["sequence"]["value"]
        print(f"\n The amino acid sequence of the target is {sequence}")
        return sequence

    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

"""
Provides general medical information about given drugs.

Parameters:
drug_names: Comma-separated string of drug names.
Returns: Information on the medical usage of each drug.
"""
def medical_agent(drug_names):

  response = client.chat.completions.create(
      model="gpt-4-0613",
      messages=[
          {
                  "role": "system",
                  "content": "You are a medical doctor who provides explanation to how these drugs are used."
              },
              {
                  "role": "user",
                  "content": f"Tell me how these drugs are used and what they are important at: {drug_names}"
              }
      ]

    )
  return response.choices[0].message.content


def test(proposal):
    print ("Ok input received")
    return ("This should be the result")


def main():
  run_agent()


def run_agent():
  proposal = input("Tell me about your proposal:")
  # Call the agent to extract drug names
  drug_names = drug_names_extractor_agent(proposal)
  print("\n The drugs you are using in this proposal are: ")
  print (drug_names)
  # Call the agent to extract target names
  target_names = target_names_extractor_agent(proposal)
  print("\n The target proteins that the above drugs are binding to in this proposal are: ")
  print (target_names)
  #predict biding score between drug and target
  #multi_targets = target_names.split(",")
  #if len(multi_targets) > 1: #multiple targets detected 
  #  print("You entered more than one target")
    #multi_targets = target_names.split(",")
  #  result = get_multiple_dti_scores(drug_names, multi_targets)
  #else:
  result = prediction_agent(drug_names, target_names)
 
  medical = input(f"Would you like me to provide you medical information on your drug {drug_names}")
  if(medical == "yes"):
     advice = medical_agent(drug_names)
     print ("\n")
     print (advice)



if __name__ == "__main__":
  main()


  