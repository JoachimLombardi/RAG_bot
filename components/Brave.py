import requests
import json


def brave_api(msg, brave):
    url = "https://api.search.brave.com/res/v1/web/search"

    querystring = {"q": msg}

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave,
    }
    response = requests.get(url, headers=headers, params=querystring)
    json.dump(response.json(), open("results.json", "w"))
    return response.json()

def extract_descriptions_and_urls_to_json(json_data):
    results = json_data.get("web", {}).get("results", [])

    output_data = {"results": []}
    for result in results:
        description = result.get("description")
        url = result.get("url")
        output_data["results"].append({"description": description, "url": url})
    return output_data