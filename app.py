import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import numpy as np
import base64
import os
from utils.storage import get_user_data, update_user_data, get_user_history, add_history_entry, verify_user
from utils.detection import detect_columns, calculate_fairness_metrics

# Page config
st.set_page_config(
    page_title="FairSight AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
        
        :root {
            --primary-orange: #FF6B00;
            --bg-dark: #0A0A0B;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: #E0E0E0;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0E0E10;
            border-right: 1px solid var(--border);
            width: 260px !important;
        }
        
        /* Compact Sidebar Links */
        .st-emotion-cache-16idsys p {
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* Titles and Headers */
        .logo-text {
            font-family: 'Orbitron', sans-serif;
            color: var(--primary-orange);
            font-size: 1.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            padding-top: 1rem;
        }

        .main-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #FF6B00, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        /* Glass Cards */
        .glass-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
            margin-bottom: 1.5rem;
        }

        /* Profile Bottom Sidebar */
        .sidebar-footer {
            position: fixed;
            bottom: 20px;
            width: 220px;
            padding: 10px;
            border-top: 1px solid var(--border);
            background: #0E0E10;
        }
        
        .profile-mini {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }
        
        .profile-img-sidebar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: 2px solid var(--primary-orange);
            object-fit: cover;
        }
        
        .profile-name-sidebar {
            font-size: 0.85rem;
            font-weight: 600;
            color: #FFF;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton>button[kind="primary"] {
            background-color: var(--primary-orange);
            border: none;
        }
        
        .stButton>button[kind="primary"]:hover {
            background-color: #E65A00;
            box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
        }

        /* Metric Score */
        .score-display {
            font-family: 'Orbitron', sans-serif;
            font-size: 5rem;
            font-weight: 700;
            text-align: center;
            margin: 1rem 0;
        }

        .score-label {
            text-align: center;
            font-size: 1.2rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #555;
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 4rem;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- SESSION STATE ---
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'df' not in st.session_state:
    st.session_state.df = None

if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# --- HELPERS ---
def logout():
    st.session_state.current_user = None
    st.session_state.df = None
    st.session_state.scan_results = None
    st.rerun()

def get_img_as_base64(binary_data):
    if not binary_data:
        return "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    return f"data:image/png;base64,{base64.b64encode(binary_data).decode()}"

# --- PAGES ---

def login_signup_page():
    st.markdown('<div style="text-align: center; margin-bottom: 3rem;">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">FAIRSIGHT AI ⚖️</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #888; font-size: 1.1rem;">Precision Audit Tool for Algorithmic Fairness</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Welcome Back")
                email = st.text_input("Work Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Enter Dashboard", type="primary", use_container_width=True)
                
                if submit:
                    if verify_user(email, password):
                        st.session_state.current_user = get_user_data(email)
                        st.success("Access Granted.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

        with tab2:
            with st.form("signup_form"):
                st.subheader("Initialize Account")
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Work Email")
                col_a, col_d = st.columns(2)
                new_age = col_a.number_input("Age", 18, 100, 25)
                new_dob = col_d.date_input("DOB", date(1995, 1, 1), min_value=date(1950, 1, 1), max_value=date(2010, 12, 31))
                new_pass = st.text_input("Create Password", type="password")
                
                submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                
                if submit:
                    if new_name and new_email and new_pass:
                        if get_user_data(new_email):
                            st.error("User already exists.")
                        else:
                            user_data = {
                                "name": new_name,
                                "email": new_email,
                                "age": new_age,
                                "dob": new_dob,
                                "password": new_pass,
                                "profile_pic": None
                            }
                            update_user_data(new_email, user_data)
                            st.session_state.current_user = get_user_data(new_email)
                            st.success("Account Initialized.")
                            st.rerun()
                    else:
                        st.error("Please fill all fields.")

def home_page():
    st.header("🏠 Data Upload & Intelligence")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Step 1: Context Selection")
        domain = st.selectbox("Select Application Domain", 
                            ["Hiring/Resume Audit", "Bank Loans", "Medical Diagnostics", "Finance/Portfolio", "Insurance Underwriting", "Educational Admissions", "General Bias Audit"])
        
        st.markdown("### Step 2: Ingest Dataset")
        uploaded_file = st.file_uploader("Upload CSV or XLSX for profiling", type=["csv", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df
                st.success(f"Successfully ingested {uploaded_file.name}")
                
                if st.button("Record to Repository"):
                    add_history_entry(st.session_state.current_user['email'], {
                        "filename": uploaded_file.name,
                        "domain": domain,
                        "rows": len(df),
                        "cols": len(df.columns),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.toast("Metadata persisted to history.")
                    
            except Exception as e:
                st.error(f"Ingestion Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.df is not None:
            df = st.session_state.df
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Profile Overview")
            st.metric("Total Records", f"{len(df):,}")
            st.metric("Feature Count", f"{len(df.columns)}")
            st.metric("Missing Data", f"{df.isnull().sum().sum()}")
            
            with st.expander("Peek at Raw Data"):
                st.dataframe(df.head(20), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a dataset to begin profiling.")

def bias_scan_page():
    st.header("⚖️ Automated Fairness Audit")
    
    if st.session_state.df is None:
        st.warning("No active dataset. Please upload a dataset in the Home section.")
        return

    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
    if st.button("RUN AUTOMATIC BIAS SCAN", type="primary", use_container_width=False, help="Automatically detects protected attributes and runs parity checks."):
        with st.spinner("Analyzing data vectors for disparate impact..."):
            target, protected = detect_columns(st.session_state.df)
            
            if not protected:
                st.error("No common protected attributes detected automatically.")
            else:
                # For now, scan the first detected protected attribute
                results = calculate_fairness_metrics(st.session_state.df, target, protected[0])
                st.session_state.scan_results = {
                    "results": results,
                    "target": target,
                    "protected": protected[0]
                }
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.scan_results:
        res = st.session_state.scan_results['results']
        target = st.session_state.scan_results['target']
        protected = st.session_state.scan_results['protected']
        
        # Display Score
        score = res['score']
        color = "#2ECC71" if score > 80 else "#F39C12" if score > 50 else "#E74C3C"
        
        st.markdown(f'<div class="score-display" style="color: {color};">{score:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="score-label">Global Fairness Score</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_l, col_r = st.columns([2, 3])
        
        with col_l:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Executive Summary")
            st.markdown(f"**Target Outcome:** `{target}`")
            st.markdown(f"**Protected Attribute:** `{protected}`")
            st.markdown(f"**Favorable Outcome:** `{res['fav_outcome']}`")
            
            st.markdown("#### Analysis")
            if score > 80:
                st.success("The system exhibits high demographic parity. Disparate impact is negligible.")
            elif score > 50:
                st.warning(f"Moderate bias detected. The `{res['min_group']}` group receives far fewer favorable outcomes than `{res['max_group']}`.")
            else:
                st.error(f"Critical Bias Detected. Systemic disparity of {res['disparity']*100:.1f}% found against the `{res['min_group']}` group.")
            
            st.markdown("**Recommendation:** Review training data for sampling bias or historical imbalances.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_r:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Disparity Distribution")
            rates_df = pd.DataFrame(res['rates'].items(), columns=[protected, 'Success Rate'])
            fig = px.bar(rates_df, x=protected, y='Success Rate', 
                         color='Success Rate', color_continuous_scale='Oranges',
                         template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

def history_page():
    st.header("📖 Audit Repository")
    history = get_user_history(st.session_state.current_user['email'])
    
    if not history:
        st.info("No audit history found.")
        return
    
    for item in reversed(history):
        with st.expander(f"{item['filename']} - {item['timestamp']}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Domain", item['domain'])
            c2.metric("Records", item['rows'])
            c3.metric("Features", item['cols'])
            c4.write(f"**Status:** Audited ✅")

def profile_page():
    st.header("👤 Security & Profile")
    user = get_user_data(st.session_state.current_user['email'])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        profile_url = get_img_as_base64(user.get('profile_pic'))
        st.markdown(f'<img src="{profile_url}" style="width: 200px; height: 200px; border-radius: 50%; border: 4px solid var(--primary-orange); object-fit: cover; margin-bottom: 20px;">', unsafe_allow_html=True)
        
        new_pic = st.file_uploader("Update Avatar", type=["png", "jpg", "jpeg"])
        if new_pic:
            update_user_data(user['email'], {"profile_pic": new_pic.getvalue()})
            st.session_state.current_user = get_user_data(user['email'])
            st.toast("Avatar updated.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("profile_edit"):
            st.markdown("### Edit Identity")
            name = st.text_input("Full Name", value=user.get('name'))
            email = st.text_input("Contact Email", value=user.get('email'), disabled=True)
            age = st.number_input("Age", 1, 120, value=user.get('age', 25))
            dob = st.date_input("Date of Birth", value=user.get('dob', date(1995, 1, 1)))
            
            if st.form_submit_button("PERSIST CHANGES", type="primary"):
                update_user_data(email, {"name": name, "age": age, "dob": dob})
                st.session_state.current_user = get_user_data(email)
                st.success("Identity updated successfully.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN NAVIGATION ---

def main():
    if st.session_state.current_user is None:
        login_signup_page()
    else:
        # User is logged in
        user = st.session_state.current_user
        
        # Sidebar
        with st.sidebar:
            st.markdown('<div class="logo-text">FAIRSIGHT AI ⚖️</div>', unsafe_allow_html=True)
            
            # Nav built using st.navigation
            pages = {
                "Workplace": [
                    st.Page(home_page, title="Home / Upload", icon="🏠"),
                    st.Page(bias_scan_page, title="Bias Scan", icon="⚖️"),
                    st.Page(history_page, title="History", icon="📖"),
                ],
                "Security": [
                    st.Page(profile_page, title="Profile Settings", icon="👤"),
                ]
            }
            
            pg = st.navigation(pages, position="sidebar")
            
            # Anchor profile to bottom
            st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True) # Spacer
            
            profile_html = f"""
            <div class="sidebar-footer">
                <div class="profile-mini">
                    <img src="{get_img_as_base64(user.get('profile_pic'))}" class="profile-img-sidebar">
                    <div class="profile-name-sidebar">{user['name']}</div>
                </div>
            """
            st.markdown(profile_html, unsafe_allow_html=True)
            if st.button("LOGOUT", use_container_width=True, key="logout_btn"):
                logout()
            st.markdown('</div>', unsafe_allow_html=True)

        pg.run()
    
    st.markdown('<div class="footer">FairSight AI Audit Engine © 2026. All Rights Reserved.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
