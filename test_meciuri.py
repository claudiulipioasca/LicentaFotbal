import pandas as pd

url_csv = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"

print("Descarcam istoricul meciurilor si statisticile detaliate...\n")

meciuri = pd.read_csv(url_csv)

print("SUCCES: Am descarcat toate meciurile jucate pana acum!\n")
coloane_selectate = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HS', 'AS', 'HC', 'AC']

print("--- ULTIMELE 5 MECIURI JUCATE ---")
print(meciuri[coloane_selectate].tail(5).to_string(index=False))