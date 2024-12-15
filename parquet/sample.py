import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate sample customer sales data
def generate_sample_data(num_records=150):
    # Generate dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': np.random.randint(1000, 9999, num_records),
        'transaction_date': [start_date + timedelta(days=np.random.randint(0, 30)) for _ in range(num_records)],
        'product_category': np.random.choice([
            'Electronics', 'Clothing', 'Home & Garden', 
            'Sports', 'Books', 'Toys'
        ], num_records),
        'sales_amount': np.round(np.random.uniform(10, 500, num_records), 2),
        'quantity': np.random.randint(1, 10, num_records),
        'is_repeat_customer': np.random.choice([True, False], num_records)
    })
    
    # Sort by transaction date
    df = df.sort_values('transaction_date')
    
    return df

# Generate and save the sample data
sample_data = generate_sample_data()

# Save as Parquet file
sample_data.to_parquet('sample_customer_sales.parquet', index=False)

# Print out first few rows for verification
print(sample_data.head())
print("\nFile 'sample_customer_sales.parquet' has been created.")
print(f"Total records: {len(sample_data)}")