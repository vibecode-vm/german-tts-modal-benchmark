"""Buchhaltungs-Dialog: Agent fordert Rechnung an, User fragt nach Upload-Link.

Verwendet von allen TTS-Tests, damit die Modelle direkt vergleichbar sind.
"""

# (speaker, line) — Agent (weiblich/männlich) und User wechseln
DIALOG = [
    ("agent", "Guten Tag, hier spricht die Buchhaltung von Servas AI."),
    ("agent", "Wir benötigen noch Ihre Rechnung vom April zweitausendsechsundzwanzig."),
    ("user",  "Guten Tag. Können Sie mir sagen, wo ich diese Rechnung finde?"),
    ("agent", "Selbstverständlich. Die finden Sie in Ihrem Kundenportal unter dem Punkt Rechnungen."),
    ("user",  "Verstehe. Und wo genau soll ich die Datei dann hochladen?"),
    ("agent", "Sie erhalten gleich eine E-Mail mit einem persönlichen Upload-Link."),
    ("agent", "Bitte laden Sie die Rechnung über diesen Link hoch, nicht per Antwort-Mail."),
    ("user",  "Alles klar. Bis wann muss das erledigt sein?"),
    ("agent", "Spätestens bis Freitag, den dreiundzwanzigsten Mai, achtzehn Uhr."),
    ("user",  "Wunderbar. Vielen Dank für die Information, auf Wiederhören."),
    ("agent", "Vielen Dank, einen schönen Tag noch."),
]

SHORT_TESTS = [
    ("greeting", "Guten Tag, Frau Schäfer! Wie geht es Ihnen heute?"),
    ("umlauts",  "Müller, Schäfer, Größe, Straße, Übermütig — alle Umlaute klar?"),
    ("numbers",  "Ihre Rechnung über einhundertneunundzwanzig Euro fünfzig Cent ist überfällig."),
    ("phone",    "Erreichen Sie uns unter null-eins-fünf-eins, zwei-drei-vier-fünf, sechs-sieben-acht-neun."),
]

if __name__ == "__main__":
    for spk, line in DIALOG:
        print(f"[{spk}] {line}")
