import streamlit as st
import pytesseract
from PIL import Image
import re
import base64
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="XRPL Overlap Detector", layout="centered")

# Optional: Tesseract path for Windows users
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------- AUTHENTICATION SETUP ----------------------
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='main', form_name='Login')

if authenticator.authentication_status:
    name = authenticator.name
    username = authenticator.username

    # ---------------------- LOGO + STYLING ----------------------
    image_path = "XRPL overlap Detector logo.png"
    with open(image_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
    <style>
        .main {{
            background-color: #f7f9fc;
            padding: 2rem;
            font-family: 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background-color: #f7f9fc;
        }}

        .block-container {{
            padding-top: 2rem;
        }}

        h1 {{
            color: #2f4f75;
            text-align: center;
            font-weight: bold;
        }}

        .custom-logo {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 180px;
            margin-bottom: 1rem;
        }}
    </style>

    <img class="custom-logo" src="data:image/png;base64,{encoded_logo}" />
    """, unsafe_allow_html=True)

    st.title("🔁 XRPL Overlap Detector")

    st.markdown("""
    Before investing in any XRPL-related project, it's important to stay alert.  
    Many scam groups use the same wallet addresses across multiple projects to orchestrate **pump & dump schemes**, create **fake hype**, or **drain liquidity**.

    🔎 This tool h
