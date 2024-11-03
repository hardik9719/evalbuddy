# evaluator.py

import os
import tempfile
import zipfile
import shutil
import json
import ollama

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

def summarize_codebase(source, is_github_link=False):
    temp_dir = tempfile.mkdtemp()  # Still need this for extracted files
    
    if is_github_link:
        from urllib import request
        import io
        
        # Convert GitHub URL to ZIP download URL
        if 'github.com' in source:
            repo_path = source.replace('https://github.com/', '').rstrip('.git')
        else:
            repo_path = source
            
        # Try 'main' branch first, then 'master' if that fails
        branches = ['main', 'master']
        success = False
        
        for branch in branches:
            zip_url = f'https://github.com/{repo_path}/archive/refs/heads/{branch}.zip'
            try:
                response = request.urlopen(zip_url)
                zip_data = io.BytesIO(response.read())
                with zipfile.ZipFile(zip_data) as zip_ref:
                    zip_ref.extractall(temp_dir)
                success = True
                break
            except Exception:
                continue
                
        if not success:
            raise ValueError("Failed to download GitHub repository: Neither 'main' nor 'master' branch found")
            
    else:
        # Handle uploaded ZIP file directly
        with zipfile.ZipFile(source) as zip_ref:
            zip_ref.extractall(temp_dir)

    # Process the files and create summary
    all_code = ""
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    all_code += f"\n\n=== File: {file_path} ===\n"
                    all_code += file_content
            except Exception:
                continue

    # Clean up and return
    shutil.rmtree(temp_dir)
    return summarize_code(all_code, "Complete Codebase")

def summarize_code(code, file_path):
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
    return f"\nSummary of {file_path}:\n{response}\n"

def evaluate_project(doc_text, code_summary):
    prompt = f"""
You are an expert code analyst and project evaluator. Your task is to summarize the contents of a zip file containing multiple code files, and then evaluate the project based on specific criteria.



Part 1: Project Evaluation
Using the project description and code summary, evaluate the project on the following criteria. Provide a score from 1 to 10 for each criterion and justify your scoring.

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

Please analyze the contents of the zip file, provide the requested information for both parts, and evaluate the project. Your response should be in valid JSON format only, without any additional explanation.

"""
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

# # # Now evaluate both together
# evaluation = evaluate_project(doc_text, code_summary)
# print(json.dumps(evaluation, indent=2))  # Pretty print the results
if __name__ =='__main__':
    print(generate_evaluation_factors('Design Patterns',' Best Desgin patterns'))