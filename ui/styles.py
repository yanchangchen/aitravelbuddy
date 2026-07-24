"""Custom Light Mode CSS styles, typography, and badges for Travel Buddy."""

import streamlit as st


def inject_custom_css():
    """Inject custom light-mode styling into Streamlit application."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
        color: #0F172A;
    }

    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFC857 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .sub-header {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .badge-approved {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
        border: 1px solid #BBF7D0;
    }

    .badge-busted {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
        border: 1px solid #FECACA;
    }

    .result-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;

    }

    .log-box {
        background-color: #0F172A;
        color: #38BDF8;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.82rem;
        padding: 1rem;
        border-radius: 8px;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }

    .stButton>button:hover {
        transform: translateY(-1px);

    }

    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 50%, #FFC857 100%);
        border-radius: 2px;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
