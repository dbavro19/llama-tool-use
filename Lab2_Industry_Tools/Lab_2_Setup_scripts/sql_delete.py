import sqlite3
import os

# Get the parent directory of the current script's directory
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the path to the database file in the parent directory
db_file = os.path.join(parent_directory, 'test_database.db')

# Ensure all connections are closed
try:
    connection = sqlite3.connect(db_file)
    connection.close()
except Exception as e:
    print("Error closing the connection:", e)

# Delete the database file if it exists in the parent directory
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"{db_file} has been deleted.")
else:
    print(f"{db_file} does not exist.")
