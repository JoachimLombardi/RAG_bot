from langchain_community.document_loaders import BraveSearchLoader
import yaml

with open(".cred.yml", "r") as stream:
    try:
        cred = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

brave = cred["BRAVE_TOKEN"]

def brave_api(msg):
    loader = BraveSearchLoader(
        query=msg, api_key=brave, search_kwargs={"count": 3}
    )
    docs = loader.load()
    return docs

response = brave_api("Qui est macron ?")

print(response)
