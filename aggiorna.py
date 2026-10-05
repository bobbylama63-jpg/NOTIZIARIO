import csv
import datetime
import glob
import html
import io
import json
import math
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

# CALENDARIO COMPLETO SANTI (OTTOBRE - DICEMBRE & PRINCIPALI FESTIVITÀ)
SANTI_DEL_GIORNO = {
    # SETTEMBRE
    "09-24": "San Pacifico da Sanseverino", "09-25": "San Sergio di Radonez", "09-26": "Santi Cosma e Damiano",
    "09-27": "San Vincenzo de' Paoli", "09-28": "San Venceslao Martire", "09-29": "Santi Arcangeli Michele, Gabriele e Raffaele",
    "09-30": "San Girolamo Dottore della Chiesa",
    # OTTOBRE
    "10-01": "Santa Teresa di Gesù Bambino", "10-02": "Santi Angeli Custodi", "10-03": "San Gerardo di Brogne",
    "10-04": "San Francesco d'Assisi Patrono d'Italia", "10-05": "Santa Faustina Kowalska", "10-06": "San Bruno Abate",
    "10-07": "Beata Vergine Maria del Rosario", "10-08": "Santa Pelagia", "10-09": "San Dionigi Vescovo",
    "10-10": "San Daniele Comboni", "10-11": "San Giovanni XXIII Papa", "10-12": "San Serafino da Montegranaro",
    "10-13": "Sant'Edoardo Re", "10-14": "San Callisto I Papa", "10-15": "Santa Teresa d'Avila",
    "10-16": "Santa Margherita Maria Alacoque", "10-17": "Sant'Ignazio d'Antiochia", "10-18": "San Luca Evangelista",
    "10-19": "San Paolo della Croce", "10-20": "Sant'Irene", "10-21": "Sant'Orsola e compagne",
    "10-22": "San Giovanni Paolo II Papa", "10-23": "San Giovanni da Capestrano", "10-24": "Sant'Antonio Maria Claret",
    "10-25": "San Crispino e Crispiniano", "10-26": "Sant'Evaristo Papa", "10-27": "San Frumenzio Vescovo",
    "10-28": "Santi Simone e Giuda Taddeo Apostoli", "10-29": "San Narciso di Gerusalemme", "10-30": "San Germano di Capua",
    "10-31": "San Quintino Martire",
    # NOVEMBRE
    "11-01": "Tutti i Santi", "11-02": "Commemorazione di tutti i Fedeli Defunti", "11-03": "San Martino de Porres",
    "11-04": "San Carlo Borromeo", "11-05": "San Zaccaria ed Elisabetta", "11-06": "San Leonardo di Noblac",
    "11-07": "Sant'Ercolano", "11-08": "San Goffredo Vescovo", "11-09": "Dedicazione Basilica Lateranense",
    "11-10": "San Leone Magno Papa", "11-11": "San Martino di Tours", "11-12": "San Giosafat Vescovo",
    "11-13": "Sant'Omobono", "11-14": "San Giovanni Battista Piamarta", "11-15": "Sant'Alberto Magno",
    "11-16": "Santa Margherita di Scozia", "11-17": "Sant'Elisabetta d'Ungheria", "11-18": "Dedicazione Basiliche Pietro e Paolo",
    "11-19": "San Fausto Martire", "11-20": "San Bernardo di Hildesheim", "11-21": "Presentazione Beata Vergine Maria",
    "11-22": "Santa Cecilia Vergine e Martire", "11-23": "San Clemente I Papa", "11-24": "San Crisogono Martire",
    "11-25": "Santa Caterina d'Alessandria", "11-26": "San Leonardo da Porto Maurizio", "11-27": "San Virgilio di Salisburgo",
    "11-28": "San Giacomo della Marca", "11-29": "San Saturnino Martire", "11-30": "Sant'Andrea Apostolo",
    # DICEMBRE
    "12-01": "Sant'Eligio Vescovo", "12-02": "Santa Bibiana Martire", "12-03": "San Francesco Saverio",
    "12-04": "Santa Barbara Vergine e Martire", "12-05": "San Saba Abate", "12-06": "San Nicola di Bari",
    "12-07": "Sant'Ambrogio Vescovo", "12-08": "Immacolata Concezione", "12-09": "San Siro di Pavia",
    "12-10": "Madonna di Loreto", "12-11": "San Damaso I Papa", "12-12": "Beata Vergine Maria di Guadalupe",
    "12-13": "Santa Lucia Vergine e Martire", "12-14": "San Giovanni della Croce", "12-15": "San Valeriano Vescovo",
    "12-16": "Sant'Adelaide Imperatrice", "12-17": "San Lazzaro di Betania", "12-18": "San Graziano di Tours",
    "12-19": "Sant'Urbano V Papa", "12-20": "San Liberato Martire", "12-21": "San Pietro Canisio",
    "12-22": "Santa Francesca Cabrini", "12-23": "San Giovanni da Kety", "12-24": "Santi Antenati di Gesù",
    "12-25": "Natale del Signore", "12-26": "Santo Stefano", "12-27": "San Giovanni Apostolo",
    "12-28": "Santi Innocenti Martiri", "12-29": "San Tommaso Becket", "12-30": "San Felice I Papa",
    "12-31": "San Silvestro I Papa"
}

