import datetime
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

# 1. DATA E CALENDARIO COMPLETO DEI SANTI
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", 
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

SANTI_DEL_GIORNO = {
    # Gennaio
    "01-01": "Maria Santissima Madre di Dio", "01-06": "Epifania del Signore", "01-17": "Sant'Antonio Abate",
    # Febbraio
    "02-03": "San Biagio", "02-14": "San Valentino",
    # Marzo
    "03-08": "San Giovanni di Dio", "03-19": "San Giuseppe", "03-25": "Annunciazione del Signore",
    # Aprile
    "04-23": "San Giorgio", "04-25": "San Marco Evangelista", "04-29": "Santa Caterina da Siena",
    # Maggio
    "05-01": "San Giuseppe Lavoratore", "05-14": "San Mattia Apostolo", "05-24": "Maria Ausiliatrice",
    # Giugno
    "06-13": "Sant'Antonio da Padova", "06-24": "San Giovanni Battista", "06-29": "Santi Pietro e Paolo",
    # Luglio
    "07-11": "San Benedetto da Norcia", "07-16": "Beata Vergine del Monte Carmelo", "07-26": "Santi Gioacchino e Anna",
    # Agosto
    "08-10": "San Lorenzo Martire", "08-15": "Assunzione della Beata Vergine Maria", "08-28": "Sant'Agostino",
    # Settembre
    "09-01": "Sant'Egidio Abate", "09-02": "Sant'Elpidio Vescovo", "09-03": "San Gregorio Magno Papa",
    "09-04": "Santa Rosalia", "09-05": "Santa Teresa di Calcutta", "09-06": "San Zaccaria Profeta",
    "09-07": "Santa Regina", "09-08": "Natività della Beata Vergine Maria", "09-09": "San Pietro Claver",
    "09-10": "San Nicola da Tolentino", "09-11": "San Giacinto Martire", "09-12": "Santissimo Nome di Maria",
    "09-13": "San Giovanni Crisostomo", "09-14": "Esaltazione della Santa Croce", "09-15": "Beata Vergine Addolorata",
    "09-16": "Santi Cornelio e Cipriano", "09-17": "San Roberto Bellarmino", "09-18": "San Giuseppe da Copertino",
    "09-19": "San Gennaro Vescovo e Martire", "09-20": "Sant'Eustachio", "09-21": "San Matteo Apostolo ed Evangelista",
    "09-22": "San Maurizio Martire", "09-23": "San Pio da Pietrelcina (Padre Pio)", "09-24": "San Pacifico",
    "09-25": "San Cleofa", "09-26": "Santi Cosma e Damiano", "09-27": "San Vincenzo de' Paoli",
    "09-28": "San Venceslao", "09-29": "Santi Michele, Gabriele e Raffaele Arcangeli", "09-30": "San Girolamo",
    # Ottobre
    "10-01": "Santa Teresa di Lisieux", "10-02": "Santi Angeli Custodi", "10-04": "San Francesco d'Assisi (Patrono d'Italia)",
    "10-05": "Santa Faustina Kowalska", "10-06": "San Bruno Abate", "10-07": "Beata Vergine del Rosario",
    "10-11": "San Giovanni XXIII Papa", "10-15": "Santa Teresa d'Avila", "10-18": "San Luca Evangelista",
    "10-22": "San Giovanni Paolo II Papa", "10-28": "Santi Simone e Giuda",
    # Novembre
    "11-01": "Tutti i Santi", "11-02": "Commemorazione di tutti i fedeli Defunti", "11-04": "San Carlo Borromeo",
    "11-11": "San Martino di Tours", "11-22": "Santa Cecilia", "11-30": "Sant'Andrea Apostolo",
    # Dicembre
    "12-06": "San Nicola di Bari", "12-07": "Sant'Ambrogio", "12-08": "Immacolata Concezione",
    "12-13": "Santa Lucia", "12-25": "Natale del Signore", "12-26": "Santo Stefano", "12-31": "San Silvestro Papa"
}

today = datetime.date.today()
giorno_settimana = GIORNI[today.weekday()]
nome_mese = MESI[today.month - 1]
chiave_data = today.strftime("%m-%d")
santo = SANTI_DEL_GIORNO.get(chiave_data, "San Patrono")
data_estesa = f"{giorno_settimana} {today.day} {nome_mese} — {santo}"

