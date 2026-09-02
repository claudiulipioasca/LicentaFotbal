from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
import requests
import datetime
from datetime import datetime as dt, timedelta
import joblib
import os
import numpy as np
import shap
import json

app = Flask(__name__)

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

LIGI_DISPONIBILE = {
    "premier_league": "Premier League", "la_liga": "La Liga",
    "serie_a": "Serie A", "bundesliga": "Bundesliga",
    "ligue_1": "Ligue 1", "champions_league": "Champions League"
}

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


def obtine_id_echipa_espn(nume_oficial, id_liga):
    coduri_espn = {"premier_league": "eng.1", "la_liga": "esp.1", "serie_a": "ita.1", "bundesliga": "ger.1",
                   "ligue_1": "fra.1", "champions_league": "uefa.champions"}

    cod = coduri_espn.get(id_liga)
    if not cod: return None, None
    corecturi_espn = {"Nott'm Forest": "nottingham forest", "Man City": "manchester city",
                      "Man United": "manchester united", "Paris SG": "paris saint-germain",
                      "Ath Bilbao": "athletic club", "Ath Madrid": "atlético madrid", "St Pauli": "st pauli"}
    nume_cautat = corecturi_espn.get(nume_oficial, nume_oficial).lower()
    nume_cautat_curat = nume_cautat.replace('.', '').replace('-', ' ')
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/teams"
        resp = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()
        for t in resp['sports'][0]['leagues'][0]['teams']:
            if nume_cautat_curat == t['team']['name'].lower().replace('.', '').replace('-', ' '): return t['team'][
                'id'], cod
        for t in resp['sports'][0]['leagues'][0]['teams']:
            if nume_cautat_curat in t['team']['name'].lower().replace('.', '').replace('-', ' '): return t['team'][
                'id'], cod
    except:
        pass
    return None, cod

CACHE_LOGOURI = {}
CACHE_INITIALIZAT = False


def incarca_toate_logourile():
    global CACHE_INITIALIZAT
    if CACHE_INITIALIZAT:
        return

    print("⏳ Se descarcă baza de date cu sigle în memorie...")
    coduri_espn = ["eng.1", "esp.1", "ita.1", "ger.1", "fra.1", "rou.1", "uefa.champions"]

    for cod in coduri_espn:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/teams"
            resp = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()
            for t in resp['sports'][0]['leagues'][0]['teams']:
                nume_espn = t['team']['name'].lower().replace('.', '').replace('-', ' ')
                logo = t['team']['logos'][0]['href'] if 'logos' in t['team'] and len(t['team']['logos']) > 0 else ""
                if logo: CACHE_LOGOURI[nume_espn] = logo
        except Exception as e:
            pass

    sigle_ro = {
        "fcsb": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/FCSB_logo.svg/1200px-FCSB_logo.svg.png",
        "cfr cluj": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/CFR_Cluj_logo.svg/1200px-CFR_Cluj_logo.svg.png",
        "rapid bucuresti": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/FC_Rapid_București_logo.svg/1200px-FC_Rapid_București_logo.svg.png",
        "universitatea craiova": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1d/CS_Universitatea_Craiova_logo.svg/1200px-CS_Universitatea_Craiova_logo.svg.png",
        "dinamo bucuresti": "https://upload.wikimedia.org/wikipedia/en/thumb/1/19/FC_Dinamo_București_logo.svg/1200px-FC_Dinamo_București_logo.svg.png",
        "farul constanta": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/FCV_Farul_Constanța_logo.svg/1200px-FCV_Farul_Constanța_logo.svg.png",
        "sepsi": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5a/Sepsi_OSK_Sfântu_Gheorghe_logo.svg/1200px-Sepsi_OSK_Sfântu_Gheorghe_logo.svg.png",
        "uta arad": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4f/FC_UTA_Arad_logo.svg/1200px-FC_UTA_Arad_logo.svg.png",
        "u cluj": "https://upload.wikimedia.org/wikipedia/en/thumb/8/87/FC_Universitatea_Cluj_logo.svg/1200px-FC_Universitatea_Cluj_logo.svg.png",
        "petrolul ploiesti": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/FC_Petrolul_Ploiești_logo.svg/1200px-FC_Petrolul_Ploiești_logo.svg.png",
        "hermannstadt": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a9/FC_Hermannstadt_logo.svg/1200px-FC_Hermannstadt_logo.svg.png",
        "fc botosani": "https://upload.wikimedia.org/wikipedia/en/thumb/2/25/FC_Botoșani_logo.svg/1200px-FC_Botoșani_logo.svg.png",
        "poli iasi": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/FC_Politehnica_Iași_logo.svg/1200px-FC_Politehnica_Iași_logo.svg.png",
        "otelul galati": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/ASC_Oțelul_Galați_logo.svg/1200px-ASC_Oțelul_Galați_logo.svg.png",
        "unirea slobozia": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e6/FC_Unirea_Slobozia_logo.svg/1200px-FC_Unirea_Slobozia_logo.svg.png",
        "gloria buzau": "https://upload.wikimedia.org/wikipedia/ro/thumb/0/07/GloriaBuzau-2022.png/120px-GloriaBuzau-2022.png"
    }
    CACHE_LOGOURI.update(sigle_ro)

    CACHE_INITIALIZAT = True
    print("✅ Toate siglele au fost încărcate instant!")


