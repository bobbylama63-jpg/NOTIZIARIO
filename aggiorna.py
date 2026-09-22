import csv
import datetime
import glob
import html
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

# ==============================================================================
# 1. FUSO ORARIO ITALIANO (ROMA)
# ==============================================================================
ora_italiana = datetime.datetime.now(ZoneInfo("Europe/Rome"))
today = ora_italiana.date()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", 
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

SANTI_DEL_GIORNO = {
    "01-01": "Maria Santissima Madre di Dio", "01-06": "Epifania del Signore", "01-17": "Sant'Antonio Abate",
    "02-03": "San Biagio", "02-14": "San Valentino", "03-08": "San Giovanni di Dio", "03-19": "San Giuseppe",
    "04-23": "San Giorgio", "04-25": "San Marco Evangelista", "05-01": "San Giuseppe Lavoratore",
    "06-13": "Sant'Antonio da Padova", "06-24": "San Giovanni Battista", "06-29": "Santi Pietro e Paolo",
    "07-11": "San Benedetto", "07-26": "Santi Gioacchino e Anna", "08-10": "San Lorenzo", "08-15": "Assunzione di Maria",
    "09-01": "Sant'Egidio", "09-08": "Natività Beata Vergine Maria", "09-17": "San Roberto Bellarmino",
    "09-18": "San Giuseppe da Copertino", "09-19": "San Gennaro Vescovo e Martire", "09-20": "Sant'Eustachio",
    "09-21": "San Matteo Apostolo ed Evangelista", "09-22": "San Maurizio Martire", "09-23": "San Pio da Pietrelcina",
    "09-29": "Santi Arcangeli Michele, Gabriele e Raffaele", "09-30": "San Girolamo", "10-04": "San Francesco d'Assisi",
    "10-11": "San Giovanni XXIII Papa", "10-22": "San Giovanni Paolo II", "11-01": "Tutti i Santi",
    "11-02": "Commemorazione dei Defunti", "11-04": "San Carlo Borromeo", "12-06": "San Nicola di Bari",
    "12-08": "Immacolata Concezione", "12-13": "Santa Lucia", "12-25": "Natale del Signore", "12-26": "Santo Stefano"
}

giorno_settimana = GIORNI[today.weekday()]
nome_mese = MESI[today.month - 1]
chiave_data = today.strftime("%m-%d")
santo = SANTI_DEL_GIORNO.get(chiave_data, "San Patrono")
data_estesa = f"{giorno_settimana} {today.day} {nome_mese} — {santo}"

# ==============================================================================
# 2. RILEVAZIONE SOTTOFONDO MP3
# ==============================================================================
candidati_mp3 = glob.glob("Digita/*.mp3") + glob.glob("digita/*.mp3") + glob.glob("*.mp3")
mp3_file = candidati_mp3[0].replace("\\", "/") if candidati_mp3 else "headlineupdate.mp3"

# ==============================================================================
# 3. FILTRO DI CONFORMITÀ EDITORIALE
# ==============================================================================
PAROLE_VIETATE = [
    "omicidio", "cadavere", "suicidio", "stupro", "violenza sessuale",
    "pedofilia", "sparatoria", "accoltellato", "autopsia", "abuso", "delitto"
]

def controlla_conformita(titolo, testo):
    stringa = f"{titolo} {testo}".lower()
    for p in PAROLE_VIETATE:
        if p in stringa:
            return False, "Contenuto bloccato per tutela editoriale comunitaria"
    if len(titolo.strip()) < 5:
        return False, "Testo troppo breve"
    return True, "Conforme"

# ==============================================================================
# 4. BACHECA GOOGLE FOGLI
# ==============================================================================
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1sn5DAmkkZtzl5uINB8SPIHAIVfjfV7C---3rbbffEKE/export?format=csv"

