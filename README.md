# 🔁 Telegram Overlap & Wallet Detector

This tool detects overlapping Telegram users and repeated wallet addresses between two crypto projects. It’s designed to uncover coordinated pump & dump schemes, bot farms, or admin cross-project manipulation.

## 💡 What It Does

- 📸 Extracts **Telegram usernames** (e.g. `@Crypto2Guy`) and **wallet address prefixes** (e.g. `rJqREqLB...`) from uploaded screenshots using OCR
- ⚠️ Highlights **overlapping users and wallets** between two Telegram groups
- 🚩 Flags suspicious usernames
- 📥 Allows downloading of all usernames and overlaps as `.csv` files
- 🧠 Works completely visually — **no raw text input**, only images (JPG, PNG)

## 🛠️ How to Use

1. Upload **screenshots** of two Telegram member lists (e.g. Coin A and Coin B)
2. The app uses OCR (Tesseract) to scan usernames and wallet addresses
3. It compares both groups and shows:
   - All usernames and wallet fragments from each group
   - Overlapping entries
4. You can download all results as CSVs

## ✅ Use Cases

- Spot pump & dump groups
- Detect wallet reuse across projects
- Investigate suspicious admins or fake communities
- Prevent falling for scammy clone projects

## 🔧 Installation

Make sure you have [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system.

Then run the app locally:

```bash
pip install streamlit pytesseract pillow
streamlit run scam_detector_app.py
📦 scam-detector-app/
├── scam_detector_app.py     # Main Streamlit app
├── README.md                # This file
└── requirements.txt         # Optional dependency list