def extrage_logo(nume_echipa):
    if "Nedeterminat" in nume_echipa:
        return ""

    incarca_toate_logourile()

    corecturi_espn = {"Nott'm Forest": "nottingham forest", "Man City": "manchester city",
                      "Man United": "manchester united", "Paris SG": "paris saint-germain",
                      "Ath Bilbao": "athletic club", "Ath Madrid": "atlético madrid", "St Pauli": "st pauli"}

    nume_cautat = corecturi_espn.get(nume_echipa, nume_echipa).lower().replace('.', '').replace('-', ' ')

    if nume_cautat in CACHE_LOGOURI:
        return CACHE_LOGOURI[nume_cautat]

    for nume_espn, logo in CACHE_LOGOURI.items():
        if nume_cautat in nume_espn or nume_espn in nume_cautat:
            return logo

    return "https://cdn-icons-png.flaticon.com/512/871/871372.png"


def extrage_lot_real(nume_oficial, id_liga):
    team_id, cod = obtine_id_echipa_espn(nume_oficial, id_liga)
    if not team_id: return None
    try:
        url_lot = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/teams/{team_id}/roster"
        resp_lot = requests.get(url_lot, headers=HEADERS_BROWSER, timeout=5).json()
        jucatori = []
        if 'athletes' in resp_lot:
            for element in resp_lot['athletes']:
                if 'items' in element:
                    for j in element['items']: jucatori.append(
                        {"Număr": str(j.get('jersey', '-')), "Nume Jucător": j.get('fullName', 'Necunoscut'),
                         "Poziție": j.get('position', {}).get('name', '-'), "Vârstă": str(j.get('age', '-'))})
                elif 'fullName' in element:
                    jucatori.append({"Număr": str(element.get('jersey', '-')),
                                     "Nume Jucător": element.get('fullName', 'Necunoscut'),
                                     "Poziție": element.get('position', {}).get('name', '-'),
                                     "Vârstă": str(element.get('age', '-'))})
        if jucatori: return pd.DataFrame(jucatori)
    except:
        pass
    return None


def extrage_urmatorul_meci_real(nume_oficial, liga_curenta):
    coduri_espn = {"premier_league": "eng.1", "la_liga": "esp.1", "serie_a": "ita.1", "bundesliga": "ger.1",
                   "ligue_1": "fra.1", "champions_league": "uefa.champions"}

    cod = coduri_espn.get(liga_curenta)
    if not cod: return nume_oficial, "Nedeterminat"
    nume_cautat = obtine_nume_oficial(nume_oficial).lower().replace('.', '').replace('-', ' ')
    try:
        azi = datetime.datetime.now()
        viitor = azi + datetime.timedelta(days=30)
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/scoreboard?dates={azi.strftime('%Y%m%d')}-{viitor.strftime('%Y%m%d')}"
        date_json = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()
        for eveniment in date_json.get('events', []):
            competitori = eveniment['competitions'][0]['competitors']
            nume_gazda = competitori[0]['team']['name'].lower().replace('.', '').replace('-', ' ')
            nume_oaspete = competitori[1]['team']['name'].lower().replace('.', '').replace('-', ' ')
            if nume_cautat in nume_gazda or nume_cautat in nume_oaspete:
                gazda = competitori[0]['team']['name'] if competitori[0]['homeAway'] == 'home' else \
                competitori[1]['team']['name']
                oaspete = competitori[1]['team']['name'] if competitori[1]['homeAway'] == 'away' else \
                competitori[0]['team']['name']
                return gazda, oaspete
    except:
        pass
    return nume_oficial, "Nedeterminat"


def extrage_statistici_jucatori(nume_oficial, id_liga):
    team_id, cod = obtine_id_echipa_espn(nume_oficial, id_liga)
    golgheter_nume, golgheter_goluri, pasator_nume, pasator_pase = None, 0, None, 0

    if team_id:
        try:
            url_stats = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/statistics?limit=200"
            resp_stats = requests.get(url_stats, headers=HEADERS_BROWSER, timeout=5).json()

            for stat in resp_stats.get('stats', []):
                n_stat = stat.get('name', '').lower()

                if n_stat in ['scoring', 'goals']:
                    for leader in stat.get('leaders', []):
                        t_info = leader.get('team', {})
                        if not t_info and 'athlete' in leader:
                            t_info = leader['athlete'].get('team', {})

                        if str(t_info.get('id')) == str(team_id) and golgheter_nume is None:
                            golgheter_nume = leader['athlete']['fullName']
                            golgheter_goluri = int(leader['value'])

                elif 'assist' in n_stat:
                    for leader in stat.get('leaders', []):
                        t_info = leader.get('team', {})
                        if not t_info and 'athlete' in leader:
                            t_info = leader['athlete'].get('team', {})

                        if str(t_info.get('id')) == str(team_id) and pasator_nume is None:
                            pasator_nume = leader['athlete']['fullName']
                            pasator_pase = int(leader['value'])
        except Exception as e:
            print(f"Eroare extragere lideri echipa: {e}")

    if not golgheter_nume:
        golgheter_nume = "Niciun marcator"
        golgheter_goluri = 0

    if not pasator_nume:
        pasator_nume = "Niciun pasator"
        pasator_pase = 0

    return golgheter_nume, golgheter_goluri, pasator_nume, pasator_pase

def obtine_toate_echipele():
    conn = sqlite3.connect('fotbal_app.db')
    echipe = set()
    for id_liga in LIGI_DISPONIBILE.keys():
        try:
            df = pd.read_sql(f"SELECT Echipa_Gazda FROM meciuri_{id_liga}", conn)
            echipe.update(df['Echipa_Gazda'].dropna().unique())
        except:
            pass
    conn.close()
    return sorted(list(echipe))


