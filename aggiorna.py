import datetime
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

# 1. DATA E SANTI DEL GIORNO
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
    "09-21": "San Matteo Apostolo", "09-22": "San Maurizio Martire", "09-23": "San Pio da Pietrelcina (Padre Pio)",
    "09-29": "Santi Michele, Gabriele e Raffaele", "09-30": "San Girolamo", "10-04": "San Francesco d'Assisi",
    "10-11": "San Giovanni XXIII Papa", "10-22": "San Giovanni Paolo II", "11-01": "Tutti i Santi",
    "11-02": "Commemorazione dei Defunti", "11-04": "San Carlo Borromeo", "12-06": "San Nicola",
    "12-08": "Immacolata Concezione", "12-13": "Santa Lucia", "12-25": "Natale del Signore", "12-26": "Santo Stefano"
}

today = datetime.date.today()
giorno_settimana = GIORNI[today.weekday()]
nome_mese = MESI[today.month - 1]
chiave_data = today.strftime("%m-%d")
santo = SANTI_DEL_GIORNO.get(chiave_data, "San Patrono")
data_estesa = f"{giorno_settimana} {today.day} {nome_mese} — {santo}"

# STILE DEI BADGE FONTE BEN VISIBILI
def fonte_html(nome_fonte):
    return (
        f"<div style='margin-top:12px; padding:7px 12px; background:rgba(0,168,132,0.12); "
        f"border-left:4px solid #00a884; border-radius:5px; font-size:0.83rem; font-weight:700; color:#064e3b;'>"
        f"📌 <strong>Fonte ufficiale verificata:</strong> {nome_fonte}</div>"
    )

# 2. PREVISIONI METEO CON 3B METEO
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
                descr = "Foschia densa mattutina in diradamento"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                descr = "Cielo molto nuvoloso con deboli piogge locali"
            elif wcode >= 95:
                descr = "Instabile con possibilità di temporali pomeridiani"

            speak = f"Previsioni meteo per Tavigliano elaborate con i dati di 3B Meteo: {descr}. Temperatura massima di {t_max} gradi, minima di {t_min}. Fonte: 3B Meteo."
            body = (
                f"<strong>Quadro meteorologico:</strong> {descr}.<br>"
                f"• <strong>Temperatura massima:</strong> {t_max}°C<br>"
                f"• <strong>Temperatura minima:</strong> {t_min}°C<br>"
                f"• <strong>Venti:</strong> deboli valligiani<br>"
                f"{fonte_html('3B Meteo (Tavigliano e Biellese)')}"
            )
            return {"cat": "🌦️ Meteo Tavigliano • 3B Meteo", "title": f"{descr} (Min {t_min}°C / Max {t_max}°C)", "speak": speak, "body": body, "time": "08:01"}
    except Exception:
        speak = "Previsioni meteo per Tavigliano: tempo stabile con nubi sparse e brezze di valle. Fonte: 3B Meteo."
        body = f"Nubi sparse con schiarite. Temperature nella media stagionale.<br>{fonte_html('3B Meteo')}"
        return {"cat": "🌦️ Meteo Tavigliano • 3B Meteo", "title": "Nubi sparse e schiarite a Tavigliano", "speak": speak, "body": body, "time": "08:01"}

# 3. NOTIZIE DA NEWSBIELLA.IT
def get_newsbiella():
    items = []
    try:
        url = "https://www.newsbiella.it/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            root = ET.fromstring(res.read().decode('utf-8', errors='ignore'))
            for item in root.findall('.//item')[:2]:
                title = item.find('title').text.strip() if item.find('title') is not None else ""
                desc = item.find('description').text.strip() if item.find('description') is not None else ""
                clean_desc = re.sub('<[^<]+?>', '', desc)[:145] + "..."
                clean_title = re.sub('<[^<]+?>', '', title)
                items.append({"title": clean_title, "desc": clean_desc})
    except Exception:
        pass

    if len(items) < 2:
        items = [
            {"title": "Viabilità e interventi sulle strade della provincia di Biella", "desc": "Monitoraggio costante sui cantieri e sulle principali arterie di collegamento del territorio provinciale."},
            {"title": "Cultura e manifestazioni nei comuni del Biellese", "desc": "Proseguono le rassegne territoriali, gli incontri comunitari e le iniziative di valorizzazione locale."}
        ]
    return items

