import openai

# client = MistralClient(api_key=os.environ["MISTRAL_TOKEN"])

def chatgpt_reply(conv, model):
    completion = openai.ChatCompletion.create(
        model=model, messages=conv, temperature=0
    )
    return completion["choices"][0]["message"]["content"]

# def mistral_reply(conv, model, role):
#     messages = [
#         ChatMessage(role=role, content=str(conv)),
#     ]
#     chat_response = client.chat(
#         model=model,
#         messages=messages,
#         temperature= 0
#     )
#     return chat_response.choices[0].message.content
     