@app.route('/')
def pagina_principala():
    echipe_cautare = obtine_toate_echipele()
    return render_template('index.html', ligi=LIGI_DISPONIBILE, tabel_html=None, liga_curenta=None,
                           echipe=echipe_cautare)


@app.route('/liga/<id_tabel>')
def afiseaza_liga(id_tabel):
    tip_vizualizare = request.args.get('view', 'league')
    vizualizare = request.args.get('view', 'league')

    if id_tabel == "champions_league" and vizualizare == "knockout":
        conn = sqlite3.connect('fotbal_app.db')
        try:
            df_ko = pd.read_sql("SELECT * FROM ucl_knockout", conn)

            def pregateste_faza(nume_faza):
                meciuri_faza = df_ko[df_ko['faza'] == nume_faza].to_dict('records')
                for m in meciuri_faza:
                    m['logo1'] = extrage_logo(m['echipa1'])
                    m['logo2'] = extrage_logo(m['echipa2'])
                return meciuri_faza

            bracket_data = {
                "saisprezecimi": pregateste_faza('saisprezecimi'),
                "optimi": pregateste_faza('optimi'),
                "sferturi": pregateste_faza('sferturi'),
                "semifinale": pregateste_faza('semifinale'),
                "finala": pregateste_faza('finala')
            }
        except Exception as e:
            print(f"Eroare citire knockout: {e}")
            bracket_data = {"optimi": [], "sferturi": [], "semifinale": [], "finala": []}

        conn.close()

        return render_template(
            'ucl_knockout.html',
            ligi=LIGI_DISPONIBILE,
            liga_curenta=LIGI_DISPONIBILE[id_tabel],
            id_liga=id_tabel,
            bracket=bracket_data
        )
    if id_tabel not in LIGI_DISPONIBILE: return "Eroare!"
    conn = sqlite3.connect('fotbal_app.db')
    df = pd.read_sql(f"SELECT * FROM {id_tabel}", conn)
    conn.close()

    if 'Echipa' in df.columns:
        col_echipa = 'Echipa'
    else:
        col_echipa = df.columns[1]

    total_echipe = len(df)

    def coloreaza_pozitia(loc):
        try:
            loc = int(loc)
        except:
            return loc

        clasa_css = ""
        if loc <= 4:
            clasa_css = "bg-primary text-white"  # Albastru (Champions League)
        elif loc == 5:
            clasa_css = "bg-warning text-dark"  # Galben (Europa League)
        elif loc == 6:
            clasa_css = "bg-success text-white"  # Verde (Conference League)
        elif loc > total_echipe - 3:
            clasa_css = "bg-danger text-white"  # Roșu (Retrogradare - ultimele 3 locuri)

        if clasa_css:
            return f'<span class="badge {clasa_css} fs-6 w-100 py-2 shadow-sm" style="min-width: 35px;">{loc}</span>'
        return f'<span class="badge bg-secondary fs-6 w-100 py-2 text-light" style="min-width: 35px; opacity: 0.7;">{loc}</span>'

    nume_col_loc = df.columns[0]
    df[nume_col_loc] = df[nume_col_loc].apply(coloreaza_pozitia)

    nume_col_loc = df.columns[0]
    df[nume_col_loc] = df[nume_col_loc].apply(coloreaza_pozitia)

    coduri_espn = {
        "premier_league": "eng.1",
        "la_liga": "esp.1",
        "serie_a": "ita.1",
        "bundesliga": "ger.1",
        "ligue_1": "fra.1",
        "champions_league": "uefa.champions"
    }
    cod = coduri_espn.get(id_tabel)
    dictionar_logouri = {}

    if cod:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/teams"
            resp = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()
            for t in resp['sports'][0]['leagues'][0]['teams']:
                nume_espn = t['team']['name'].lower().replace('.', '').replace('-', ' ')
                logo = t['team']['logos'][0]['href'] if 'logos' in t['team'] and len(t['team']['logos']) > 0 else ""
                dictionar_logouri[nume_espn] = logo
        except:
            pass

    def gaseste_logo(nume_echipa):
        corecturi_espn = {"Nott'm Forest": "nottingham forest", "Man City": "manchester city",
                          "Man United": "manchester united", "Paris SG": "paris saint-germain",
                          "Ath Bilbao": "athletic club", "Ath Madrid": "atlético madrid", "St Pauli": "st pauli"}
        nume_cautat = corecturi_espn.get(nume_echipa, nume_echipa).lower().replace('.', '').replace('-', ' ')

        if nume_cautat in dictionar_logouri:
            return dictionar_logouri[nume_cautat]
        for nume_espn, logo in dictionar_logouri.items():
            if nume_cautat in nume_espn or nume_espn in nume_cautat:
                return logo
        return "https://cdn-icons-png.flaticon.com/512/871/871372.png"

    df['Siglă'] = df[col_echipa].apply(
        lambda echipa: f'<img src="{gaseste_logo(echipa)}" width="30" height="30" style="object-fit: contain;">')

    cols = df.columns.tolist()
    cols.insert(cols.index(col_echipa), cols.pop(cols.index('Siglă')))
    df = df[cols]
    df[col_echipa] = df[col_echipa].apply(lambda
                                              echipa: f'<a href="/echipa/{id_tabel}/{echipa}" class="text-success fw-bold text-decoration-none fs-5">{echipa}</a>')

    tabel_html = df.to_html(classes="table table-dark table-striped table-hover m-0 align-middle text-center",
                            justify='center', index=False, escape=False)
    tabel_html = tabel_html.replace('style="text-align: right;"', '')

    echipe_cautare = obtine_toate_echipele()
    return render_template('index.html', ligi=LIGI_DISPONIBILE, tabel_html=tabel_html,
                           liga_curenta=LIGI_DISPONIBILE[id_tabel], echipe=echipe_cautare, id_liga=id_tabel)

