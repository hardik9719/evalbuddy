import streamlit as st
import pandas as pd
import plotly.express as px
import random
from PIL import Image

# Page configuration
st.set_page_config(layout="wide", page_title="Project Evaluation Dashboard")

# Main title
st.title("🎯 Project Evaluation Dashboard")

metrics = []
# Function to simulate getting evaluation factors from a language model
def get_evaluation_factors(title, description):
    # This is a placeholder for the actual call to a language model
    # Replace this with the actual API call to get evaluation factors
    prompt = f"Title: {title}\nDescription: {description}\nProvide key evaluation factors:"
    # Simulate response
    return ["Factor 1", "Factor 2", "Factor 3"]

# Add a form to accept metric title and description
st.subheader("Add New Metric")
with st.form("metric_form"):
    metric_title = st.text_input("Metric Title")
    metric_description = st.text_area("Metric Description")
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Get evaluation factors using the language model
        evaluation_factors = get_evaluation_factors(metric_title, metric_description)
        
        # Create a new metric entry
        new_metric = {
            "id": len(metrics) + 1,  # Assuming 'metrics' is a list of existing metrics
            "title": metric_title,
            "description": metric_description,
            "weightage": 0,  # Default weightage, can be adjusted later
            "evaluationFactors": evaluation_factors
        }
        
        # Display the new metric
        st.json(new_metric)
        st.success("New metric added successfully!")

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
    def radar_chart(val=7):  
        df = pd.DataFrame(dict(
            r=[random.randint(0,val) for _ in range(5)],
            theta=['AI Integration', 'Technical Innovation', 'Problem Solving',
                  'Market Potential', 'Scalability']))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False
        )
        st.plotly_chart(fig)

    radar_chart()
    
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
