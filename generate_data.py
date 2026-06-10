import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_sales_data(num_records=500):
    np.random.seed(42)
    
    # Categories
    products = ['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard']
    regions = ['North', 'South', 'East', 'West']
    
    # Generate dates over the past year
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(num_records)]
    
    data = {
        'Date': dates,
        'Product': [random.choice(products) for _ in range(num_records)],
        'Region': [random.choice(regions) for _ in range(num_records)],
        'Quantity': np.random.randint(1, 20, size=num_records),
        'Unit_Price': []
    }
    
    # Assign prices based on product
    price_map = {
        'Laptop': 1200,
        'Smartphone': 800,
        'Tablet': 500,
        'Monitor': 300,
        'Keyboard': 100
    }
    
    for p in data['Product']:
        # Add some random noise to prices
        noise = np.random.normal(0, 0.05)
        base_price = price_map[p]
        data['Unit_Price'].append(round(base_price * (1 + noise), 2))
        
    df = pd.DataFrame(data)
    df['Total_Sales'] = df['Quantity'] * df['Unit_Price']
    
    # Sort by date
    df = df.sort_values(by='Date').reset_index(drop=True)
    
    # Save to CSV
    df.to_csv('sales.csv', index=False)
    print("Successfully generated sales.csv with 500 records.")

if __name__ == "__main__":
    generate_sales_data()