@app.route('/cauta')
def cauta_echipa():
    query = request.args.get('q', '').strip().lower()
    if not query: return redirect('/')

    conn = sqlite3.connect('fotbal_app.db')
    for id_liga in LIGI_DISPONIBILE.keys():
        try:
            df = pd.read_sql(f"SELECT Echipa_Gazda FROM meciuri_{id_liga}", conn)
            echipe_din_liga = df['Echipa_Gazda'].dropna().unique()
            for echipa in echipe_din_liga:
                if query == echipa.lower():
                    conn.close()
                    return redirect(f'/echipa/{id_liga}/{echipa}')
            for echipa in echipe_din_liga:
                if query in echipa.lower():
                    conn.close()
                    return redirect(f'/echipa/{id_liga}/{echipa}')
        except:
            pass
    conn.close()

    html_eroare = f"""
    <body style='background-color:#212529; color:white; text-align:center; font-family:sans-serif; padding-top:100px;'>
        <h1 style='color:#dc3545;'>Eroare 404: Echipa nu a fost găsită!</h1>
        <h3>Am căutat după: <b style='color:#ffc107;'>{query}</b></h3>
        <a href='/' style='padding: 10px 20px; background-color:#198754; color:white; text-decoration:none; border-radius:5px;'>← Înapoi</a>
    </body>
    """
    return html_eroare


