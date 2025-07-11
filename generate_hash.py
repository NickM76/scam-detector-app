from streamlit_authenticator.utilities.hasher import Hasher

hashed_password = Hasher().hash("MijnSterkWachtwoord123")
print(hashed_password)
