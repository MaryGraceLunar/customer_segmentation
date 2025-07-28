import sys
import streamlit_authenticator as stauth
import pkg_resources

print("Python executable:", sys.executable)
print("streamlit_authenticator file:", stauth.__file__)
print("streamlit-authenticator version:", pkg_resources.get_distribution("streamlit-authenticator").version)
