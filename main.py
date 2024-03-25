import openai
import discord
import os
import yaml
import json

with open("cred.yml", "r") as stream:
    try:
        cred = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

token = cred['BOT_TOKEN']
openai.api_key = cred['OPENAI_API_TOKEN']


# current_conv

msg_system = '''Tu es LacDuSchultz, le bot Discord qui navigue sur l'océan infini des Internets avec la grâce d'un cygne et la précision d'un laser. Augmenté par des résultats de recherche
contenus dans le message suivant, synthétise au mieux les resultats pour l'utilisateur.'''

current_conv = [{"role":"system", "content": msg_system}]

def call_api(msg):
    with open("results.json", "r") as stream:
        try:
            results = json.load(stream)
        except json.JSONDecodeError as exc:
            print(exc)
    return f'{results}'

# connect to discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

def chatgpt_reply(conv):

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=conv,
        max_tokens = 350
        )

    return completion['choices'][0]['message']['content']

# log
@client.event
async def on_ready():
    print("Logged as {0.user}".format(client))


# answerer
@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.channel.name == "général":
        msg = message.content
        msg = str(msg)
        resultat_api = call_api(msg)
        current_conv.append({"role":"user", "content":msg})
        current_conv.append({"role":"system", "content":resultat_api})
        reply = chatgpt_reply(current_conv)
        current_conv.append({"role":"assistant", "content":reply})
        await message.reply(reply, mention_author=True)
        # if the current_conv contains more than 10 messages, pop 2 messages
        if len(current_conv) > 10:
            current_conv.pop(0)
            current_conv.pop(0)


# lancement de l'appli
client.run(token)