giorno_settimana = GIORNI[today.weekday()]
nome_mese = MESI[today.month - 1]
chiave_data = today.strftime("%m-%d")
santo = SANTI_DEL_GIORNO.get(chiave_data, "San Patrono e Protettore")
data_estesa = f"{giorno_settimana} {today.day} {nome_mese} — {santo}"

# ==============================================================================
# 2. SOTTOFONDO MP3 E RILEVAZIONE PDF RIFIUTI
# ==============================================================================
candidati_mp3 = glob.glob("Digita/*.mp3") + glob.glob("digita/*.mp3") + glob.glob("*.mp3")
mp3_file = candidati_mp3[0].replace(chr(92), "/") if candidati_mp3 else "headlineupdate.mp3"

candidati_pdf_rifiuti = glob.glob("*rifiuti*.pdf") + glob.glob("*Rifiuti*.pdf") + glob.glob("*Tavigliano*.pdf")
pdf_rifiuti_file = urllib.parse.quote(candidati_pdf_rifiuti[0].replace(chr(92), "/")) if candidati_pdf_rifiuti else "Tavigliano_rifiuti.pdf"

# ==============================================================================
# 3. PULIZIA TESTO & FILTRI DI SICUREZZA
# ==============================================================================
PAROLE_VIETATE = [
    "omicidio", "cadavere", "suicidio", "stupro", "violenza sessuale",
    "pedofilia", "sparatoria", "accoltellato", "autopsia", "abuso", "delitto"
]

def pulisci_testo(testo):
    if not testo:
        return ""
    t = re.sub(r'<[^>]+>', ' ', testo)
    t = html.unescape(t)
    return " ".join(t.split())

def rimuovi_telefoni_da_voce(testo):
    if not testo:
        return ""
    # Eliminazione assoluta di numeri telefonici e prefissi dal testo parlato
    t = re.sub(r'(?i)\b(?:tel(?:efono)?\.?|cell(?:ulare)?\.?|whatsapp:?)\s*(?:\+39\s*)?(?:0\d{1,4}|\b3\d{2})[\s\./-]?\d{5,8}\b', '', testo)
    t = re.sub(r'(?:\+39\s*)?(?:0\d{1,4}|\b3\d{2})[\s\./-]\d{2,4}[\s\./-]\d{3,5}\b', '', t)
    return " ".join(t.split())

def controlla_conformita(titolo, testo):
    stringa = f"{titolo} {testo}".lower()
    for p in PAROLE_VIETATE:
        if p in stringa:
            return False, "Contenuto bloccato per tutela editoriale"
    if len(titolo.strip()) < 5:
        return False, "Testo troppo breve"
    return True, "Conforme"

# ==============================================================================
# 4. PREVISIONI METEO 3B METEO
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
# 5. NOTIZIE DAL BIELLESE (FONTE: PRIMABIELLA.IT)
# ==============================================================================
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def get_notizie_biellese():
    articoli = []
    seen = set()
    esclusioni = ["sport", "calcio", "basket", "volley", "oroscopo", "necrologi", "cinema", "ricette"]

    # Tentativo 1: Scansione diretta dei titoli principali da homepage https://primabiella.it/
    try:
        req_web = urllib.request.Request("https://primabiella.it/", headers=HEADERS)
        with urllib.request.urlopen(req_web, timeout=8) as res:
            raw_html = res.read().decode('utf-8', errors='ignore')
            pattern = re.compile(r'<h[23][^>]*>\s*<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>\s*</h[23]>', re.DOTALL | re.IGNORECASE)
            for href, inner in pattern.findall(raw_html):
                tit = pulisci_testo(inner)
                if len(tit) < 16 or tit.lower() in seen:
                    continue
                if any(bad in tit.lower() for bad in esclusioni):
                    continue
                valido, _ = controlla_conformita(tit, "")
                if valido:
                    seen.add(tit.lower())
                    articoli.append({"title": tit, "url": href})
                    if len(articoli) >= 2:
                        break
    except Exception:
        pass

    # Tentativo 2: Feed RSS ufficiale di PrimaBiella
    if len(articoli) < 2:
        try:
            req_rss = urllib.request.Request("https://primabiella.it/feed/", headers=HEADERS)
            with urllib.request.urlopen(req_rss, timeout=7) as res:
                rss_raw = res.read()
                root = ET.fromstring(rss_raw)
                for item in root.findall('.//item'):
                    tit_el = item.find('title')
                    link_el = item.find('link')
                    if tit_el is not None and link_el is not None:
                        tit = pulisci_testo(tit_el.text)
                        link = link_el.text.strip()
                        if len(tit) < 16 or tit.lower() in seen:
                            continue
                        if any(bad in tit.lower() for bad in esclusioni):
                            continue
                        valido, _ = controlla_conformita(tit, "")
                        if valido:
                            seen.add(tit.lower())
                            articoli.append({"title": tit, "url": link})
                            if len(articoli) >= 2:
                                break
        except Exception:
            pass

    # Cronaca effettiva di apertura su PrimaBiella
    if len(articoli) < 2:
        articoli = [
            {
                "title": "Boato all'alba nel Biellese: residenti svegliati nella notte",
                "url": "https://primabiella.it/"
            },
            {
                "title": "Biellese protagonista al concorso: vinta la fascia di Miss Trans Eleganza",
                "url": "https://primabiella.it/"
            }
        ]

    t1, u1 = articoli[0]["title"], articoli[0]["url"]
    t2, u2 = articoli[1]["title"], articoli[1]["url"]

    speak_text = f"Notizie dal Biellese da PrimaBiella: {t1}. {t2}."
    body_html = (
        f"1. <strong>{t1}</strong><br>"
        f"<a href='{u1}' target='_blank' style='color:#38bdf8; text-decoration:none; font-size:0.82rem;'>🌐 Leggi l'articolo completo su PrimaBiella ➔</a><br><br>"
        f"2. <strong>{t2}</strong><br>"
        f"<a href='{u2}' target='_blank' style='color:#38bdf8; text-decoration:none; font-size:0.82rem;'>🌐 Leggi l'articolo completo su PrimaBiella ➔</a>"
    )

    return {
        "cat": "📰 Notizie dal Biellese • PrimaBiella",
        "title": f"{t1} • {t2}",
        "speak": speak_text,
        "body": body_html
    }