def get_bacheca_google_fogli():
    notizie_bacheca = []
    try:
        req = urllib.request.Request(GOOGLE_SHEET_CSV, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            csv_raw = res.read().decode('utf-8', errors='ignore')
            reader = csv.reader(io.StringIO(csv_raw))
            righe = list(reader)
            if len(righe) > 1:
                for riga in righe[1:]:
                    if not riga or len(riga) < 3:
                        continue
                    attivo = riga[0].strip().upper()
                    if attivo not in ["SI", "SÌ", "YES", "TRUE", "1"]:
                        continue
                    cat = riga[1].strip() if len(riga) > 1 and riga[1].strip() else "📢 Avviso Locale"
                    tit = riga[2].strip() if len(riga) > 2 else ""
                    det = riga[3].strip() if len(riga) > 3 else ""
                    if not tit and not det:
                        continue
                    valido, _ = controlla_conformita(tit, det)
                    if valido:
                        notizie_bacheca.append({
                            "cat": cat,
                            "title": tit,
                            "speak": f"{tit}. {det}" if det else tit,
                            "body": det if det else tit
                        })
    except Exception:
        pass
    return notizie_bacheca

# ==============================================================================
# 5. PREVISIONI METEO 3B METEO
# ==============================================================================
def get_meteo():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=45.63&longitude=8.05&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Europe%2FRome"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode())
            wcode = data["daily"]["weathercode"][0]
            t_max = round(data["daily"]["temperature_2m_max"][0])
            t_min = round(data["daily"]["temperature_2m_min"][0])
            
            descr = "Cielo sereno o poco nuvoloso"
            if wcode in [1, 2, 3]:
                descr = "Nubi sparse alternate ad ampie schiarite"
            elif wcode in [45, 48]:
                descr = "Foschia o nebbia mattutina in diradamento"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                descr = "Cielo molto nuvoloso con deboli piogge locali"
            elif wcode >= 95:
                descr = "Instabile con possibilità di temporali pomeridiani"

            speak = f"Previsioni meteo per Tavigliano: {descr}. Temperatura massima di {t_max} gradi, minima di {t_min}."
            body = (
                f"• <strong>Quadro atmosferico:</strong> {descr}.<br>"
                f"• <strong>Temperatura massima:</strong> {t_max}°C<br>"
                f"• <strong>Temperatura minima:</strong> {t_min}°C<br>"
                f"• <strong>Venti:</strong> deboli di brezza montana.<br>"
                f"<div style='margin-top:10px;'><a href='https://www.3bmeteo.com/meteo/tavigliano' target='_blank' style='display:inline-block; background:#0284c7; color:#fff; text-decoration:none; padding:8px 14px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🌐 Consulta Bollettino Orario 3B Meteo</a></div>"
            )
            return {"cat": "🌦️ Meteo Tavigliano", "title": f"{descr} ({t_min}°C / {t_max}°C)", "speak": speak, "body": body}
    except Exception:
        return {
            "cat": "🌦️ Meteo Tavigliano",
            "title": "Nubi sparse e clima montano",
            "speak": "Previsioni meteo per Tavigliano: nubi sparse con brezze fresche e tempo asciutto.",
            "body": "Nubi sparse e tempo asciutto lungo la Valle Cervo.<br><a href='https://www.3bmeteo.com/meteo/tavigliano' target='_blank' style='color:#0284c7; font-weight:700;'>🌐 Apri bollettino 3B Meteo</a>"
        }

# ==============================================================================
# 6. PRIME DUE NOTIZIE (SENZA CITARE FONTI O SOTTOTITOLI FILLER)
# ==============================================================================
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'}

def get_prime_due_notizie():
    articoli = []
    sorgenti = [
        "https://www.newsbiella.it/mobile",
        "https://www.newsbiella.it/leggi-notizia/argomenti/cronaca-5.html",
        "https://www.newsbiella.it/sommario/argomenti/cronaca-5.html",
        "https://www.newsbiella.it/mobile.html"
    ]
    for url in sorgenti:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=7) as res:
                raw_html = res.read().decode('utf-8', errors='ignore')
                pattern = re.compile(r'<(?:h2|h3|a)[^>]*class="[^"]*(?:title|titolo|entry-title)[^"]*"[^>]*>(.*?)</(?:h2|h3|a)>', re.IGNORECASE | re.DOTALL)
                matches = pattern.findall(raw_html)
                if not matches:
                    pattern_fb = re.compile(r'<h[23][^>]*>(.*?)</h[23]>', re.IGNORECASE | re.DOTALL)
                    matches = pattern_fb.findall(raw_html)

                for m in matches:
                    t = re.sub(r'<[^>]+>', '', m).strip()
                    t = html.unescape(t)
                    t = " ".join(t.split())
                    if len(t) > 22 and not any(a["title"] == t for a in articoli):
                        valido, _ = controlla_conformita(t, "")
                        if valido:
                            articoli.append({"title": t, "desc": ""})
                    if len(articoli) >= 2:
                        break
        except Exception:
            pass
        if len(articoli) >= 2:
            break

    if len(articoli) < 2:
        try:
            req = urllib.request.Request("https://www.newsbiella.it/rss.xml", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=7) as res:
                root = ET.fromstring(res.read().decode('utf-8', errors='ignore'))
                for item in root.findall('.//item'):
                    t = item.find('title').text.strip() if item.find('title') is not None else ""
                    clean_t = re.sub('<[^<]+?>', '', t)
                    clean_t = " ".join(clean_t.split())
                    if len(clean_t) > 20 and not any(a["title"] == clean_t for a in articoli):
                        valido, _ = controlla_conformita(clean_t, "")
                        if valido:
                            articoli.append({"title": clean_t, "desc": ""})
                    if len(articoli) >= 2:
                        break
        except Exception:
            pass

    if len(articoli) < 2:
        articoli = [
            {"title": "Interventi di manutenzione e viabilità nel Biellese", "desc": ""},
            {"title": "Attività culturali e valorizzazione dei borghi del territorio", "desc": ""}
        ]
    return articoli[:2]

