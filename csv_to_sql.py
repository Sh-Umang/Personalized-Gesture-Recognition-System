import pandas as pd
import sqlite3

# Specify the path to your CSV file and the SQLite database
csv_file_path = "model\keypoints1\keypoints_joker.csv"
sqlite_db_path = "d:\programming\db_gesture.db"

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path, header=None)

# Create a connection to the SQLite database
conn = sqlite3.connect(sqlite_db_path)

# Define the table schema based on the number of columns in your CSV
num_columns = len(df.columns)
table_schema = ",".join([f"col{i} TEXT" for i in range(1, num_columns + 1)])

# Create the table in the SQLite database
create_table_query = f"CREATE TABLE IF NOT EXISTS your_table_name ({table_schema})"
conn.execute(create_table_query)

# Use pandas to_sql method to write the DataFrame to the SQLite table
df.to_sql("your_table_name", conn, index=False, if_exists="replace")

# Close the connection
conn.close()
