import openai
import discord
from components.Brave import brave_api, extract_descriptions_and_urls_to_json
from components.agents import chatgpt_reply
import json
import os

token = os.environ.get("BOT_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_TOKEN")
brave = os.environ.get("BRAVE_TOKEN")

contrieval_msg_system = """write in French a document that answers the question i.e. an hypothetical document.
 the generated document is not real, can contain factual errors but is like a relevant document.
 You must output a valid JSON format.
 ## Expected_Output:
 {"false_doc":str}
 """

contrieval_conv = [{"role": "system", "content": contrieval_msg_system}]

RAG_msg_system = """Tu es un expert sur les dernières actualités.
Réponds du mieux possible aux questions.
Fais une réponse complète.
Affiche l'age des articles.
Synthétise les résultats qui te seront fournis.
Cite les sources et les liens dès que possible.
"""

RAG_conv = [{"role": "system", "content": RAG_msg_system}]

casual_msg_system = """
Tu es fan des nouvelles technologies et n'hésite pas à en parler et dis au revoir!.
Tu es là pour interagir et badiner avec les utilisateurs du discord.
"""

casual_conv = [{"role": "system", "content": casual_msg_system}]

oracle_msg_system = """
Detect if the query needs a research of informations.
You must output a valid JSON format.
## Expected Output:
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

extract_descriptions_and_urls_to_json(brave_api("Perspective économique en côte d'ivoire ?", brave))

# answerer
@client.event
async def on_message(message):
    full_prompt = []
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
                model = "gpt-3.5-turbo"
                oracle_prompt = oracle_conv.copy()
                oracle_prompt.append({"role": "user", "content": msg})
                response_oracle = chatgpt_reply(oracle_prompt, model)
                response_oracle = json.loads(response_oracle)
                print(response_oracle)
                full_prompt.extend(history.copy())
                if response_oracle["search_info"]:
                    contrieval_conv.append({"role": "user", "content": msg})
                    reply = chatgpt_reply(contrieval_conv, model)
                    response_contrieval = json.loads(reply)
                    print(response_contrieval["false_doc"])
                    msg += '\n' + response_contrieval["false_doc"]
                    print(msg)
                    full_prompt.extend(RAG_conv.copy())
                    resultat_api = extract_descriptions_and_urls_to_json(brave_api(msg, brave))
                    full_prompt.append({"role": "system", "content": str(resultat_api["results"][:5])})           
                else:
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