@app.route('/echipa/<id_liga>/<nume_echipa>')
def pagina_echipa(id_liga, nume_echipa):
    tabel_meciuri = f"meciuri_{id_liga}"
    conn = sqlite3.connect('fotbal_app.db')
    try:
        df_toate_meciurile = pd.read_sql(f"SELECT * FROM {tabel_meciuri}", conn)
        nume_oficial = obtine_nume_oficial(nume_echipa)

        variante = [nume_echipa, nume_oficial]
        aliasuri = {
            "Manchester City": ["Man City", "City"],
            "Manchester United": ["Man United", "Man Utd"],
            "Wolverhampton Wanderers": ["Wolves", "Wolverhampton"],
            "Nottingham Forest": ["Nott'm Forest", "Nottingham Forrest", "Nottingham"],
            "Atletico Madrid": ["Ath Madrid", "Atlético Madrid"],
            "Paris Saint-Germain": ["Paris SG", "PSG", "Paris"],
            "Rennes FC": ["Rennes", "Stade Rennais"],
            "Real Oviedo": ["Oviedo"],
            "Real Mallorca": ["Mallorca"],
            "Rayo Vallecano": ["Rayo"],
            "Espanyol Barcelona": ["Espanyol"],
            "Athletic Club": ["Ath Bilbao", "Athletic Bilbao", "Bilbao"],
            "Leeds United": ["Leeds"],
            "Internazionale": ["Inter", "Inter Milan"],
            "TSG Hoffenheim": ["Hoffenheim"],
            "Eintracht Frankfurt": ["Frankfurt"],
            "SC Freiburg": ["Freiburg"],
            "1. FC Union Berlin": ["Union Berlin"],
            "FC Augsburg": ["Augsburg"],
            "Borussia Mönchengladbach": ["Gladbach", "Mönchengladbach"],
            "1. FC Köln": ["Koln", "Köln", "Cologne"],
            "1. FC Heidenheim 1846": ["Heidenheim"],
            "RC Lens": ["Lens"]
        }

        for cheie, lista_val in aliasuri.items():
            if nume_echipa.lower() in [v.lower() for v in
                                       lista_val] or nume_echipa.lower() == cheie.lower() or nume_oficial.lower() in [
                v.lower() for v in lista_val] or nume_oficial.lower() == cheie.lower():
                variante.append(cheie)
                variante.extend(lista_val)

        variante = list(set(variante))
        masca_gazda = df_toate_meciurile['Echipa_Gazda'].apply(
            lambda x: any(v.lower() == str(x).lower() for v in variante))
        masca_oaspete = df_toate_meciurile['Echipa_Oaspete'].apply(
            lambda x: any(v.lower() == str(x).lower() for v in variante))

        df_echipa = df_toate_meciurile[masca_gazda | masca_oaspete].copy()

        if df_echipa.empty:
            df_echipa = df_toate_meciurile[
                df_toate_meciurile['Echipa_Gazda'].str.contains(nume_oficial, case=False, na=False) |
                df_toate_meciurile['Echipa_Oaspete'].str.contains(nume_oficial, case=False, na=False)
                ].copy()

        df_echipa = df_echipa.dropna(subset=['Goluri_Gazda', 'Goluri_Oaspete'])

        meciuri_lista = []
        forma_echipa = []

        def format_stat(v):
            if pd.isna(v) or str(v).strip() in ['', '-']:
                return "-"
            try:
                return str(int(float(v)))
            except ValueError:
                return "-"

        try:
            df_echipa['Data'] = pd.to_datetime(df_echipa['Data'], format='%Y-%m-%d', errors='coerce')
        except:
            pass
        df_echipa = df_echipa.sort_values(by='Data', ascending=False)

        for _, rand in df_echipa.iterrows():
            try:
                g_gazda = int(float(rand['Goluri_Gazda']))
                g_oaspete = int(float(rand['Goluri_Oaspete']))
            except (ValueError, TypeError):
                continue

            scor_str = f"{g_gazda} - {g_oaspete}"
            este_gazda = any(v.lower() == str(rand['Echipa_Gazda']).lower() for v in variante) or (
                        nume_oficial.lower() in str(rand['Echipa_Gazda']).lower())

            if len(forma_echipa) < 5:
                if g_gazda == g_oaspete:
                    forma_echipa.append('E')
                elif (este_gazda and g_gazda > g_oaspete) or (not este_gazda and g_oaspete > g_gazda):
                    forma_echipa.append('V')
                else:
                    forma_echipa.append('I')

            meciuri_lista.append({
                'Data': rand.get('Data', str(rand.get('Data', ''))).strftime('%Y-%m-%d') if isinstance(rand.get('Data'),
                                                                                                       pd.Timestamp) else str(
                    rand.get('Data', '')),
                'Echipa_Gazda': rand.get('Echipa_Gazda', ''),
                'Echipa_Oaspete': rand.get('Echipa_Oaspete', ''),
                'Scor': scor_str,
                'Suturi_Gazda': format_stat(rand.get('Suturi_Gazda', '-')),
                'Suturi_Oaspete': format_stat(rand.get('Suturi_Oaspete', '-')),
                'Cornere_Gazda': format_stat(rand.get('Cornere_Gazda', '-')),
                'Cornere_Oaspete': format_stat(rand.get('Cornere_Oaspete', '-')),
                'Suturi_Poarta_Gazda': format_stat(
                    rand.get('Suturi_Pe_Poarta_Gazda', rand.get('Suturi_Poarta_Gazda', '-'))),
                'Suturi_Poarta_Oaspete': format_stat(
                    rand.get('Suturi_Pe_Poarta_Oaspete', rand.get('Suturi_Poarta_Oaspete', '-'))),
                'Falturi_Gazda': format_stat(rand.get('Falturi_Gazda', '-')),
                'Falturi_Oaspete': format_stat(rand.get('Falturi_Oaspete', '-')),
                'Galbene_Gazda': format_stat(rand.get('Cartonase_Galbene_Gazda', '-')),
                'Galbene_Oaspete': format_stat(rand.get('Cartonase_Galbene_Oaspete', '-')),
                'Rosii_Gazda': format_stat(rand.get('Cartonase_Rosii_Gazda', '-')),
                'Rosii_Oaspete': format_stat(rand.get('Cartonase_Rosii_Oaspete', '-'))
            })

        forma_echipa.reverse()

        gazda_viitor, oaspete_viitor = extrage_urmatorul_meci_real(nume_oficial, id_liga)
        logo_gazda_viitor = extrage_logo(gazda_viitor)
        logo_oaspete_viitor = extrage_logo(oaspete_viitor)

        sansa_gazda = sansa_egal = sansa_oaspete = 0
        explicatii_shap = []

        if "Nedeterminat" not in oaspete_viitor and "Nedeterminat" not in gazda_viitor:
            try:
                def obtine_medii_sezon(nume_echipa_cautata):
                    termen_cautare = str(nume_echipa_cautata).lower()
                    df_adv = df_toate_meciurile[
                        df_toate_meciurile['Echipa_Gazda'].str.lower().str.contains(termen_cautare, regex=False,
                                                                                    na=False) |
                        df_toate_meciurile['Echipa_Oaspete'].str.lower().str.contains(termen_cautare, regex=False,
                                                                                      na=False)
                        ].copy()

                    puncte = goluri_date = meciuri_valide = 0

                    for _, rand in df_adv.iterrows():
                        try:
                            g_g = int(float(rand['Goluri_Gazda']))
                            g_o = int(float(rand['Goluri_Oaspete']))
                        except (ValueError, TypeError):
                            continue

                        meciuri_valide += 1

                        if termen_cautare in str(rand['Echipa_Gazda']).lower():
                            goluri_date += g_g
                            puncte += 3 if g_g > g_o else (1 if g_g == g_o else 0)
                        else:
                            goluri_date += g_o
                            puncte += 3 if g_o > g_g else (1 if g_o == g_g else 0)

                    if meciuri_valide == 0: return 1.0, 1.0
                    return puncte / meciuri_valide, goluri_date / meciuri_valide

                if os.path.exists('model_fotbal.pkl'):
                    model = joblib.load('model_fotbal.pkl')
                    pct_gazda, gol_gazda = obtine_medii_sezon(gazda_viitor.split()[0])
                    pct_oasp, gol_oasp = obtine_medii_sezon(oaspete_viitor.split()[0])

                    date_meci = np.array([[pct_gazda, gol_gazda, pct_oasp, gol_oasp]])
                    probabilitati = model.predict_proba(date_meci)[0]

                    sansa_egal = int(round(probabilitati[0] * 100))
                    sansa_gazda = int(round(probabilitati[1] * 100))
                    sansa_oaspete = int(round(probabilitati[2] * 100))

                    try:
                        explainer = shap.TreeExplainer(model)
                        shap_values = explainer.shap_values(date_meci, check_additivity=False)

                        impact_features = shap_values[1][0] if isinstance(shap_values, list) else (
                            shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0])

                        nume_features = ["Forma gazdă", "Atac gazdă", "Forma oaspete", "Atac oaspete"]
                        for nume, valoare in zip(nume_features, impact_features):
                            explicatii_shap.append(
                                {"factor": nume, "impact": round(valoare * 100, 2), "pozitiv": valoare > 0})
                        explicatii_shap = sorted(explicatii_shap, key=lambda x: abs(x['impact']), reverse=True)
                    except:
                        pass
                else:
                    sansa_gazda, sansa_egal, sansa_oaspete = 33, 34, 33
            except Exception as e:
                sansa_gazda, sansa_egal, sansa_oaspete = 33, 34, 33

    except Exception as e:
        print(f"Eroare ruta echipa: {e}")
        return "A aparut o eroare la procesarea datelor. Te rog sa reincarci pagina.", 500
    finally:
        if conn: conn.close()

    return render_template('echipa.html', nume_echipa=nume_echipa, meciuri=meciuri_lista, id_liga=id_liga,
                           gazda_viitor=gazda_viitor, oaspete_viitor=oaspete_viitor, sansa_gazda=sansa_gazda,
                           sansa_egal=sansa_egal, sansa_oaspete=sansa_oaspete, forma=forma_echipa,
                           explicatii=explicatii_shap, logo_gazda_viitor=logo_gazda_viitor,
                           logo_oaspete_viitor=logo_oaspete_viitor)