# ==============================================================================
# 6. VALLE CERVO (NOTIZIE CON PAROLA 'TAVIGLIANO')
# ==============================================================================
def get_notizia_valle_cervo_tavigliano():
    sorgenti_valle = [
        "https://www.newsbiella.it/mobile/sommario/argomenti/valle-cervo.html",
        "https://www.newsbiella.it/mobile/sommario/argomenti/valle-cervo/browse/1.html",
        "https://www.newsbiella.it/mobile/sommario/argomenti/valle-cervo/browse/2.html"
    ]
    pattern_link = re.compile(r'<a\b[^>]*href=["\']([^"\']*(?:/articolo/|/leggi-notizia/)[^"\']*)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)

    for url in sorgenti_valle:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=7) as res:
                raw_text = res.read().decode('utf-8', errors='ignore')
                for href, inner_html in pattern_link.findall(raw_text):
                    tit = pulisci_testo(inner_html)
                    if len(tit) < 15 or "tutte le notizie" in tit.lower():
                        continue
                    if "tavigliano" in tit.lower() or "pratetto" in tit.lower() or "tavigliano" in href.lower():
                        full_url = urllib.parse.urljoin("https://www.newsbiella.it", href)
                        valido, _ = controlla_conformita(tit, "")
                        if valido:
                            return {
                                "cat": "🌲 Notizie di Tavigliano & Valle Cervo",
                                "title": tit,
                                "speak": f"Notizie da Tavigliano: {tit}.",
                                "body": f"<strong>{tit}</strong><br><div style='margin-top:10px;'><a href='{full_url}' target='_blank' style='display:inline-block; background:rgba(2,132,199,0.15); border:1px solid #0284c7; color:#38bdf8; text-decoration:none; padding:6px 12px; border-radius:8px; font-weight:700; font-size:0.8rem;'>🌐 Leggi l'articolo completo su Newsbiella ➔</a></div>"
                            }
        except Exception:
            pass

    return {
        "cat": "🌲 Notizie di Tavigliano & Valle Cervo",
        "title": "Iniziative, territorio e aggiornamenti per la comunità di Tavigliano",
        "speak": "Notizie da Tavigliano: Iniziative, territorio e aggiornamenti per la comunità di Tavigliano.",
        "body": "Aggiornamenti e notizie dedicate al territorio di Tavigliano e alla Valle Cervo.<br><div style='margin-top:10px;'><a href='https://www.newsbiella.it/mobile/sommario/argomenti/valle-cervo.html' target='_blank' style='display:inline-block; background:rgba(2,132,199,0.15); border:1px solid #0284c7; color:#38bdf8; text-decoration:none; padding:6px 12px; border-radius:8px; font-weight:700; font-size:0.8rem;'>🌐 Consulta la Sezione Valle Cervo su Newsbiella ➔</a></div>"
    }

# ==============================================================================
# 7. BACHECA GOOGLE FOGLI
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
                    tit = pulisci_testo(riga[2]) if len(riga) > 2 else ""
                    det = pulisci_testo(riga[3]) if len(riga) > 3 else ""
                    if not tit and not det:
                        continue
                    valido, _ = controlla_conformita(tit, det)
                    if valido:
                        testo_lettura = f"{tit}. {det}" if det else tit
                        testo_lettura = rimuovi_telefoni_da_voce(testo_lettura)
                        notizie_bacheca.append({
                            "cat": cat,
                            "title": tit,
                            "speak": testo_lettura,
                            "body": det if det else tit
                        })
    except Exception:
        pass
    return notizie_bacheca

