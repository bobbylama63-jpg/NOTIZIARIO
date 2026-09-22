<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Notiziario di Tavigliano</title>
  
  <meta name="theme-color" content="#1E3138">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Notiziario">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">

  <style>
    :root {
      --paper: #F4F5F1;
      --surface: #FFFFFF;
      --ink: #14181A;
      --ink-soft: #525B5E;
      --line: #DBDED6;
      --accent: #2F6B7C;
      --accent-soft: #DFEAED;
      --alert: #8F3728;
      --alert-soft: #F5E1DC;
      --tan: #A86C33;
      --tan-soft: #F2E6D6;
      --radius: 14px;
      box-sizing: border-box;
      padding-top: env(safe-area-inset-top, 0px);
      padding-bottom: env(safe-area-inset-bottom, 0px);
      color-scheme: light dark;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --paper: #121619;
        --surface: #1B2126;
        --ink: #ECEFEA;
        --ink-soft: #A0AAAE;
        --line: #2D363C;
        --accent: #84BECE;
        --accent-soft: #1E3138;
        --alert: #E38271;
        --alert-soft: #38211C;
        --tan: #D9A362;
        --tan-soft: #33291C;
      }
    }

    *, *::before, *::after { box-sizing: inherit; }
    html { height: 100%; background: var(--paper); -webkit-text-size-adjust: 100%; }
    body {
      margin: 0;
      min-height: 100%;
      background: var(--paper);
      color: var(--ink);
      font-family: "Source Serif 4", Georgia, serif;
      font-size: 16.5px;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }

    .wrap {
      max-width: 650px;
      margin: 0 auto;
      padding: 0 18px 80px;
    }

    header {
      padding: 24px 0 16px;
      border-bottom: 1px solid var(--line);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .05em;
      color: var(--accent);
      background: var(--accent-soft);
      padding: 4px 10px;
      border-radius: 999px;
    }
    .badge .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
    }
    h1 {
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: clamp(26px, 7vw, 36px);
      line-height: 1.1;
      font-weight: 800;
      margin: 12px 0 4px;
      letter-spacing: -0.02em;
    }
    .date-sub {
      color: var(--ink-soft);
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 14.5px;
      margin: 0;
    }

    /* Player Vocale */
    .player-box {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 14px 16px;
      margin: 18px 0;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .player-status {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 14px;
      font-weight: 600;
    }
    .on-air {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--alert);
    }
    .on-air-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--alert);
      animation: pulse 1.2s infinite;
    }
    @keyframes pulse {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(0.85); }
      100% { opacity: 1; transform: scale(1); }
    }
    .controls {
      display: flex;
      gap: 8px;
    }
    .btn {
      font-family: "Bricolage Grotesque", sans-serif;
      font-weight: 600;
      font-size: 14.5px;
      background: var(--ink);
      color: var(--paper);
      border: 0;
      border-radius: 999px;
      padding: 9px 16px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn.ghost {
      background: none;
      color: var(--ink);
      border: 1px solid var(--line);
    }

    /* Sezioni Schede */
    .section-title {
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 18px;
      font-weight: 700;
      margin: 24px 0 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 16px 18px;
      margin-bottom: 12px;
    }
    .card.alert-card {
      border-left: 5px solid var(--accent);
    }
    .card h3 {
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 16.5px;
      font-weight: 700;
      margin: 0 0 6px;
    }
    .card p {
      margin: 0;
      font-size: 15px;
      color: var(--ink-soft);
      line-height: 1.45;
    }
    .card .meta-highlight {
      display: inline-block;
      margin-top: 8px;
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--ink);
      background: var(--accent-soft);
      padding: 3px 8px;
      border-radius: 6px;
    }

    /* Tabella / Prezzi Carburante */
    .fuel-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 8px;
    }
    .fuel-box {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 12px;
    }
    .fuel-box b {
      display: block;
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 14px;
      color: var(--ink);
      margin-bottom: 2px;
    }
    .fuel-price {
      font-family: "Bricolage Grotesque", sans-serif;
      font-size: 18px;
      font-weight: 800;
      color: var(--accent);
      margin-bottom: 4px;
    }
    .fuel-station {
      font-size: 12.5px;
      color: var(--ink-soft);
      line-height: 1.3;
    }

    /* Condivisione WhatsApp */
    .share-btn {
      width: 100%;
      background: #25D366;
      color: #FFFFFF;
      margin-top: 20px;
      padding: 12px;
      border-radius: 999px;
      font-family: "Bricolage Grotesque", sans-serif;
      font-weight: 700;
      font-size: 15px;
      border: 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
    }

    /* Sezione Fonti solo alla fine */
    .sources-box {
      margin-top: 36px;
      padding-top: 16px;
      border-top: 1px dashed var(--line);
      font-size: 13px;
      color: var(--ink-soft);
    }
    .sources-box h4 {
      font-family: "Bricolage Grotesque", sans-serif;
      margin: 0 0 6px;
      font-size: 13.5px;
      color: var(--ink);
      text-transform: uppercase;
      letter-spacing: .03em;
    }
    .sources-box ul {
      margin: 0;
      padding-left: 18px;
    }
    .sources-box li {
      margin-bottom: 4px;
    }

    footer {
      margin-top: 20px;
      text-align: center;
      font-size: 12.5px;
      color: var(--ink-soft);
      font-family: "Bricolage Grotesque", sans-serif;
    }
  </style>
