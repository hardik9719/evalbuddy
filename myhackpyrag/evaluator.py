# evaluator.py
import io
import os
import tempfile
import time
import zipfile
import shutil
import json
from urllib import request

import ollama
import pathspec


def extract_text_from_document(doc_file):
    """
    Extract text content from an uploaded document file
    """
    # Check file extension
    file_extension = os.path.splitext(doc_file.name)[1].lower()
    if file_extension != '.txt':
        raise ValueError("Only .txt files are supported")
    
    # Read the file content directly
    text = doc_file.read().decode('utf-8', errors='ignore')
    return text

def extract_and_summarize_code(source, is_github_link):
    start = time.perf_counter()
    temp_dir = tempfile.mkdtemp()  # Temporary directory for extracted files

    # Download and extract if it's a GitHub repository
    if is_github_link:
        # Convert GitHub URL to ZIP download URL
        repo_path = source.replace('https://github.com/', '').rstrip('.git')
        zip_url = f'https://github.com/{repo_path}/archive/refs/heads/master.zip'
        try:
            response = request.urlopen(zip_url)
            zip_data = io.BytesIO(response.read())
            with zipfile.ZipFile(zip_data) as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            print(f"Error downloading or extracting GitHub repo: {e}")
            shutil.rmtree(temp_dir)
            return None
    else:
        # Handle uploaded ZIP file directly
        with zipfile.ZipFile(source) as zip_ref:
            zip_ref.extractall(temp_dir)

    # Load .gitignore file if it exists
    gitignore_path = os.path.join(temp_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            gitignore_rules = gitignore_file.read().splitlines()
        gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_rules)
    else:
        gitignore_spec = None

    # Process the files and create summary
    all_code = ""

    for root, dirs, files in os.walk(temp_dir):
        print(files)
        for file in files:
            file_path = os.path.join(root, file)
            # Check if the file should be ignored
            relative_path = os.path.relpath(file_path, temp_dir)
            if gitignore_spec and gitignore_spec.match_file(relative_path):
                continue  # Skip ignored files

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    all_code += f"\n\n=== File: {file_path} ===\n"
                    all_code += file_content
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue

    # Clean up and return
    shutil.rmtree(temp_dir)
    end = time.perf_counter()
    print(f'Took {end-start:.3f} seconds')
    return summarize_code(all_code, "Complete Codebase")

def summarize_code(code, file_path):
    start = time.perf_counter()
    prompt = f"""
You are an expert code analyzer. Please analyze the following code file and provide both a detailed narrative summary and structured analysis.

File: {file_path}

Code:
{code}

Please provide your analysis in two parts:

Part 1: Narrative Summary
Provide a detailed paragraph explaining what this code does, its purpose, and how it works. Include any notable implementation details or interesting aspects of the code. This should be a well-written, technical explanation that a developer would find useful.

Part 2: Structured Analysis (in JSON format):
{{
    "summary": "Brief overview of what this code does",
    "main_functionality": [
        "List of main functions/features"
    ],
    "technologies": {{
        "languages": [],
        "frameworks": [],
        "libraries": [],
        "ai_components": []
    }},
    "code_patterns": [
        "List of notable design patterns or coding practices used"
    ],
    "complexity_analysis": {{
        "level": "low|medium|high",
        "explanation": "Brief explanation of complexity assessment"
    }},
    "potential_improvements": [
        "List of suggested improvements or optimizations"
    ]
}}

Start your response with the narrative summary, followed by a line containing only '---', and then the JSON analysis.
Ensure the JSON portion is valid JSON. Focus on technical accuracy and be specific about AI-related components if present.
"""
    response = get_llm_response(prompt, 'text')
    end = time.perf_counter()
    print(f' SUMMARIZE : Took {end-start:.3f} seconds')

    return f"\nSummary of {file_path}:\n{response}\n"

