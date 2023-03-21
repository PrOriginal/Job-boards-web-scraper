import openai

openai.api_key = "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"
model_engine = "gpt-3.5-turbo"

response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role":"user",
        "content":'Motivate me please'
        }
    ]
)
message = response.choices[0].message
print("{}: {}".format(message['role'], message['content']))