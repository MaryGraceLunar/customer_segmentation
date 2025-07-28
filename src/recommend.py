import pandas as pd

def get_top_products_by_cluster(df, rfm, top_n=5):
    merged = df.merge(rfm[['CustomerID', 'Cluster', 'Segment']], on='CustomerID')
    top_products = (merged.groupby(['Cluster', 'Segment', 'Description'])['Quantity']
                    .sum()
                    .reset_index()
                    .sort_values(['Cluster', 'Quantity'], ascending=[True, False]))
    top_recommendations = top_products.groupby('Cluster').head(top_n).reset_index(drop=True)

    return top_recommendations