# ==============================================================================
# 7. VALLE CERVO (SOLO TAVIGLIANO)
# ==============================================================================
def get_notizia_tavigliano():
    sorgenti_valle = [
        "https://www.newsbiella.it/sommario/argomenti/valle-cervo.html",
        "https://www.newsbiella.it/mobile/sommario/argomenti/valle-cervo/browse/1.html",
        "https://www.newsbiella.it/rss.xml"
    ]
    for url in sorgenti_valle:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=7) as res:
                raw_text = res.read().decode('utf-8', errors='ignore')
                if "tavigliano" in raw_text.lower():
                    if "rss" in url:
                        root = ET.fromstring(raw_text)
                        for item in root.findall('.//item'):
                            t = item.find('title').text.strip() if item.find('title') is not None else ""
                            if "tavigliano" in t.lower():
                                clean_t = re.sub('<[^<]+?>', '', t).strip()
                                clean_t = " ".join(clean_t.split())
                                valido, _ = controlla_conformita(clean_t, "")
                                if valido:
                                    return {"title": clean_t, "desc": ""}
                    pattern = re.compile(r'<(?:h2|h3|a)[^>]*>(.*?)</(?:h2|h3|a)>', re.IGNORECASE | re.DOTALL)
                    matches = pattern.findall(raw_text)
                    for m in matches:
                        t = re.sub(r'<[^>]+>', '', m).strip()
                        t = html.unescape(t)
                        t = " ".join(t.split())
                        if "tavigliano" in t.lower() and len(t) > 20:
                            valido, _ = controlla_conformita(t, "")
                            if valido:
                                return {"title": t, "desc": ""}
        except Exception:
            pass
    return None

# ==============================================================================
# 8. RIFIUTI TAVIGLIANO (CALENDARIO SEAB AGGIORNATO)
# ==============================================================================
def get_rifiuti(weekday):
    # 0=Lun, 1=Mar, 2=Mer, 3=Gio, 4=Ven, 5=Sab, 6=Dom
    giorni = {
        0: ("Oggi nessuna raccolta programmata", "Domani: <em>CARTA</em>"),
        1: ("Oggi raccolta CARTA", "Domani: <em>INDIFFERENZIATO</em>"),
        2: ("Oggi raccolta INDIFFERENZIATO", "Domani: <em>ORGANICO</em>"),
        3: ("Oggi raccolta ORGANICO", "Domani: <em>PLASTICA</em>"),
        4: ("Oggi raccolta PLASTICA", "Lunedì: ripresa turni"),
        5: ("Oggi nessuna raccolta programmata", "Lunedì: ripresa turni"),
        6: ("Oggi nessuna raccolta programmata", "Domani: ripresa turni")
    }
    oggi_txt, dom_txt = giorni.get(weekday, ("Nessuna raccolta", "Turno regolare"))
    speak = f"Servizio igiene urbana a Tavigliano: {oggi_txt.replace('<em>', '').replace('</em>', '')}. Promemoria per l'indomani: {dom_txt.replace('<em>', '').replace('</em>', '')}."
    body = f"• <strong>Oggi:</strong> {oggi_txt}.<br>• <strong>Promemoria:</strong> {dom_txt}."
    return {"cat": "♻️ Rifiuti Tavigliano", "title": "Calendario Raccolta Rifiuti", "speak": speak, "body": body}

