import streamlit as st
import pytesseract
from PIL import Image
import re

# ---------------------- PAGE CONFIG & LOGO ----------------------
import base64

# Load and encode logo
image_path = "XRPL overlap Detector logo.png"
with open(image_path, "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode()

# Inject custom CSS + logo
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

st.set_page_config(page_title="XRPL Overlap Detector", layout="centered")

# Load and display logo
logo = Image.open("XRPL overlap Detector logo.png")
st.image(logo, width=180)

st.title("🔁 XRPL Overlap Detector")

st.markdown("""
Before investing in any XRPL-related project, it's important to stay alert.  
Many scam groups use the same wallet addresses across multiple projects to orchestrate **pump & dump schemes**, create **fake hype**, or **drain liquidity**.

🔎 This tool helps you a little uncover suspicious patterns by scanning **Telegram usernames** but more **wallet fragments** (first 9 characters) from uploaded screenshots.  
By comparing two different projects, you can detect overlaps and identify possible red flags — helping you avoid manipulation and make smarter investment decisions.
""")

# ---------------------- REGEX SETUP ----------------------
USERNAME_REGEX = re.compile(r"^@?[a-zA-Z0-9_]{5,32}$")
WALLET_REGEX = re.compile(r"r[a-zA-Z0-9]{8}")
SUSPECT_KEYWORDS = ["shill", "shibo", "winners", "winner"]

# ---------------------- DATA EXTRACTION ----------------------
def extract_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    usernames = set()
    wallets = set()
    for line in lines:
        wallets.update(WALLET_REGEX.findall(line))
        if not line.lower().startswith(("last seen", "seen", "recently seen")):
            candidate = line.split(" ")[0].strip()
            if USERNAME_REGEX.match(candidate):
                usernames.add(candidate.lstrip("@"))
    return usernames, wallets

# ---------------------- FILE UPLOAD ----------------------
st.subheader("🅰️ Upload screenshots from Project A")
images_a = st.file_uploader("Select one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="a")

st.subheader("🅱️ Upload screenshots from Project B")
images_b = st.file_uploader("Select one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="b")

# ---------------------- PROCESSING ----------------------
if images_a and images_b:
    usernames_a, usernames_b = set(), set()
    wallets_a, wallets_b = set(), set()

    with st.spinner("🔍 Scanning Project A..."):
        for img_file in images_a:
            img = Image.open(img_file)
            st.expander(f"📝 OCR output A – {img_file.name}").write(pytesseract.image_to_string(img))
            u, w = extract_data(img)
            usernames_a.update(u)
            wallets_a.update(w)

    with st.spinner("🔍 Scanning Project B..."):
        for img_file in images_b:
            img = Image.open(img_file)
            st.expander(f"📝 OCR output B – {img_file.name}").write(pytesseract.image_to_string(img))
            u, w = extract_data(img)
            usernames_b.update(u)
            wallets_b.update(w)

    # ---------------------- RESULTS ----------------------
    overlap_users = usernames_a.intersection(usernames_b)
    overlap_wallets = wallets_a.intersection(wallets_b)

    st.markdown("## 📊 Results")
    col1, col2 = st.columns(2)
    col1.metric("👥 Users in A", len(usernames_a))
    col2.metric("👥 Users in B", len(usernames_b))

    st.markdown(f"### ⚠️ Overlapping usernames: `{len(overlap_users)}`")
    if overlap_users:
        st.warning("🚨 Suspicious overlap detected:")
        for user in sorted(overlap_users):
            is_sus = any(k in user.lower() for k in SUSPECT_KEYWORDS)
            icon = "🚩" if is_sus else "🔗"
            st.markdown(f"[{icon} @{user}](https://t.me/{user})", unsafe_allow_html=True)
        st.download_button("📥 Download usernames (CSV)", "\n".join([f"@{u}" for u in sorted(overlap_users)]), "overlap_users.csv", "text/csv")
    else:
        st.success("✅ No overlapping Telegram usernames found.")

    st.markdown(f"### 💸 Overlapping wallet fragments: `{len(overlap_wallets)}`")
    if overlap_wallets:
        st.warning("💰 Wallet overlap detected:")
        for w in sorted(overlap_wallets):
            st.markdown(f"- `{w}`")
        st.download_button("📥 Download wallets (CSV)", "\n".join(sorted(overlap_wallets)), "overlap_wallets.csv", "text/csv")
    else:
        st.success("✅ No overlapping wallets detected.")

    # ---------------------- FULL EXPORTS ----------------------
    with st.expander("🅰️ All usernames in Project A"):
        for u in sorted(usernames_a):
            st.markdown(f"- [`@{u}`](https://t.me/{u})")

    with st.expander("🅱️ All usernames in Project B"):
        for u in sorted(usernames_b):
            st.markdown(f"- [`@{u}`](https://t.me/{u})")

    st.download_button("⬇️ Download all usernames A", "\n".join([f"@{u}" for u in sorted(usernames_a)]), "project_a_usernames.csv", "text/csv")
    st.download_button("⬇️ Download all usernames B", "\n".join([f"@{u}" for u in sorted(usernames_b)]), "project_b_usernames.csv", "text/csv")

else:
    st.info("📎 Upload screenshots from both projects to start comparison.")
