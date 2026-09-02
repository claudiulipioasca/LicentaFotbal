import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib


def pregateste_si_antreneaza():
    print("⏳ Se extrag datele din baza de date...")
    conn = sqlite3.connect('fotbal_app.db')
    ligi = ["premier_league", "la_liga", "serie_a", "bundesliga", "ligue_1"]
    toate_meciurile = []

    # 1. Colectăm toate meciurile
    for liga in ligi:
        try:
            df = pd.read_sql(f"SELECT * FROM meciuri_{liga}", conn)
            df = df.dropna(subset=['Goluri_Gazda', 'Goluri_Oaspete'])
            toate_meciurile.append(df)
        except Exception:
            pass

    df_complet = pd.concat(toate_meciurile, ignore_index=True)

    # 2. Calculăm mediile pe sezon (Puncte/meci și Goluri date/meci)
    stats = {}
    for _, rand in df_complet.iterrows():
        g_gazda, g_oaspete = rand['Echipa_Gazda'], rand['Echipa_Oaspete']
        gol_g, gol_o = float(rand['Goluri_Gazda']), float(rand['Goluri_Oaspete'])

        for echipa in [g_gazda, g_oaspete]:
            if echipa not in stats:
                stats[echipa] = {'meciuri': 0, 'puncte': 0, 'goluri': 0}

        stats[g_gazda]['meciuri'] += 1
        stats[g_oaspete]['meciuri'] += 1
        stats[g_gazda]['goluri'] += gol_g
        stats[g_oaspete]['goluri'] += gol_o

        if gol_g > gol_o:
            stats[g_gazda]['puncte'] += 3
        elif gol_g == gol_o:
            stats[g_gazda]['puncte'] += 1
            stats[g_oaspete]['puncte'] += 1
        else:
            stats[g_oaspete]['puncte'] += 3

    def get_medii(echipa):
        if echipa in stats and stats[echipa]['meciuri'] > 0:
            return stats[echipa]['puncte'] / stats[echipa]['meciuri'], stats[echipa]['goluri'] / stats[echipa][
                'meciuri']
        return 1.0, 1.0


    X, y = [], []
    for _, rand in df_complet.iterrows():
        gol_g, gol_o = float(rand['Goluri_Gazda']), float(rand['Goluri_Oaspete'])

        pct_g, med_gol_g = get_medii(rand['Echipa_Gazda'])
        pct_o, med_gol_o = get_medii(rand['Echipa_Oaspete'])

        if gol_g > gol_o:
            rezultat = 1
        elif gol_g == gol_o:
            rezultat = 0
        else:
            rezultat = 2

        y.append(rezultat)
        X.append([pct_g, med_gol_g, pct_o, med_gol_o])

    print(" Se antrenează Noul Model Random Forest...")
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)

    joblib.dump(model, 'model_fotbal.pkl')
    print(" Model salvat cu noile reguli!")


if __name__ == "__main__":
    pregateste_si_antreneaza()