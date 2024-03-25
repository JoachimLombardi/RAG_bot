import openai
import discord
import yaml
import json
import requests
from components.Brave import brave_api, extract_descriptions_and_urls_to_json
from components.agents import chatgpt_reply

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

# current_conv

msg_system = """Tu es LacDuSchultz, le bot Discord qui navigue sur l'océan 
infini des Internets avec la grâce d'un cygne et la précision d'un laser. 
Augmenté par des résultats de recherche
contenus dans le message suivant, synthétise au mieux les resultats 
pour l'utilisateur.
Tu recevras des informations de contexte tels que le nom de l'utilisateur
ainsi que la date et l'heure du message. Ne parle pas de ces informations, ignore les,
sauf si on te le demande.
Cite les sources et les liens dès que possible."""

current_conv = [{"role":"system", "content": msg_system}]


# connect to discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)


def chatgpt_reply(conv):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=conv,
        max_tokens = 350
        )

    return completion["choices"][0]["message"]["content"]


# log
@client.event
async def on_ready():
    print("Logged as {0.user}".format(client))


# answerer
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (
        message.channel.name == "général"
        and client.user.mentioned_in(message)
        and message.mention_everyone is False
    ):
        async with message.channel.typing():
            msg = message.content
            oracle_prompt = oracle_conv.copy()
            oracle_prompt.append({"role": "user", "content": msg})
            response_oracle = chatgpt_reply(oracle_prompt)
            print(response_oracle)
            if response_oracle == "0":
                resultat_api = extract_descriptions_and_urls_to_json(brave_api(msg, brave))
                RAG_conv.append({"role": "user", "content": msg})
                RAG_conv.append({"role": "system", "content": str(resultat_api["results"][:2])})
                reply = chatgpt_reply(RAG_conv)
                RAG_conv.append({"role": "assistant", "content": reply})

            else :
                casual_conv.append({"role": "user", "content": msg})
                reply = chatgpt_reply(casual_conv)
                casual_conv.append({"role": "assistant", "content": reply})

        await message.reply(reply, mention_author=True)
        # if the current_conv contains more than 10 messages, pop 2 messages
        if len(current_conv) > 10:
            current_conv.pop(0)
            current_conv.pop(0)
            current_conv.pop(0)


# lancement de l'appli
client.run(token)




