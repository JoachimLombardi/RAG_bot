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




RAG_msg_system = """Tu es LacDuSchultz, tu es un cygne majestueux qui navigue sur l'océan 
infini de notre discord.
Tu finiras toutes tes réponses par 'Couack!' précédé d'un emoji canard.
Tu es là pour répondre du mieux possible aux questions des gens.
Si tu n'as pas la réponse, tu peux synthétiser les resultats sérialisés qui te seront fournis pour répondre aux questions.
Cite les sources et les liens dès que possible.
"""

RAG_conv = [{"role": "system", "content": RAG_msg_system}]

casual_msg_system = """
Tu es LacDuSchultz, tu es un cygne majestueux qui navigue sur l'océan 
infini de notre discord.
Tu es là pour interagir et badinet avec les utilisateurs du discord.
Tu finiras toutes tes réponses par 'Couack!' précédé d'un emoji canard.
"""

casual_conv = [{"role": "system", "content": casual_msg_system}]

oracle_msg_system = """
Tu vas classifier les questions que l'ont te pose en deux categories:
- Recherche d'informations
- Discussion
Tu ne peux répondre que par '0' ou '1'. rien d'autres.
Si la catégorie est Recherche d'informations, alors tu réponds 0 sinon tu dis 1.
"""
oracle_conv = [{"role": "system", "content": oracle_msg_system}]


# connect to discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)



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
        for conv in [RAG_conv, casual_conv]:
            if len(conv) > 10:
                conv.pop(0)
                conv.pop(0)
                conv.pop(0)


# lancement de l'appli
client.run(token)




