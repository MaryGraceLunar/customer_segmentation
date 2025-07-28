from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import pickle
import os

import os
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

def find_best_k_silhouette(rfm_data, min_k=2, max_k=10):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(rfm_data[['Recency', 'Frequency', 'Monetary']])

    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)

    # Save the scaler
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    silhouette_scores = []
    for k in range(min_k, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(scaled_data)
        score = silhouette_score(scaled_data, labels)
        silhouette_scores.append(score)
        print(f"K={k} → Silhouette Score = {score:.4f}")

    plt.figure(figsize=(8, 5))
    plt.plot(range(min_k, max_k + 1), silhouette_scores, marker='o')
    plt.title('Silhouette Score vs Number of Clusters (k)')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette Score')
    plt.grid(True)
    plt.show()

    best_k_index = silhouette_scores.index(max(silhouette_scores))
    best_k = range(min_k, max_k + 1)[best_k_index]
    best_score = silhouette_scores[best_k_index]
    print(f"\nBest K based on Silhouette Score: {best_k}")

    # Save best_k and best_score to file
    with open("models/best_k.pkl", "wb") as f:
        pickle.dump(best_k, f)
        
    with open("models/best_score.pkl", "wb") as f:
        pickle.dump(best_score, f)


    return best_k, scaled_data, scaler,best_score

def train_kmeans_model(scaled_data, rfm, k):
    model = KMeans(n_clusters=k, random_state=42)
    rfm['Cluster'] = model.fit_predict(scaled_data)

    # Save the trained KMeans model
    os.makedirs("models", exist_ok=True)
    with open("models/kmeans_model.pkl", "wb") as f:
        pickle.dump(model, f)

    segment_map = {
        0: "Promising",
        1: "At Risk",
        2: "Loyal",
        3: "Champion"
    }
    rfm['Segment'] = rfm['Cluster'].map(segment_map)
    return rfm, model
