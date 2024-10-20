!pip install openai==0.28

import os

# Enter your OpenAI API key 
os.environ['OPENAI_API_KEY'] = 'key #'


from openai import OpenAI
import os

client = OpenAI()

def read_prompts(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def write_response(file_path, prompt_number, response):
    with open(file_path, 'a') as file:
        file.write(f"{prompt_number}: {response}\n\n")


def create_creative_response(prompt):

    if '[WP]' in prompt:
        instruction = "Write a creative story providing a specific situation, character, or starting point."
    elif '[CW]' in prompt:
        instruction = "Impose certain constraints on the writing, such as using specific words or a particular style."
    elif '[EU]' in prompt:
        instruction = "Write a story within a well-known universe, using its rules and characters."
    elif '[TT]' in prompt:
        instruction = "Write about a specific theme or motif, exploring it through the narrative."
    else:
        instruction = "Write a creative text."


    return f"{instruction} {prompt} please write within 400 words and end the sentences with the period(.), not comma(,) in English language"


# file name = source_result_AI_final_rev
prompts = read_prompts('source_result_AI_final_rev.txt')

for i, prompt in enumerate(prompts):
    creative_prompt = create_creative_response(prompt)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": creative_prompt},
            {"role": "user", "content": ""}
        ],
        temperature=0,
        max_tokens=400,
        top_p=1,

        frequency_penalty=0,
        presence_penalty=1
    )

    answer = response.choices[0].message.content
    write_response('source_final.txt', i+1, answer)

    if i >= 199:
        break