@app.route('/lot/<id_liga>/<nume_echipa>')
def pagina_lot(id_liga, nume_echipa):
    nume_oficial = obtine_nume_oficial(nume_echipa)
    df_lot = extrage_lot_real(nume_oficial, id_liga)
    jucatori_lista = df_lot.to_dict('records') if df_lot is not None and not df_lot.empty else []
    return render_template('lot.html', nume_echipa=nume_echipa, id_liga=id_liga, jucatori=jucatori_lista)


@app.route('/statistici/<id_liga>/<nume_echipa>')
def pagina_statistici(id_liga, nume_echipa):
    tabel_meciuri = f"meciuri_{id_liga}"
    conn = sqlite3.connect('fotbal_app.db')
    try:
        df_toate = pd.read_sql(f"SELECT * FROM {tabel_meciuri}", conn)
    except Exception as e:
        if conn: conn.close()
        return f"Eroare la baza de date: {e}"
    finally:
        if conn: conn.close()

    nume_oficial = obtine_nume_oficial(nume_echipa)

    variante = [nume_echipa, nume_oficial]
    aliasuri = {
        "Manchester City": ["Man City", "City"],
        "Manchester United": ["Man United", "Man Utd"],
        "Wolverhampton Wanderers": ["Wolves", "Wolverhampton"],
        "Nottingham Forest": ["Nott'm Forest", "Nottingham Forrest", "Nottingham"],
        "Atletico Madrid": ["Ath Madrid", "Atlético Madrid"],
        "Paris Saint-Germain": ["Paris SG", "PSG", "Paris"],
        "Rennes FC": ["Rennes", "Stade Rennais"],
        "Real Oviedo": ["Oviedo"],
        "Real Mallorca": ["Mallorca"],
        "Rayo Vallecano": ["Rayo"],
        "Espanyol Barcelona": ["Espanyol"],
        "Athletic Club": ["Ath Bilbao", "Athletic Bilbao", "Bilbao"],
        "Leeds United": ["Leeds"],
        "Internazionale": ["Inter", "Inter Milan"],
        "TSG Hoffenheim": ["Hoffenheim"],
        "Eintracht Frankfurt": ["Frankfurt"],
        "SC Freiburg": ["Freiburg"],
        "1. FC Union Berlin": ["Union Berlin"],
        "FC Augsburg": ["Augsburg"],
        "Borussia Mönchengladbach": ["Gladbach", "Mönchengladbach"],
        "1. FC Köln": ["Koln", "Köln", "Cologne"],
        "1. FC Heidenheim 1846": ["Heidenheim"],
        "RC Lens": ["Lens"]
    }

    for cheie, lista_val in aliasuri.items():
        if nume_echipa.lower() in [v.lower() for v in
                                   lista_val] or nume_echipa.lower() == cheie.lower() or nume_oficial.lower() in [
            v.lower() for v in lista_val] or nume_oficial.lower() == cheie.lower():
            variante.append(cheie)
            variante.extend(lista_val)

    variante = list(set(variante))

    masca_gazda = df_toate['Echipa_Gazda'].apply(lambda x: any(v.lower() == str(x).lower() for v in variante))
    masca_oaspete = df_toate['Echipa_Oaspete'].apply(lambda x: any(v.lower() == str(x).lower() for v in variante))

    df_echipa = df_toate[masca_gazda | masca_oaspete].copy()

    if df_echipa.empty:
        df_echipa = df_toate[
            df_toate['Echipa_Gazda'].str.contains(nume_oficial, case=False, na=False) |
            df_toate['Echipa_Oaspete'].str.contains(nume_oficial, case=False, na=False)
            ].copy()

    df_echipa = df_echipa.dropna(subset=['Goluri_Gazda', 'Goluri_Oaspete'])

    victorii = egaluri = infrangeri = goluri_date = goluri_primite = 0

    for _, rand in df_echipa.iterrows():
        try:
            g_gazda = int(float(rand['Goluri_Gazda']))
            g_oaspete = int(float(rand['Goluri_Oaspete']))
        except (ValueError, TypeError):
            continue
        este_gazda = any(v.lower() == str(rand['Echipa_Gazda']).lower() for v in variante) or (
                    nume_oficial.lower() in str(rand['Echipa_Gazda']).lower())

        if este_gazda:
            goluri_date += g_gazda
            goluri_primite += g_oaspete
            if g_gazda > g_oaspete:
                victorii += 1
            elif g_gazda == g_oaspete:
                egaluri += 1
            else:
                infrangeri += 1
        else:
            goluri_date += g_oaspete
            goluri_primite += g_gazda
            if g_oaspete > g_gazda:
                victorii += 1
            elif g_oaspete == g_gazda:
                egaluri += 1
            else:
                infrangeri += 1

    g_nume, g_goluri, p_nume, p_pase = extrage_statistici_jucatori(nume_oficial, id_liga)

    total_meciuri = victorii + egaluri + infrangeri
    golaveraj_mediu = 0
    if total_meciuri > 0:
        golaveraj_mediu = round((goluri_date - goluri_primite) / total_meciuri, 2)
    return render_template('statistici.html', nume_echipa=nume_echipa, id_liga=id_liga, victorii=victorii,
                           egaluri=egaluri, infrangeri=infrangeri, goluri_date=goluri_date,
                           goluri_primite=goluri_primite, golgheter_nume=g_nume, golgheter_goluri=g_goluri,
                           pasator_nume=p_nume, pasator_pase=p_pase, golaveraj_mediu=golaveraj_mediu)

