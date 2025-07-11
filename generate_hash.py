from streamlit_authenticator.utilities.hasher import Hasher

hashed_password = Hasher(['MijnSterkWachtwoord123']).generate()
print(hashed_password[0])
