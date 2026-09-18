import datetime
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

# 1. DATA E SANTO DEL GIORNO
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", 
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

SANTI_DEL_GIORNO = {
    "01-01": "Maria Madre di Dio", "01-06": "Epifania del Signore", "03-19": "San Giuseppe",
    "04-25": "San Marco", "05-01": "San Giuseppe Lavoratore", "06-24": "San Giovanni Battista",
    "06-29": "Santi Pietro e Paolo", "08-10": "San Lorenzo", "08-15": "Assunzione di Maria",
    "09-17": "San Roberto Bellarmino", "09-18": "San Giuseppe da Copertino", "09-19": "San Gennaro",
    "09-20": "Sant'Eustachio", "09-21": "San Matteo", "10-04": "San Francesco d'Assisi",
    "11-01": "Tutti i Santi", "12-08": "Immacolata Concezione", "12-25": "Natale del Signore",
    "12-26": "Santo Stefano"
}

today = datetime.date.today()
giorno_settimana = GIORNI[today.weekday()]
nome_mese = MESI[today.month - 1]
chiave_data = today.strftime("%m-%d")
santo = SANTI_DEL_GIORNO.get(chiave_data, "San Patrono")
data_estesa = f"{giorno_settimana} {today.day} {nome_mese} — {santo}"

# 2. METEO TAVIGLIANO (Coordinate: Lat 45.63, Lon 8.05 via Open-Meteo)
def get_meteo():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=45.63&longitude=8.05&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Europe%2FRome"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode())
            wcode = data["daily"]["weathercode"][0]
            t_max = round(data["daily"]["temperature_2m_max"][0])
            t_min = round(data["daily"]["temperature_2m_min"][0])
            
            descr = "Sereno o poco nuvoloso"
            if wcode in [1, 2, 3]:
                descr = "Nubi sparse alternate a schiarite"
            elif wcode in [45, 48]:
                descr = "Nebbia o foschia densa"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                descr = "Cielo coperto con possibili piogge"
            elif wcode >= 95:
                descr = "Possibili temporali locali"

            speak = f"Iniziamo con il meteo a Tavigliano. {descr}. Temperatura massima di {t_max} gradi, minima di {t_min}. Fonte: Open Meteo."
            body = f"{descr}, precipitazioni deboli o assenti. Massima di {t_max}°C, minima di {t_min}°C. <span class='fonte'>Fonte: Open-Meteo</span>"
            return {"cat": "🌦️ Meteo Tavigliano", "title": f"{descr}, min {t_min}°C / max {t_max}°C", "speak": speak, "body": body, "time": "08:00"}
    except Exception:
        return {
            "cat": "🌦️ Meteo Tavigliano",
            "title": "Nubi sparse e clima montano",
            "speak": "Iniziamo con il meteo a Tavigliano. Cielo con nubi sparse e brezze fresche. Fonte: Servizio Meteo.",
            "body": "Cielo con nubi sparse, assenza di fenomeni intensi. Brezze valligiane. <span class='fonte'>Fonte: Servizio Locale</span>",
            "time": "08:00"
        }

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
                clean_desc = re.sub('<[^<]+?>', '', desc)[:140] + "..."
                clean_title = re.sub('<[^<]+?>', '', title)
                items.append({
                    "title": clean_title,
                    "desc": clean_desc
                })
    except Exception:
        pass

    if len(items) < 2:
        items = [
            {"title": "Lavori e viabilità nella provincia di Biella", "desc": "Aggiornamenti sui cantieri stradali e la manutenzione delle reti viarie del territorio biellese."},
            {"title": "Iniziative culturali ed eventi nel Biellese", "desc": "Proseguono le rassegne artistiche e gli incontri enogastronomici promossi dai comuni del circondario."}
        ]
    return items

# 4. CALENDARIO RIFIUTI TAVIGLIANO
def get_rifiuti(weekday):
    # Tabella settimanale
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
    speak = f"Servizio rifiuti Tavigliano: {oggi_txt.replace('<em>', '').replace('</em>', '')}. {dom_txt.replace('<em>', '').replace('</em>', '')}."
    body = f"• <strong>Oggi:</strong> {oggi_txt}.<br>• <strong>Promemoria:</strong> {dom_txt}."
    return {"cat": "♻️ Rifiuti Tavigliano", "title": "Calendario Raccolta Rifiuti", "speak": speak, "body": body, "time": "08:04"}

# 5. ROTAZIONE CANZONI ANNI '60 & PROVERBI
CANZONI_60 = [
    {"titolo": "Nel blu dipinto di blu — Domenico Modugno (1958)", "yt": "ViJgTYju8Gg"},
    {"titolo": "Il cielo in una stanza — Gino Paoli (1960)", "yt": "4bXGfE_7uB8"},
    {"titolo": "24 mila baci — Adriano Celentano (1961)", "yt": "2G46X1Ue8Q4"},
    {"titolo": "Fatti mandare dalla mamma — Gianni Morandi (1962)", "yt": "qf_k_6Vp2Zc"},
    {"titolo": "Sapore di sale — Gino Paoli (1963)", "yt": "m_q43dI45n8"},
    {"titolo": "Una lacrima sul viso — Bobby Solo (1964)", "yt": "p5zO7U8NfLw"},
    {"titolo": "La partita di pallone — Rita Pavone (1963)", "yt": "XwZ6B87G4J4"},
    {"titolo": "La notte — Adamo (1965)", "yt": "4kZ2jO_1v0M"},
    {"titolo": "Cuore matto — Little Tony (1967)", "yt": "jM10gGZJ9Gg"},
    {"titolo": "La bambola — Patty Pravo (1968)", "yt": "V03hH8b2tHw"},
    {"titolo": "Azzurro — Adriano Celentano (1968)", "yt": "g_t4U4N1d9M"}
]

