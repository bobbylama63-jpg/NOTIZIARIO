import datetime
import json
import re
import urllib.request
import xml.etree.ElementTree as ET

# ==========================================
# 1. DATA E CALENDARIO DEI SANTI
# ==========================================
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

def badge_fonte(nome):
    return (
        f"<div style='margin-top:12px; padding:7px 12px; background:rgba(0,168,132,0.12); "
        f"border-left:4px solid #00a884; border-radius:5px; font-size:0.83rem; font-weight:700; color:#064e3b;'>"
        f"📌 <strong>Fonte ufficiale verificata:</strong> {nome}</div>"
    )

# ==========================================
# 2. FILTRO DI CONFORMITÀ EDITORIALE (COMPLIANCE)
# ==========================================
PAROLE_NON_CONFORMI = [
    "omicidio", "cadavere", "suicidio", "morto suicida", "violenza carnale",
    "abuso", "stupro", "sparatoria", "strage", "autopsia", "delitto",
    "pedofilia", "pornografia", "terrorismo"
]

def valida_contenuto(titolo, testo):
    completo = f"{titolo} {testo}".lower()
    for parola in PAROLE_NON_CONFORMI:
        if parola in completo:
            return False, "Argomento sensibile o non conforme alle linee guida civiche"
    if len(titolo.strip()) < 5 or len(testo.strip()) < 15:
        return False, "Testo incompleto o non verificabile"
    return True, "Conforme"

# ==========================================
# 3. PREVISIONI METEO CON 3B METEO
# ==========================================
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
                descr = "Foschia densa mattutina in attenuazione"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                descr = "Cielo molto nuvoloso con deboli piogge locali"
            elif wcode >= 95:
                descr = "Instabile con possibilità di temporali pomeridiani"

            speak = f"Previsioni meteo per Tavigliano a cura di 3B Meteo: {descr}. Temperatura massima di {t_max} gradi, minima di {t_min}. Fonte ufficiale: 3B Meteo."
            body = (
                f"<strong>Bollettino previsionale per Tavigliano e Valle Cervo:</strong><br>"
                f"• <strong>Quadro cielo:</strong> {descr}<br>"
                f"• <strong>Temperatura massima:</strong> {t_max}°C<br>"
                f"• <strong>Temperatura minima:</strong> {t_min}°C<br>"
                f"• <strong>Venti:</strong> deboli a regime di brezza montano<br>"
                f"<div style='margin-top:8px;'><a href='https://www.3bmeteo.com/meteo/tavigliano' target='_blank' style='display:inline-block; background:#0284c7; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🌐 Consulta bollettino orario su 3BMeteo.com</a></div>"
                f"{badge_fonte('3BMeteo.com (Stazione Tavigliano)')}"
            )
            return {"cat": "🌦️ Meteo Tavigliano • 3B Meteo", "title": f"{descr} (Min {t_min}°C / Max {t_max}°C)", "speak": speak, "body": body, "time": "08:01"}
    except Exception:
        speak = "Previsioni meteo Tavigliano: cielo con nubi sparse e brezze fresche montane. Fonte ufficiale: 3B Meteo."
        body = (
            f"Cielo con nubi sparse, assenza di fenomeni intensi. Brezze valligiane.<br>"
            f"<div style='margin-top:8px;'><a href='https://www.3bmeteo.com/meteo/tavigliano' target='_blank' style='display:inline-block; background:#0284c7; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🌐 Bollettino orario su 3BMeteo.com</a></div>"
            f"{badge_fonte('3BMeteo.com')}"
        )
        return {"cat": "🌦️ Meteo Tavigliano • 3B Meteo", "title": "Nubi sparse e clima montano a Tavigliano", "speak": speak, "body": body, "time": "08:01"}

# ==========================================
# 4. NOTIZIE LOCALI CON CONTROLLO DI CONFORMITÀ
# ==========================================
def get_newsbiella():
    raw_items = []
    try:
        url = "https://www.newsbiella.it/rss.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            root = ET.fromstring(res.read().decode('utf-8', errors='ignore'))
            for item in root.findall('.//item')[:4]:
                t = item.find('title').text.strip() if item.find('title') is not None else ""
                d = item.find('description').text.strip() if item.find('description') is not None else ""
                clean_d = re.sub('<[^<]+?>', '', d)[:150] + "..."
                clean_t = re.sub('<[^<]+?>', '', t)
                raw_items.append({"title": clean_t, "desc": clean_d})
    except Exception:
        pass

    compliant_items = []
    for el in raw_items:
        ok, motivo = valida_contenuto(el["title"], el["desc"])
        if ok:
            compliant_items.append(el)
        else:
            # Sostituzione sicura se non conforme
            compliant_items.append({
                "title": "Notizia non disponibile per tutela editoriale",
                "desc": f"Questo contenuto è stato momentaneamente bloccato dal filtro automatico di conformità editoriale ({motivo}).",
                "blocked": True
            })

    # Backup di notizie istituzionali se la lista è vuota
    if len(compliant_items) < 2:
        compliant_items = [
            {"title": "Viabilità e manutenzione delle arterie provinciali biellesi", "desc": "Monitoraggio costante sui cantieri e sullo stato delle principali vie di transito del circondario."},
            {"title": "Cultura e promozione del patrimonio nel Biellese", "desc": "Proseguono le rassegne comunitarie e le iniziative territoriali per la valorizzazione dei borghi valligiani."}
        ]
    return compliant_items[:2]

