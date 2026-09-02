import pandas as pd
import requests
from io import StringIO
import sqlite3
import time
import random

ligi_sky_sports = {
    "premier_league": "https://www.skysports.com/premier-league-table",
    "la_liga": "https://www.skysports.com/la-liga-table",
    "serie_a": "https://www.skysports.com/serie-a-table",
    "bundesliga": "https://www.skysports.com/bundesliga-table",
    "ligue_1": "https://www.skysports.com/ligue-1-table"
}

url_superliga = "https://www.gsp.ro/rezultate-live/clasamente/18-superliga"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

conn = sqlite3.connect('fotbal_app.db')

print("--- INCEPEM ACTUALIZAREA CELOR 6 LIGI --- \n")

session = requests.Session()

for nume_tabel, url in ligi_sky_sports.items():
    print(f"Extragem datele pentru: {nume_tabel.upper().replace('_', ' ')}...")

    succes = False
    for incercare in range(3):
        headers = {"User-Agent": random.choice(user_agents)}
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            try:
                html_data = StringIO(response.text)
                tabele = pd.read_html(html_data)
                clasament = tabele[0]
                clasament.to_sql(nume_tabel, conn, if_exists='replace', index=False)
                print(f"-> Succes! Salvat in tabelul '{nume_tabel}'.\n")
                succes = True
                break
            except ValueError:
                print(f"-> [Incercarea {incercare + 1}/3] Tabel negasit, reincercam...")
        else:
            print(f"-> [Incercarea {incercare + 1}/3] Eroare {response.status_code}, reincercam...")

        time.sleep(3)

    if not succes:
        print(f"-> EROARE CRITICA la {nume_tabel}. Nu s-a putut descarca!\n")

print("Extragem datele pentru: SUPERLIGA ROMANIEI...")
headers_ro = {"User-Agent": user_agents[0]}
response_ro = session.get(url_superliga, headers=headers_ro)

if response_ro.status_code == 200:
    html_data_ro = StringIO(response_ro.text)
    tabele_ro = pd.read_html(html_data_ro)
    clasament_ro = tabele_ro[0]

    clasament_ro.to_sql('superliga', conn, if_exists='replace', index=False)
    print("-> Succes! Salvat in tabelul 'superliga'.\n")
else:
    print(f"-> EROARE la Superliga: Cod {response_ro.status_code}\n")

conn.close()

print("----- ACTUALIZARE COMPLETA -----")
print("Toate cele 6 clasamente sunt acum la zi in baza de date!")