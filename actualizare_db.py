import pandas as pd
import sqlite3

ligi = {
    "premier_league": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "la_liga": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "serie_a": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "bundesliga": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "ligue_1": "https://www.football-data.co.uk/mmz4281/2526/F1.csv"
}

print("Incepem REPARAREA clasamentelor...")
conn = sqlite3.connect('fotbal_app.db')

for id_liga, url in ligi.items():
    try:
        df = pd.read_csv(url)
        coloane = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'AS', 'HC', 'AC', 'HST', 'AST', 'HF', 'AF',
                   'HY', 'AY', 'HR', 'AR']
        df_meciuri = df[[c for c in coloane if c in df.columns]].copy()

        redenumiri = {'Date': 'Data', 'HomeTeam': 'Echipa_Gazda', 'AwayTeam': 'Echipa_Oaspete', 'FTHG': 'Goluri_Gazda',
                      'FTAG': 'Goluri_Oaspete', 'HS': 'Suturi_Gazda', 'AS': 'Suturi_Oaspete', 'HC': 'Cornere_Gazda',
                      'AC': 'Cornere_Oaspete', 'HST': 'Suturi_Pe_Poarta_Gazda', 'AST': 'Suturi_Pe_Poarta_Oaspete',
                      'HF': 'Falturi_Gazda', 'AF': 'Falturi_Oaspete', 'HY': 'Cartonase_Galbene_Gazda',
                      'AY': 'Cartonase_Galbene_Oaspete', 'HR': 'Cartonase_Rosii_Gazda', 'AR': 'Cartonase_Rosii_Oaspete'}
        df_meciuri.rename(columns=redenumiri, inplace=True)
        df_meciuri.to_sql(f"meciuri_{id_liga}", conn, if_exists='replace', index=False)

        echipe = pd.concat([df_meciuri['Echipa_Gazda'], df_meciuri['Echipa_Oaspete']]).unique()
        clasament = []

        for echipa in echipe:
            acasa = df_meciuri[df_meciuri['Echipa_Gazda'] == echipa]
            deplasare = df_meciuri[df_meciuri['Echipa_Oaspete'] == echipa]

            v = len(acasa[acasa['Goluri_Gazda'] > acasa['Goluri_Oaspete']]) + len(
                deplasare[deplasare['Goluri_Oaspete'] > deplasare['Goluri_Gazda']])
            e = len(acasa[acasa['Goluri_Gazda'] == acasa['Goluri_Oaspete']]) + len(
                deplasare[deplasare['Goluri_Oaspete'] == deplasare['Goluri_Gazda']])
            i = len(acasa[acasa['Goluri_Gazda'] < acasa['Goluri_Oaspete']]) + len(
                deplasare[deplasare['Goluri_Oaspete'] < deplasare['Goluri_Gazda']])
            gm = int(acasa['Goluri_Gazda'].sum() + deplasare['Goluri_Oaspete'].sum())
            gp = int(acasa['Goluri_Oaspete'].sum() + deplasare['Goluri_Gazda'].sum())
            gd = gm - gp  # Golaveraj
            puncte = (v * 3) + (e * 1)

            clasament.append(
                {'Echipa': echipa, 'Meciuri': v + e + i, 'V': v, 'E': e, 'Î': i, 'GM': gm, 'GP': gp, 'Golaveraj': gd,
                 'Puncte': puncte})

        df_clasament = pd.DataFrame(clasament).sort_values(by=['Puncte', 'Golaveraj', 'GM'],
                                                           ascending=[False, False, False]).reset_index(drop=True)
        df_clasament.index += 1
        df_clasament.reset_index(inplace=True)
        df_clasament.rename(columns={'index': 'Loc'}, inplace=True)

        df_clasament.to_sql(id_liga, conn, if_exists='replace', index=False)
    except Exception as err:
        print(f"Eroare la {id_liga}: {err}")

conn.close()
print("Gata! Baza de date este complet refacuta si corecta!")