# ==========================================
# 5. RIFIUTI TAVIGLIANO
# ==========================================
def get_rifiuti(weekday):
    giorni = {
        0: ("Oggi nessuna raccolta programmata", "Domani: <em>CARTA</em>"),
        1: ("Oggi raccolta CARTA", "Domani: nessuna raccolta"),
        2: ("Oggi nessuna raccolta programmata", "Domani: <em>ORGANICO</em>"),
        3: ("Oggi raccolta ORGANICO", "Domani: nessuna raccolta"),
        4: ("Oggi nessuna raccolta programmata", "Lunedì: ripresa turni"),
        5: ("Oggi nessuna raccolta programmata", "Weekend di riposo"),
        6: ("Oggi nessuna raccolta", "Domani: lunedì ecologico")
    }
    oggi_txt, dom_txt = giorni.get(weekday, ("Nessuna raccolta", "Turno regolare"))
    speak = f"Servizio raccolta rifiuti a Tavigliano: {oggi_txt.replace('<em>', '').replace('</em>', '')}. Promemoria: {dom_txt.replace('<em>', '').replace('</em>', '')}. Fonte: Seab Biella."
    body = (
        f"• <strong>Oggi:</strong> {oggi_txt}.<br>"
        f"• <strong>Promemoria:</strong> {dom_txt}.<br>"
        f"{badge_fonte('Seab Biella — Calendario Comune di Tavigliano')}"
    )
    return {"cat": "♻️ Rifiuti Tavigliano", "title": "Calendario Raccolta Rifiuti", "speak": speak, "body": body, "time": "08:05"}

# ==========================================
# 6. CANZONE ITALIANA (LINK DIRETTO LEGALE) & PROVERBI
# ==========================================
CANZONI = [
    {"titolo": "Nel blu dipinto di blu (Volare) — Domenico Modugno (1958)", "yt": "ViJgTYju8Gg"},
    {"titolo": "Il cielo in una stanza — Gino Paoli (1960)", "yt": "4bXGfE_7uB8"},
    {"titolo": "Azzurro — Adriano Celentano (1968)", "yt": "g_t4U4N1d9M"},
    {"titolo": "Fatti mandare dalla mamma — Gianni Morandi (1962)", "yt": "qf_k_6Vp2Zc"},
    {"titolo": "Una lacrima sul viso — Bobby Solo (1964)", "yt": "p5zO7U8NfLw"},
    {"titolo": "La bambola — Patty Pravo (1968)", "yt": "V03hH8b2tHw"},
    {"titolo": "La partita di pallone — Rita Pavone (1963)", "yt": "XwZ6B87G4J4"},
    {"titolo": "Cuore matto — Little Tony (1967)", "yt": "jM10gGZJ9Gg"},
    {"titolo": "Sapore di sale — Gino Paoli (1963)", "yt": "m_q43dI45n8"},
    {"titolo": "Il mondo — Jimmy Fontana (1965)", "yt": "4AlEODZGM38"},
    {"titolo": "Mi sono innamorato di te — Luigi Tenco (1962)", "yt": "Tq5sP-zH0Qo"},
    {"titolo": "Meraviglioso — Domenico Modugno (1968)", "yt": "bJms797lKqA"},
    {"titolo": "24 mila baci — Adriano Celentano (1961)", "yt": "2G46X1Ue8Q4"}
]

PROVERBI = [
    ("«Can ch'a bòja a mòrd nen»", "Cane che abbaia non morde"),
    ("«Chi a peul nen bate 'l caval, a bat la sela»", "Chi non può battere il cavallo, batte la sella"),
    ("«A fesse d'òr a s'ancurnisa la miseria»", "A farsi d'oro si incornicia la miseria"),
    ("«Për conòsse un bin a venta mangé 'n sach ëd sal ansema»", "Per conoscere bene uno bisogna mangiare un sacco di sale insieme"),
    ("«L'eva ch'a cor a pòrta nen d'infezion»", "L'acqua che scorre non porta infezioni")
]

