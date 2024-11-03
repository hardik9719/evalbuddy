import time
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import json
from evaluator import evaluate_project, extract_and_summarize_code, generate_evaluation_factors

# Page configuration
st.set_page_config(layout="wide", page_title="Project Evaluation Dashboard")
static_summary = f"""
Summary of Complete Codebase:
**Narrative Summary**

This code implements a classic game of Minesweeper in C++. The program displays an 8x8 grid, with some cells containing hidden mines. The player's objective is to reveal all non-mine cells without detonating any mine. The game uses a simple text-based interface, where the player can navigate the grid using keyboard inputs (W, A, S, D keys) and make selections by clicking on cells.

The code uses object-oriented programming (OOP) principles to encapsulate the game's logic and data structures. It defines a `Grid` class that represents the 8x8 grid, with methods for initializing the grid, counting bomb locations, and displaying the current state of the grid. The game loop continuously updates the display and checks for user input until the game is over.

The code also implements some interesting aspects, such as using a `cursor_i` and `cursor_j` pair to keep track of the player's position on the grid. When the player clicks on a cell, the program checks if it contains a mine or not, and updates the grid accordingly. The game ends when all non-mine cells are revealed or when the player detonates a mine.

**---**

```json
{{
    "summary": "Minesweeper game implemented in C++",
    "main_functionality": [
        "Game loop to update display and check user input"
        "Initialization of 8x8 grid with mines and bomb locations"
        "Reveal non-mine cells without detonating mines"
        "Detect game over conditions (e.g., revealing all non-mine cells or detonating a mine)"
    ],
    "technologies": {{
        "languages": ["C++"],
        "frameworks": [],
        "libraries": [
            {{
                "name": "CG ALIB",
                "description": "C graphics library"
            }}
        ],
        "ai_components": []
    }},
    "code_patterns": [
        "Object-Oriented Programming (OOP)"
        "Event-driven programming using keyboard and mouse inputs"
        "Game loop with continuous updating of display and checking user input"
    ],
    "complexity_analysis": {{
        "level": "low",
        "explanation": "Simple game logic with minimal complexity"
    }},
    "potential_improvements": [
        "Optimization for performance on lower-end hardware"
        "Add additional game features (e.g., multiple levels, power-ups)"
        "Improve user interface for better accessibility and usability"
    ]
}}
```
Note that I did not include any AI-related components in the analysis, as none were present in the provided code. If you'd like to add an AI component to the Minesweeper game, it would require a significant overhaul of the existing codebase.
"""

# Main title
st.title("🎯 Project Evaluation Dashboard")

metrics = []
# Function to simulate getting evaluation factors from a language model
def get_evaluation_factors(title, description):
    # Get factors from the LLM
    new_metric = generate_evaluation_factors(title, description)
    
    # Read existing metrics
    try:
        with open('metrics.json', 'r') as f:
            data = json.load(f)
            metrics = data.get('metrics', [])
    except FileNotFoundError:
        metrics = []
    # Add to metrics list and save
    print(new_metric)
    metrics.append(new_metric)
    with open('metrics.json', 'w') as f:
        json.dump({"metrics": metrics}, f, indent=2)
    return new_metric

# Add a form to accept metric title and description
st.subheader("Project Metric")


def render_radar_chart():
    with open('metrics.json', 'r') as f:
        data = json.load(f)
        metrics = data.get('metrics', [])
    # Create a DataFrame from the JSON data
    if result:
        df = pd.DataFrame.from_dict(
            {metric: details['score'] for metric, details in result.items()},
            orient='index',
            columns=['Score']
        ).reset_index().rename(columns={'index': 'Metric'})


    fig = px.line_polar(df, r='Score', theta='Metric', line_close=True)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False
    )
    return fig

# Initial render of the chart
with st.form("metric_form"):
    metric_title = st.text_input("Metric Title")
    metric_description = st.text_area("Metric Description")
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Get evaluation factors using the language model
        evaluation_factors = get_evaluation_factors(metric_title, metric_description)
        
        # Create a new metric entry
        new_metric = {
            "title": metric_title,
            "description": metric_description,
            "weightage": 100,  # Default weightage, can be adjusted later
            "evaluationFactors": evaluation_factors
        }
        
        # Display the new metric
        st.json(new_metric)
        st.success("New metric added successfully!")
        # Re-render the radar chart

# Create columns for layout
col1, col2 = st.columns([1, 2])
if 'code_summary' not in st.session_state:
    st.session_state.code_summary = "None"
if 'doc_text' not in st.session_state:
    st.session_state.doc_text = "Nothing much"
if 'code_insight' not in st.session_state:
    st.session_state.insight = "Nothing much"
with col1:
    
    st.subheader("Project Details")
    github_link = st.text_input("GitHub File Link")
    if st.button('Static Summary Load',key='static'):
        st.session_state.code_summary = static_summary
    if st.button("Extract and Summarize Code",key='dynamic'):
        start_time = time.time()
        code_summary = extract_and_summarize_code(github_link, True)
        end_time = time.time()
        st.info(f"Summary computation took {end_time - start_time:.3f} seconds")
        st.session_state.code_summary = code_summary
    with st.container(border=True):
        st.header('Doc Text')
        st.text(st.session_state.doc_text)
    with st.container(border=True):
        st.header('Dashboard Summary')
        st.text(st.session_state.code_summary)
    
    
    # File upload section
    st.subheader("Upload Project Files")
    uploaded_slides = st.file_uploader("Upload Presentation Slides", type=["pdf", "ppt", "pptx"])
    uploaded_docs = st.file_uploader("Upload Additional Documents", type=["pdf", "doc", "docx"])
    uploaded_zip = st.file_uploader("Upload Additional Zip", type=["zip"])
    if uploaded_zip:
        if st.button("Extract and Summarize ZIP"):
            start_time = time.time()
            code_summary = extract_and_summarize_code(uploaded_zip, False)
            end_time = time.time()
            st.text_area("Code Summary", code_summary)
            st.info(f"Summary computation took {end_time - start_time:.3f} seconds")
        st.subheader("Evaluate Project")
    st.text(st.session_state.code_summary)
 


with col2:
    st.subheader("Evaluation Metrics")
    chart_placeholder = st.empty()
 






    
    # Impact Assessment

    if st.button('Feedback'):
        start_time = time.time()
        st.info('Evaluation in progress...')
        try:
            with open('static_insight.json', 'r') as f:
                result = json.load(f)
                st.session_state.code_insight = result  # Load the JSON data into the result variable
        except FileNotFoundError:
            st.error("Error: static_insight.json file not found.")
            result = {}  
        result = evaluate_project(st.session_state.doc_text, st.session_state.code_summary)
        end_time = time.time()
        st.info(f"Evaluation computation took {end_time - start_time:.3f} seconds")
        
        # New section to display evaluation results as cards
        with st.container(border=True):
            st.header('Insight')
            for metric, details in result.items():
                score = details['score']
                justification = details['justification']
                # Create a card for each metric
                st.markdown(f"### {metric}")
                st.metric(label="Score", value=f"{score}/10")
                st.write(f"**Justification:** {justification}")
                st.markdown("---")  # Separator for cards
        
        chart_placeholder.plotly_chart(render_radar_chart())


# Footer
st.markdown("---")
st.caption("Project Evaluation Dashboard v1.0")
