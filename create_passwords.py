import streamlit_authenticator as stauth

usernames = ['mary', 'john']
##passwords = ['xxx', 'xxx'] to set up, create password

hashed_credentials = stauth.Hasher.hash_passwords({
    "usernames": {
        usernames[i]: {"name": usernames[i], "password": passwords[i]}
        for i in range(len(usernames))
    }
})["usernames"]

for username, info in hashed_credentials.items():
    print(f"Username: {username}")
    print(f"Hashed password: {info['password']}\n")
