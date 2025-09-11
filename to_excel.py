from pymongo import MongoClient
import pandas as pd

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["leslibraires_france_web"]
collection = db["pdp"]  # <-- Replace with your actual collection name

docs = list(collection.find({},{'_id':0}))

# Convert to DataFrame
df = pd.DataFrame(docs)
df.fillna("N/A", inplace=True)
# Export to Excel
file_name = 'leslibraires_france_web_sample_data'
df.to_excel(f"{file_name}.xlsx", index=False,engine='openpyxl')
print(f"✅ Data exported to '{file_name}.xlsx' (excluding _id and path).")