def evaluate_project(doc_text, code_summary):
    print('Inside eval')
    with open('metrics.json', 'r') as f:
        metrics_data = json.load(f)

    # Create a dynamic string for metrics
    metric_criteria = "\n".join(
        [f"{metric['title']}: {metric['description']}\n   Evaluation Factors: {', '.join(metric['evaluationFactors'])}"
         for metric in metrics_data['metrics']])

    # Create the expected output structure
    output_structure = {metric['title']: {"score": "<score>", "justification": "<justification>"} for metric in
                        metrics_data['metrics']}
    output_structure_str = json.dumps(output_structure, indent=2)

    prompt = f"""
    You are an expert code analyst and project evaluator. Your task is to evaluate the project based on specific criteria using the provided project description and code summary.

    Criteria:
    {metric_criteria}

    Project Description:
    {doc_text}

    Code Summary:
    {code_summary}

    Your evaluation should be in JSON format for all the metrics available in the criteria, with each metric having the following structure:
    {output_structure_str}

    Replace <score> with a number from 1 to 10, and <justification> with proper highly critique justification and reasoning for the evaluation.
    Don't give N/A as score make it 0 if not applicable
    Provide your evaluation in valid JSON format only, without any additional explanation.
    """

    # Here you would call your LLM (e.g., Ollama) with this prompt
    # For demonstration, I'll just return the prompt
    print('asking prompt')
    return get_llm_response(prompt, 'json')

def get_llm_response(prompt, response_type='text', model='llama3.2'):
    """
    Generic function to get responses from the LLM

    Args:
        prompt (str): The prompt to send to the model
        response_type (str): The type of response expected ('text', 'json', or 'list')
        model (str): The model to use (default: 'llama2')

    Returns:
        The processed response based on response_type
    """
    messages = [{'role': 'user', 'content': prompt}]
    response = ''

    # Get the raw response
    for chunk in ollama.chat(model=model, messages=messages, stream=True):
        if 'message' in chunk:
            response += chunk['message']['content']
    response = response.strip()
    print(response)
    # Process based on expected response type
    if response_type == 'json':
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Attempt to extract JSON from text
            start_index = response.find('{')
            end_index = response.rfind('}') + 1
            json_text = response[start_index:end_index]
            return json.loads(json_text)
    elif response_type == 'list':
        try:
            return eval(response)
        except:
            return ["Error: Invalid response format"]
    else:
        return response

def generate_evaluation_factors(title, description):
    prompt = f"""
Given this metric title and description for a project evaluation system, generate specific evaluation factors.
Each factor should be clear, measurable, and directly related to assessing this metric.

Title: {title}
Description: {description}

Generate a list of 5-8 evaluation factors that are:
1. Specific and measurable
2. Directly related to the metric
3. Clear and actionable

Format your response as a json object no extra text at the end , for example:
{{
        "title": title,
        "description": description,
        "weightage": 10,  # Default weightage
        "evaluationFactors": [
        "Addressing a clear market need or gap",
        "Potential target audience size and reach",
        "Unique selling proposition (USP) compared to existing solutions",
        "Revenue model or monetization strategy (if applicable)",
        "Feasibility of implementation in the real world",
        "Potential for attracting investors or stakeholders"
      ]
    }}
  

Ensure each factor is concise but descriptive enough to be useful for evaluation.
"""
    return get_llm_response(prompt, 'json')


# url  = "https://github.com/dougdragon/browser-info.git"
# url  = "https://github.com/jimmc414/code_lens_llm.git"
# # First get the code summary
# # with open('test_urls.py.zip', 'rb') as zip_file:
# code_summary = summarize_codebase(url,True)
# print(code_summary)
# # Then read the project description
# with open('project_description.txt', 'r', encoding='utf-8') as doc_file:
#     doc_text = doc_file.read()
#
# # # Now evaluate both together
# evaluation = evaluate_project(doc_text, code_summary)
# print(json.dumps(evaluation, indent=2))  # Pretty print the results
# if __name__ =='__main__':
#     print(generate_evaluation_factors('Design Patterns',' Best Desgin patterns'))
#     print(generate_evaluation_factors('10th Grade Project Exhibition',' Simple and easy to parse'))
#     print(generate_evaluation_factors('Senior solutions architect',' Scalable solution'))

#     print(generate_evaluation_factors('Art professional and Painter',' Ability to paint'))
# summarize_codebase("https://github.com/hardik9719/Djangodemo.git",True)
# summarize_codebase("https://github.com/hardik9719/Codeforces.git",True)
# extract_and_summarize_code("https://github.com/hardik9719/creator-verse.git",True)