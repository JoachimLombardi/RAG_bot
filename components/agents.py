import openai

def chatgpt_reply(conv, model):
    completion = openai.ChatCompletion.create(
        model=model, messages=conv, temperature=0.1
    )
    return completion["choices"][0]["message"]["content"]