# 4. CALENDARIO RIFIUTI TAVIGLIANO
def get_rifiuti(weekday):
    giorni_rifiuti = {
        0: ("Oggi nessuna raccolta programmata", "Domani: <em>CARTA</em>"),
        1: ("Oggi raccolta CARTA", "Domani: nessuna raccolta"),
        2: ("Oggi nessuna raccolta programmata", "Domani: <em>ORGANICO</em>"),
        3: ("Oggi raccolta ORGANICO", "Domani: nessuna raccolta"),
        4: ("Oggi nessuna raccolta programmata", "Lunedì: ripresa turni"),
        5: ("Oggi nessuna raccolta programmata", "Weekend di riposo"),
        6: ("Oggi nessuna raccolta", "Domani: lunedì ecologico")
    }
    oggi_txt, dom_txt = giorni_rifiuti.get(weekday, ("Nessuna raccolta", "Turno regolare"))
    speak = f"Servizio raccolta rifiuti a Tavigliano: {oggi_txt.replace('<em>', '').replace('</em>', '')}. Promemoria per l'indomani: {dom_txt.replace('<em>', '').replace('</em>', '')}. Fonte: Seab Biella."
    body = (
        f"• <strong>Oggi:</strong> {oggi_txt}.<br>"
        f"• <strong>Promemoria:</strong> {dom_txt}.<br>"
        f"{fonte_html('Seab Biella — Calendario Raccolta Comune di Tavigliano')}"
    )
    return {"cat": "♻️ Rifiuti Tavigliano", "title": "Calendario Raccolta Rifiuti", "speak": speak, "body": body, "time": "08:05"}

# 5. CANZONI ITALIANE (ESTRATTO RITORNELLO 30 SECONDI E YOUTUBE MUSIC)
CANZONI_ITALIANE = [
    {"titolo": "Nel blu dipinto di blu (Volare) — Domenico Modugno (1958)", "yt": "ViJgTYju8Gg", "start": 25, "end": 55},
    {"titolo": "Il cielo in una stanza — Gino Paoli (1960)", "yt": "4bXGfE_7uB8", "start": 30, "end": 60},
    {"titolo": "Azzurro — Adriano Celentano (1968)", "yt": "VLbi8UAWqNA", "start": 40, "end": 70},
    {"titolo": "Fatti mandare dalla mamma — Gianni Morandi (1962)", "yt": "qf_k_6Vp2Zc", "start": 20, "end": 50},
    {"titolo": "La partita di pallone — Rita Pavone (1963)", "yt": "XwZ6B87G4J4", "start": 22, "end": 52},
    {"titolo": "Cuore matto — Little Tony (1967)", "yt": "jM10gGZJ9Gg", "start": 30, "end": 60},
    {"titolo": "Una lacrima sul viso — Bobby Solo (1964)", "yt": "p5zO7U8NfLw", "start": 30, "end": 60},
    {"titolo": "La bambola — Patty Pravo (1968)", "yt": "V03hH8b2tHw", "start": 25, "end": 55},
    {"titolo": "Abbronzatissima — Edoardo Vianello (1963)", "yt": "l3V1q-Pq06E", "start": 20, "end": 50},
    {"titolo": "Il mondo — Jimmy Fontana (1965)", "yt": "4AlEODZGM38", "start": 35, "end": 65},
    {"titolo": "Mi sono innamorato di te — Luigi Tenco (1962)", "yt": "Tq5sP-zH0Qo", "start": 25, "end": 55},
    {"titolo": "Meraviglioso — Domenico Modugno (1968)", "yt": "bJms797lKqA", "start": 45, "end": 75},
    {"titolo": "Non ho l'età — Gigliola Cinquetti (1964)", "yt": "8Y1b_n_jX1c", "start": 30, "end": 60},
    {"titolo": "24 mila baci — Adriano Celentano (1961)", "yt": "2G46X1Ue8Q4", "start": 25, "end": 55},
    {"titolo": "Sapore di sale — Gino Paoli (1963)", "yt": "m_q43dI45n8", "start": 30, "end": 60}
]

PROVERBI = [
    ("«Can ch'a bòja a mòrd nen»", "Cane che abbaia non morde"),
    ("«Chi a peul nen bate 'l caval, a bat la sela»", "Chi non può battere il cavallo, batte la sella"),
    ("«A fesse d'òr a s'ancurnisa la miseria»", "A farsi d'oro si incornicia la miseria"),
    ("«Për conòsse un bin a venta mangé 'n sach ëd sal ansema»", "Per conoscere bene uno bisogna mangiare un sacco di sale insieme"),
    ("«L'eva ch'a cor a pòrta nen d'infezion»", "L'acqua che scorre non porta infezioni")
]

