import openai
import discord
import yaml
import json
from langchain_community.document_loaders import BraveSearchLoader
import requests


with open(".cred.yml", "r") as stream:
    try:
        cred = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

token = cred["BOT_TOKEN"]
openai.api_key = cred["OPENAI_API_TOKEN"]
brave = cred["BRAVE_TOKEN"]


def brave_api(msg, brave):
    url = "https://api.search.brave.com/res/v1/web/search"

    querystring = {"q": msg}

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave
    }
    response = requests.get(url, headers=headers, params=querystring)
    json.dump(response.json(), open("results.json", "w"))
    return response.json()


def extract_descriptions_and_urls_to_json(json_data):
    results = json_data.get('web', {}).get('results', [])

    output_data = {'results': []}
    for result in results:
        description = result.get('description')
        url = result.get('url')
        output_data['results'].append({'description': description, 'url': url})
    return output_data

print(extract_descriptions_and_urls_to_json(brave_api("Qui est macron ?", brave)))