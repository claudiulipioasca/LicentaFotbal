import sqlite3
import pandas as pd


def genereaza_tablou_final():
    conn = sqlite3.connect('fotbal_app.db')

    date_flashscore = [
        {"faza": "saisprezecimi", "echipa1": "Monaco", "scor1": "2-2", "echipa2": "Paris SG", "scor2": "3-2",
         "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Chelsea", "scor1": "BYE", "echipa2": "-", "scor2": "-",
         "status": "Calificată"},

        {"faza": "saisprezecimi", "echipa1": "Galatasaray", "scor1": "3-4", "echipa2": "Juventus", "scor2": "2-1",
         "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Liverpool", "scor1": "BYE", "echipa2": "-", "scor2": "-",
         "status": "Calificată"},

        {"faza": "saisprezecimi", "echipa1": "Benfica", "scor1": "0-1", "echipa2": "Real Madrid", "scor2": "1-2",
         "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Man City", "scor1": "BYE", "echipa2": "-", "scor2": "-",
         "status": "Calificată"},

        {"faza": "saisprezecimi", "echipa1": "Dortmund", "scor1": "1-2", "echipa2": "Atalanta", "scor2": "2-2",
         "status": "Finalizat"},
        {"faza": "saisprezecimi", "echipa1": "Bayern Munich", "scor1": "BYE", "echipa2": "-", "scor2": "-",
         "status": "Calificată"},

        {"faza": "optimi", "echipa1": "Paris SG", "scor1": "1", "echipa2": "Chelsea", "scor2": "0",
         "status": "Doar Tur"},
        {"faza": "optimi", "echipa1": "Galatasaray", "scor1": "0", "echipa2": "Liverpool", "scor2": "2",
         "status": "Doar Tur"},
        {"faza": "optimi", "echipa1": "Real Madrid", "scor1": "1", "echipa2": "Man City", "scor2": "1",
         "status": "Doar Tur"},
        {"faza": "optimi", "echipa1": "Atalanta", "scor1": "0", "echipa2": "Bayern Munich", "scor2": "3",
         "status": "Doar Tur"},
    ]

    df = pd.DataFrame(date_flashscore)
    df.to_sql('ucl_knockout', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Baza de date a fost actualizată cu scoruri Tur-Retur!")


if __name__ == '__main__':
    genereaza_tablou_final()