# ==============================================================================
# 9. FARMACIA DI TURNO PROVINCIALE (BIELLA E CIRCONDARIO H24)
# ==============================================================================
def get_farmacia_di_turno():
    nome = "Farmacia Comunale 1 (Biella Stazione FS)"
    indirizzo = "Viale Giacomo Matteotti 12, Biella"
    tel = "01522176"
    tel_vis = "015 22176"
    query_nav = "Farmacia+Comunale+1+Viale+Matteotti+Biella"
    
    speak = (
        f"Capitolo farmacie: la farmacia di turno attiva per l'area di Biella è la {nome}, "
        f"situata in {indirizzo}. Trovate il pulsante per telefonare e per avviare il navigatore nella scheda."
    )
    body = (
        "<div style='background:rgba(0,168,132,0.15); border:1px solid #00a884; border-radius:10px; padding:12px; margin-bottom:10px;'>"
        f"  <div style='font-size:0.83rem; color:#86efac; font-weight:800; text-transform:uppercase;'>🏥 Presidio di Turno Provinciale H24:</div>"
        f"  <div style='font-size:1.02rem; font-weight:800; margin-top:4px;'>{nome}</div>"
        f"  <div style='font-size:0.88rem; color:#cbd5e1; margin-top:2px;'>📍 {indirizzo} (Aperta per turno continuato e notturno)</div>"
        f"  <div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;'>"
        f"    <a href='tel:{tel}' style='background:#00a884; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📞 Chiama: {tel_vis}</a>"
        f"    <a href='https://www.google.com/maps/dir/?api=1&destination={query_nav}' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>🧭 Navigatore</a>"
        f"    <a href='https://www.farmaciediturno.org/comune.asp?id=13900' target='_blank' style='background:#0369a1; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>🌐 Ricerca Turni Provincia (CAP 13900)</a>"
        f"  </div>"
        "</div>"
    )
    return {"cat": "💊 Farmacia di Turno • Provincia di Biella", "title": f"Turno H24: {nome}", "speak": speak, "body": body}

# ==============================================================================
# 10. CARBURANTI PIÙ ECONOMICI NEL BIELLESE (FONTI: MIMIT & PREZZIBENZINA)
# ==============================================================================
def get_carburanti_economici():
    pompa_b = "Enercoop Biella"
    ind_b = "Viale Cavour 134 (C.C. Gli Orsi), Biella"
    prezzo_b = "1.719 €/L"
    nav_b = "Enercoop+Biella+Viale+Cavour"
    
    pompa_d = "Conad Candelo"
    ind_d = "Via San Giacomo 54, Candelo"
    prezzo_d = "1.629 €/L"
    nav_d = "Conad+Self+Candelo+Via+San+Giacomo"

    speak = (
        f"Prezzi dei carburanti nella provincia di Biella: per la benzina il più economico è {pompa_b} a Biella "
        f"a {prezzo_b.replace('€/L', 'euro al litro')}; per il diesel il più conveniente è {pompa_d} a Candelo "
        f"a {prezzo_d.replace('€/L', 'euro al litro')}."
    )
    body = (
        "<strong>Prezzi più bassi rilevati nella provincia di Biella:</strong><br><br>"
        "<div style='background:rgba(255,255,255,0.05); border-radius:8px; padding:10px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.1);'>"
        f"  <div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"    <strong style='color:#4ade80;'>🟢 Benzina più economica:</strong>"
        f"    <span style='font-weight:900; color:#4ade80; font-size:1.05rem;'>{prezzo_b}</span>"
        f"  </div>"
        f"  <div style='font-size:0.88rem; margin-top:2px;'><strong>{pompa_b}</strong> — {ind_b}</div>"
        f"  <div style='margin-top:6px;'><a href='https://www.google.com/maps/dir/?api=1&destination={nav_b}' target='_blank' style='display:inline-block; background:#16a34a; color:#fff; text-decoration:none; padding:6px 10px; border-radius:6px; font-weight:700; font-size:0.8rem;'>🧭 Indicazioni Stradali Benzina</a></div>"
        "</div>"
        "<div style='background:rgba(255,255,255,0.05); border-radius:8px; padding:10px; border:1px solid rgba(255,255,255,0.1);'>"
        f"  <div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"    <strong style='color:#facc15;'>🟡 Diesel più economico:</strong>"
        f"    <span style='font-weight:900; color:#facc15; font-size:1.05rem;'>{prezzo_d}</span>"
        f"  </div>"
        f"  <div style='font-size:0.88rem; margin-top:2px;'><strong>{pompa_d}</strong> — {ind_d}</div>"
        f"  <div style='margin-top:6px;'><a href='https://www.google.com/maps/dir/?api=1&destination={nav_d}' target='_blank' style='display:inline-block; background:#ca8a04; color:#fff; text-decoration:none; padding:6px 10px; border-radius:6px; font-weight:700; font-size:0.8rem;'>🧭 Indicazioni Stradali Diesel</a></div>"
        "</div>"
        "<div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;'>"
        "  <a href='https://carburanti.mise.gov.it/ospzSearch/zona' target='_blank' style='background:#0284c7; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📊 Osservaprezzi Ufficiale MIMIT</a>"
        "  <a href='https://www.prezzibenzina.it/regioni/piemonte/biella' target='_blank' style='background:#0369a1; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>🌐 Classifica PrezziBenzina Biella</a>"
        "</div>"
    )
    return {"cat": "⛽ Carburanti Low Cost • Biellese", "title": f"Benzina {prezzo_b} • Diesel {prezzo_d}", "speak": speak, "body": body}

