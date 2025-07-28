import streamlit as st
import streamlit_authenticator as stauth

credentials = {
    "usernames": {
        "mary": {"name": "Mary Grace", "password": "$2b$12$MQ/v6fGWoXs.wri5CJ8EOeOOTf5KHMEuxrQQ1mIKa/7qUxc0iUGji"},
        "john": {"name": "John Smith", "password": "$2b$12$z9V/PxJZJ1sQF.lDvFF8vuOnEDkC8Jo7V9AiSAVX8V0qzqgCTO4HK"}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "segmentation_dashboard",
    "abcdef",
    cookie_expiry_days=1
)

# Show login form in the sidebar; does not return values
authenticator.login(location="sidebar")

# Check authentication status from session state
if st.session_state.get("authentication_status"):
    name = st.session_state["name"]
    st.sidebar.success(f"Welcome {name}")
    st.write("Main app content visible after login")
elif st.session_state.get("authentication_status") is False:
    st.sidebar.error("Username/password is incorrect")
else:
    st.sidebar.warning("Please enter your username and password")