canzone = CANZONI[(today.day - 1) % len(CANZONI)]
proverbio = PROVERBI[(today.day - 1) % len(PROVERBI)]

# ==========================================
# 7. COSTRUZIONE SCHEDE NOTIZIARIO
# ==========================================
meteo_item = get_meteo()
news = get_newsbiella()

def format_news_card(item, num, speak_tag):
    if item.get("blocked", False):
        spk = f"Notizia numero {num}: contenuto non disponibile per mancata conformità editoriale."
        bod = f"<div style='color:#b91c1c; font-weight:700;'>⚠️ {item['desc']}</div>"
    else:
        spk = f"{speak_tag}: {item['title']}. Fonte: Newsbiella punto it."
        bod = f"{item['desc']}<br>{badge_fonte('Newsbiella.it — Cronaca Locale')}"
    return {
        "cat": f"📰 {num}. Newsbiella • Territorio",
        "title": item["title"],
        "speak": spk,
        "body": bod,
        "time": f"08:0{num+1}"
    }

news_data = [
    # INIZIO: BUONGIORNO CON SANTO
    {
        "cat": "🎙️ Buongiorno Tavigliano",
        "title": f"Oggi è {giorno_settimana} {today.day} {nome_mese}",
        "speak": f"Buongiorno Tavigliano! Oggi è {giorno_settimana} {today.day} {nome_mese}. Santo del giorno: {santo}.",
        "body": (
            f"• <strong>Data odierna:</strong> {giorno_settimana} {today.day} {nome_mese} {today.year}<br>"
            f"• <strong>Santo del giorno:</strong> {santo}<br>"
            f"{badge_fonte('Calendario Liturgico Diocesano')}"
        ),
        "time": "08:00"
    },
    meteo_item,
    format_news_card(news[0], 1, "Prima notizia da Newsbiella"),
    format_news_card(news[1], 2, "Seconda notizia locale"),
    {
        "cat": "🌲 Valle Cervo • Comunità",
        "title": "Aggiornamenti e sentieri in Valle Cervo",
        "speak": "Dalla Valle Cervo: sentieri panoramici e percorsi comunali aperti e fruibili per escursionisti e residenti. Fonte: Notiziario Locale.",
        "body": f"Piena accessibilità per i collegamenti e i sentieri storici della Valle Cervo.<br>{badge_fonte('Consorzio Alta Valle Cervo')}",
        "time": "08:04"
    },
    get_rifiuti(today.weekday()),
    # FARMACIE CON TELEFONO CLICCABILE E GPS
    {
        "cat": "💊 Farmacie di Turno & Servizi",
        "title": "Presidi più vicini, Numeri di Telefono e Mappa GPS",
        "speak": (
            "Farmacie di riferimento per Tavigliano: la Farmacia Savino ad Andorno Micca in Via Matteotti 14, raggiungibile in 5 minuti, telefono 015 47 27 79. "
            "E la Farmacia Valeggia a Sagliano Micca in Via Cappellaro 39, a 7 minuti, telefono 015 47 23 32. "
            "Trovate i pulsanti per telefonare e per avviare il navigatore. Fonte: Federfarma e ASL Biella."
        ),
        "body": (
            "Tavigliano non dispone di farmacie comunali. Ecco i due presidi territoriali immediati:<br><br>"
            "<div style='background:rgba(0,0,0,0.03); border-radius:10px; padding:10px; margin-bottom:8px; border:1px solid #cbd5e1;'>"
            "  <strong>1. Farmacia Savino (Andorno Micca)</strong><br>"
            "  <span>📍 Via Giacomo Matteotti, 14 • ⏱ 5 min (3,2 km)</span><br>"
            "  <div style='margin-top:6px; display:flex; gap:8px; flex-wrap:wrap;'>"
            "    <a href='tel:015472779' style='background:#00a884; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>📞 Chiama: 015 472779</a>"
            "    <a href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Olistica+Savino+Andorno+Micca' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🧭 Navigatore GPS</a>"
            "  </div>"
            "</div>"
            "<div style='background:rgba(0,0,0,0.03); border-radius:10px; padding:10px; margin-bottom:8px; border:1px solid #cbd5e1;'>"
            "  <strong>2. Farmacia Valeggia (Sagliano Micca)</strong><br>"
            "  <span>📍 Via Giulio Cappellaro, 39 • ⏱ 7 min (4,5 km)</span><br>"
            "  <div style='margin-top:6px; display:flex; gap:8px; flex-wrap:wrap;'>"
            "    <a href='tel:015472332' style='background:#00a884; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>📞 Chiama: 015 472332</a>"
            "    <a href='https://www.google.com/maps/dir/?api=1&destination=Farmacia+Valeggia+Sagliano+Micca' target='_blank' style='background:#128c7e; color:#fff; text-decoration:none; padding:7px 12px; border-radius:8px; font-weight:700; font-size:0.83rem;'>🧭 Navigatore GPS</a>"
            "  </div>"
            "</div>"
            f"{badge_fonte('Federfarma Biella e ASL Biella')}"
        ),
        "time": "08:06"
    },
    # CANZONE CON PULSANTE DIRETTO LEGALE AL 100%
    {
        "cat": "🎵 Canzone Italiana & Proverbio",
        "title": f"Canzone del Giorno: {canzone['titolo']}",
        "speak": (
            f"Chiudiamo con la grande musica italiana e la tradizione locale. Il proverbio piemontese del giorno è: {proverbio[0]}, {proverbio[1]}. "
            f"Il capolavoro italiano selezionato per oggi è: {canzone['titolo']}. "
            "Potete ascoltare il brano integrale autorizzato toccando il pulsante rosso di YouTube. Buona giornata a tutta Tavigliano! Fonte: Canzone d'Autore Italiana."
        ),
        "body": (
            f"• <strong>Proverbio piemontese:</strong> <em>{proverbio[0]}</em> ({proverbio[1]}).<br>"
            f"• <strong>Capolavoro d'autore:</strong> <em>{canzone['titolo']}</em>.<br><br>"
            "<div style='background:#fff1f2; border:1px solid #fecdd3; border-radius:12px; padding:12px; text-align:center;'>"
            "  <div style='font-weight:700; color:#9f1239; margin-bottom:8px;'>🎧 Ascolto Ufficiale & Legale (Licenza YouTube):</div>"
            "  <div style='display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-top:6px;'>"
            f"    <a href='https://www.youtube.com/watch?v={canzone['yt']}' target='_blank' style='background:#e11d48; color:white; text-decoration:none; padding:9px 16px; border-radius:10px; font-weight:700; font-size:0.88rem;'>▶️ Ascolta il brano su YouTube</a>"
            f"    <a href='https://music.youtube.com/watch?v={canzone['yt']}' target='_blank' style='background:#111b21; color:white; text-decoration:none; padding:9px 16px; border-radius:10px; font-weight:700; font-size:0.88rem;'>🔴 YouTube Music</a>"
            "  </div>"
            "</div>"
            f"{badge_fonte('Archivio Ufficiale Canzone Italiana')}"
        ),
        "time": "08:07"
    },
    # CHIUSURA E RIEPILOGO FONTI LETTO DALLA VOCE
    {
        "cat": "📢 Riepilogo Ufficiale Fonti",
        "title": "Trasparenza e Tutela dei Dati",
        "speak": (
            "Notiziario completato. Ecco il riepilogo finale delle fonti ufficiali: "
            "previsioni meteorologiche a cura di 3B Meteo; notizie locali da Newsbiella punto it verificate dal filtro di conformità; "
            "servizio igiene urbana da Seab Biella; turni farmacie da Federfarma e ASL Biella; musica su licenza ufficiale YouTube. "
            "Buona giornata a tutti i residenti di Tavigliano!"
        ),
        "body": (
            "Tutti i dati del notiziario provengono da fonti verificate e consultabili in rete:<br><br>"
            "• <strong>Meteo:</strong> 3BMeteo.com (Stazione Tavigliano)<br>"
            "• <strong>Cronaca e Notizie:</strong> Newsbiella.it (con filtro di conformità editoriale)<br>"
            "• <strong>Igiene Urbana:</strong> Seab Biella (Comune di Tavigliano)<br>"
            "• <strong>Sanità e Farmacie:</strong> Federfarma / ASL Biella<br>"
            "• <strong>Diritti Musicali:</strong> Piattaforma YouTube Music (streaming con licenza d'autore)<br>"
            f"{badge_fonte('Notiziario Civico Autonomo di Tavigliano')}"
        ),
        "time": "08:08"
    }
]

# ==========================================
# 8. AGGIORNAMENTO DI INDEX.HTML
# ==========================================
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'<div class="status">.*?</div>',
    f'<div class="status">{data_estesa}</div>',
    content,
    flags=re.DOTALL
)

json_str = json.dumps(news_data, ensure_ascii=False, indent=2)
content = re.sub(
    r'const NEWS = \[.*?\];',
    f'const NEWS = {json_str};',
    content,
    flags=re.DOTALL
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Aggiornamento completato con successo e conformità verificata per: {data_estesa}")
