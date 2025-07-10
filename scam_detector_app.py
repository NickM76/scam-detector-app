import streamlit as st
import pytesseract
from PIL import Image
import re

st.set_page_config(page_title="Telegram & Wallet Overlap Detector", layout="centered")

st.title("🔍 Telegram & Wallet Overlap Detector")

st.markdown("""
Upload screenshots van twee verschillende Telegram groepen (bijv. Coin A en Coin B).  
Deze tool vergelijkt gebruikersnamen **én walletadressen (eerste 9 tekens)** via OCR — ideaal voor het opsporen van systematisch pump & dump-gedrag.
""")

USERNAME_REGEX = re.compile(r"^@[a-zA-Z0-9_]{5,32}$")
WALLET_REGEX = re.compile(r"r[a-zA-Z0-9]{8}")  # XRPL wallet prefix (first 9 chars)

SUSPECT_KEYWORDS = ["airdrop", "pump", "scam", "bot", "admin", "mod", "giveaway"]

def extract_usernames_and_wallets(image):
    try:
        text = pytesseract.image_to_string(image, config='--psm 6')
        lines = [line.strip() for line in text.splitlines()]
        usernames = set()
        wallets = set()
        for line in lines:
            if len(line) >= 3 and not line.lower().startswith(("laatst gezien", "gezien", "recent gezien")):
                for word in line.split():
                    if USERNAME_REGEX.match(word):
                        usernames.add(word[1:])
                    if WALLET_REGEX.match(word):
                        wallets.add(WALLET_REGEX.match(word).group())
        return usernames, wallets, text
    except Exception as e:
        st.error(f"Fout bij OCR: {e}")
        return set(), set(), ""

st.subheader("🅰️ Coin A screenshots")
images_a = st.file_uploader("Upload screenshots van Coin A", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="a")

st.subheader("🅱️ Coin B screenshots")
images_b = st.file_uploader("Upload screenshots van Coin B", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="b")

if images_a and images_b:
    usernames_a, wallets_a = set(), set()
    usernames_b, wallets_b = set(), set()

    with st.spinner("🔍 OCR uitvoeren op Coin A..."):
        for image_file in images_a:
            img = Image.open(image_file)
            u, w, raw = extract_usernames_and_wallets(img)
            usernames_a.update(u)
            wallets_a.update(w)
            st.expander(f"📝 OCR-output Coin A – {image_file.name}").write(raw)

    with st.spinner("🔍 OCR uitvoeren op Coin B..."):
        for image_file in images_b:
            img = Image.open(image_file)
            u, w, raw = extract_usernames_and_wallets(img)
            usernames_b.update(u)
            wallets_b.update(w)
            st.expander(f"📝 OCR-output Coin B – {image_file.name}").write(raw)

    overlap_users = usernames_a.intersection(usernames_b)
    overlap_wallets = wallets_a.intersection(wallets_b)

    st.markdown("## 📊 Resultaten")
    col1, col2 = st.columns(2)
    col1.metric("Coin A gebruikers", len(usernames_a))
    col2.metric("Coin B gebruikers", len(usernames_b))
    col1.metric("Coin A wallets", len(wallets_a))
    col2.metric("Coin B wallets", len(wallets_b))

    st.markdown(f"### ⚠️ Overlappende Telegram gebruikers: `{len(overlap_users)}`")
    if overlap_users:
        for user in sorted(overlap_users):
            suspect = any(keyword in user.lower() for keyword in SUSPECT_KEYWORDS)
            icon = "🚩" if suspect else "🔗"
            st.markdown(f"[{icon} @{user}](https://t.me/{user})", unsafe_allow_html=True)

        st.download_button("📥 Download overlappende gebruikers", "\n".join([f"@{u}" for u in sorted(overlap_users)]), "overlapping_users.csv", "text/csv")
    else:
        st.success("✅ Geen overlappende gebruikersnamen gevonden.")

    st.markdown(f"### 💸 Overlappende wallets (eerste 9 tekens): `{len(overlap_wallets)}`")
    if overlap_wallets:
        for wallet in sorted(overlap_wallets):
            st.markdown(f"🔁 `{wallet}`")
        st.download_button("📥 Download overlappende wallets", "\n".join(sorted(overlap_wallets)), "overlapping_wallets.csv", "text/csv")
    else:
        st.success("✅ Geen overlappende walletadressen gevonden.")

    with st.expander("🅰️ Alle gebruikers & wallets in Coin A"):
        st.markdown("**Gebruikers**:")
        for u in sorted(usernames_a):
            st.markdown(f"- [`@{u}`](https://t.me/{u})")
        st.markdown("**Wallets**:")
        for w in sorted(wallets_a):
            st.markdown(f"- `{w}`")

    with st.expander("🅱️ Alle gebruikers & wallets in Coin B"):
        st.markdown("**Gebruikers**:")
        for u in sorted(usernames_b):
            st.markdown(f"- [`@{u}`](https://t.me/{u})")
        st.markdown("**Wallets**:")
        for w in sorted(wallets_b):
            st.markdown(f"- `{w}`")

else:
    st.info("📎 Upload screenshots van beide coins om overlap te detecteren.")