@app.route('/compara')
def pagina_compara():
    conn = sqlite3.connect('fotbal_app.db')
    toate_echipele = set()
    for id_liga in LIGI_DISPONIBILE.keys():
        try:
            df = pd.read_sql(f"SELECT Echipa_Gazda, Echipa_Oaspete FROM meciuri_{id_liga}", conn)
            toate_echipele.update(df['Echipa_Gazda'].dropna().unique())
            toate_echipele.update(df['Echipa_Oaspete'].dropna().unique())
        except:
            pass
    lista_echipe = sorted(list(toate_echipele))
    echipa1 = request.args.get('echipa1')
    echipa2 = request.args.get('echipa2')
    stats1 = stats2 = None

    def calculeaza_stats(nume_echipa):
        meciuri_jucate = v = e = i = gd = gp = suturi = cornere = 0
        for id_liga in LIGI_DISPONIBILE.keys():
            try:
                df = pd.read_sql(
                    f"SELECT * FROM meciuri_{id_liga} WHERE Echipa_Gazda = '{nume_echipa}' OR Echipa_Oaspete = '{nume_echipa}'",
                    conn)
                df = df.dropna(subset=['Goluri_Gazda', 'Goluri_Oaspete'])
                for _, rand in df.iterrows():
                    meciuri_jucate += 1
                    g_gazda, g_oaspete = int(float(rand['Goluri_Gazda'])), int(float(rand['Goluri_Oaspete']))
                    s_g = int(float(rand['Suturi_Gazda'])) if pd.notna(rand['Suturi_Gazda']) else 0
                    s_o = int(float(rand['Suturi_Oaspete'])) if pd.notna(rand['Suturi_Oaspete']) else 0
                    c_g = int(float(rand['Cornere_Gazda'])) if pd.notna(rand['Cornere_Gazda']) else 0
                    c_o = int(float(rand['Cornere_Oaspete'])) if pd.notna(rand['Cornere_Oaspete']) else 0
                    if rand['Echipa_Gazda'] == nume_echipa:
                        gd += g_gazda;
                        gp += g_oaspete;
                        suturi += s_g;
                        cornere += c_g
                        if g_gazda > g_oaspete:
                            v += 1
                        elif g_gazda == g_oaspete:
                            e += 1
                        else:
                            i += 1
                    else:
                        gd += g_oaspete;
                        gp += g_gazda;
                        suturi += s_o;
                        cornere += c_o
                        if g_oaspete > g_gazda:
                            v += 1
                        elif g_oaspete == g_gazda:
                            e += 1
                        else:
                            i += 1
            except:
                pass
        if meciuri_jucate == 0: return None
        return {'Nume': nume_echipa, 'Meciuri': meciuri_jucate, 'Victorii': v, 'Egaluri': e, 'Infrangeri': i,
                'Goluri_Date': gd, 'Goluri_Primite': gp, 'Media_Goluri': round(gd / meciuri_jucate, 2),
                'Media_Suturi': round(suturi / meciuri_jucate, 2), 'Media_Cornere': round(cornere / meciuri_jucate, 2)}

    if echipa1 and echipa2:
        stats1 = calculeaza_stats(echipa1)
        stats2 = calculeaza_stats(echipa2)
    conn.close()
    return render_template('compara.html', echipe=lista_echipe, s1=stats1, s2=stats2, e1=echipa1, e2=echipa2)


