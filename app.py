import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FairSight AI", page_icon="⚖️", layout="wide")

# Modern clean design implemented via CSS 
st.markdown("""
<style>
    .title-orange {
        color: #FF6B00;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 1.5rem;
        color: #CCCCCC;
        margin-top: -10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Application Sidebar 
with st.sidebar:
    st.title("Navigation")
    
    # Custom Sidebar Navigation layout
    choice = st.radio(
        "Go to",
        ["Home", "Upload Dataset", "Bias Scan (disabled for now)", "Mitigation (disabled for now)", "About"]
    )

    st.markdown("---")
    st.caption("🚀 Hackathon Day 1 Build")

if choice in ["Home", "Upload Dataset"]:
    # Home Page Interface
    st.markdown('<p class="title-orange">FairSight AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ensuring Fairness and Detecting Bias in Automated Decisions</p>', unsafe_allow_html=True)
    st.markdown("""
    **Problem Statement:** In today's AI-driven world, automated decisions can unintentionally perpetuate biases, 
    leading to unfair outcomes in hiring, lending, law enforcement, and more. FairSight AI provides a transparent, easy-to-use 
    platform to scan for hidden biases in your datasets and apply effective mitigation strategies.
    """)
    
    st.markdown("---")
    st.subheader("Upload Your Dataset")
    
    # Dataset uploader (supports CSV and XLSX)
    uploaded_file = st.file_uploader("Drop your dataset here (CSV or XLSX)", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # Read file based on type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                # Requires openpyxl installed
                df = pd.read_excel(uploaded_file)
            
            # Store in session state for later use across pages/components
            st.session_state['df'] = df
            
            # Success notification with emoji
            st.success("🎉 Dataset uploaded successfully!")
            
            st.markdown("### Dataset Overview")
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])
            col3.metric("Missing Values", df.isnull().sum().sum())
            
            # Display top 10 rows
            st.markdown("#### First 10 Rows")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Display column types summary
            st.markdown("#### Column Types Summary")
            type_counts = df.dtypes.value_counts().reset_index()
            type_counts.columns = ['Data Type', 'Count']
            type_counts['Data Type'] = type_counts['Data Type'].astype(str)
            
            # Plotly bar chart
            fig = px.bar(type_counts, x='Data Type', y='Count', title="Column Types", color_discrete_sequence=['#FF6B00'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyze button acting as a placeholder for Day 2
            if st.button("Analyze for Bias", type="primary"):
                st.info("🚀 Coming on Day 2")
                
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.info("Make sure you upload a valid CSV or Excel file.")

elif choice == "Bias Scan (disabled for now)":
    st.title("Bias Scan")
    st.warning("Feature disabled. Coming on Day 2!")

elif choice == "Mitigation (disabled for now)":
    st.title("Mitigation")
    st.warning("Feature disabled. Coming on Day 2!")

elif choice == "About":
    st.title("About FairSight AI")
    st.markdown("""
    **FairSight AI** is being built over the course of a competitive Hackathon to demonstrate equitable Machine Learning practices. 
    
    ### Goals:
    - **Democratize fairness**: Provide intuitive indicators of potential bias in unstructured and structured data.
    - **Actionable mitigation**: Integrate automatic scaling and transformation strategies to mitigate unwanted discrepancies.
    """)
