# my_app.py

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import pickle
import numpy as np
from db_utils import create_sql_server_engine, query_db
import plotly.express as px
import time

# Page config
st.set_page_config(page_title="Customer Segmentation", layout="centered")


# ── Authentication Setup ──
credentials = {
    "usernames": {
        "mary": {"name": "Mary Grace", "password": "$2b$12$MQ/v6fGWoXs.wri5CJ8EOeOOTf5KHMEuxrQQ1mIKa/7qUxc0iUGji"},
        "john": {"name": "John Smith", "password": "$2b$12$z9V/PxJZJ1sQF.lDvFF8vuOnEDkC8Jo7V9AiSAVX8V0qzqgCTO4HK"}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="segmentation_dashboard",
    key="abcdef",
    cookie_expiry_days=1
)

authenticator.login(location="sidebar")

# ── Create DB Engine ──
server = 'MELO0501\\SQLEXPRESS02'
database = 'CustomerSegmentation'

@st.cache_resource
def get_engine():
    return create_sql_server_engine(server, database)

engine = get_engine()

# ── Load Model ──
@st.cache_resource
def load_models():
    with open("models/scaler.pkl", "rb") as f1, open("models/kmeans_model.pkl", "rb") as f2:
        return pickle.load(f1), pickle.load(f2)

def predict_segment(recency, frequency, monetary):
    scaler, model = load_models()
    input_df = pd.DataFrame([[recency, frequency, monetary]], columns=["Recency", "Frequency", "Monetary"])
    input_scaled = scaler.transform(input_df)
    cluster = int(model.predict(input_scaled)[0])
    segment_map = {
        0: "Promising",
        1: "At Risk",
        2: "Loyal",
        3: "Champion"
    }
    return cluster, segment_map.get(cluster, "Unknown")

@st.cache_data
def load_clustered_customers():
    query = "SELECT * FROM dbo.Clustered_Customers"
    return query_db(engine, query)

@st.cache_data
def load_recommendations():
    query = "SELECT * FROM dbo.Top_Recommendations"
    return query_db(engine, query)

# ── Fetch unique Customer IDs for dropdown ──
@st.cache_data
def load_customer_ids():
    query = "SELECT DISTINCT CustomerID FROM dbo.Clustered_Customers WHERE CustomerID IS NOT NULL"
    df_customers = query_db(engine, query)
    return df_customers['CustomerID'].dropna().astype(int).astype(str).tolist()

customer_ids = load_customer_ids()

# Fetch unique Customer IDs from the database

df_customers = query_db(engine,"SELECT DISTINCT CustomerID FROM dbo.Clustered_Customers WHERE CustomerID IS NOT NULL")
customer_ids = df_customers['CustomerID'].dropna().astype(int).astype(str).tolist()

# ── Main ──
if st.session_state.get("authentication_status"):
    if "customer_id" not in st.session_state:
        st.session_state["customer_id"] = None
    if "predicted_cluster" not in st.session_state:
        st.session_state["predicted_cluster"] = None
    if "predicted_segment" not in st.session_state:
        st.session_state["predicted_segment"] = None

    name = st.session_state["name"]
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")

    st.title("🛍️Shopper Profile & Curated Picks")
    st.markdown("""
    Discover your unique shopping profile based on how often and how much you shop.
    See personalized insights, find out your customer segment, and get product recommendations just for you.
    """)

    tab1, tab2 = st.tabs(["Customer Profile & Segment", "Visual Analytics"])

    # ── Tab 1 ──
    with tab1:
        st.subheader("Customer Segmentation & Recommendations")

        previous_user_type = st.session_state.get("previous_user_type", None)
        user_type = st.selectbox("Are you a new customer or existing customer?", ["Select...", "New", "Existing"])
        st.session_state["user_type"] = user_type

        # Reset fields when switching types
        if user_type != previous_user_type:
            st.session_state["previous_user_type"] = user_type
            
            # Clear previous prediction
            st.session_state.pop("predicted_cluster", None)
            st.session_state.pop("predicted_segment", None)

            # Clear fields specific to the *other* type
            if user_type == "New":
                st.session_state.pop("customer_id", None)
            elif user_type == "Existing":
                st.session_state.pop("recency", None)
                st.session_state.pop("frequency", None)
                st.session_state.pop("monetary", None)

        if user_type == "Existing":
            customer_input = st.text_input("Enter your Customer ID", key="existing_customer_id")

            if st.button("Submit", key="submit_existing"):
                # Clear previous outputs first
                st.session_state['predicted_cluster'] = None
                st.session_state['predicted_segment'] = None
                st.session_state['customer_id'] = None

                if customer_input.isdigit():
                    customer_id = int(customer_input)
                    if str(customer_id) in customer_ids:
                        with st.spinner("Predicting segment and fetching top picks..."):
                            time.sleep(1.5)
                            st.session_state.user_type = "existing"
                            st.session_state.customer_id = customer_id

                        rfm_clustered = load_clustered_customers()
                        cust_info = rfm_clustered[rfm_clustered["CustomerID"] == customer_id]
                        if not cust_info.empty:
                            cluster = int(cust_info["Cluster"].iloc[0])
                            segment = cust_info["Segment"].iloc[0]
                            st.session_state['predicted_cluster'] = cluster
                            st.session_state['predicted_segment'] = segment
                        else:
                            st.warning("Customer ID not found.")
                    else:
                        st.warning("Customer ID does not exist. Please try again.")
                else:
                    st.warning("Please enter a valid numeric Customer ID.")



        elif user_type == "New":
            recency = st.number_input("Days Since Last Purchase", min_value=0, value=30, key="recency_input")
            frequency = st.number_input("Number of Purchases", min_value=0, value=3, key="frequency_input")
            monetary = st.number_input("Average Spend per Purchase", min_value=0.0, value=200.0, key="monetary_input")
            st.caption("We’ll estimate total spend by average spend × number of purchases.")
            if st.button("Submit", key="submit_new"):
                with st.spinner("Predicting segment and fetching top picks..."):
                    time.sleep(1.5)
                    st.session_state.user_type = "new"
                    st.session_state.recency = recency
                    st.session_state.frequency = frequency
                    st.session_state.monetary = monetary*frequency
                
                cluster, segment = predict_segment(recency, frequency, monetary)
                st.session_state['predicted_cluster'] = cluster
                st.session_state['predicted_segment'] = segment

        if 'predicted_cluster' in st.session_state and 'predicted_segment' in st.session_state:
            cluster = st.session_state['predicted_cluster']
            segment = st.session_state['predicted_segment']

            # Check if customer ID is valid (for existing users only)
            customer_id = st.session_state.get("customer_id")
            rfm_clustered = load_clustered_customers()

            is_valid_customer = (
                st.session_state.get("user_type") == "existing"
                and isinstance(customer_id, (int, float))
                and not pd.isna(customer_id)
                and customer_id in rfm_clustered["CustomerID"].values
            )

            # Always show segment info for new users or valid existing customers
            if st.session_state.get("user_type") == "new" or is_valid_customer:

                segment_descriptions = {
                    "Promising": "You’re starting to show great potential — keep it up!",
                    "At Risk": "You haven’t shopped for a while. We’d love to see you back!",
                    "Loyal": "You consistently choose us — we appreciate you!",
                    "Champion": "You’re a top spender — we want to reward you!"
                }
                desc = segment_descriptions.get(segment, "Here's what makes you unique.")

                if segment == "At Risk":
                    st.error(f"#### You're an **{segment}** shopper — let's fix that!")
                elif segment in ["Loyal", "High Value", "Champion"]:
                    st.success(f"#### What a **{segment}** customer!")
                elif segment == "Promising":
                    st.info(f"#### You are a **{segment}** customer!")
                else:
                    st.warning(f"#### Your CustomerID cannot be found!")

                st.markdown(f"<p style='font-size:16px; margin-top: -10px;'>{desc}</p>", unsafe_allow_html=True)

                # Show key stats only for valid existing users
                if st.session_state.get("user_type") == "existing":
                    cust_info = rfm_clustered[rfm_clustered["CustomerID"] == customer_id]
                    if not cust_info.empty:
                        st.write(f"Your key stats at a glance:")
                        r = cust_info["Recency"].iloc[0]
                        f = cust_info["Frequency"].iloc[0]
                        m = cust_info["Monetary"].iloc[0]

                        col1, col2, col3 = st.columns(3)
                        col1.write(f"**Recency**  \n{r}")
                        col2.write(f"**Frequency**  \n{f}")
                        col3.write(f"**Total Spent**  \n${m:.2f}")

                # Recommendations
                recommendations = load_recommendations()
                cluster_recs = recommendations[recommendations["Cluster"] == cluster]

                st.write(f"**Recommended items just for you:**")
                if not cluster_recs.empty:
                    product_names = cluster_recs["Description"].unique().tolist()

                    st.markdown(
                        """
                        <style>
                            .pill {
                                display: inline-block;
                                padding: 6px 12px;
                                margin: 4px 4px 4px 0;
                                background-color: #fce8e6;
                                color: #5c2c2c;
                                border-radius: 20px;
                                font-size: 14px;
                                font-family: sans-serif;
                            }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    pill_html = "".join([f'<span class="pill">{name}</span>' for name in product_names])
                    st.markdown(pill_html, unsafe_allow_html=True)
                else:
                    st.info("No recommendations found for this cluster.")


        # ── Tab 2 ──
    with tab2:
        st.subheader("Where You Fit in Our Customer Landscape")

        # Show cluster and segment (both new and existing)
        if (
                    'predicted_cluster' in st.session_state and
                    'predicted_segment' in st.session_state and
                    st.session_state['predicted_cluster'] is not None and
                    st.session_state['predicted_segment'] is not None and
                    st.session_state.get("customer_id") is not None
                ):
            if segment == "At Risk":
                st.error(f"#### You're an **{segment}** shopper — let's fix that!")
            elif segment in ["Loyal", "Champion"]:
                st.success(f"#### What a **{segment}** customer!")
            elif segment in ["Promising"]:
                st.info(f"#### You are a **{segment}** customer!")
            else:
                st.warning(f"#### You are a **{segment}** customer!")
        else:
            st.warning("Please submit your data in Tab 1 first.")
        
        # ── Show Silhouette Score as Model Confidence ──
        with open("models/best_score.pkl", "rb") as f:
            silhouette_score_value = round(pickle.load(f), 2)
 
        confidence_label = (
            "High" if silhouette_score_value > 0.6 else
            "Moderate" if silhouette_score_value > 0.4 else
            "Low"
        )

        st.markdown(f"**How confidently we grouped you with similar customers**: {confidence_label} (Score:{silhouette_score_value})")

        with st.expander("What does this mean?"):
            st.markdown("""
            We analyzed shopping habits to group similar customers together.
            
            - A **higher score** close to 1 means you're clearly similar to others in your group, so the recommendations are more accurate.
            - A **lower score** close to -1 means customer habits are more unique — which makes things a bit more flexible!
            
            Right now, our confidence in your group placement is **{}**.
            """.format(confidence_label))

        rfm_clustered = load_clustered_customers()

        user_type = st.session_state.get("user_type", None)
        customer_point = None

        if user_type == "existing" and st.session_state.get("customer_id") is not None:
            customer_id = int(st.session_state.customer_id)
            customer_row = rfm_clustered[rfm_clustered["CustomerID"] == customer_id]
            if not customer_row.empty:
                customer_point = customer_row.iloc[0]
        elif user_type == "new" and all(k in st.session_state for k in ["recency", "frequency", "monetary"]):
            customer_point = {
            "Recency": st.session_state["recency"],
            "Frequency": st.session_state["frequency"],
            "Monetary": st.session_state["monetary"]
        }

        # Define custom colors for each segment
        custom_colors = {
            "Champion": "#28a745",      
            "At Risk": "#E998C0",       
            "Promising": "#ffc107",    
            "Loyal": "#2b57db",
        }

        fig3d = px.scatter_3d(
            rfm_clustered,
            x="Recency",
            y="Frequency",
            z="Monetary",
            color="Segment",
            opacity=0.6,
            color_discrete_map=custom_colors
        )
        
        fig3d.update_layout(
            width=900,
            height=500,
            legend=dict(
                font=dict(
                    size=14
                )
            )
        )
        
    # Show only the user's segment
        selected_segment = st.session_state.get('predicted_segment')
        if selected_segment:
            for trace in fig3d.data:
                if trace.name == selected_segment:
                    trace.visible = True  
                elif trace.name != "This is you":
                    trace.visible = "legendonly" 

        if customer_point is not None:
            fig3d.add_scatter3d(
                x=[customer_point["Recency"]],
                y=[customer_point["Frequency"]],
                z=[customer_point["Monetary"]],
                mode="markers",
                marker=dict(size=10, color="red"),
                name="You are here"
            )
        st.caption("🔄 Tip: Explore the 3D chart by clicking and dragging to rotate the view. Click legend items on the right to show/hide segments.")
        with st.container():
            st.plotly_chart(fig3d, use_container_width=False)
            
        
    
# ── Authentication Feedback ──
elif st.session_state.get("authentication_status") is False:
    st.sidebar.error("❌ Incorrect username or password")
else:
    st.sidebar.warning("⚠️ Please enter your username and password")