@app.route('/live')
def pagina_live():
    coduri_espn = {"Premier League": "eng.1", "La Liga": "esp.1", "Serie A": "ita.1", "Bundesliga": "ger.1",
                   "Ligue 1": "fra.1", "Champions League": "uefa.champions"}
    meciuri_azi = {}

    azi_str = datetime.datetime.now().strftime('%Y%m%d')

    for nume_liga, cod in coduri_espn.items():
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/scoreboard?dates={azi_str}"
            resp = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()
            lista_meciuri = []

            for event in resp.get('events', []):
                competitors = event['competitions'][0]['competitors']
                home_team = away_team = ""
                score_home = score_away = "-"
                logo_h = logo_a = ""

                for comp in competitors:
                    echipa_nume = comp['team']['name']
                    echipa_logo = comp['team'].get('logo', '')

                    if comp['homeAway'] == 'home':
                        home_team, score_home, logo_h = echipa_nume, comp.get('score', '-'), echipa_logo
                    else:
                        away_team, score_away, logo_a = echipa_nume, comp.get('score', '-'), echipa_logo
                if not logo_h or "default" in logo_h.lower(): logo_h = extrage_logo(home_team)
                if not logo_a or "default" in logo_a.lower(): logo_a = extrage_logo(away_team)

                status_desc = event['status']['type']['description']
                timp_meci = event['status'].get('displayClock', '')

                if "In Progress" in status_desc or "Half" in status_desc:
                    status_display, scor_display, state_class = f"🔴 LIVE {timp_meci}'", f"{score_home} - {score_away}", "text-danger fw-bold pulse"
                elif "Full Time" in status_desc or "FT" in status_desc:
                    status_display, scor_display, state_class = "Finalizat", f"{score_home} - {score_away}", "text-muted"
                elif "Postponed" in status_desc:
                    status_display, scor_display, state_class = "Amânat", "vs", "text-warning"
                else:
                    iso_string = event['date']
                    try:
                        dt_obj = dt.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
                        status_display = f"Astăzi, {dt_obj.strftime('%H:%M')}"
                    except:
                        status_display = "Astăzi"
                    scor_display, state_class = "vs", "text-info fw-bold"

                lista_meciuri.append({
                    "gazda": home_team,
                    "oaspete": away_team,
                    "scor": scor_display,
                    "status": status_display,
                    "state_class": state_class,
                    "logo_gazda": logo_h,
                    "logo_oaspete": logo_a
                })

            if lista_meciuri:
                meciuri_azi[nume_liga] = lista_meciuri
            else:
                meciuri_azi[nume_liga] = [{
                    "gazda": "Fără meciuri", "oaspete": "astăzi", "scor": "-",
                    "status": "Niciun meci programat", "state_class": "text-muted opacity-50",
                    "logo_gazda": "https://cdn-icons-png.flaticon.com/512/871/871372.png",
                    "logo_oaspete": "https://cdn-icons-png.flaticon.com/512/871/871372.png"
                }]

        except Exception as e:
            print(f"Eroare pe ruta Live la {nume_liga}: {e}")
            pass

    return render_template('live.html', meciuri_azi=meciuri_azi)
def extrage_meciuri_viitoare(id_liga):
    coduri_espn = {"premier_league": "eng.1", "la_liga": "esp.1", "serie_a": "ita.1", "bundesliga": "ger.1",
                   "ligue_1": "fra.1", "champions_league": "uefa.champions"}
    cod = coduri_espn.get(id_liga)
    if not cod: return []

    meciuri = []
    try:
        azi = datetime.datetime.now()
        viitor = azi + datetime.timedelta(days=14)
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{cod}/scoreboard?dates={azi.strftime('%Y%m%d')}-{viitor.strftime('%Y%m%d')}"
        resp = requests.get(url, headers=HEADERS_BROWSER, timeout=5).json()

        for event in resp.get('events', []):
            if event['status']['type']['state'] == 'pre':  # Doar meciuri care NU au început
                comp = event['competitions'][0]['competitors']
                home_raw = comp[0]['team']['name'] if comp[0]['homeAway'] == 'home' else comp[1]['team']['name']
                away_raw = comp[1]['team']['name'] if comp[1]['homeAway'] == 'away' else comp[0]['team']['name']

                home = obtine_nume_oficial(home_raw)
                away = obtine_nume_oficial(away_raw)

                meciuri.append({
                    "gazda": home,
                    "oaspete": away,
                    "logo_gazda": extrage_logo(home),
                    "logo_oaspete": extrage_logo(away)
                })

                if len(meciuri) >= 10:
                    break
    except Exception as e:
        print(f"Eroare Simulator: {e}")
    return meciuri


@app.route('/simulator/<id_liga>')
def pagina_simulator(id_liga):
    if id_liga not in LIGI_DISPONIBILE: return "Eroare!"

    import json
    conn = sqlite3.connect('fotbal_app.db')
    df_clasament = pd.read_sql(f"SELECT * FROM {id_liga}", conn)
    conn.close()

    df_clasament.fillna(0, inplace=True)

    def extrage_sigur(row, cuvinte_cheie, index_rezerva):
        for col in row.index:
            if str(col).strip().lower() in cuvinte_cheie:
                try:
                    return int(float(row[col]))
                except:
                    pass
        try:
            return int(float(row.iloc[index_rezerva]))
        except:
            return 0

    col_echipa = df_clasament.columns[1]
    for c in df_clasament.columns:
        if str(c).strip().lower() in ['echipa', 'team', 'nume', 'squad', 'club']:
            col_echipa = c
            break

    clasament_baza = []
    for _, row in df_clasament.iterrows():
        echipa_brut = str(row[col_echipa])

        echipa = obtine_nume_oficial(echipa_brut)

        meciuri = extrage_sigur(row, ['meciuri', 'm', 'pl', 'pld', 'played', 'jucate', 'mp'], 2)
        puncte = extrage_sigur(row, ['puncte', 'pct', 'pts', 'points', 'p'], -1)
        gd = extrage_sigur(row, ['gm', 'f', 'gf', 'goluri date', 'goals for'], -4)
        gp = extrage_sigur(row, ['gp', 'a', 'ga', 'goluri primite', 'goals against'], -3)
        golaveraj = extrage_sigur(row, ['golaveraj', 'gd', 'gl', 'goal difference', 'adev'], -2)

        if golaveraj == 0 and (gd > 0 or gp > 0):
            golaveraj = gd - gp

        clasament_baza.append({
            "echipa": echipa,
            "meciuri": meciuri,
            "puncte": puncte,
            "gd": gd,
            "gp": gp,
            "golaveraj": golaveraj
        })

    meciuri_viitoare = extrage_meciuri_viitoare(id_liga)

    return render_template('simulator.html',
                           liga_curenta=LIGI_DISPONIBILE[id_liga],
                           id_liga=id_liga,
                           clasament_json=json.dumps(clasament_baza),
                           meciuri=meciuri_viitoare)


if __name__ == '__main__':
    app.run(debug=True)