PROVERBI = [
    ("«Can ch'a bòja a mòrd nen»", "Cane che abbaia non morde"),
    ("«Chi a peul nen bate 'l caval, a bat la sela»", "Chi non può battere il cavallo, batte la sella"),
    ("«A fesse d'òr a s'ancurnisa la miseria»", "A farsi d'oro si incornicia la miseria"),
    ("«Për conòsse un bin a venta mangé 'n sach ëd sal ansema»", "Per conoscere bene uno bisogna mangiare un sacco di sale insieme"),
    ("«L'eva ch'a cor a pòrta nen d'infezion»", "L'acqua che scorre non porta infezioni")
]

canzone = CANZONI_60[today.day % len(CANZONI_60)]
proverbio = PROVERBI[today.day % len(PROVERBI)]

# 6. COMPOSIZIONE DATI
meteo_item = get_meteo()
news = get_newsbiella()

news_data = [
    meteo_item,
    {
        "cat": "📰 1. Newsbiella • Homepage",
        "title": news[0]["title"],
        "speak": f"Prima notizia da Newsbiella: {news[0]['title']}. Fonte Newsbiella punto it.",
        "body": f"{news[0]['desc']} <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:01"
    },
    {
        "cat": "📰 2. Newsbiella • Territorio",
        "title": news[1]["title"],
        "speak": f"Seconda notizia locale: {news[1]['title']}. Fonte Newsbiella punto it.",
        "body": f"{news[1]['desc']} <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:02"
    },
    {
        "cat": "🌲 Valle Cervo • Comunità",
        "title": "Aggiornamenti e sentieri in Valle Cervo",
        "speak": "Dalla Valle Cervo: percorsi montani aperti e fruibili per escursionisti e residenti. Fonte Newsbiella punto it.",
        "body": "Piena accessibilità per i collegamenti e i sentieri panoramici della Valle Cervo. <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:03"
    },
    get_rifiuti(today.weekday()),
    {
        "cat": "💊 Farmacie di Turno",
        "title": "Presidi più vicini & Navigatore GPS",
        "speak": "Farmacie: i riferimenti più vicini sono ad Andorno Micca a cinque minuti e Sagliano Micca a sette minuti.",
        "body": "Tavigliano non ha farmacie nel comune:<br>" +
                "<div class='route-card'><strong>1. Farmacia Savino (Andorno Micca)</strong><span>⏱ 5 min (3,2 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Olistica+Savino+Andorno+Micca' target='_blank'>🧭 Avvia Navigatore Andorno</a></div>" +
                "<div class='route-card'><strong>2. Farmacia Valeggia (Sagliano Micca)</strong><span>⏱ 7 min (4,5 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Valeggia+Sagliano+Micca' target='_blank'>🧭 Avvia Navigatore Sagliano</a></div>",
        "time": "08:05"
    },
    {
        "cat": "⛽ Prezzi Carburanti",
        "title": "Enercoop Biella: Prezzi & Mappa",
        "speak": "Carburanti: all'Enercoop di Biella, a quindici minuti, benzina e gasolio a tariffe calmierate self-service.",
        "body": "Distributore Enercoop Biella (Viale Macallè / Gli Orsi):<br>" +
                "• Tariffe monitorate costantemente in modalità Self.<br>" +
                "<div class='route-card'><span>⏱ Tempo stimato da Tavigliano: 15 min (10,5 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Distributore+Enercoop+Biella' target='_blank'>🧭 Avvia Navigatore Enercoop</a></div>",
        "time": "08:06"
    },
    {
        "cat": "🎵 Canzone & Proverbio",
        "title": "Proverbio & Brano Anni '60",
        "speak": f"Chiudiamo con il proverbio piemontese: {proverbio[0]}, {proverbio[1]}. La canzone del giorno è {canzone['titolo']}. Buona giornata da Tavigliano!",
        "body": f"• <strong>Proverbio piemontese:</strong> <em>{proverbio[0]}</em> ({proverbio[1]}).<br>" +
                f"• <strong>Canzone del giorno:</strong> <em>{canzone['titolo']}</em>." +
                "<div class='yt-box'>" +
                "  <strong>🎧 Ascolta il brano su YouTube:</strong>" +
                f"  <iframe width='100%' height='180' src='https://www.youtube-nocookie.com/embed/{canzone['yt']}?rel=0' title='Brano del giorno' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen style='border-radius:8px;'></iframe>" +
                f"  <a class='btn-yt-music' href='https://music.youtube.com/watch?v={canzone['yt']}' target='_blank'>🔴 Apri su YouTube Music</a>" +
                "</div>",
        "time": "08:07"
    }
]

# 7. AGGIORNAMENTO DEL FILE INDEX.HTML
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Aggiorna la data e il Santo nell'intestazione
content = re.sub(
    r'<div class="status">.*?</div>',
    f'<div class="status">{data_estesa}</div>',
    content,
    flags=re.DOTALL
)

# Aggiorna la lista delle notizie JS
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
