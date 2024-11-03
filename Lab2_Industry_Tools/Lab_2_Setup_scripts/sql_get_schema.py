import sqlite3
import os

# Connect to the existing database file
# Get the parent directory of the current script's directory
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the path to the database file in the parent directory
db_file = os.path.join(parent_directory, 'test_database.db')

# Connect to the SQLite database file in the parent directory
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

# Retrieve the schema information for the table
cursor.execute("PRAGMA table_info(trade_blotter)")
columns = cursor.fetchall()


# Print the column names
print("Schema for trade_blotter table:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Retrieve the schema information for the table
cursor.execute("PRAGMA table_info(traders)")
columns = cursor.fetchall()

# Print the column names
print("Schema for traders table:")
for column in columns:
    print(f"Column: {column[1]}, Type: {column[2]}")


# Close the connection when done
connection.close()
