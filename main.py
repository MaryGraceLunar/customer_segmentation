# main.py

from src.data_preprocessing import load_and_clean_data, create_rfm_features
from src.clustering_model import find_best_k_silhouette, train_kmeans_model
from src.recommend import get_top_products_by_cluster
from db_utils import create_sql_server_engine, query_db, save_table

import pickle
import os
import pandas as pd

def run_pipeline(top_n=5):
    # Connect to SQL Server
    server = 'MELO0501\\SQLEXPRESS02'
    database = 'CustomerSegmentation'
    engine = create_sql_server_engine(server, database)

    # Load raw data from SQL
    raw_data_query = "SELECT * FROM raw_data"
    df = query_db(engine, raw_data_query)

    # Clean and transform
    df = load_and_clean_data(df)
    rfm = create_rfm_features(df)
    best_k, scaled_data, scaler,best_score = find_best_k_silhouette(rfm)
    rfm_clustered, model = train_kmeans_model(scaled_data, rfm, k=best_k)
    recommendations = get_top_products_by_cluster(df, rfm_clustered, top_n=top_n)

    # Save the model and scaler for reuse
    os.makedirs("models", exist_ok=True)
    with open("models/kmeans_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    # Save CSVs as backup
    os.makedirs("data", exist_ok=True)
    rfm.to_csv("data/cleaned_data.csv", index=False)
    rfm_clustered.to_csv("data/clustered_customers.csv", index=False)
    recommendations.to_csv("data/top_recommendations.csv", index=False)

    # Save to SQL Server using db_utils
    save_table(rfm_clustered, "Clustered_Customers", "replace", engine)
    save_table(recommendations, "Top_Recommendations", "replace", engine)
    print("Data saved to SQL Server")

    return rfm_clustered, recommendations, model

# Execute pipeline
if __name__ == "__main__":
    rfm_clustered, recommendations, model = run_pipeline(top_n=5)

    print("\nRFM Clustered Customers:")
    print(rfm_clustered.head())

    print("\nTop Product Recommendations by Cluster:")
    print(recommendations.head())