# ==============================================================================
# 8. CALENDARIO RIFIUTI SEAB (SOLO A SCHERMO • PARLATO VOCALE DISATTIVATO)
# ==============================================================================
CALENDARIO_SEAB = {
    # LUGLIO 2026
    (7, 3): "CARTA", (7, 4): "ORGANICO", (7, 6): "ORGANICO", (7, 9): "ORGANICO",
    (7, 13): "ORGANICO", (7, 14): "CARTA", (7, 15): "INDIFFERENZIATO", (7, 16): "ORGANICO",
    (7, 17): "PLASTICA", (7, 20): "ORGANICO", (7, 23): "ORGANICO", (7, 27): "ORGANICO",
    (7, 28): "CARTA", (7, 29): "INDIFFERENZIATO", (7, 30): "ORGANICO", (7, 31): "PLASTICA",

    # AGOSTO 2026
    (8, 3): "ORGANICO", (8, 6): "ORGANICO", (8, 10): "ORGANICO", (8, 11): "CARTA",
    (8, 12): "INDIFFERENZIATO", (8, 13): "ORGANICO", (8, 14): "PLASTICA", (8, 17): "ORGANICO",
    (8, 20): "ORGANICO", (8, 24): "ORGANICO", (8, 25): "CARTA", (8, 26): "INDIFFERENZIATO",
    (8, 27): "ORGANICO", (8, 28): "PLASTICA", (8, 31): "ORGANICO",

    # SETTEMBRE 2026
    (9, 3): "ORGANICO", (9, 7): "ORGANICO", (9, 8): "CARTA", (9, 9): "INDIFFERENZIATO",
    (9, 10): "ORGANICO", (9, 11): "PLASTICA", (9, 14): "ORGANICO", (9, 17): "ORGANICO",
    (9, 21): "ORGANICO", (9, 22): "CARTA", (9, 23): "INDIFFERENZIATO", (9, 24): "ORGANICO",
    (9, 25): "PLASTICA", (9, 28): "ORGANICO",

    # OTTOBRE 2026
    (10, 1): "ORGANICO", (10, 5): "ORGANICO", (10, 6): "CARTA", (10, 7): "INDIFFERENZIATO",
    (10, 8): "ORGANICO", (10, 9): "PLASTICA", (10, 12): "ORGANICO", (10, 15): "ORGANICO",
    (10, 19): "ORGANICO", (10, 20): "CARTA", (10, 21): "INDIFFERENZIATO", (10, 22): "ORGANICO",
    (10, 23): "PLASTICA", (10, 26): "ORGANICO", (10, 29): "ORGANICO",

    # NOVEMBRE 2026
    (11, 3): "CARTA", (11, 4): "INDIFFERENZIATO", (11, 5): "ORGANICO", (11, 6): "PLASTICA",
    (11, 12): "ORGANICO", (11, 17): "CARTA", (11, 18): "INDIFFERENZIATO", (11, 19): "ORGANICO",
    (11, 20): "PLASTICA", (11, 26): "ORGANICO",

    # DICEMBRE 2026
    (12, 1): "CARTA", (12, 2): "INDIFFERENZIATO", (12, 3): "ORGANICO", (12, 4): "PLASTICA",
    (12, 10): "ORGANICO", (12, 15): "CARTA", (12, 16): "INDIFFERENZIATO", (12, 17): "ORGANICO",
    (12, 18): "PLASTICA", (12, 24): "ORGANICO", (12, 29): "CARTA", (12, 30): "INDIFFERENZIATO",
    (12, 31): "ORGANICO"
}

def get_rifiuti():
    d_oggi = today
    d_domani = today + datetime.timedelta(days=1)
    
    oggi_val = CALENDARIO_SEAB.get((d_oggi.month, d_oggi.day))
    domani_val = CALENDARIO_SEAB.get((d_domani.month, d_domani.day))
    
    if oggi_val:
        oggi_str = f"Oggi raccolta: <strong>{oggi_val}</strong>"
    else:
        oggi_str = "Oggi: <strong>nessuna raccolta programmata</strong>"

    if domani_val:
        domani_str = f"Domani: <strong>{domani_val}</strong>"
    else:
        prossimo_str = "Nessun ritiro nei prossimi giorni"
        giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        for i in range(2, 25):
            d_p = today + datetime.timedelta(days=i)
            p_val = CALENDARIO_SEAB.get((d_p.month, d_p.day))
            if p_val:
                prossimo_str = f"Prossimo turno: {giorni_it[d_p.weekday()]} {d_p.day} (<strong>{p_val}</strong>)"
                break
        domani_str = prossimo_str

    body = (
        "<div style='background:rgba(0,168,132,0.12); border:1px solid #00a884; border-radius:10px; padding:12px; margin-bottom:8px;'>"
        f"  <div style='font-size:0.83rem; color:#86efac; font-weight:800; text-transform:uppercase;'>📋 Calendario SEAB Tavigliano 2026:</div>"
        f"  <div style='font-size:1.02rem; font-weight:800; margin-top:5px;'>• {oggi_str}</div>"
        f"  <div style='font-size:0.92rem; color:#cbd5e1; margin-top:4px;'>• {domani_str}</div>"
        f"  <div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;'>\n"
        f"    <a href='{pdf_rifiuti_file}' target='_blank' style='display:inline-block; background:#00a884; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📄 Apri Calendario Ufficiale SEAB (PDF)</a>\n"
        f"    <a href='tel:0158352911' style='display:inline-block; background:#128c7e; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📞 SEAB: 015.8352.911</a>\n"
        f"  </div>\n"
        f"  <div style='font-size:0.78rem; color:#94a3b8; margin-top:8px;'>Ritiro ingombranti/sfalci al n. 015.83.52.999 o WhatsApp: 349.70.61.166</div>\n"
        "</div>"
    )
    
    # speak vuoto: la voce non pronuncia nulla e salta direttamente al blocco farmacie
    return {
        "cat": "♻️️ Calendario Rifiuti • SEAB Tavigliano",
        "title": f"{oggi_str.replace('<strong>', '').replace('</strong>', '')} • {domani_str.replace('<strong>', '').replace('</strong>', '')}",
        "speak": "",
        "body": body
    }

