import pandas as pd

def load_and_clean_data(df):
    df = df.dropna(subset=['CustomerID'])
    df.drop_duplicates(inplace=True)
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df = df[df['Quantity'] > 0]
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df = df[df['UnitPrice'] > 0]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce')
    return df

def create_rfm_features(df):
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalAmount': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    return rfm
