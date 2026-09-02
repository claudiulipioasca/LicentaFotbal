import pandas as pd
import sqlite3

conn = sqlite3.connect('fotbal_app.db')

fisiere_csv = {
    "meciuri_premier_league": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "meciuri_la_liga": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
    "meciuri_serie_a": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
    "meciuri_bundesliga": "https://www.football-data.co.uk/mmz4281/2627/D1.csv",
    "meciuri_ligue_1": "https://www.football-data.co.uk/mmz4281/2627/F1.csv"
}

coloane_dorite = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'AS', 'HC', 'AC',
                  'HST', 'AST', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR']

print("--- INCEPEM DESCARCAREA MECIURILOR --- \n")

for nume_tabel, url in fisiere_csv.items():
    print(f"Procesam: {nume_tabel} ...")
    df = pd.read_csv(url)

    coloane_disponibile = [c for c in coloane_dorite if c in df.columns]
    df_curat = df[coloane_disponibile].dropna(subset=['HomeTeam'])

    redenumiri = {
        'Date': 'Data', 'HomeTeam': 'Echipa_Gazda', 'AwayTeam': 'Echipa_Oaspete',
        'FTHG': 'Goluri_Gazda', 'FTAG': 'Goluri_Oaspete',
        'HS': 'Suturi_Gazda', 'AS': 'Suturi_Oaspete',
        'HC': 'Cornere_Gazda', 'AC': 'Cornere_Oaspete',
        'HST': 'Suturi_Pe_Poarta_Gazda', 'AST': 'Suturi_Pe_Poarta_Oaspete',
        'HF': 'Falturi_Gazda', 'AF': 'Falturi_Oaspete',
        'HY': 'Cartonase_Galbene_Gazda', 'AY': 'Cartonase_Galbene_Oaspete',
        'HR': 'Cartonase_Rosii_Gazda', 'AR': 'Cartonase_Rosii_Oaspete'
    }
    df_curat.rename(columns=redenumiri, inplace=True)

    df_curat.to_sql(nume_tabel, conn, if_exists='replace', index=False)
    print(f" -> Salvat cu succes in '{nume_tabel}'!")

conn.close()
print("\n----- ACTUALIZARE COMPLETA! -----")