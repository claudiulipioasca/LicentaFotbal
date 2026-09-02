def genereaza_bracket_real_2026():
    print("⏳ Actualizăm Tabloul REAL UCL cu rezultatele din Martie 2026...")
    conn = sqlite3.connect('fotbal_app.db')

    date_reale = [
        {"faza": "saisprezecimi", "echipa1": "Monaco", "scor1": "4", "echipa2": "Paris SG", "scor2": "5", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Galatasaray", "scor1": "7", "echipa2": "Juventus", "scor2": "5", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Benfica", "scor1": "1", "echipa2": "Real Madrid", "scor2": "3", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Dortmund", "scor1": "3", "echipa2": "Atalanta", "scor2": "4", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Qarabağ", "scor1": "3", "echipa2": "Newcastle", "scor2": "9", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Club Brugge", "scor1": "4", "echipa2": "Ath Madrid", "scor2": "7", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Bodø/Glimt", "scor1": "5", "echipa2": "Inter", "scor2": "2", "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Olympiacos", "scor1": "0", "echipa2": "Leverkusen", "scor2": "2", "status": "Finalizat"},

        {"faza": "optimi", "echipa1": "Paris SG", "scor1": "5", "echipa2": "Chelsea", "scor2": "2", "status": "Retur 17 Mar"},
        {"faza": "optimi", "echipa1": "Galatasaray", "scor1": "1", "echipa2": "Liverpool", "scor2": "0", "status": "Retur 18 Mar"},
        {"faza": "optimi", "echipa1": "Real Madrid", "scor1": "3", "echipa2": "Man City", "scor2": "0", "status": "Retur 17 Mar"},
        {"faza": "optimi", "echipa1": "Atalanta", "scor1": "1", "echipa2": "Bayern Munich", "scor2": "6", "status": "Retur 18 Mar"},
        {"faza": "optimi", "echipa1": "Newcastle", "scor1": "1", "echipa2": "Barcelona", "scor2": "1", "status": "Retur 18 Mar"},
        {"faza": "optimi", "echipa1": "Ath Madrid", "scor1": "5", "echipa2": "Tottenham", "scor2": "2", "status": "Retur 18 Mar"},
        {"faza": "optimi", "echipa1": "Bodø/Glimt", "scor1": "3", "echipa2": "Sporting", "scor2": "0", "status": "Retur 17 Mar"},
        {"faza": "optimi", "echipa1": "Leverkusen", "scor1": "1", "echipa2": "Arsenal", "scor2": "1", "status": "Retur 17 Mar"},

        # --- FAZE VIITOARE ---
        {"faza": "sferturi", "echipa1": "Nedeterminat", "scor1": "-", "echipa2": "Nedeterminat", "scor2": "-", "status": "Aprilie"},
        {"faza": "semifinale", "echipa1": "Nedeterminat", "scor1": "-", "echipa2": "Nedeterminat", "scor2": "-", "status": "Mai"},
        {"faza": "finala", "echipa1": "Nedeterminat", "scor1": "-", "echipa2": "Nedeterminat", "scor2": "-", "status": "Budapesta"}
    ]

    df_knockout = pd.DataFrame(date_reale)
    df_knockout.to_sql('ucl_knockout', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Succes! Rezultatele din optimi (tur) au fost introduse.")