import openai


def chatgpt_reply(conv):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=conv, temperature=0.7
    )

    return completion["choices"][0]["message"]["content"]