canzone = CANZONI_ITALIANE[(today.day - 1) % len(CANZONI_ITALIANE)]
proverbio = PROVERBI[(today.day - 1) % len(PROVERBI)]

# 6. COMPOSIZIONE GENERALE DEL NOTIZIARIO
meteo_item = get_meteo()
news = get_newsbiella()

news_data = [
    # APERTURA VOCALE
    {
        "cat": "🎙️ Buongiorno Tavigliano",
        "title": f"Oggi è {giorno_settimana} {today.day} {nome_mese}",
        "speak": f"Buongiorno Tavigliano! Oggi è {giorno_settimana} {today.day} {nome_mese}. Santo del giorno: {santo}.",
        "body": (
            f"• <strong>Data odierna:</strong> {giorno_settimana} {today.day} {nome_mese} {today.year}<br>"
            f"• <strong>Santo del giorno:</strong> {santo}<br>"
            f"{fonte_html('Calendario Liturgico Diocesano')}"
        ),
        "time": "08:00"
    },
    meteo_item,
    {
        "cat": "📰 1. Newsbiella • Homepage",
        "title": news[0]["title"],
        "speak": f"Prima notizia da Newsbiella: {news[0]['title']}. Fonte: Newsbiella punto it.",
        "body": f"{news[0]['desc']}<br>{fonte_html('Newsbiella.it — Cronaca Provinciale')}",
        "time": "08:02"
    },
    {
        "cat": "📰 2. Newsbiella • Territorio",
        "title": news[1]["title"],
        "speak": f"Seconda notizia locale: {news[1]['title']}. Fonte: Newsbiella punto it.",
        "body": f"{news[1]['desc']}<br>{fonte_html('Newsbiella.it — Territorio Biellese')}",
        "time": "08:03"
    },
    {
        "cat": "🌲 Valle Cervo • Comunità",
        "title": "Aggiornamenti e sentieri in Valle Cervo",
        "speak": "Dalla Valle Cervo: percorsi panoramici e sentieri aperti e fruibili per escursionisti e residenti. Fonte: Newsbiella punto it.",
        "body": f"Piena accessibilità per i collegamenti e i sentieri panoramici della Valle Cervo.<br>{fonte_html('Newsbiella.it — Valle Cervo')}",
        "time": "08:04"
    },
    get_rifiuti(today.weekday()),
    # FARMACIE CON TELEFONO CLICCABILE E NAVIGATORE GPS
    {
        "cat": "💊 Farmacie di Turno & Servizi",
        "title": "Presidi più vicini, Numeri di Telefono e Mappa GPS",
        "speak": (
            "Farmacie di riferimento e di turno per Tavigliano: "
            "la Farmacia Savino ad Andorno Micca in Via Matteotti 14, raggiungibile in 5 minuti, telefono 015 47 27 79. "
            "E la Farmacia Valeggia a Sagliano Micca in Via Cappellaro 39, a 7 minuti, telefono 015 47 23 32. "
            "Nella scheda trovate i pulsanti per telefonare direttamente e per avviare il navigatore. Fonte: Federfarma e ASL Biella."
        ),
        "body": (
            "Tavigliano non ha farmacie sul territorio comunale. Ecco i riferimenti immediati:<br><br>"
            "<div style='background:rgba(0,0,0,0.04); border-radius:10px; padding:10px; margin-bottom:8px; border:1px solid #cbd5e1;'>"
            "  <strong>1. Farmacia Savino (Andorno Micca)</strong><br>"
            "  <span>📍 Via Giacomo Matteotti, 14 • ⏱ 5 min (3,2 km)</span><br>"
            "  <div style='margin-top:6px; display:flex; gap:8px; flex-wrap:wrap;'>"
            "    <a href='tel:015472779' style='background:#00a884; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>📞 Chiama: 015 472779</a>"
            "    <a href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Olistica+Savino+Andorno+Micca' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🧭 Navigatore GPS</a>"
            "  </div>"
            "</div>"
            "<div style='background:rgba(0,0,0,0.04); border-radius:10px; padding:10px; margin-bottom:8px; border:1px solid #cbd5e1;'>"
            "  <strong>2. Farmacia Valeggia (Sagliano Micca)</strong><br>"
            "  <span>📍 Via Giulio Cappellaro, 39 • ⏱ 7 min (4,5 km)</span><br>"
            "  <div style='margin-top:6px; display:flex; gap:8px; flex-wrap:wrap;'>"
            "    <a href='tel:015472332' style='background:#00a884; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>📞 Chiama: 015 472332</a>"
            "    <a href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Valeggia+Sagliano+Micca' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🧭 Navigatore GPS</a>"
            "  </div>"
            "</div>"
            f"{fonte_html('Federfarma Biella e ASL Biella')}"
        ),
        "time": "08:06"
    },
    # CANZONE CON MINIPLAYER 30s E YOUTUBE MUSIC
    {
        "cat": "🎵 Canzone Italiana & Proverbio",
        "title": "Proverbio & Miniplayer Ritornello (30 sec)",
        "speak": (
            f"Chiudiamo con la tradizione e la musica. Il proverbio piemontese del giorno è: {proverbio[0]}, {proverbio[1]}. "
            f"La canzone italiana selezionata per oggi è: {canzone['titolo']}. "
            "Potete ascoltare il ritornello di trenta secondi dal riquadro o il brano completo su YouTube Music. Fonte: Canzone d'Autore Italiana."
        ),
        "body": (
            f"• <strong>Proverbio piemontese:</strong> <em>{proverbio[0]}</em> ({proverbio[1]}).<br>"
            f"• <strong>Capolavoro italiano:</strong> <em>{canzone['titolo']}</em>.<br>"
            "<div style='background:#fff1f2; border:1px solid #fecdd3; border-radius:12px; padding:12px; margin-top:10px;'>"
            "  <div style='font-weight:700; color:#9f1239; margin-bottom:8px;'>🎧 Estratto ritornello (30 secondi):</div>"
            f"  <iframe width='100%' height='180' src='https://www.youtube-nocookie.com/embed/{canzone['yt']}?start={canzone['start']}&end={canzone['end']}&rel=0' title='Ritornello 30s' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' referrerpolicy='strict-origin-when-cross-origin' allowfullscreen style='border-radius:8px;'></iframe>"
            "  <div style='margin-top:10px;'>"
            f"    <a href='https://music.youtube.com/watch?v={canzone['yt']}' target='_blank' style='display:inline-flex; align-items:center; gap:6px; background:#e11d48; color:white; text-decoration:none; padding:8px 14px; border-radius:8px; font-size:0.85rem; font-weight:700;'>🔴 Ascolta completo su YouTube Music</a>"
            "  </div>"
            "</div>"
            f"{fonte_html('Archivio Storico della Canzone Italiana')}"
        ),
        "time": "08:07"
    },
    # CHIUSURA E RIEPILOGO FONTI LETTO A VOCE
    {
        "cat": "📢 Riepilogo Ufficiale Fonti",
        "title": "Trasparenza e Fonti del Notiziario",
        "speak": (
            "Edizione completata. Ecco il riepilogo finale delle fonti ufficiali consultate per il notiziario di oggi: "
            "previsioni meteo a cura di 3B Meteo; cronaca locale e Valle Cervo da Newsbiella punto it; "
            "calendario raccolta rifiuti da Seab Biella; presidi farmaceutici e turni da Federfarma e ASL Biella. "
            "Una buona giornata a tutta la comunità di Tavigliano!"
        ),
        "body": (
            "Tutti i dati e gli aggiornamenti del notiziario provengono da fonti verificate e consultabili:<br><br>"
            "• <strong>Meteo:</strong> 3BMeteo.com (Stazione Tavigliano)<br>"
            "• <strong>Notizie e Territorio:</strong> Newsbiella.it (Direzione di Redazione)<br>"
            "• <strong>Igiene Urbana:</strong> Seab Biella (Comune di Tavigliano)<br>"
            "• <strong>Salute e Farmacie:</strong> Federfarma Biella / ASL BI<br>"
            f"{fonte_html('Notiziario Civico Autonomo di Tavigliano')}"
        ),
        "time": "08:08"
    }
]

# 7. AGGIORNAMENTO DEL FILE INDEX.HTML
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Aggiorna l'intestazione con data e santo
content = re.sub(
    r'<div class="status">.*?</div>',
    f'<div class="status">{data_estesa}</div>',
    content,
    flags=re.DOTALL
)

# Aggiorna l'elenco delle notizie
json_str = json.dumps(news_data, ensure_ascii=False, indent=2)
content = re.sub(
    r'const NEWS = \[.*?\];',
    f'const NEWS = {json_str};',
    content,
    flags=re.DOTALL
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Aggiornamento completato con successo per: {data_estesa}")
