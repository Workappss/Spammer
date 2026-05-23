import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- TU WPISZ SWOJE DANE ---
SERWER_SMTP = "smtp.gmail.com"
PORT = 465
NADAWCA = "spammv2.1@gmail.com"
HASLO = "cgly gdcl fsyg jmug"

def usun_polskie_znaki(tekst):
    slownik = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
    return tekst.translate(slownik)

HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automated Email Messenger</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0c0d0e; margin: 0; padding: 15px; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }
        .app-container { width: 100%; max-width: 440px; background: #121314; padding: 20px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .app-title { font-size: 20px; font-weight: 500; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .panel-header { background: #3b82f6; color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 14px; }
        .panel-subheader { background: #18191a; padding: 12px 16px; font-size: 13px; color: #a1a1aa; border-bottom: 1px solid #27272a; }
        .console-label { background: #27272a; color: #a1a1aa; font-size: 11px; font-weight: bold; padding: 6px 16px; font-family: monospace; letter-spacing: 0.5px; }

        /* Twoja idealna zielona konsola */
        .console-box { background: #000000; padding: 20px; border-radius: 0 0 8px 8px; font-family: 'Courier New', Courier, monospace; font-size: 14px; color: #22c55e; min-height: 140px; max-height: 200px; overflow-y: auto; line-height: 1.6; border-bottom: 1px solid #27272a; font-weight: bold; }

        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; text-align: center; padding: 15px 0; border-bottom: 1px solid #27272a; margin-bottom: 15px; }
        .stats-label { color: #a1a1aa; font-size: 13px; margin-bottom: 6px; }
        .stats-value { font-size: 15px; font-weight: 500; }
        .input-group { display: flex; align-items: center; margin-bottom: 12px; gap: 10px; }
        .input-group label { width: 110px; font-size: 13px; color: #a1a1aa; font-weight: 500; }
        .input-group input, .input-group textarea { flex: 1; background: #1c1d1f; border: 1px solid #27272a; border-radius: 6px; padding: 8px 12px; color: white; font-size: 13px; }
        .input-group textarea { resize: none; height: 36px; font-family: inherit; }
        .slider-container { display: flex; align-items: center; gap: 15px; margin-top: 15px; }
        .slider-container label { width: 110px; font-size: 13px; color: #a1a1aa; }
        .slider-container input[type="range"] { flex: 1; accent-color: #3b82f6; cursor: pointer; }
        .count-badge { background: #1c1d1f; padding: 6px 12px; border-radius: 6px; font-size: 13px; min-width: 24px; text-align: center; border: 1px solid #27272a; }
        .run-btn { background: #27272a; border: none; width: 32px; height: 32px; border-radius: 50%; color: white; cursor: pointer; display: flex; justify-content: center; align-items: center; font-size: 12px; }
        .run-btn:hover { background: #3b82f6; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="app-title">
            <span>Automated Email Messenger</span>
            <button class="run-btn" onclick="uruchomWysylke()">▶</button>
        </div>

        <div class="panel-header">Python Mailer v2.1</div>
        <div id="sub-status" class="panel-subheader">Gotowy.</div>
        <div class="console-label">CONSOLE OUTPUT</div>
        <div id="console" class="console-box">Gotowy do wysylki. Skonfiguruj parametry i kliknij 'Uruchom'.</div>

        <div class="stats-grid">
            <div>
                <div class="stats-label">Status</div>
                <div id="status-val" class="stats-value">Idle</div>
            </div>
            <div>
                <div class="stats-label">Progress</div>
                <div id="progress-val" class="stats-value">0%</div>
            </div>
        </div>

        <div class="input-group">
            <label>Recipient Email</label>
            <input type="email" id="odbiorca" value="przyklad@gmail.com">
        </div>

        <div class="input-group">
            <label>Email Content</label>
            <textarea id="tresc">Czesc, to jest automatyczna wiadomosc!</textarea>
        </div>

        <div class="slider-container">
            <label>Count of Emails</label>
            <input type="range" id="ilosc" min="1" max="50" value="10" oninput="updateCount(this.value)">
            <div id="count-badge" class="count-badge">10</div>
        </div>
    </div>

    <script>
        function updateCount(val) {
            document.getElementById('count-badge').innerText = val;
        }

        async function uruchomWysylke() {
            const odbiorca = document.getElementById('odbiorca').value;
            const tresc = document.getElementById('tresc').value;
            const ilosc = parseInt(document.getElementById('ilosc').value);
            const temat = "Automated Messenger";

            if(!odbiorca || !tresc) {
                alert("Uzupelnij pola!");
                return;
            }

            const consoleBox = document.getElementById('console');
            const statusVal = document.getElementById('status-val');
            const progressVal = document.getElementById('progress-val');
            const subStatus = document.getElementById('sub-status');

            // Dokładne odtworzenie Twoich logów startowych
            consoleBox.innerHTML = "--- SYSTEM: Rozpoczynanie procesu ---<br>Nawiazywanie polaczenia z serwerem SMTP...<br>";
            statusVal.innerText = "Running";
            subStatus.innerText = "Wysylanie...";

            let zalogowano = false;

            for (let i = 1; i <= ilosc; i++) {
                if(!zalogowano) {
                    consoleBox.innerHTML += "Zalogowano pomyslnie: auth_success<br>";
                    zalogowano = true;
                }

                // Wyciągamy samą nazwę użytkownika przed znakiem @ do logów, tak jak na Twoim screenie
                let nazwaUsera = odbiorca.split('@')[0];
                consoleBox.innerHTML += `Wyslano mail ${i}/${ilosc} do ${nazwaUsera}<br>`;
                consoleBox.scrollTop = consoleBox.scrollHeight;

                let response = await fetch('/send_one', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ odbiorca, temat, tresc, aktualny: i, ogółem: ilosc })
                });

                let wynik = await response.json();
                if (wynik.status !== "ok") {
                    consoleBox.innerHTML += `<span style="color:#ef4444;">Blad: ${wynik.message}</span><br>Status: FAILURE<br>`;
                    statusVal.innerText = "Error";
                    subStatus.innerText = "Przerwano.";
                    return;
                }

                let procent = Math.round((i / ilosc) * 100);
                progressVal.innerText = procent + '%';
            }

            // Twoje oryginalne zakończenie logów
            consoleBox.innerHTML += "Proces zakonczony. Rozlaczanie...<br>Status: SUCCESS<br>";
            consoleBox.scrollTop = consoleBox.scrollHeight;
            statusVal.innerText = "Success";
            progressVal.innerText = "100%";
            subStatus.innerText = "Zakresource pomyslnie.";
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/send_one", methods=["POST"])
def send_one():
    dane = request.get_json()
    odbiorca = usun_polskie_znaki(dane["odbiorca"])
    temat = usun_polskie_znaki(dane["temat"])
    tresc = usun_polskie_znaki(dane["tresc"])
    i = dane["aktualny"]
    ilosc = dane["ogółem"]

    try:
        serwer = smtplib.SMTP_SSL(SERWER_SMTP, PORT)
        serwer.login(NADAWCA, HASLO)

        msg = MIMEMultipart()
        msg["From"] = NADAWCA
        msg["To"] = odbiorca
        msg["Subject"] = f"{temat} [{i}/{ilosc}]"
        msg.attach(MIMEText(tresc, "plain"))

        serwer.sendmail(NADAWCA, odbiorca, msg.as_string())
        serwer.quit()

        time.sleep(0.3)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)