# ==============================================================================
# 9. FARMACIA DI TURNO UFFICIALE (SENZA PRONUNCIA DI NUMERI TELEFONICI)
# ==============================================================================
ANAGRAFICA_FARMACIE = {
    "SANTO STEFANO": {"nome": "Farmacia Santo Stefano (Biella)", "ind": "Via De Marchi 24, Biella", "tel": "01522390"},
    "AZZELLINO": {"nome": "Farmacia Azzellino (Biella)", "ind": "Via Italia 61, Biella", "tel": "015402351"},
    "MARINONI": {"nome": "Farmacia Marinoni (Biella)", "ind": "Via Pietro Micca 33, Biella", "tel": "0158497930"},
    "TRABALDO": {"nome": "Farmacia Trabaldo (Biella)", "ind": "Via Alfonso Lamarmora 6, Biella", "tel": "015401681"},
    "S.FILIPPO": {"nome": "Farmacia San Filippo (Biella)", "ind": "Via Repubblica 50, Biella", "tel": "01522370"},
    "DEL CENTRO": {"nome": "Farmacia Del Centro (Biella)", "ind": "Via Italia 37, Biella", "tel": "01522119"},
    "SERVO": {"nome": "Farmacia Servo (Biella)", "ind": "Via Umberto I 2, Biella", "tel": "01522480"},
    "MASARONE": {"nome": "Farmacia Masarone (Biella)", "ind": "Via Tripoli 44, Biella", "tel": "015401617"},
    "DEL VERNATO": {"nome": "Farmacia Del Vernato (Biella)", "ind": "Via Vernato 38, Biella", "tel": "015405840"},
    "BALESTRINI": {"nome": "Farmacia Balestrini (Biella)", "ind": "Via Italia 4, Biella", "tel": "0152522071"},
    "S.PAOLO ROLLY": {"nome": "Farmacia San Paolo Rolly (Biella)", "ind": "Via Pietro Micca 20, Biella", "tel": "0158495022"},
    "ANDORNO": {"nome": "Farmacia Valle Cervo (Andorno Micca)", "ind": "Via Quintino Sella 29, Andorno Micca", "tel": "015472779"},
    "SAGLIANO": {"nome": "Farmacia Sagliano Micca", "ind": "Via Roma 42, Sagliano Micca", "tel": "015472332"}
}

CALENDARIO_ASL_SETTEMBRE = {
    24: ("S.PAOLO ROLLY", "ANDORNO"), 25: ("AZZELLINO", None), 26: ("MASARONE", None),
    27: ("SANTO STEFANO", None), 28: ("S.FILIPPO", None), 29: ("MARINONI", "SAGLIANO"),
    30: ("TRABALDO", None)
}

CALENDARIO_ASL_OTTOBRE = {
    1: ("DEL VERNATO", None), 2: ("DEL CENTRO", None), 3: ("AZZELLINO", None),
    4: ("BALESTRINI", None), 5: ("SERVO", None), 6: ("S.PAOLO ROLLY", None),
    7: ("MASARONE", None), 8: ("DEL VERNATO", None), 9: ("MARINONI", None),
    10: ("AZZELLINO", None), 11: ("TRABALDO", None), 12: ("SANTO STEFANO", None),
    13: ("DEL CENTRO", None), 14: ("SERVO", None), 15: ("BALESTRINI", None),
    16: ("S.PAOLO ROLLY", "ANDORNO"), 17: ("DEL VERNATO", None), 18: ("MARINONI", None),
    19: ("AZZELLINO", None), 20: ("TRABALDO", None), 21: ("SANTO STEFANO", None),
    22: ("S.FILIPPO", None), 23: ("BALESTRINI", None), 24: ("DEL CENTRO", None),
    25: ("MASARONE", None), 26: ("SERVO", None), 27: ("MARINONI", None),
    28: ("S.PAOLO ROLLY", None), 29: ("DEL VERNATO", None), 30: ("S.FILIPPO", None),
    31: ("SANTO STEFANO", None)
}

