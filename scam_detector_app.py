import streamlit as st
import pytesseract
from PIL import Image
import re

st.set_page_config(page_title="Telegram Overlap & Wallet Detector", layout="centered")
st.title("🔁 Telegram User & Wallet Overlap Detector")

st.markdown("""
Upload screenshots from two different Telegram groups (e.g., Project A and Project B).  
This tool detects overlapping **Telegram usernames** and **wallet addresses** (based on first 9 characters) to uncover suspicious group activity.
""")

# Regex to identify valid Telegram usernames (with or without '@')
USERNAME_REGEX = re.compile(r"^@?[a-zA-Z0-9_]{5,32}$")

# Regex to identify XRPL-style wallet addresses (e.g., rH1BPfix2...)
WALLET_REGEX = re.compile(r"r[a-zA-Z0-9]{8}")

# Keywords that may indicate suspicious accounts
SUSPECT_KEYWORDS = ["airdrop", "pump", "scam", "bot", "admin", "mod", "giveaway"]

def extract_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    lines = [line.strip() for line in text.splitlines()]
    usernames = set()
    wallets = set()

    for line in lines:
        # Wallets (first 9 chars, starts with r)
        wallets.update(WALLET_REGEX.findall(line))

        # Usernames (first word, not a timestamp or 'seen')
        if len(line) >= 3 and not line.lower().startswith(("last seen", "seen", "recently seen")):
            candidate = line.split(" ")[0].strip()
            if len(candidate.split()) <= 4 and USERNAME_REGEX.match(candidate):
                usernames.add(candidate.lstrip("@"))  # remove @ if present

    return usernames, wallets

# Upload sections
st.subheader("🅰️ Project A screenshots")
images_a = st.file_uploader("Upload one or more screenshots from Project A", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="a")

st.subheader("🅱️ Project B screenshots")
images_b = st.file_uploader("Upload one or more screenshots from Project B", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="b")

# Analysis
if images_a and images_b:
    usernames_a, usernames_b = set(), set()
    wallets_a, wallets_b = set(), set()

    with st.spinner("🔍 Running OCR on Project A screenshots..."):
        for image_file in images_a:
            img = Image.open(image_file)
            text = pytesseract.image_to_string(img)
            st.expander(f"📝 OCR Output A – {image_file.name}").write(text)
            users, wallets = extract_data(img)
            usernames_a.update(users)
            wallets_a.update(wallets)

    with st.spinner("🔍 Running OCR on Project B screenshots..."):
        for image_file in images_b:
            img = Image.open(image_file)
            text = pytesseract.image_to_string(img)
            st.expander(f"📝 OCR Output B – {image_file.name}").write(text)
            users, wallets = extract_data(img)
            usernames_b.update(users)
            wallets_b.update(wallets)

    # Results
    overlap_users = usernames_a.intersection(usernames_b)
    overlap_wallets = wallets_a.intersection(wallets_b)

    st.markdown("## 📊 Results")
    col1, col2 = st.columns(2)
    col1.metric("Users in Project A", len(usernames_a))
    col2.metric("Users in Project B", len(usernames_b))
    st.markdown(f"### ⚠️ Overlapping Telegram usernames: `{len(overlap_users)}`")

    if overlap_users:
        st.warning("🚨 Suspicious user overlap detected:")
        for user in sorted(overlap_users):
            is_suspect = any(k in user.lower() for k in SUSPECT_KEYWORDS)
            icon = "🚩" if is_suspect else "🔗"
            st.markdown(f"[{icon} @{user}](https://t.me/{user})", unsafe_allow_html=True)

        st.download_button("📥 Download overlapping usernames (CSV)", data="\n".join([f"@{u}" for u in sorted(overlap_users)]), file_name="overlap_users.csv", mime="text/csv")
    else:
        st.success("✅ No overlapping Telegram usernames found.")

    st.markdown(f"### 💸 Overlapping wallets (first 9 characters): `{len(overlap_wallets)}`")
    if overlap_wallets:
        st.warning("💰 Possible wallet overlap:")
        for wallet in sorted(overlap_wallets):
            st.markdown(f"- `{wallet}`")
        st.download_button("📥 Download overlapping wallets (CSV)", data="\n".join(sorted(overlap_wallets)), file_name="overlap_wallets.csv", mime="text/csv")
    else:
        st.success("✅ No overlapping wallets detected.")

    # Full lists
    with st.expander("🅰️ All usernames in Project A"):
        for user in sorted(usernames_a):
            st.markdown(f"- [`@{user}`](https://t.me/{user})")

    with st.expander("🅱️ All usernames in Project B"):
        for user in sorted(usernames_b):
            st.markdown(f"- [`@{user}`](https://t.me/{user})")

    st.download_button("📥 Download Project A usernames", data="\n".join([f"@{u}" for u in sorted(usernames_a)]), file_name="project_a_usernames.csv", mime="text/csv")
    st.download_button("📥 Download Project B usernames", data="\n".join([f"@{u}" for u in sorted(usernames_b)]), file_name="project_b_usernames.csv", mime="text/csv")

else:
    st.info("📎 Upload screenshots from both projects to start comparison.")
