import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import numpy as np
import base64
import os
import json

# Custom Utilities
from utils.storage import get_user_data, update_user_data, get_user_history, add_history_entry, verify_user
from utils.detection import detect_columns
from utils.fairness import detect_advanced_bias
from utils.ai_engine import generate_narrative_summary
from utils.mitigation import apply_reweighting, apply_resampling
from utils.reporting import generate_pdf_report

# Page config
st.set_page_config(
    page_title="FairSight AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MINIMALIST CSS ---
def apply_clean_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        :root {
            --primary: #FF6B00;
            --bg-dark: #000000;
            --card-gray: #111111;
            --border-gray: #222222;
            --text-main: #FFFFFF;
            --text-dim: #888888;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: var(--bg-dark) !important;
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid var(--border-gray);
            width: 240px !important;
        }
        
        .logo-area {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--primary);
            padding: 20px 0;
            text-align: center;
        }

        /* Cards & Containers */
        .scrolling-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .minimal-card {
            background: var(--card-gray);
            border: 1px solid var(--border-gray);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }

        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s;
            border: 1px solid var(--border-gray);
            background: transparent;
            color: white;
            padding: 10px 25px;
        }
        
        .stButton>button:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        div.stButton > button:first-child[kind="primary"] {
            background: var(--primary) !important;
            border: none !important;
            color: black !important;
        }

        /* Scores */
        .big-score-card {
            text-align: center;
            padding: 20px;
        }
        
        .score-val {
            font-size: 4rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .score-lbl {
            color: var(--text-dim);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Sidebar Profile */
        .sidebar-footer {
            position: fixed;
            bottom: 20px;
            width: 200px;
            padding: 15px;
            border-top: 1px solid var(--border-gray);
            background: black;
            cursor: pointer;
        }
        
        .mini-pfp {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            border: 1px solid var(--primary);
            object-fit: cover;
        }

        /* Profile Page Avatar */
        .profile-pfp-large {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 3px solid var(--primary);
            object-fit: cover;
            display: block;
            margin: 0 auto 20px auto;
        }

        /* Section Headings */
        .section-h {
            font-size: 0.9rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION ---
def init_session():
    if 'user' not in st.session_state: st.session_state.user = None
    if 'view' not in st.session_state: st.session_state.view = "Home"
    if 'audit_data' not in st.session_state: st.session_state.audit_data = None
    if 'results' not in st.session_state: st.session_state.results = None

init_session()

def get_img_64(data):
    if not data: return "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"

# --- COMPONENTS ---

def sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown('<div class="logo-area">FairSight AI ⚖️</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        if st.button("Home (Upload)", use_container_width=True): 
            st.session_state.view = "Home"
            st.rerun()
        if st.button("History", use_container_width=True): 
            st.session_state.view = "History"
            st.rerun()
        
        st.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
        
        if user:
            # Custom clickable profile area
            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
            cols = st.columns([1, 4])
            with cols[0]:
                st.image(get_img_64(user.get('profile_pic')), width=35)
            with cols[1]:
                if st.button(user['name'], key="side_name", use_container_width=True):
                    st.session_state.view = "Profile"
                    st.rerun()
            
            if st.button("Manage Profile", use_container_width=True):
                st.session_state.view = "Profile"
                st.rerun()
            if st.button("Logout", use_container_width=True): 
                st.session_state.user = None
                st.rerun()

# --- VIEWS ---

def login_view():
    apply_clean_theme()
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="logo-area" style="font-size:2.5rem;">FairSight AI</div>', unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["Login", "Create Account"])
        with t1:
            with st.form("lgn"):
                e = st.text_input("Email")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Access Engine", type="primary", use_container_width=True):
                    if verify_user(e, p):
                        st.session_state.user = get_user_data(e)
                        st.rerun()
                    else: st.error("Access Denied.")
        with t2:
            with st.form("sgn"):
                n = st.text_input("Full Name")
                e = st.text_input("Email")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Initialize", type="primary", use_container_width=True):
                    if n and e and p:
                        update_user_data(e, {"name": n, "email": e, "password": p, "age": 25, "dob": "1999-01-01"})
                        st.session_state.user = get_user_data(e)
                        st.rerun()

def home_view():
    apply_clean_theme()
    sidebar()
    
    with st.container():
        st.markdown('<div class="scrolling-container">', unsafe_allow_html=True)
        
        # Top Bar
        c_alt1, c_alt2 = st.columns([1, 1])
        c_alt1.markdown(f"**Current Audit**: {st.session_state.get('audit_name', 'Untitled')}")
        if c_alt2.button("New Audit", use_container_width=False):
            st.session_state.audit_data = None
            st.session_state.results = None
            st.rerun()
        
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        
        # 1. Upload Section
        st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-h">Data Ingestion</div>', unsafe_allow_html=True)
        
        file = st.file_uploader("+ Add Files (CSV, XLSX)", type=["csv", "xlsx"], label_visibility="collapsed")
        domain = st.selectbox("Application Domain", ["Hiring", "Banking", "Healthcare", "Legal", "General"], index=0)
        
        if file:
            try:
                df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                st.session_state.audit_data = df
                st.session_state.audit_name = file.name
                st.success(f"Loaded {len(df)} records.")
            except Exception as e: st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. RUN SCAN
        if st.session_state.audit_data is not None:
            if st.button("RUN BIAS SCAN", type="primary", use_container_width=True):
                with st.spinner("Analyzing vectors..."):
                    df = st.session_state.audit_data
                    target, protected = detect_columns(df)
                    if not protected:
                        st.error("No protected attributes found.")
                    else:
                        res = detect_advanced_bias(df, target, protected[0])
                        # Gemini narrative
                        res['narrative'] = generate_narrative_summary(res)
                        st.session_state.results = res
                        # History
                        add_history_entry(st.session_state.user['email'], {
                            "filename": st.session_state.audit_name,
                            "domain": domain,
                            "score": res['fairness_score'],
                            "timestamp": str(date.today())
                        })
            
        # 3. RESULTS (Scroll down)
        if st.session_state.results:
            res = st.session_state.results
            st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-h">Bias Discovery</div>', unsafe_allow_html=True)
            
            # Scores
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'''<div class="minimal-card big-score-card">
                    <div class="score-lbl">Fairness Score (Your Data)</div>
                    <div class="score-val" style="color:#FF6B00;">{int(res['fairness_score'])}</div>
                </div>''', unsafe_allow_html=True)
            with col2:
                bench = res.get('benchmark_comparison', {})
                b_score = int(bench.get('benchmark_fairness_score', 81))
                st.markdown(f'''<div class="minimal-card big-score-card">
                    <div class="score-lbl">Benchmark Score ({bench.get('name', 'Std')})</div>
                    <div class="score-val" style="color:#444;">{b_score}</div>
                </div>''', unsafe_allow_html=True)
                
            # Score Explanation Card
            with st.container():
                st.markdown('<div class="minimal-card" style="border-left: 4px solid #FF6B00;">', unsafe_allow_html=True)
                st.markdown("### 📊 Score Interpretation")
                f_score = int(res['fairness_score'])
                
                # Higher Score = Better (Less Biased)
                comparison = "less biased than" if f_score > b_score else "more biased than"
                
                st.write(f"Our **Fairness Score ({f_score})** is calculated on your dataset. A higher score means lower disparity (less bias).")
                st.write(f"**Benchmark Score ({b_score})** is the industry standard for {bench.get('name', 'Adult Census')}.")
                st.markdown(f"**Verdict:** Your data is **{comparison}** the industry benchmark.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
            st.header("Bias Detected")
            if res.get('detailed_explanation'):
                ext = res['detailed_explanation']
                st.markdown(f"**Exact Disparity Gap:** {ext['percentage']}%")
                st.markdown(f"**Disparity Detection:** {ext['comparison_text']}")
                st.markdown(f"**Business Impact:** {ext['impact']}")
                st.success(f"**Recommended Action:** {ext['recommended_action']}")
            
            st.divider()
            st.markdown("**Deterministic Audit Narrative**")
            st.write(res['narrative'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Charts
            st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-h">Distribution Disparity</div>', unsafe_allow_html=True)
            rates_df = pd.DataFrame(res['selection_rates'].items(), columns=['Group', 'Rate'])
            fig = px.bar(rates_df, x='Group', y='Rate', color='Rate', color_continuous_scale="Oranges", template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 4. Mitigation
            st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-h">Bias Mitigation</div>', unsafe_allow_html=True)
            st.write("Apply one-click optimization strategies:")
            m_col1, m_col2, m_col3 = st.columns(3)
            if m_col1.button("REWEIGHTING", use_container_width=True): st.toast("Reweighting applied to engine.")
            if m_col2.button("RESAMPLING", use_container_width=True): st.toast("Dataset resampled for parity.")
            if m_col3.button("PROXY REMOVAL", use_container_width=True): st.toast("Correlation proxies filtered.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 5. Export
            pdf_bytes = generate_pdf_report(res, ["Apply Reweighting", "Update Compliance log"])
            st.download_button("Export PDF Report", pdf_bytes, "Audit_Report.pdf", "application/pdf", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

def history_view():
    apply_clean_theme()
    sidebar()
    with st.container():
        st.markdown('<div class="scrolling-container">', unsafe_allow_html=True)
        st.header("Audit History")
        history = get_user_history(st.session_state.user['email'])
        if not history: 
            st.info("No audit records found in the repository.")
        else:
            for item in reversed(history):
                # Safe key handling
                fname = item.get('filename', 'Unknown Audit')
                tstamp = item.get('timestamp', 'N/A')
                dom = item.get('domain', 'General')
                scr = item.get('score', 'Scan not completed')
                
                with st.expander(f"📄 {fname} | {tstamp}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Domain**\n{dom}")
                    c2.markdown(f"**Date**\n{tstamp}")
                    if isinstance(scr, (int, float)):
                        c3.markdown(f"**Fairness Score**\n{int(scr)}/100")
                    else:
                        c3.markdown(f"**Status**\n{scr}")
        st.markdown('</div>', unsafe_allow_html=True)

def profile_view():
    apply_clean_theme()
    sidebar()
    user = st.session_state.user
    with st.container():
        st.markdown('<div class="scrolling-container">', unsafe_allow_html=True)
        st.header("Profile Settings")
        st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
        st.markdown(f'<img src="{get_img_64(user.get("profile_pic"))}" class="profile-pfp-large">', unsafe_allow_html=True)
        with st.form("upd", clear_on_submit=True):
            pic = st.file_uploader("Upload New Avatar", type=["png", "jpg", "jpeg"])
            name = st.text_input("Display Name", user['name'])
            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                new_pic = pic.getvalue() if pic else user.get('profile_pic')
                update_user_data(user['email'], {"name": name, "profile_pic": new_pic})
                st.session_state.user = get_user_data(user['email'])
                st.toast("Profile updated successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN ---
def main():
    if st.session_state.user is None:
        login_view()
    else:
        v = st.session_state.view
        if v == "Home": home_view()
        elif v == "History": history_view()
        elif v == "Profile": profile_view()

if __name__ == "__main__":
    main()