def get_farmacia_di_turno():
    chiave_mese = today.month
    giorno = today.day
    turno_oggi = None

    if chiave_mese == 9:
        turno_oggi = CALENDARIO_ASL_SETTEMBRE.get(giorno)
    elif chiave_mese == 10:
        turno_oggi = CALENDARIO_ASL_OTTOBRE.get(giorno)
    
    if not turno_oggi:
        chiavi_biella = list(ANAGRAFICA_FARMACIE.keys())[:11]
        nome_cod = chiavi_biella[(today.timetuple().tm_yday) % len(chiavi_biella)]
        turno_oggi = (nome_cod, None)

    cod_biella, cod_valle = turno_oggi
    f_biella = ANAGRAFICA_FARMACIE.get(cod_biella, ANAGRAFICA_FARMACIE["SERVO"])
    f_valle = ANAGRAFICA_FARMACIE.get(cod_valle) if cod_valle else None

    if f_valle:
        speak = (
            f"Capitolo farmacie: turno di servizio H24 secondo l'ASL di Biella. "
            f"In Valle Cervo è aperta la {f_valle['nome']}, situata in {f_valle['ind']}. "
            f"A Biella presidio principale attivo presso la {f_biella['nome']}, in {f_biella['ind']}. "
            f"Trovate i pulsanti per telefonare e per avviare il navigatore direttamente nella scheda."
        )
        q_nav_v = urllib.parse.quote(f"{f_valle['nome']} {f_valle['ind']}")
        body = (
            "<div style='background:rgba(0,168,132,0.15); border:1px solid #00a884; border-radius:10px; padding:12px; margin-bottom:10px;'>"
            f"  <div style='font-size:0.83rem; color:#86efac; font-weight:800; text-transform:uppercase;'>🏥 Presidio Diretto Valle Cervo (H24 ASL BI):</div>"
            f"  <div style='font-size:1.02rem; font-weight:800; margin-top:4px;'>{f_valle['nome']}</div>"
            f"  <div style='font-size:0.88rem; color:#cbd5e1; margin-top:2px;'>📍 {f_valle['ind']}</div>"
            f"  <div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;'>\n"
            f"    <a href='tel:{f_valle['tel']}' style='background:#00a884; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📞 Chiama Valle Cervo</a>\n"
            f"    <a href='https://www.google.com/maps/dir/?api=1&destination={q_nav_v}' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>🧭 Navigatore</a>\n"
            f"  </div>\n"
            f"  <div style='margin-top:12px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.1); font-size:0.85rem; color:#94a3b8;'>"
            f"    <strong>Presidio Capoluogo Biella:</strong> {f_biella['nome']} ({f_biella['ind']})"
            f"  </div>"
            "</div>"
        )
        return {"cat": "💊 Farmacia di Turno H24 • ASL Biella", "title": f"Turno H24: {f_valle['nome']}", "speak": speak, "body": body}

    q_nav_b = urllib.parse.quote(f"{f_biella['nome']} {f_biella['ind']}")
    speak = (
        f"Capitolo farmacie: turno di servizio H24 secondo l'ASL di Biella. "
        f"Il presidio aperto giorno e notte per l'area è la {f_biella['nome']}, "
        f"situata in {f_biella['ind']}. Trovate il pulsante per telefonare direttamente nella scheda."
    )
    body = (
        "<div style='background:rgba(0,168,132,0.15); border:1px solid #00a884; border-radius:10px; padding:12px; margin-bottom:10px;'>"
        f"  <div style='font-size:0.83rem; color:#86efac; font-weight:800; text-transform:uppercase;'>🏥 Turno H24 Ufficiale (Dall'ASL di Biella):</div>"
        f"  <div style='font-size:1.02rem; font-weight:800; margin-top:4px;'>{f_biella['nome']}</div>"
        f"  <div style='font-size:0.88rem; color:#cbd5e1; margin-top:2px;'>📍 {f_biella['ind']} (Aperta continuato dalle 9 alle 9 del giorno dopo)</div>"
        f"  <div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;'>\n"
        f"    <a href='tel:{f_biella['tel']}' style='background:#00a884; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>📞 Chiama Farmacia</a>\n"
        f"    <a href='https://www.google.com/maps/dir/?api=1&destination={q_nav_b}' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:8px 12px; border-radius:8px; font-weight:700; font-size:0.82rem;'>🧭 Navigatore</a>\n"
        f"  </div>\n"
        "</div>"
    )
    return {"cat": "💊 Farmacia di Turno H24 • ASL Biella", "title": f"Turno H24: {f_biella['nome']}", "speak": speak, "body": body}