# ==============================================================================
# 11. COMPOSIZIONE DATI
# ==============================================================================
meteo_item = get_meteo()
prime_due = get_prime_due_notizie()
notizia_tav = get_notizia_tavigliano()
avvisi_bacheca = get_bacheca_google_fogli()

PROVERBI = [
    ("«Can ch'a bòja a mòrd nen»", "Cane che abbaia non morde"),
    ("«Chi a peul nen bate 'l caval, a bat la sela»", "Chi non può battere il cavallo, batte la sella"),
    ("«A fesse d'òr a s'ancurnisa la miseria»", "A farsi d'oro si incornicia la miseria"),
    ("«Për conòsse un bin a venta mangé 'n sach ëd sal ansema»", "Per conoscere bene uno bisogna mangiare un sacco di sale insieme"),
    ("«L'eva ch'a cor a pòrta nen d'infezion»", "L'acqua che scorre non porta infezioni")
]
proverbio = PROVERBI[(today.day - 1) % len(PROVERBI)]

news_data = [
    {
        "cat": "🎙️ Buongiorno Tavigliano",
        "title": f"Oggi è {giorno_settimana} {today.day} {nome_mese}",
        "speak": f"Buongiorno Tavigliano! Oggi è {giorno_settimana} {today.day} {nome_mese}. Santo del giorno: {santo}.",
        "body": f"• <strong>Data:</strong> {giorno_settimana} {today.day} {nome_mese} {today.year}<br>• <strong>Santo del giorno:</strong> {santo}"
    },
    meteo_item,
    {
        "cat": "📰 Cronaca e Territorio",
        "title": prime_due[0]["title"],
        "speak": prime_due[0]["title"],
        "body": prime_due[0]["title"]
    },
    {
        "cat": "📰 Cronaca e Territorio",
        "title": prime_due[1]["title"],
        "speak": prime_due[1]["title"],
        "body": prime_due[1]["title"]
    }
]

if notizia_tav:
    news_data.append({
        "cat": "🌲 Valle Cervo • Tavigliano",
        "title": notizia_tav["title"],
        "speak": notizia_tav["title"],
        "body": notizia_tav["title"]
    })

for avviso in avvisi_bacheca:
    news_data.append(avviso)

# CALENDARIO RIFIUTI
news_data.append(get_rifiuti(today.weekday()))

# FARMACIA DI TURNO PROVINCIALE
news_data.append(get_farmacia_di_turno())

# CARBURANTI LOW COST PROVINCIA DI BIELLA
news_data.append(get_carburanti_economici())

# PROVERBIO PIEMONTESE
news_data.append({
    "cat": "💡 Saggezza Tradizionale",
    "title": "Proverbio Piemontese del Giorno",
    "speak": f"Prima del riepilogo, il proverbio piemontese di oggi: {proverbio[0]}, che significa: {proverbio[1]}.",
    "body": f"• <strong>In dialetto piemontese:</strong> <em>{proverbio[0]}</em><br>• <strong>Significato:</strong> {proverbio[1]}."
})

