# evaluator.py

import os
import tempfile
import zipfile
import shutil
import json
import ollama

def extract_text_from_document(doc_file):
    # Read the uploaded document file
    file_extension = os.path.splitext(doc_file.name)[1].lower()
    if file_extension != '.txt':
        raise ValueError("Only .txt files are supported")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(doc_file.read())
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    os.unlink(tmp_file_path)  # Delete the temporary file
    return text

def summarize_codebase(zip_file):
    # Extract code files from the zip
    temp_dir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        tmp_zip.write(zip_file.read())
        tmp_zip_path = tmp_zip.name

    with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Read all files and combine their contents
    all_code = ""
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    all_code += f"\n\n=== File: {file_path} ===\n"
                    all_code += file_content
            except Exception as e:
                continue  # Skip files that can't be read

    # Get one comprehensive summary for all files
    code_summary = summarize_code(all_code, "Complete Codebase")

    # Clean up temp files
    os.unlink(tmp_zip_path)
    shutil.rmtree(temp_dir)
    
    return code_summary

def summarize_code(code, file_path):
    prompt = f"""
You are an AI assistant helping to summarize code files for a project evaluation. Analyze the following code file and identify any AI models, libraries, and technologies used. Provide insights on the sophistication of AI models and any innovative coding practices.

File Path: {file_path}

Code:
{code}

Provide a brief summary:
"""
    response = ollama_chat(prompt)
    return f"\nSummary of {file_path}:\n{response}\n"

def evaluate_project(doc_text, code_summary):
    prompt = f"""
You are an expert project evaluator assessing submissions based on specific criteria. Using the project description and code summary provided, evaluate the project on the following criteria. Provide a score from 1 to 10 for each criterion and justify your scoring.

Criteria:
1. Market Potential and Business Viability
2. AI Integration and Innovation
3. Creativity Level

Project Description:
{doc_text}

Code Summary:
{code_summary}

Your evaluation should be in JSON format like this:
{{
    "Market Potential and Business Viability": {{
        "score": <score>,
        "justification": "<justification>"
    }},
    "AI Integration and Innovation": {{
        "score": <score>,
        "justification": "<justification>"
    }},
    "Creativity Level": {{
        "score": <score>,
        "justification": "<justification>"
    }}
}}

Provide only the JSON response.
"""
    response = ollama_chat(prompt)
    # Attempt to parse the JSON response
    try:
        evaluation = json.loads(response)
    except json.JSONDecodeError:
        # If JSON parsing fails, attempt to extract JSON from text
        start_index = response.find('{')
        end_index = response.rfind('}') + 1
        json_text = response[start_index:end_index]
        evaluation = json.loads(json_text)
    return evaluation

def ollama_chat(prompt, model='llama2'):
    messages = [{'role': 'user', 'content': prompt}]
    response = ''
    for chunk in ollama.chat(model=model, messages=messages, stream=True):
        if 'message' in chunk:
            response += chunk['message']['content']
    return response.strip()

# First get the code summary
with open('test_urls.py.zip', 'rb') as zip_file:
    code_summary = summarize_codebase(zip_file)

# Then read the project description
with open('project_description.txt', 'r', encoding='utf-8') as doc_file:
    doc_text = doc_file.read()

# Now evaluate both together
evaluation = evaluate_project(doc_text, code_summary)
print(json.dumps(evaluation, indent=2))  # Pretty print the results
