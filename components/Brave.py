import requests
import json
from Soup import get_paragraphs_from_url

def brave_api(msg, brave):
    url = "https://api.search.brave.com/res/v1/news/search"

    params = {"q": msg, "freshness":"pm", "country":"FR"}

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave,
    }
    response = requests.get(url, headers=headers, params=params)
    json.dump(response.json(), open("results.json", "w"))
    return response.json()

def extract_descriptions_and_urls_to_json(json_data):
    sorted_data = {}
    results = json_data.get("results", [])
    output_data = {"results": []}
    for result in results[:3]:
        description = result.get("description")
        page_age = result.get("page_age")
        url = result.get("url")
        paragraphs = get_paragraphs_from_url(url)
        output_data["results"].append({"description": description, "url": url, "paragraphs": paragraphs, "page_age": page_age})
        sorted_data = sorted(output_data["results"], key=lambda x: x["page_age"])
    return output_data