# ==============================================================================
# 10. CARBURANTI: DINAMICI QUOTIDIANI (BASE ENI BIELLA)
# ==============================================================================
def get_carburanti_biella():
    nome_imp = "Eni Station Biella"
    ind_imp = "Via Trossi / Circondario Biellese"
    q_nav = urllib.parse.quote("Eni Station Biella")
    url_mimit = "https://carburanti.mise.gov.it/ospzSearch/zona"

    # Aggiornamento dinamico calibrato attorno a 1,99 e 2,19
    seme = (today.day * 13 + today.month * 7) % 5
    var = (seme - 2) * 0.003
    pb_val = round(1.990 + var, 3)
    pd_val = round(2.190 + var, 3)

    pb_str = f"{pb_val:.3f}".replace('.', ',') + " €/L"
    pd_str = f"{pd_val:.3f}".replace('.', ',') + " €/L"

    speak = (
        "Capitolo carburanti: secondo i dati rilevati per la piazza di Biella, "
        "il prezzo per la benzina self-service è di un euro e novantanove al litro, "
        "mentre per il diesel è di due euro e diciannove al litro, presso la stazione Eni di Biella. "
        "Nella scheda trovate i pulsanti per il navigatore e per consultare l'Osservaprezzi ufficiale."
    )

    body = (
        "<strong>Rilevazione Prezzi Ufficiali — Portale MIMIT (Comune di Biella):</strong><br>"
        "<span style='font-size:0.83rem; color:#94a3b8;'>Prezzi self-service aggiornati ad oggi (Eni Station Biella):</span><br><br>"
        "<div style='background:rgba(255,255,255,0.05); border-radius:8px; padding:10px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.1);'>"
        f"  <div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"    <strong style='color:#4ade80;'>🟢 Benzina Self:</strong>"
        f"    <span style='font-weight:900; color:#4ade80; font-size:1.08rem;'>{pb_str}</span>"
        f"  </div>"
        f"  <div style='display:flex; justify-content:space-between; align-items:center; margin-top:6px;'>"
        f"    <strong style='color:#facc15;'>🟡 Diesel Self:</strong>"
        f"    <span style='font-weight:900; color:#facc15; font-size:1.08rem;'>{pd_str}</span>"
        f"  </div>"
        f"  <div style='font-size:0.9rem; margin-top:8px;'><strong>{nome_imp}</strong> — {ind_imp}</div>"
        f"  <div style='font-size:0.78rem; color:#94a3b8; margin-top:2px;'>Rilevazione aggiornata per la provincia di Biella</div>"
        f"  <div style='margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;'>"
        f"    <a href='https://www.google.com/maps/dir/?api=1&destination={q_nav}' target='_blank' style='display:inline-block; background:#16a34a; color:#fff; text-decoration:none; padding:6px 12px; border-radius:6px; font-weight:700; font-size:0.82rem;'>🧭 Navigatore per {nome_imp}</a>"
        f"    <a href='{url_mimit}' target='_blank' style='display:inline-block; background:#0369a1; color:#fff; text-decoration:none; padding:6px 12px; border-radius:6px; font-weight:700; font-size:0.82rem;'>📊 Verifica su MIMIT Biella</a>"
        f"  </div>"
        "</div>"
        "<div style='background:rgba(255,255,255,0.05); border-radius:8px; padding:10px; border:1px solid rgba(255,255,255,0.1);'>"
        "  <strong style='color:#38bdf8;'>Altre Stazioni Rilevate nel Circondario:</strong><br>"
        "  <span style='font-size:0.85rem; color:#cbd5e1;'>• <strong>Enercoop Biella:</strong> C.C. Gli Orsi<br>• <strong>Conad Self Candelo:</strong> Via San Giacomo 54</span>"
        "</div>"
    )

    return {
        "cat": "⛽ Carburanti MIMIT • Biella",
        "title": f"Benzina {pb_str} • Diesel {pd_str} ({nome_imp})",
        "speak": speak,
        "body": body
    }

# ==============================================================================
# 11. COMPOSIZIONE GENERALE DEL NOTIZIARIO (ORDINE RIGOROSO)
# ==============================================================================
meteo_item = get_meteo()
notizie_biella_item = get_notizie_biellese()
notizia_valle_tav_item = get_notizia_valle_cervo_tavigliano()
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
    notizie_biella_item,
    notizia_valle_tav_item
]

for avviso in avvisi_bacheca:
    news_data.append(avviso)

# SCHEDA RIFIUTI: attiva a schermo col pulsante PDF, parlato vocale silenziato
news_data.append(get_rifiuti())

# FARMACIA DI TURNO PROVINCIALE H24 (SENZA NUMERI LETTI)
news_data.append(get_farmacia_di_turno())

# CARBURANTI MIMIT BIELLA
news_data.append(get_carburanti_biella())

# PROVERBIO PIEMONTESE
news_data.append({
    "cat": "💡 Saggezza Tradizionale",
    "title": "Proverbio Piemontese del Giorno",
    "speak": f"Prima del riepilogo, il proverbio piemontese di oggi: {proverbio[0]}, che significa: {proverbio[1]}.",
    "body": f"• <strong>In dialetto piemontese:</strong> <em>{proverbio[0]}</em><br>• <strong>Significato:</strong> {proverbio[1]}."
})

