# ---------------------- DEPENDENCIES ----------------------
import streamlit as st
import pytesseract
from PIL import Image
import re
import base64
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------------------- CONFIG ----------------------
st.set_page_config(page_title="XRPL Overlap Detector", layout="centered")

# Optional: Tesseract pad (Windows users)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------- AUTH ----------------------
try:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ config.yaml not found. Please add it to your root directory.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login(location='main', form_name='Login')

if authentication_status:
    # ---------------------- LOGO + STYLING ----------------------
    try:
        with open("XRPL overlap Detector logo.png", "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        encoded_logo = ""

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
    Stay alert when investing in XRPL projects.  
    This tool scans **Telegram usernames** and **wallet fragments** from screenshots to detect suspicious overlaps.

    ✅ Use it to reveal duplicate actors between projects.  
    📎 Upload screenshots or paste wallet addresses manually.
    """)

    # ---------------------- REGEX ----------------------
    USERNAME_REGEX = re.compile(r"^@?[a-zA-Z0-9_]{5,32}$")
    WALLET_REGEX = re.compile(r"r[a-zA-Z0-9]{8}")
    FULL_WALLET_REGEX = re.compile(r"r[1-9A-HJ-NP-Za-km-z]{24,34}")
    SUSPECT_KEYWORDS = ["shill", "shibo", "winner", "winners"]

    # ---------------------- OCR + EXTRACT ----------------------
    def extract_data(image):
        try:
            text = pytesseract.image_to_string(image, config='--psm 6')
        except Exception:
            return set(), set()

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

    # ---------------------- INPUTS ----------------------
    st.subheader("🅰️ Upload screenshots from Project A")
    images_a = st.file_uploader("Select image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="a")

    st.subheader("🅱️ Upload screenshots from Project B")
    images_b = st.file_uploader("Select image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="b")

    st.subheader("✍️ Paste full wallet addresses (optional)")
    wallets_manual_input = st.text_area("One per line", placeholder="rXYZ...\nrABC...", height=120)
    manual_wallets = set(line.strip() for line in wallets_manual_input.splitlines() if FULL_WALLET_REGEX.match(line.strip()))

    # ---------------------- LOGIC ----------------------
    if (images_a and images_b) or manual_wallets:
        usernames_a, usernames_b = set(), set()
        wallets_a, wallets_b = set(), set()

        if images_a:
            with st.spinner("🔍 Scanning Project A..."):
                for img_file in images_a:
                    try:
                        img = Image.open(img_file)
                        u, w = extract_data(img)
                        usernames_a.update(u)
                        wallets_a.update(w)
                        st.expander(f"OCR A – {img_file.name}").write(pytesseract.image_to_string(img))
                    except Exception as e:
                        st.error(f"❌ {img_file.name} failed: {e}")

        if images_b:
            with st.spinner("🔍 Scanning Project B..."):
                for img_file in images_b:
                    try:
                        img = Image.open(img_file)
                        u, w = extract_data(img)
                        usernames_b.update(u)
                        wallets_b.update(w)
                        st.expander(f"OCR B – {img_file.name}").write(pytesseract.image_to_string(img))
                    except Exception as e:
                        st.error(f"❌ {img_file.name} failed: {e}")

        wallets_b.update(manual_wallets)

        overlap_users = usernames_a & usernames_b
        overlap_wallets = wallets_a & wallets_b

        st.markdown("## 📊 Results")
        col1, col2 = st.columns(2)
        col1.metric("👥 Users A", len(usernames_a))
        col2.metric("👥 Users B", len(usernames_b))

        st.markdown(f"### ⚠️ Overlapping usernames: `{len(overlap_users)}`")
        if overlap_users:
            for user in sorted(overlap_users):
                sus = any(k in user.lower() for k in SUSPECT_KEYWORDS)
                icon = "🚩" if sus else "🔗"
                st.markdown(f"- [{icon} @{user}](https://t.me/{user})", unsafe_allow_html=True)
            st.download_button("⬇️ Download Overlaps", "\n".join([f"@{u}" for u in sorted(overlap_users)]), "overlap_users.csv", "text/csv")
        else:
            st.success("✅ No overlapping Telegram usernames found.")

        st.markdown(f"### 💸 Overlapping wallet fragments: `{len(overlap_wallets)}`")
        if overlap_wallets:
            for w in sorted(overlap_wallets):
                if len(w) >= 25:
                    st.markdown(f"- [`{w}`](https://xrpscan.com/account/{w})")
                else:
                    st.markdown(f"- `{w}` (partial match)")
            st.download_button("⬇️ Download Wallets", "\n".join(sorted(overlap_wallets)), "overlap_wallets.csv", "text/csv")
        else:
            st.success("✅ No overlapping wallets found.")

        with st.expander("🅰️ Usernames Project A"):
            for u in sorted(usernames_a):
                st.markdown(f"- [`@{u}`](https://t.me/{u})")
        with st.expander("🅱️ Usernames Project B"):
            for u in sorted(usernames_b):
                st.markdown(f"- [`@{u}`](https://t.me/{u})")

        st.download_button("⬇️ Download A", "\n".join([f"@{u}" for u in sorted(usernames_a)]), "project_a_usernames.csv", "text/csv")
        st.download_button("⬇️ Download B", "\n".join([f"@{u}" for u in sorted(usernames_b)]), "project_b_usernames.csv", "text/csv")
    else:
        st.info("📎 Upload screenshots from both projects or paste wallet addresses to compare.")

    authenticator.logout("Logout", "sidebar")

elif authentication_status is False:
    st.error("❌ Incorrect username or password.")
    st.stop()

elif authentication_status is None:
    st.warning("🔐 Please log in to access the XRPL Overlap Detector.")
    st.stop()
