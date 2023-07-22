import os
import openai

os.environ["http_proxy"] = "http://127.0.0.1:1081"
os.environ["https_proxy"] = "https://127.0.0.1:1081"
openai.api_key = "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"

def chatGpt(prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=100
    )
    # print("comoletion:", completion)
    return completion.choices[0].message.content


if __name__ == "__main__":

        prompt = "一句话概括水的作用"
        print("My> ", prompt)
        chatResult = chatGpt(prompt)
        print("Ai> ",chatResult)
