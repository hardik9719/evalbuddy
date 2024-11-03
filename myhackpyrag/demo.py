import time
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import json
from evaluator import evaluate_project, extract_and_summarize_code, generate_evaluation_factors

# Page configuration
st.set_page_config(layout="wide", page_title="Project Evaluation Dashboard")

# Main title
st.title("🎯 MyEvalBuddy")

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
    if st.button("Extract and Summarize Code",key='dynamic'):
        start_time = time.time()
        code_summary = extract_and_summarize_code(github_link, True)
        end_time = time.time()
        st.info(f"Summary computation took {end_time - start_time:.3f} seconds")
        st.session_state.code_summary = code_summary
    
    # New section for Doc Text input and save button
    st.header('Doc Text')
    doc_text_input = st.text_area("Enter Document Text", value=st.session_state.doc_text)
    if st.button("Save Doc Text"):
        st.session_state.doc_text = doc_text_input  # Save to session state
        st.success("Document text saved successfully!")
    
    with st.container(border=True):
        st.header('Dashboard Summary')
        st.text(st.session_state.code_summary)
    
    
    # File upload section
    st.subheader("Upload Project Files")
    uploaded_zip = st.file_uploader("Upload Additional Zip", type=["zip"])
    if uploaded_zip:
        if st.button("Extract and Summarize ZIP"):
            start_time = time.time()
            code_summary = extract_and_summarize_code(uploaded_zip, False)
            end_time = time.time()
            st.text_area("Code Summary", code_summary)
            st.info(f"Summary computation took {end_time - start_time:.3f} seconds")
        st.subheader("Evaluate Project")
 


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
