import openai
import discord
from dotenv import load_dotenv
import os
import re

load_dotenv()
token = os.getenv("TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")


# current_conv

msg_system = "Tu es un agent intelligent. Ton objectif est d'aider l'utilisateur à apprendre des notions complexes en intelligence artificielle."

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
        current_conv.append({"role":"user", "content":msg})
        reply = chatgpt_reply(current_conv)
        current_conv.append({"role":"assistant", "content":reply})
        await message.reply(reply, mention_author=True)

# lancement de l'appli
client.run(token)