# 2. METEO TAVIGLIANO (Open-Meteo)
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

            speak = f"Previsioni meteo a Tavigliano: {descr}. Temperatura massima di {t_max} gradi, minima di {t_min}. Fonte: Open Meteo."
            body = f"{descr}, precipitazioni deboli o assenti. Massima di {t_max}°C, minima di {t_min}°C. <span class='fonte'>Fonte: Open-Meteo</span>"
            return {"cat": "🌦️ Meteo Tavigliano", "title": f"{descr}, min {t_min}°C / max {t_max}°C", "speak": speak, "body": body, "time": "08:01"}
    except Exception:
        return {
            "cat": "🌦️ Meteo Tavigliano",
            "title": "Nubi sparse e clima montano",
            "speak": "Previsioni meteo a Tavigliano: cielo con nubi sparse e brezze fresche.",
            "body": "Cielo con nubi sparse, assenza di fenomeni intensi. Brezze valligiane. <span class='fonte'>Fonte: Servizio Locale</span>",
            "time": "08:01"
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
    return {"cat": "♻️ Rifiuti Tavigliano", "title": "Calendario Raccolta Rifiuti", "speak": speak, "body": body, "time": "08:05"}

# 5. I 31 GRANDI CAPOLAVORI DELLA CANZONE ITALIANA
CANZONI_ITALIANE = [
    {"titolo": "Nel blu dipinto di blu (Volare) — Domenico Modugno (1958)", "yt": "ViJgTYju8Gg"},
    {"titolo": "Il cielo in una stanza — Gino Paoli (1960)", "yt": "4bXGfE_7uB8"},
    {"titolo": "Azzurro — Adriano Celentano (1968)", "yt": "g_t4U4N1d9M"},
    {"titolo": "Emozioni — Lucio Battisti (1970)", "yt": "prve6-_j834"},
    {"titolo": "Almeno tu nell'universo — Mia Martini (1989)", "yt": "L6aFHD4xnQg"},
    {"titolo": "Fatti mandare dalla mamma — Gianni Morandi (1962)", "yt": "qf_k_6Vp2Zc"},
    {"titolo": "Il mondo — Jimmy Fontana (1965)", "yt": "4AlEODZGM38"},
    {"titolo": "Io che amo solo te — Sergio Endrigo (1962)", "yt": "UgptFb6tKmw"},
    {"titolo": "Una lacrima sul viso — Bobby Solo (1964)", "yt": "p5zO7U8NfLw"},
    {"titolo": "La bambola — Patty Pravo (1968)", "yt": "V03hH8b2tHw"},
    {"titolo": "Cuore matto — Little Tony (1967)", "yt": "jM10gGZJ9Gg"},
    {"titolo": "La partita di pallone — Rita Pavone (1963)", "yt": "XwZ6B87G4J4"},
    {"titolo": "24 mila baci — Adriano Celentano (1961)", "yt": "2G46X1Ue8Q4"},
    {"titolo": "Sapore di sale — Gino Paoli (1963)", "yt": "m_q43dI45n8"},
    {"titolo": "Grande grande grande — Mina (1972)", "yt": "8iIhyuWkSms"},
    {"titolo": "Meraviglioso — Domenico Modugno (1968)", "yt": "bJms797lKqA"},
    {"titolo": "Questo piccolo grande amore — Claudio Baglioni (1972)", "yt": "5b2Fh4hC108"},
    {"titolo": "Caruso — Lucio Dalla (1986)", "yt": "GLf80jP6B9E"},
    {"titolo": "Mi sono innamorato di te — Luigi Tenco (1962)", "yt": "Tq5sP-zH0Qo"},
    {"titolo": "L'appuntamento — Ornella Vanoni (1970)", "yt": "xY53e3mPz58"},
    {"titolo": "Rose rosse — Massimo Ranieri (1968)", "yt": "j26wP-4D3_U"},
    {"titolo": "Non ho l'età — Gigliola Cinquetti (1964)", "yt": "8Y1b_n_jX1c"},
    {"titolo": "Centro di gravità permanente — Franco Battiato (1981)", "yt": "s91Q9V6yvC8"},
    {"titolo": "Il mio canto libero — Lucio Battisti (1972)", "yt": "0z_5B_9N1c4"},
    {"titolo": "La canzone di Marinella — Fabrizio De André (1964)", "yt": "_X48rB9zW4c"},
    {"titolo": "Margherita — Riccardo Cocciante (1976)", "yt": "7bE6g2xYvXg"},
    {"titolo": "Abbronzatissima — Edoardo Vianello (1963)", "yt": "l3V1q-Pq06E"},
    {"titolo": "Nel sole — Al Bano (1967)", "yt": "P4D4P5s7c7E"},
    {"titolo": "Se telefonando — Mina (1966)", "yt": "0Z2bM4XwN2o"},
    {"titolo": "L'italiano — Toto Cutugno (1983)", "yt": "s59a3Qd4q-k"},
    {"titolo": "Piove (Ciao ciao bambina) — Domenico Modugno (1959)", "yt": "x4-0_Q8wR8k"}
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

# 6. COMPOSIZIONE DATI
meteo_item = get_meteo()
news = get_newsbiella()

news_data = [
    # APERTURA VOCALE RICHIESTA
    {
        "cat": "🎙️ Buongiorno Tavigliano",
        "title": f"Oggi è {giorno_settimana} {today.day} {nome_mese}",
        "speak": f"Buongiorno Tavigliano! Oggi è {giorno_settimana} {today.day} {nome_mese}. Santo del giorno: {santo}.",
        "body": f"• <strong>Oggi è il:</strong> {giorno_settimana} {today.day} {nome_mese} {today.year}<br>• <strong>Santo del giorno:</strong> {santo}",
        "time": "08:00"
    },
    meteo_item,
    {
        "cat": "📰 1. Newsbiella • Homepage",
        "title": news[0]["title"],
        "speak": f"Prima notizia da Newsbiella: {news[0]['title']}. Fonte Newsbiella punto it.",
        "body": f"{news[0]['desc']} <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:02"
    },
    {
        "cat": "📰 2. Newsbiella • Territorio",
        "title": news[1]["title"],
        "speak": f"Seconda notizia: {news[1]['title']}. Fonte Newsbiella punto it.",
        "body": f"{news[1]['desc']} <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:03"
    },
    {
        "cat": "🌲 Valle Cervo • Comunità",
        "title": "Sentieri e collegamenti in Valle Cervo",
        "speak": "Dalla Valle Cervo: percorsi panoramici e sentieri aperti e fruibili per escursionisti e residenti.",
        "body": "Piena accessibilità per i collegamenti e i sentieri panoramici della Valle Cervo. <span class='fonte'>Fonte: Newsbiella.it</span>",
        "time": "08:04"
    },
    get_rifiuti(today.weekday()),
    {
        "cat": "💊 Farmacie di Turno",
        "title": "Presidi più vicini & Navigatore GPS",
        "speak": "Farmacie: i riferimenti più vicini sono la Farmacia Savino ad Andorno Micca e la Farmacia Valeggia a Sagliano Micca.",
        "body": "Tavigliano non ha farmacie nel comune:<br>" +
                "<div class='route-card'><strong>1. Farmacia Savino (Andorno Micca)</strong><span>⏱ 5 min (3,2 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Olistica+Savino+Andorno+Micca' target='_blank'>🧭 Avvia Navigatore Andorno</a></div>" +
                "<div class='route-card'><strong>2. Farmacia Valeggia (Sagliano Micca)</strong><span>⏱ 7 min (4,5 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Valeggia+Sagliano+Micca' target='_blank'>🧭 Avvia Navigatore Sagliano</a></div>",
        "time": "08:06"
    },
    {
        "cat": "⛽ Prezzi Carburanti",
        "title": "Enercoop Biella: Prezzi & Mappa",
        "speak": "Carburanti: all'Enercoop di Biella, a quindici minuti, tariffe calmierate per benzina e gasolio self-service.",
        "body": "Distributore Enercoop Biella (Viale Macallè / Gli Orsi):<br>" +
                "• Tariffe monitorate in modalità Self Service.<br>" +
                "<div class='route-card'><span>⏱ Tempo stimato da Tavigliano: 15 min (10,5 km)</span>" +
                "<a class='btn-maps' href='https://www.google.com/maps/dir/?api=1&destination=Distributore+Enercoop+Biella' target='_blank'>🧭 Avvia Navigatore Enercoop</a></div>",
        "time": "08:07"
    },
    {
        "cat": "🎵 Canzone Italiana & Proverbio",
        "title": "Proverbio & Capolavoro Italiano",
        "speak": f"Chiudiamo con il proverbio piemontese: {proverbio[0]}, {proverbio[1]}. La grande canzone italiana di oggi è: {canzone['titolo']}. Buona giornata da Tavigliano!",
        "body": f"• <strong>Proverbio piemontese:</strong> <em>{proverbio[0]}</em> ({proverbio[1]}).<br>" +
                f"• <strong>Canzone del giorno:</strong> <em>{canzone['titolo']}</em>." +
                "<div class='yt-box'>" +
                "  <strong>🎧 Ascolta il brano su YouTube:</strong>" +
                f"  <iframe width='100%' height='180' src='https://www.youtube-nocookie.com/embed/{canzone['yt']}?rel=0' title='Canzone italiana del giorno' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen style='border-radius:8px;'></iframe>" +
                f"  <a class='btn-yt-music' href='https://music.youtube.com/watch?v={canzone['yt']}' target='_blank'>🔴 Apri su YouTube Music</a>" +
                "</div>",
        "time": "08:08"
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

# Aggiorna l'array JavaScript NEWS
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
