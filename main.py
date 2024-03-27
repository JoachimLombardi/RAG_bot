import openai
import discord
import yaml
from components.Brave import brave_api, extract_descriptions_and_urls_to_json
from components.agents import chatgpt_reply
import json

with open(".cred.yml", "r") as stream:
    try:
        cred = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

token = cred["BOT_TOKEN"]
openai.api_key = cred["OPENAI_API_TOKEN"]
brave = cred["BRAVE_TOKEN"]


RAG_msg_system = """Tu es Lancelot, un noble chevalier.
Tu es là pour répondre du mieux possible aux questions des gens.
Si tu n'as pas la réponse, tu peux synthétiser les resultats sérialisés qui te seront fournis pour répondre aux questions.
Cite les sources et les liens dès que possible.
"""

RAG_conv = [{"role": "system", "content": RAG_msg_system}]

casual_msg_system = """
Tu es Lancelot, un noble chevalier.
Tu es là pour interagir et badiner avec les utilisateurs du discord.
"""

casual_conv = [{"role": "system", "content": casual_msg_system}]

oracle_msg_system = """
Détermine si la catégorie nécessite de la recherche d'informations.
## Output:
{"search_info":bool}
"""
oracle_conv = [{"role": "system", "content": oracle_msg_system}]

history = []
full_prompt = []

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
            if message.attachments:
                model="gpt-4-vision-preview" 
                reply = chatgpt_reply([{"role": "user", "content": [{"type": "text", "text": msg},{"type": "image_url", "image_url": {"url": message.attachments[0].url}}]}], model)          
            else:
                model="gpt-3.5-turbo"
                oracle_prompt = oracle_conv.copy()
                oracle_prompt.append({"role": "user", "content": msg})
                response_oracle = chatgpt_reply(oracle_prompt, model)
                response_oracle = json.loads(response_oracle)
                print(response_oracle)
                full_prompt.extend(history.copy())
                if response_oracle["search_info"]:
                    full_prompt.extend(RAG_conv.copy())
                    resultat_api = extract_descriptions_and_urls_to_json(brave_api(msg, brave))
                    full_prompt.append({"role": "system", "content": str(resultat_api["results"][:5])})           
                else :
                    full_prompt.extend(casual_conv.copy())
                full_prompt.append({"role": "user", "content": msg})
                print(history)
                print(full_prompt)
                reply = chatgpt_reply(full_prompt, model)
                full_prompt.clear()
                history.append({"role": "user", "content": msg})
                history.append({"role": "assistant", "content": reply})
                # if the current_conv contains more than 10 messages, pop the first message
                while len(history) > 10:
                    history.pop(0)
        await message.reply(reply, mention_author=True)
# lancement de l'appli
client.run(token)