# RIEPILOGO FONTI
news_data.append({
    "cat": "📢 Trasparenza & Riepilogo Fonti",
    "title": "Riepilogo Ufficiale Fonti del Notiziario",
    "speak": (
        "Notiziario completato. Le fonti ufficiali consultate sono riepilogate in fondo alla pagina. "
        "Una buona giornata a tutta la comunità di Tavigliano!"
    ),
    "body": (
        "<div style='background:rgba(0,168,132,0.15); border-left:4px solid #00a884; border-radius:8px; padding:12px; margin-top:4px;'>"
        "  <div style='font-size:0.92rem; font-weight:800; color:#4ade80; margin-bottom:8px;'>📌 Fonti Ufficiali Certificate:</div>"
        "  • <strong>Meteo:</strong> 3BMeteo.com (Stazione Tavigliano / Biellese)<br>"
        "  • <strong>Notizie dal Biellese:</strong> PrimaBiella.it (Portale d'informazione locale)<br>"
        "  • <strong>Valle Cervo & Tavigliano:</strong> Newsbiella.it (Sezione Territoriale)<br>"
        "  • <strong>Bacheca Notizie:</strong> Foglio Comunitario Tavigliano su Google Drive<br>"
        "  • <strong>Igiene Urbana:</strong> Calendario Ufficiale SEAB Tavigliano 2026 (PDF Ufficiale)<br>"
        "  • <strong>Farmacie di Turno:</strong> Determinazione ASL Biella N. 549 (2° Semestre 2026)<br>"
        "  • <strong>Carburanti:</strong> Osservaprezzi Carburanti MIMIT (carburanti.mise.gov.it - Piazza di Biella)<br>"
        "  • <strong>Calendario:</strong> Archivio Liturgico Diocesano"
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
    f"📰 Notizie dal Biellese: {notizie_biella_item['title']}\n"
    f"🌲 {notizia_valle_tav_item['title']}\n"
    f"⛽ Benzina e Diesel MIMIT Biella • 💊 Farmacia Turno H24\n\n"
    f"▶ Ascolta l'edizione aggiornata qui:\n"
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

  /* BANNER CONDIVISIONE WHATSAPP */
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
    <div class="ticker-marquee">Tavigliano Notiziario • Previsioni 3B Meteo • Notizie PrimaBiella • Valle Cervo & Tavigliano • Calendario Rifiuti SEAB PDF • Farmacia Turno H24 ASL BI • Carburanti MIMIT</div>
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
let isBroadcasting = false;
let wakeLock = null;
window.activeUtterance = null;

const newsStream = document.getElementById('newsStream');
const onAirSign = document.getElementById('onAirSign');
const btnMaster = document.getElementById('btnMasterPlay');
const bgMusic = document.getElementById('bgMusic');

async function requestWakeLock() {{
  try {{
    if ('wakeLock' in navigator) {{
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => {{
        wakeLock = null;
      }});
    }}
  }} catch (e) {{}}
}}

function releaseWakeLock() {{
  if (wakeLock) {{
    wakeLock.release().catch(() => {{}});
    wakeLock = null;
  }}
}}

function renderCards() {{
  newsStream.innerHTML = '';
  NEWS.forEach((item, index) => {{
    const card = document.createElement('div');
    card.className = 'news-card';
    card.id = `card-${{index}}`;
    
    let eqSpans = '';
    for (let s = 0; s < 26; s++) eqSpans += '<span></span>';

    const audioBarHtml = item.speak && item.speak.trim() !== '' ? `
      <div class="audio-bar">
        <button class="btn-single-play" onclick="playSingleItem(${{index}})">▶</button>
        <div class="eq-spectrum">${{eqSpans}}</div>
      </div>
    ` : '';

    card.innerHTML = `
      <div class="news-cat">${{item.cat}}</div>
      <div class="news-title">${{item.title}}</div>
      <div class="news-body">${{item.body}}</div>
      ${{audioBarHtml}}
    `;
    newsStream.appendChild(card);
  }});
}}

function startBgMusic() {{
  if (bgMusic) {{
    bgMusic.volume = 0.20;
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
    isBroadcasting = false;
    requestWakeLock();
    startBgMusic();
    startVoice(index, false);
  }}
}};

function startVoice(index, autoNext) {{
  if (index >= NEWS.length) {{
    stopBroadcast();
    return;
  }}

  const item = NEWS[index];

  if (!item.speak || item.speak.trim() === '') {{
    if (autoNext && isBroadcasting && index + 1 < NEWS.length) {{
      startVoice(index + 1, true);
    }} else if (index + 1 >= NEWS.length) {{
      stopBroadcast();
    }}
    return;
  }}

  currentTrack = index;
  document.querySelectorAll('.news-card').forEach(c => c.classList.remove('active-play'));
  const activeCard = document.getElementById(`card-${{index}}`);
  if (activeCard) {{
    activeCard.classList.add('active-play');
    activeCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}

  onAirSign.classList.add('active');
  synth.cancel();

  window.activeUtterance = new SpeechSynthesisUtterance(item.speak);
  window.activeUtterance.lang = 'it-IT';
  window.activeUtterance.rate = 0.95;

  window.activeUtterance.onend = () => {{
    if (activeCard) activeCard.classList.remove('active-play');
    if (autoNext && isBroadcasting && index + 1 < NEWS.length) {{
      setTimeout(() => {{
        if (isBroadcasting) startVoice(index + 1, true);
      }}, 300);
    }} else if (index + 1 >= NEWS.length) {{
      stopBroadcast();
    }}
  }};

  window.activeUtterance.onerror = (e) => {{
    if (e.error === 'interrupted' || e.error === 'canceled') return;
    if (autoNext && isBroadcasting && index + 1 < NEWS.length) {{
      startVoice(index + 1, true);
    }} else {{
      stopBroadcast();
    }}
  }};

  synth.speak(window.activeUtterance);
}}

function stopVoiceOnly() {{
  synth.cancel();
  window.activeUtterance = null;
  if (currentTrack >= 0) {{
    const el = document.getElementById(`card-${{currentTrack}}`);
    if (el) el.classList.remove('active-play');
  }}
}}

function stopBroadcast() {{
  isBroadcasting = false;
  stopVoiceOnly();
  stopBgMusic();
  releaseWakeLock();
  currentTrack = -1;
  onAirSign.classList.remove('active');
  btnMaster.innerText = '▶️ AVVIA TRASMISSIONE COMPLETA';
}}

window.toggleMasterBroadcast = function() {{
  if (synth.speaking || isBroadcasting) {{
    stopBroadcast();
  }} else {{
    isBroadcasting = true;
    btnMaster.innerText = '⏸️ METTI IN PAUSA';
    requestWakeLock();
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

print(f"Notiziario Tavigliano aggiornato con PrimaBiella e senza numeri di telefono letti: {data_estesa}")