</head>
<body>
  <div class="wrap">
    
    <header>
      <span class="badge"><span class="dot"></span> Notiziario Territoriale</span>
      <h1>L'Eco di Tavigliano</h1>
      <p class="date-sub">Edizione di Mercoledì 23 Settembre 2026</p>
    </header>

    <!-- Lettore Vocale -->
    <div class="player-box">
      <div class="player-status">
        <span id="playerStateText">Ascolta l'edizione audio</span>
        <span class="on-air" id="onAirBadge" hidden><span class="on-air-dot"></span> IN VOCE</span>
      </div>
      <div class="controls">
        <button class="btn" id="playBtn" type="button">▶ Ascolta</button>
        <button class="btn ghost" id="pauseBtn" type="button" disabled>⏸ Pausa</button>
        <button class="btn ghost" id="stopBtn" type="button" disabled>⏹ Stop</button>
      </div>
    </div>

    <!-- 1. METEO -->
    <div class="section-title">🌤️ Meteo Biella BI</div>
    <div class="card">
      <h3>Tempo parzialmente soleggiato</h3>
      <p>Giornata con cielo sereno o poco nuvoloso. Temperature miti con una massima di 20°C e una minima notturna di 12°C. Vento debole da sud-est (4 mph) e precipitazioni scarse (probabilità 10%).</p>
    </div>

    <!-- 2. RACCOLTA RIFIUTI -->
    <div class="section-title">🗑️ Raccolta Rifiuti SEAB</div>
    <div class="card alert-card">
      <h3>Mercoledì 23 Settembre: INDIFFERENZIATO</h3>
      <p>Domani è regolarmente attivo il passaggio per il secco non riciclabile (indifferenziato).</p>
      <div class="meta-highlight">Esposizione: martedì sera dopo le ore 20:00 o mercoledì mattina presto</div>
    </div>

    <!-- 3. NOTIZIE DAL TERRITORIO -->
    <div class="section-title">📰 Notizie dal Territorio</div>
    
    <div class="card">
      <h3>Furto di cavi di rame sulla Biella-Novara: ritardi e disagi</h3>
      <p>La circolazione ferroviaria tra Casaleggio e Agognate ha subito forti rallentamenti e alcune cancellazioni a causa del furto notturno di cavi dell'infrastruttura. L'intervento delle squadre tecniche ha permesso il ripristino della tratta.</p>
    </div>

    <div class="card">
      <h3>Bici rubate a Biella ritrovate al porto di Genova</h3>
      <p>Tre biciclette da corsa di alto valore sottratte nei giorni scorsi sono state rintracciate e sequestrate al terminal imbarchi di Genova, occultate a bordo di un mezzo diretto verso l'estero. Determinante la geolocalizzazione installata sul manubrio da uno dei proprietari.</p>
    </div>

    <div class="card">
      <h3>Città Studi: Notte europea dei ricercatori</h3>
      <p>In vista dell'appuntamento del 25 settembre, il polo universitario biellese prepara i laboratori aperti al pubblico con incontri dedicati all'intelligenza artificiale, alla sostenibilità ambientale e alle nuove tecnologie per tutte le fasce d'età.</p>
    </div>

    <!-- 4. FARMACIA DI TURNO PROVINCIALE -->
    <div class="section-title">💊 Farmacia di Turno (Provincia di Biella)</div>
    <div class="card">
      <h3>Farmacia Del Centro (Dott. Tarricone) — Biella</h3>
      <p><strong>Indirizzo:</strong> Via Italia, 23 - 13900 Biella (BI)<br>
      <strong>Telefono:</strong> 015 22480<br>
      <strong>Servizio:</strong> In turno continuativo e reperibilità notturna h24 per l'area provinciale.</p>
    </div>

    <!-- 5. CARBURANTI PIÙ ECONOMICI -->
    <div class="section-title">⛽ Carburanti più economici (Biella e provincia)</div>
    <div class="card">
      <p style="margin-bottom:8px">I distributori con i prezzi self-service più bassi registrati sul territorio provinciale:</p>
      <div class="fuel-grid">
        <div class="fuel-box">
          <b>BENZINA (Self)</b>
          <div class="fuel-price">1,914 €/L</div>
          <div class="fuel-station">Pompe Bianche<br>Via Tripoli 5, Biella</div>
        </div>
        <div class="fuel-box">
          <b>DIESEL / GASOLIO (Self)</b>
          <div class="fuel-price">2,015 €/L</div>
          <div class="fuel-station">Pompe Bianche / Europam<br>Biella e prov.</div>
        </div>
      </div>
    </div>

    <!-- Condivisione WhatsApp -->
    <a id="waShare" class="share-btn" target="_blank" href="#">
      Condividi l'Eco su WhatsApp
    </a>

    <!-- SEZIONE FONTI (ESCLUSIVAMENTE ALLA FINE) -->
    <div class="sources-box">
      <h4>Fonti ufficiali consultate per questa edizione:</h4>
      <ul>
        <li>Dati Meteo Biella BI (Google Weather)</li>
        <li>Calendario Ufficiale Raccolta Rifiuti SEAB Biella</li>
        <li>Notiziari locali di Biella e provincia (cronaca e territorio)</li>
        <li>Turnario ufficiale ASL Biella / Ordine Farmacisti Biella</li>
        <li>Osservaprezzi Carburanti - Ministero delle Imprese e del Made in Italy (MIMIT)</li>
      </ul>
    </div>

    <footer>
      Notiziario informativo locale ad uso civico — Tavigliano (BI)
    </footer>

  </div>

  <script>
    // Testo rigorosamente ripulito da formule introduttive o fonti per la lettura vocale
    const voiceText = `Benvenuti all'Eco di Tavigliano per mercoledì 23 settembre 2026. 
Meteo per Biella: tempo parzialmente soleggiato, con temperatura massima di 20 gradi e minima di 12. 
Servizio rifiuti: domani mercoledì è prevista la raccolta dell'indifferenziato. Ricordarsi di esporre il mastello questa sera dopo le ore venti. 
Cronaca dal territorio: 
Furto di cavi di rame sulla linea ferroviaria Biella-Novara, con cancellazioni e ritardi poi rientrati nella giornata. 
Tre biciclette rubate a Biella sono state rintracciate e recuperate al porto di Genova grazie al sistema satellitare. 
Città Studi prepara le iniziative per la Notte Europea dei Ricercatori con laboratori aperti alla cittadinanza. 
Farmacia di turno: per la provincia di Biella è attiva in turno continuativo la Farmacia Del Centro in via Italia 23 a Biella. 
Prezzi carburanti: i distributori più economici rilevati in provincia sono le Pompe Bianche di via Tripoli a Biella per la benzina a 1 euro e 91 centesimi, e per il gasolio a 2 euro e 1 centesimo. 
Buona giornata da Tavigliano.`;

    // Configurazione Sintesi Vocale
    let synth = window.speechSynthesis;
    let utterance = null;
    const playBtn = document.getElementById("playBtn");
    const pauseBtn = document.getElementById("pauseBtn");
    const stopBtn = document.getElementById("stopBtn");
    const stateText = document.getElementById("playerStateText");
    const onAirBadge = document.getElementById("onAirBadge");

    function setupUtterance() {
      utterance = new SpeechSynthesisUtterance(voiceText);
      utterance.lang = "it-IT";
      utterance.rate = 0.98;

      const voices = synth.getVoices();
      const itVoice = voices.find(v => v.lang.startsWith("it"));
      if (itVoice) utterance.voice = itVoice;

      utterance.onstart = () => {
        stateText.textContent = "Riproduzione vocale in corso...";
        onAirBadge.hidden = false;
        playBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      };

      utterance.onend = () => {
        resetControls();
      };

      utterance.onerror = () => {
        resetControls();
      };
    }

    function resetControls() {
      stateText.textContent = "Ascolta l'edizione audio";
      onAirBadge.hidden = true;
      playBtn.disabled = false;
      pauseBtn.disabled = true;
      stopBtn.disabled = true;
    }

    playBtn.addEventListener("click", () => {
      if (synth.paused) {
        synth.resume();
        stateText.textContent = "Riproduzione vocale in corso...";
        onAirBadge.hidden = false;
        playBtn.disabled = true;
        pauseBtn.disabled = false;
      } else {
        synth.cancel();
        setupUtterance();
        synth.speak(utterance);
      }
    });

    pauseBtn.addEventListener("click", () => {
      if (synth.speaking && !synth.paused) {
        synth.pause();
        stateText.textContent = "In pausa";
        onAirBadge.hidden = true;
        playBtn.disabled = false;
        pauseBtn.disabled = true;
      }
    });

    stopBtn.addEventListener("click", () => {
      synth.cancel();
      resetControls();
    });

    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => {
        if (!utterance) setupUtterance();
      };
    }

    // Link WhatsApp
    const waText = encodeURIComponent("Leggi l'edizione di oggi dell'Eco di Tavigliano (Meteo, Rifiuti: Indifferenziato, Farmacia di Turno e Notizie): " + window.location.href);
    document.getElementById("waShare").href = "https://api.whatsapp.com/send?text=" + waText;
  </script>
</body>
</html>