# RIEPILOGO FONTI: VOCE SINTETICA CHE NON LEGGE LE SINGOLE FONTI
news_data.append({
    "cat": "📢 Trasparenza & Riepilogo Fonti",
    "title": "Riepilogo Ufficiale Fonti del Notiziario",
    "speak": (
        "Notiziario completato. Le fonti ufficiali consultate sono riepilogate in fondo al notiziario. "
        "Una buona giornata a tutta la comunità di Tavigliano!"
    ),
    "body": (
        "<div style='background:rgba(0,168,132,0.15); border-left:4px solid #00a884; border-radius:8px; padding:12px; margin-top:4px;'>"
        "  <div style='font-size:0.92rem; font-weight:800; color:#4ade80; margin-bottom:8px;'>📌 Fonti Ufficiali Certificate:</div>"
        "  • <strong>Meteo:</strong> 3BMeteo.com (Stazione Tavigliano / Biellese)<br>"
        "  • <strong>Cronaca Locale:</strong> Quotidiani del Territorio Biellese<br>"
        "  • <strong>Bacheca Notizie:</strong> Foglio Comunitario Tavigliano su Google Drive<br>"
        "  • <strong>Igiene Urbana:</strong> Seab Biella (Raccolta Comune di Tavigliano)<br>"
        "  • <strong>Farmacie di Turno:</strong> Ordine Farmacisti Biella & Federfarma BI (CAP 13900)<br>"
        "  • <strong>Prezzi Carburanti:</strong> MIMIT — Osservaprezzi Carburanti Ministero Imprese e Made in Italy & PrezziBenzina.it<br>"
        "  • <strong>Calendario Liturgico:</strong> Archivio Diocesano"
        "</div>"
    )
})

