import streamlit as st
import pandas as pd
import plotly.express as px
import random
import json
from evaluator import generate_evaluation_factors

# Page configuration
st.set_page_config(layout="wide", page_title="Project Evaluation Dashboard")

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
st.subheader("Add New Metric")


def render_radar_chart():
    with open('metrics.json', 'r') as f:
        data = json.load(f)
        metrics = data.get('metrics', [])

    df = pd.DataFrame(dict(
        r=[random.randint(0, 10) for _ in range(len(metrics))],
        theta=[metric['title'] for metric in metrics]
    ))

    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False
    )
    return fig
chart_placeholder = st.empty()

# Initial render of the chart
chart_placeholder.plotly_chart(render_radar_chart())
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
        chart_placeholder.plotly_chart(render_radar_chart())

# Create columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Domain Selection")
    domains = ["Health", "Education", "Finance", "Environment", "Technology"]
    selected_domain = st.selectbox("Select Project Domain", domains)
    
    st.subheader("Project Details")
    project_name = st.text_input("Project Name")
    project_description = st.text_area("Project Description")
    
    # File upload section
    st.subheader("Upload Project Files")
    uploaded_slides = st.file_uploader("Upload Presentation Slides", type=["pdf", "ppt", "pptx"])
    uploaded_docs = st.file_uploader("Upload Additional Documents", type=["pdf", "doc", "docx"])
    github_link = st.text_input("GitHub Repository Link")

with col2:
    st.subheader("Evaluation Metrics")
    
    # AI Usage Metric
    st.markdown("### AI Integration Score")
    ai_score = random.randint(60, 95)
    st.progress(ai_score/100)
    st.caption(f"AI Usage Score: {ai_score}%")
    
    # Creativity Level
    st.markdown("### Innovation Metrics")






    
    # Impact Assessment
    st.markdown("### Impact Assessment")
    impact_metrics = {
        "Social Impact": random.randint(1, 10),
        "Technical Achievement": random.randint(1, 10),
        "Market Potential": random.randint(1, 10)
    }
    
    for metric, value in impact_metrics.items():
        st.metric(metric, f"{value}/10")

# Action buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Evaluate Project"):
        st.success("Project evaluation completed!")
with col2:
    if st.button("Generate Report"):
        st.info("Generating comprehensive report...")
with col3:
    if st.button("Save Results"):
        st.info("Saving evaluation results...")

# Footer
st.markdown("---")
st.caption("Project Evaluation Dashboard v1.0")
