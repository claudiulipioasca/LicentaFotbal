import pandas as pd
import requests
from io import StringIO
import sqlite3

MAPARE_ECHIPE = {
    "Manchester City": "Man City", "Manchester United": "Man United",
    "Tottenham Hotspur": "Tottenham", "Newcastle United": "Newcastle",
    "Wolverhampton Wanderers": "Wolves", "Nottingham Forest": "Nott'm Forest",
    "West Ham United": "West Ham", "Brighton and Hove Albion": "Brighton",
    "Real Madrid": "Real Madrid", "Real Betis": "Betis", "Real Sociedad": "Sociedad",
    "Real Valladolid": "Valladolid", "Celta Vigo": "Celta", "Athletic Bilbao": "Ath Bilbao",
    "Atletico Madrid": "Ath Madrid", "Paris Saint-Germain": "Paris SG",
    "Olympique de Marseille": "Marseille", "Olympique Lyonnais": "Lyon", "Paris FC": "Paris FC",
    "AC Milan": "Milan", "Internazionale": "Inter", "Juventus": "Juventus", "Roma": "Roma",
    "Bayern Munich": "Bayern Munich", "Borussia Dortmund": "Dortmund", "Bayer Leverkusen": "Leverkusen",
    "Napoli": "Napoli", "St Pauli": "St Pauli"
}


def obtine_nume_oficial(nume_echipa_site):
    return MAPARE_ECHIPE.get(nume_echipa_site, nume_echipa_site)


def actualizeaza_ucl_real():
    print("⏳ Se descarcă clasamentul UEFA Champions League (Faza Ligii)...")
    url = "https://www.skysports.com/champions-league-table"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"❌ EROARE: SkySports a răspuns cu codul {response.status_code}")
            return

        html_data = StringIO(response.text)
        tabele = pd.read_html(html_data)

        if not tabele:
            print("❌ EROARE: Nu s-a găsit niciun tabel pe pagină.")
            return

        df_clasament = tabele[0]

        df_clasament = df_clasament.dropna(axis=1, how='all')

        col_echipa = df_clasament.columns[1]

        df_clasament[col_echipa] = df_clasament[col_echipa].apply(obtine_nume_oficial)

        conn = sqlite3.connect('fotbal_app.db')
        df_clasament.to_sql('champions_league', conn, if_exists='replace', index=False)

        df_meciuri_gol = pd.DataFrame(columns=[
            'Data', 'Echipa_Gazda', 'Echipa_Oaspete', 'Goluri_Gazda', 'Goluri_Oaspete',
            'Suturi_Gazda', 'Suturi_Oaspete', 'Cornere_Gazda', 'Cornere_Oaspete',
            'Suturi_Pe_Poarta_Gazda', 'Suturi_Pe_Poarta_Oaspete', 'Falturi_Gazda', 'Falturi_Oaspete',
            'Cartonase_Galbene_Gazda', 'Cartonase_Galbene_Oaspete', 'Cartonase_Rosii_Gazda', 'Cartonase_Rosii_Oaspete'
        ])
        df_meciuri_gol.to_sql('meciuri_champions_league', conn, if_exists='replace', index=False)
        conn.close()

        print(f"✅ SUCCES TOTAL! Au fost găsite {len(df_clasament)} echipe. Salvare în fotbal_app.db efectuată!")
        print("\n🏆 Top 5 Champions League:")
        print(df_clasament.head(5).to_string(index=False))

    except Exception as e:
        print(f"❌ Eroare la extragerea datelor: {e}")


if __name__ == '__main__':
    actualizeaza_ucl_real()