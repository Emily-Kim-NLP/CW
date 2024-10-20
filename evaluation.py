!pip install openai

import os

# Enter your OpenAI API's key
os.environ['OPENAI_API_KEY'] = 'your API's key #'

from docx import Document
import pandas as pd
from openai import OpenAI
import re

def extract_text_from_docx(file_path):
  
    doc = Document(file_path)
    # Dictionary to store sections with their section titles as keys
    sections = {}
    # Variable to store the current section title
    current_section_title = None

    # Regular expression pattern for finding section titles (number followed by a colon)
    section_pattern = re.compile(r'(\d+):')

    # Iterate over each paragraph in the document
    for para in doc.paragraphs:
        # Use regex to check if the paragraph starts with a section title
        match = section_pattern.match(para.text.strip())
        if match:
            # Extract the section title
            current_section_title = match.group()
            # Initialize the section text with the paragraph text (excluding the section title part)
            sections[current_section_title] = para.text[len(current_section_title):].strip()
        elif current_section_title:
            # If we are inside a section, append paragraph text to the current section text
            sections[current_section_title] += "\n" + para.text.strip()

    # Return the dictionary of sections
    return sections

def generate_evaluation_prompts(text):
    prompts = f"""
    You are required to evaluate the crative writings as a Grant Writer.
    The goal of your code is to assess the quality of creativity in human and ChatGPT writings, "
                        "assigning a score of 1, 2, or 3 based on specific standards for each category. The criteria are:\n"
                        "Fluency: The ability to generate multiple ideas. Scoring is based on the range of ideas considered.\n"
                        "Flexibility: The ability to consider different types of ideas. Scoring is based on the diversity of ideas.\n"
                        "Originality: The uniqueness of the idea. Scoring is based on how unique or novel the idea is.\n"
                        "Elaboration: The level of detail and development in the idea. Scoring is based on the depth of detail and development.\n"
                        "Usefulness: The practicality and applicability of the idea. Scoring is based on how well the idea meets and adds value to the end-user's needs.\n"
                        "Specific creativity strategy: The effective selection and application of a creative thinking strategy. Scoring is based on the deliberate and effective use of a strategy to support creativity.\n"
                        "Scores for each category:\n"
                        "1 (Novice): The lowest level of achievement in the given criteria.\n"
                        "2 (Developing): An intermediate level of achievement, showing improvement over novice.\n"
                        "3 (Expert): The highest level of achievement, indicating advanced proficiency.\n"
                        "You should score only by numbers not with explanations.
                        Make the results appear like this example in order :
                        Evaluating:
                        Fluency: 2
                        Flexibility: 2
                        Originality: 2
                        Elaboration: 3
                        Usefulness: 2
                        Specific creativity strategy: 2
                        {text}"""
    return prompts

def manual_evaluation(prompts):
    scores = {}
    # for key, prompt in prompts.items():
    client = OpenAI()
    response = client.chat.completions.create(
    model="gpt-4o",  # You can change the model
    # GPT-3.5 Turbo 
    messages=[
        {
          "role": "system",
          "content": prompts,
        },
      ],
      temperature=0,
      max_tokens=1000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=1
    )
    answer = response.choices[0].message.content
    # print(f"prompt {prompts}")
    print(f"answer {answer}")
    print()
  
    score_pattern = re.compile(r"(\w+):\s(\d)")
    matches = score_pattern.findall(answer)
    
    for category, score in matches:
        scores[category] = int(score)
    return scores

# def save_evaluation_to_excel(evaluations, file_name="evaluation_results.xlsx"):

#     df = pd.DataFrame(evaluations).T
#     df.columns = ['Fluency', 'Flexibility', 'Originality', 'Elaboration', 'Usefulness', 'Specific creativity strategy']
#     df.to_excel(file_name)
#     print(f"Saved evaluation results to {file_name}")

def save_evaluation_to_excel(evaluations, file_name="GPTo_Human_results_Grant Writer.xlsx"):
#different names of file depending on temperature settings and persona settings    
    df = pd.DataFrame(evaluations)
    df.columns = ['Fluency', 'Flexibility', 'Originality', 'Elaboration', 'Usefulness', 'Specific creativity strategy']
   
    df.index += 1  # set-up with beginning index1 
    df.to_excel(file_name, index_label='Evaluation Number')
    print(f"Saved evaluation results to {file_name}")


file_paths = {
    "Human": "source_result_Human_final_rev.docx",
    # "AI": "source_result_AI_final_rev.docx"
  }


evaluations = {}

evaluation_list = []

for label, file_path in file_paths.items():
    text = extract_text_from_docx(file_path)
    index = 1
    max_index = 220  # 최대 인덱스 설정
    while index <= max_index:
        key = f"{index}:"
        if key in text:
            value = text[key]
            print(f"Key: {key}, Value: {value}")
            prompt = generate_evaluation_prompts(value)
            print(f"Evaluating: {label}")
            scores = manual_evaluation(prompt)
            evaluation_list.append(list(scores.values()))
            print(scores.values())
        else:
            evaluation_list.append([0, 0, 0, 0, 0, 0])
        index += 1
# saving the file
save_evaluation_to_excel(evaluation_list)
