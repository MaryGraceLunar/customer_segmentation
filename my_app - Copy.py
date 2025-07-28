# my_app.py

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import pickle
import numpy as np

# ⚠️ Page config must be first
st.set_page_config(page_title="Customer Segmentation", layout="centered")

# ── 🔐 Authentication Setup ──
credentials = {
    "usernames": {
        "mary": {"name": "Mary Grace", "password": "$2b$12$MQ/v6fGWoXs.wri5CJ8EOeOOTf5KHMEuxrQQ1mIKa/7qUxc0iUGji"},
        "john": {"name": "John Smith", "password": "$2b$12$z9V/PxJZJ1sQF.lDvFF8vuOnEDkC8Jo7V9AiSAVX8V0qzqgCTO4HK"}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="segmentation_dashboard",
    key="abcdef",  # secret used to hash cookies
    cookie_expiry_days=1
)

# Login form rendered in sidebar
authenticator.login(location="sidebar")

# ── Authentication Flow ──
if st.session_state.get("authentication_status"):
    name = st.session_state["name"]
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name} 👋")

    # ── Dashboard content ──
    st.title("🛍️ Customer Segmentation & Product Recommender")
    st.markdown("""
    Use this dashboard to explore customer segments based on Recency, Frequency, and Monetary (RFM) values.  
    View insights, predict customer segments, or explore product recommendations.
    """)

    tab1, tab2, tab3 = st.tabs([
        "🧠 Data Behind the Model",
        "🆕 Predict New Customer Segment",
        "🎯 Existing Customer Recommendations"
    ])

    # Tab 1
    with tab1:
        st.subheader("🧠 Data Behind the Model")
        st.markdown(
            '<iframe width="1140" height="700" src="https://app.powerbi.com/reportEmbed?'
            'reportId=a929b830-9106-4b56-b53a-c12c45e4b76f&autoAuth=true'
            '&ctid=ec1bd924-0a6a-4aa9-aa89-c980316c0449&filterPaneEnabled=false" '
            'frameborder="0" allowFullScreen="true"></iframe>',
            unsafe_allow_html=True,
        )

    # Tab 2
    with tab2:
        st.subheader("🆕 Predict Segment for a New Customer")

        recency = st.number_input("Recency (days since last purchase)", 0, value=30)
        frequency = st.number_input("Frequency (number of purchases)", 0, value=5)
        monetary = st.number_input("Monetary (total spent)", 0.0, format="%.2f", value=100.0)

        if st.button("🚀 Predict Segment"):
            with open("models/scaler.pkl", "rb") as f:
                scaler = pickle.load(f)
            with open("models/kmeans_model.pkl", "rb") as f:
                model = pickle.load(f)

            input_df = pd.DataFrame([[recency, frequency, monetary]],
                                    columns=["Recency", "Frequency", "Monetary"])
            input_scaled = scaler.transform(input_df)
            cluster = int(model.predict(input_scaled)[0])

            segment_map = {
                0: "Promising",
                1: "At Risk",
                2: "Champions",
                3: "Loyal Customers",
                4: "High Value",
            }
            segment = segment_map.get(cluster, "Unknown")

            st.success(f"Predicted Cluster ID: {cluster}")
            st.success(f"Predicted Segment: {segment}")

    # Tab 3
    with tab3:
        st.subheader("🎯 Recommendation for Existing Customers")

        rfm_clustered = pd.read_csv("data/clustered_customers.csv")
        recommendations = pd.read_csv("data/top_recommendations.csv")

        customer_ids = rfm_clustered["CustomerID"].astype(int).sort_values().unique()
        selected_id = st.selectbox("Select Customer ID", customer_ids)

        cust_info = rfm_clustered[rfm_clustered["CustomerID"] == selected_id]
        st.write("📊 RFM Segment Info:")
        st.dataframe(cust_info[["Recency", "Frequency", "Monetary", "Segment"]])

        cluster = int(cust_info["Cluster"].iloc[0])
        segment = cust_info["Segment"].iloc[0]

        st.write(f"🎁 Top Products for Cluster {cluster} ({segment}):")
        cluster_recs = recommendations[recommendations["Cluster"] == cluster]
        st.dataframe(cluster_recs[["Description", "Quantity"]])

elif st.session_state.get("authentication_status") is False:
    st.sidebar.error("❌ Incorrect username or password")
else:
    st.sidebar.warning("⚠️ Please enter your username and password")
