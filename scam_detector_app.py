
import streamlit as st
import pytesseract
from PIL import Image
import re

st.set_page_config(page_title="Telegram Overlap Detector", layout="centered")
st.title("🔁 Telegram Gebruikers Overlap Detector")

st.markdown("""
Upload screenshots van twee verschillende Telegram groepen (bijv. Coin A en Coin B). 
Deze tool vergelijkt welke gebruikers in beide screenshots voorkomen — een sterke indicator voor verdachte activiteit.
""")

USERNAME_REGEX = re.compile(r"^@[a-zA-Z0-9_]{5,32}$")

def extract_usernames(image):
    try:
        text = pytesseract.image_to_string(image)
        lines = [line.strip() for line in text.splitlines()]
        usernames = set()
        for line in lines:
            for word in line.split():
                if USERNAME_REGEX.match(word):
                    usernames.add(word[1:])
        return usernames
    except Exception as e:
        st.error(f"Fout bij OCR: {e}")
        return set()

st.subheader("🅰️ Coin A screenshots")
images_a = st.file_uploader("Upload één of meerdere screenshots van Coin A", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="a")

st.subheader("🅱️ Coin B screenshots")
images_b = st.file_uploader("Upload één of meerdere screenshots van Coin B", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="b")

if images_a and images_b:
    usernames_a = set()
    usernames_b = set()

    with st.spinner("🔍 OCR uitvoeren op Coin A afbeeldingen..."):
        for image_file in images_a:
            img = Image.open(image_file)
            usernames_a.update(extract_usernames(img))

    with st.spinner("🔍 OCR uitvoeren op Coin B afbeeldingen..."):
        for image_file in images_b:
            img = Image.open(image_file)
            usernames_b.update(extract_usernames(img))

    overlap = usernames_a.intersection(usernames_b)

    st.markdown("## 📊 Resultaten")
    col1, col2 = st.columns(2)
    col1.metric("Coin A gebruikers", len(usernames_a))
    col2.metric("Coin B gebruikers", len(usernames_b))
    st.markdown(f"### ⚠️ Overlappende gebruikers: `{len(overlap)}`")

    if overlap:
        st.warning("🚨 Mogelijk verdachte overlap gedetecteerd:")
        for user in sorted(overlap):
            st.markdown(f"[🔗 @{user}](https://t.me/{user})", unsafe_allow_html=True)

        st.download_button(
            "📥 Download overlap als CSV",
            data="\n".join([f"@{user}" for user in sorted(overlap)]),
            file_name="overlapping_users.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ Geen overlappende gebruikers gevonden.")

    with st.expander("🅰️ Alle gebruikers in Coin A"):
        for user in sorted(usernames_a):
            st.markdown(f"- @{user}")

    with st.expander("🅱️ Alle gebruikers in Coin B"):
        for user in sorted(usernames_b):
            st.markdown(f"- @{user}")
else:
    st.info("📎 Upload screenshots van beide coins om overlap te detecteren.")