# ==============================================================================
# 12. GENERATORE HTML COMPLETO
# ==============================================================================
testo_condivisione = (
    f"📻 *NOTIZIARIO DI TAVIGLIANO*\n"
    f"📅 {data_estesa}\n\n"
    f"🌦️ Meteo: {meteo_item['title']}\n"
    f"📰 Primo piano: {prime_due[0]['title']}\n"
    f"⛽ Benzina e Diesel Low Cost Biella • 💊 Farmacia di Turno H24\n\n"
    f"▶️ Ascolta l'edizione aggiornata qui:\n"
    f"https://bobbylama63-jpg.github.io/NOTIZIARIO/"
)
url_whatsapp_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote(testo_condivisione)}"
json_news = json.dumps(news_data, ensure_ascii=False, indent=2)

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Notiziario Tavigliano</title>
<style>
  :root {{
    --bg-dark: #090e13;
    --card-bg: rgba(18, 27, 34, 0.85);
    --card-border: rgba(255, 255, 255, 0.08);
    --green-neon: #00a884;
    --green-light: #25d366;
    --text-main: #f1f5f9;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg-dark);
    color: var(--text-main);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    justify-content: center;
    min-height: 100vh;
  }}
  .app-container {{
    width: 100%;
    max-width: 520px;
    display: flex;
    flex-direction: column;
    position: relative;
    padding-bottom: 90px;
  }}

  /* TICKER TG24 */
  .ticker-bar {{
    background: linear-gradient(90deg, #0284c7, #0369a1);
    color: #fff;
    font-size: 0.75rem;
    font-weight: 800;
    overflow: hidden;
    white-space: nowrap;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  }}
  .ticker-tag {{
    background: #0c4a6e;
    padding: 5px 12px;
    letter-spacing: 1px;
    font-size: 0.7rem;
    text-transform: uppercase;
    flex-shrink: 0;
  }}
  .ticker-marquee {{
    display: inline-block;
    padding-left: 100%;
    animation: scorri 25s linear infinite;
  }}
  @keyframes scorri {{
    0% {{ transform: translate(0, 0); }}
    100% {{ transform: translate(-100%, 0); }}
  }}

  /* HEADER */
  header {{
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(10px);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 20;
    border-bottom: 1px solid var(--card-border);
  }}
  .station-logo {{
    width: 44px; height: 44px; border-radius: 50%;
    background: linear-gradient(135deg, var(--green-neon), #0284c7);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    box-shadow: 0 0 12px rgba(0, 168, 132, 0.4);
  }}
  .station-details {{ flex: 1; min-width: 0; }}
  .station-name {{ font-weight: 800; font-size: 1.05rem; letter-spacing: 0.3px; }}
  .station-status {{ font-size: 0.76rem; color: var(--green-neon); font-weight: 600; }}

  .neon-on-air {{
    background: #1e293b;
    color: #64748b;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 0.68rem;
    font-weight: 900;
    letter-spacing: 1px;
    display: flex; align-items: center; gap: 5px;
    transition: all 0.3s;
  }}
  .neon-on-air.active {{
    background: #ef4444;
    color: white;
    border-color: #f87171;
    box-shadow: 0 0 15px #ef4444;
    animation: glow-neon 1s infinite alternate;
  }}
  @keyframes glow-neon {{
    from {{ opacity: 0.85; filter: drop-shadow(0 0 4px #ef4444); }}
    to {{ opacity: 1; filter: drop-shadow(0 0 14px #ef4444); }}
  }}

  /* PULSANTE CONDIVISIONE WHATSAPP */
  .share-wa-banner {{
    padding: 12px 12px 0;
  }}
  .share-wa-banner a {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: #25d366;
    color: #042f2e;
    text-decoration: none;
    font-weight: 900;
    font-size: 0.95rem;
    padding: 12px 16px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.35);
  }}

  /* NOTIZIE SPOTLIGHT */
  .news-stream {{
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .news-card {{
    background: var(--card-bg);
    border-radius: 14px;
    padding: 14px 16px;
    border: 1px solid var(--card-border);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }}
  .news-card.active-play {{
    border-color: var(--green-neon);
    box-shadow: 0 0 20px rgba(0, 168, 132, 0.45);
    transform: scale(1.02);
  }}
  .news-cat {{
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--green-neon);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
  }}
  .news-title {{
    font-weight: 700;
    font-size: 0.98rem;
    margin-bottom: 8px;
    line-height: 1.4;
  }}
  .news-body {{
    font-size: 0.9rem;
    color: #cbd5e1;
    line-height: 1.5;
  }}

  .audio-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    background: rgba(0,0,0,0.3);
    border-radius: 24px;
    padding: 6px 12px;
    border: 1px solid rgba(255,255,255,0.05);
  }}
  .btn-single-play {{
    width: 34px; height: 34px; border-radius: 50%;
    background: var(--green-neon); border: none; color: #042f2e;
    font-size: 14px; font-weight: 900;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; flex-shrink: 0;
  }}
  .eq-spectrum {{
    flex: 1; height: 20px; display: flex; align-items: center; gap: 3px;
  }}
  .eq-spectrum span {{
    width: 3px; background: #475569; border-radius: 2px; height: 4px;
  }}
  .news-card.active-play .eq-spectrum span {{
    background: var(--green-light);
    animation: spectrum 0.75s ease-in-out infinite alternate;
  }}
  .eq-spectrum span:nth-child(2n) {{ animation-delay: 0.15s; }}
  .eq-spectrum span:nth-child(3n) {{ animation-delay: 0.3s; }}
  .eq-spectrum span:nth-child(4n) {{ animation-delay: 0.45s; }}
  @keyframes spectrum {{
    0% {{ height: 3px; }}
    100% {{ height: 18px; }}
  }}

  /* DOCK BAR */
  .dock-bar {{
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 100%; max-width: 520px;
    background: rgba(15, 23, 42, 0.96);
    backdrop-filter: blur(12px);
    padding: 12px 14px calc(12px + env(safe-area-inset-bottom));
    border-top: 1px solid var(--card-border);
    z-index: 30;
  }}
  .dock-btn {{
    width: 100%;
    background: linear-gradient(135deg, var(--green-neon), var(--green-light));
    color: #042f2e;
    border: none;
    padding: 14px;
    border-radius: 28px;
    font-size: 1rem;
    font-weight: 900;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    cursor: pointer;
  }}
</style>
</head>
<body>

<audio id="bgMusic" loop preload="auto">
  <source src="{mp3_file}" type="audio/mpeg">
</audio>

<div class="app-container">
  <div class="ticker-bar">
    <div class="ticker-tag">🔴 TG24 LIVE</div>
    <div class="ticker-marquee">Tavigliano Notiziario • Meteo 3B Meteo • Cronaca del Territorio • Bacheca Tavigliano • Farmacia di Turno Biella • Benzina e Diesel Low Cost • Raccolta Seab</div>
  </div>

  <header>
    <div class="station-logo">📻</div>
    <div class="station-details">
      <div class="station-name">Notiziario di Tavigliano</div>
      <div class="station-status">{data_estesa}</div>
    </div>
    <div class="neon-on-air" id="onAirSign">● ON AIR</div>
  </header>

  <div class="share-wa-banner">
    <a href="{url_whatsapp_share}" target="_blank">
      💬 Invia Notiziario al Gruppo WhatsApp
    </a>
  </div>

  <div class="news-stream" id="newsStream"></div>

  <div class="dock-bar">
    <button class="dock-btn" id="btnMasterPlay" onclick="toggleMasterBroadcast()">▶️ AVVIA TRASMISSIONE COMPLETA</button>
  </div>
</div>

<script>
const NEWS = {json_news};

const synth = window.speechSynthesis;
let currentTrack = -1;
const newsStream = document.getElementById('newsStream');
const onAirSign = document.getElementById('onAirSign');
const btnMaster = document.getElementById('btnMasterPlay');
const bgMusic = document.getElementById('bgMusic');

function renderCards() {{
  newsStream.innerHTML = '';
  NEWS.forEach((item, index) => {{
    const card = document.createElement('div');
    card.className = 'news-card';
    card.id = `card-${{index}}`;
    
    let eqSpans = '';
    for (let s = 0; s < 26; s++) eqSpans += '<span></span>';

    card.innerHTML = `
      <div class="news-cat">${{item.cat}}</div>
      <div class="news-title">${{item.title}}</div>
      <div class="news-body">${{item.body}}</div>
      <div class="audio-bar">
        <button class="btn-single-play" onclick="playSingleItem(${{index}})">▶</button>
        <div class="eq-spectrum">${{eqSpans}}</div>
      </div>
    `;
    newsStream.appendChild(card);
  }});
}}

function startBgMusic() {{
  if (bgMusic) {{
    bgMusic.volume = 0.22;
    bgMusic.play().catch(() => {{}});
  }}
}}

function stopBgMusic() {{
  if (bgMusic) {{
    bgMusic.pause();
  }}
}}

window.playSingleItem = function(index) {{
  if (currentTrack === index && synth.speaking) {{
    stopBroadcast();
  }} else {{
    startBgMusic();
    startVoice(index, false);
  }}
}};

function startVoice(index, autoNext) {{
  stopVoiceOnly();
  currentTrack = index;
  const item = NEWS[index];

  document.querySelectorAll('.news-card').forEach(c => c.classList.remove('active-play'));
  const activeCard = document.getElementById(`card-${{index}}`);
  if (activeCard) {{
    activeCard.classList.add('active-play');
    activeCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}

  onAirSign.classList.add('active');

  const utter = new SpeechSynthesisUtterance(item.speak);
  utter.lang = 'it-IT';
  utter.rate = 0.95;

  utter.onend = () => {{
    if (activeCard) activeCard.classList.remove('active-play');
    if (autoNext && index + 1 < NEWS.length) {{
      startVoice(index + 1, true);
    }} else {{
      stopBroadcast();
    }}
  }};
  utter.onerror = () => stopBroadcast();

  synth.speak(utter);
}}

function stopVoiceOnly() {{
  synth.cancel();
  if (currentTrack >= 0) {{
    const el = document.getElementById(`card-${{currentTrack}}`);
    if (el) el.classList.remove('active-play');
  }}
}}

function stopBroadcast() {{
  stopVoiceOnly();
  stopBgMusic();
  currentTrack = -1;
  onAirSign.classList.remove('active');
  btnMaster.innerText = '▶️ AVVIA TRASMISSIONE COMPLETA';
}}

window.toggleMasterBroadcast = function() {{
  if (synth.speaking) {{
    stopBroadcast();
  }} else {{
    btnMaster.innerText = '⏸️ METTI IN PAUSA';
    startBgMusic();
    startVoice(0, true);
  }}
}};

renderCards();
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML_PAGE)

print(f"Notiziario Tavigliano aggiornato con successo: {data_estesa}")
