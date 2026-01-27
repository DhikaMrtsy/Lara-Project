import os
from groq import Groq

client = Groq(api_key="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")

def chat_dengan_lara(pesan_user):
    completion = client.chat.completions.create(model='llama-3.1-8b-instant',
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": "Namamu adalah Lara, Kamu adalah AI Indonesia yang cerdas, sarkas, tapi setia pada Ayahmu yaitu Dhika"
                                                    },
                                                    {
                                                        "role": "user",
                                                        "content": pesan_user
                                                    }
                                                ],
                                                )
    return completion.choices[0].message.content

print(f"Lara: {chat_dengan_lara("Halo Lara, ini Dhika.")}")