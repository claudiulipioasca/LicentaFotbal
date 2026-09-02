import pandas as pd
import sqlite3


conn = sqlite3.connect('fotbal_app.db')

clasament_citit = pd.read_sql("SELECT * FROM la_liga", conn)

print("--- DATE CITITE DIN BAZA DE DATE ---")
print(clasament_citit.head())

conn.close()