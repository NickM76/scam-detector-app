import streamlit_authenticator as stauth

hashed = stauth.Hasher(['MijnSuperGeheimWachtwoord2025!']).generate()
print(hashed[0])
