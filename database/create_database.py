"""
create_database.py
------------------
Creates the SQLite database with:
  - legal_sections table  (IPC / BNS reference data)
  - users table           (authentication)
Run this ONCE before launching the app:
    python database/create_database.py
"""

import sqlite3
import os
import bcrypt

# ── Paths ──────────────────────────────────────────────────────────────────────
DB_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "legal_sections.db")

# ── Sample legal dataset ───────────────────────────────────────────────────────
LEGAL_SECTIONS = [
    # (section, crime_name, description, punishment, keywords)
    ("IPC 300 / BNS 101",
     "Murder",
     "Whoever commits murder shall be punished. Murder is culpable homicide with intent to cause death.",
     "Death, or imprisonment for life, and fine.",
     "murder, kill, killed, death, homicide, shoot, stabbed, shot, dead body, slain"),

    ("IPC 302 / BNS 103",
     "Punishment for Murder",
     "Whoever commits murder shall be punished with death or imprisonment for life.",
     "Death or life imprisonment and fine.",
     "murder, killed, death, homicide, shoot, stab, poison"),

    ("IPC 307 / BNS 109",
     "Attempt to Murder",
     "Whoever does any act with such intention or knowledge and under such circumstances that if he thereby caused death, he would be guilty of murder.",
     "Imprisonment up to 10 years and fine; if hurt caused, life imprisonment.",
     "attempt murder, tried to kill, attack, shot at, stabbed, poison attempt"),

    ("IPC 304A / BNS 106",
     "Death by Negligence",
     "Causing death by doing a rash or negligent act not amounting to culpable homicide.",
     "Imprisonment up to 2 years, or fine, or both.",
     "accident, negligence, rash driving, vehicle, hit and run, careless"),

    ("IPC 323 / BNS 115",
     "Assault / Voluntarily Causing Hurt",
     "Whoever voluntarily causes hurt to another person by using force or violence.",
     "Imprisonment up to 1 year, or fine up to ₹1000, or both.",
     "assault, attacked, beat, hurt, slap, punch, hit, kick, injury, wound"),

    ("IPC 325 / BNS 117",
     "Voluntarily Causing Grievous Hurt",
     "Whoever voluntarily causes grievous hurt such as broken bones, loss of limb or permanent damage.",
     "Imprisonment up to 7 years and fine.",
     "grievous hurt, broken bone, acid attack, knife, severe injury, fracture, maim"),

    ("IPC 354 / BNS 74",
     "Assault or Criminal Force on Woman / Sexual Harassment",
     "Assault or use of criminal force to a woman with intent to outrage her modesty.",
     "Imprisonment 1–5 years and fine.",
     "molest, grope, eve teasing, outrage modesty, touch inappropriately, harass woman"),

    ("IPC 376 / BNS 64",
     "Rape",
     "Sexual assault / rape against a woman without her consent.",
     "Minimum 10 years rigorous imprisonment; may extend to life; fine.",
     "rape, sexual assault, forced sex, non-consensual, violated"),

    ("IPC 378 / BNS 303",
     "Theft",
     "Whoever intending to take dishonestly any moveable property out of the possession of any person without that person's consent.",
     "Imprisonment up to 3 years, or fine, or both.",
     "theft, steal, stole, stolen, pickpocket, shoplifting, took without permission"),

    ("IPC 379 / BNS 304",
     "Punishment for Theft",
     "Punishment specifically for the act of theft as defined in IPC 378.",
     "Imprisonment up to 3 years, or fine, or both.",
     "theft, steal, stole, wallet, phone, bag, property, belongings"),

    ("IPC 380 / BNS 305",
     "Theft in Dwelling",
     "Theft committed in a building used for human dwelling or for keeping custody of property.",
     "Imprisonment up to 7 years and fine.",
     "house theft, home burglary, break in, dwelling theft, room robbery"),

    ("IPC 390 / BNS 309",
     "Robbery",
     "When theft or extortion is committed with hurt or apprehension of hurt to the victim.",
     "Imprisonment up to 10 years and fine.",
     "robbery, robbed, snatched, held at gunpoint, knife robbery, threat and steal"),

    ("IPC 392 / BNS 310",
     "Punishment for Robbery",
     "Rigorous punishment for robbery involving force or intimidation.",
     "Rigorous imprisonment up to 10 years and fine.",
     "robbery, armed robbery, snatched, looted, forced robbery"),

    ("IPC 395 / BNS 311",
     "Dacoity",
     "When five or more persons conjointly commit or attempt to commit robbery.",
     "Imprisonment for life, or rigorous imprisonment up to 10 years, and fine.",
     "dacoity, gang robbery, group looting, mob robbery, armed gang"),

    ("IPC 406 / BNS 316",
     "Criminal Breach of Trust",
     "Whoever, being entrusted with property, dishonestly misappropriates it.",
     "Imprisonment up to 3 years, or fine, or both.",
     "breach of trust, embezzlement, misappropriation, entrusted, company fraud"),

    ("IPC 415 / BNS 318",
     "Cheating / Fraud",
     "Whoever deceives any person, fraudulently inducing the person to deliver property.",
     "Imprisonment up to 1 year, or fine, or both.",
     "cheat, fraud, deceive, fake, scam, false promise, mislead, con"),

    ("IPC 420 / BNS 318",
     "Cheating and Dishonest Inducement",
     "Cheating and thereby dishonestly inducing delivery of property or making, altering, or destroying valuable security.",
     "Imprisonment up to 7 years and fine.",
     "cheat, fraud, scam, 420, fake documents, false pretense, online fraud, swindle"),

    ("IPC 447 / BNS 329",
     "Criminal Trespass",
     "Whoever commits criminal trespass by entering into or upon property in the possession of another.",
     "Imprisonment up to 3 months, or fine up to ₹500, or both.",
     "trespass, illegally entered, broke into, unauthorized entry, land encroachment"),

    ("IPC 448 / BNS 330",
     "House Trespass",
     "Trespass committed in a building used as human dwelling, place of worship, or custody of property.",
     "Imprisonment up to 1 year, or fine up to ₹1000, or both.",
     "house trespass, entered home without permission, illegal entry, broke into house"),

    ("IPC 463 / BNS 336",
     "Forgery",
     "Whoever makes a false document or false electronic record with intent to cause damage or injury.",
     "Imprisonment up to 2 years, or fine, or both.",
     "forgery, forged, fake document, false signature, counterfeit, tampered document"),

    ("IPC 499 / BNS 356",
     "Defamation",
     "Whoever makes or publishes imputation to harm reputation of a person through words, signs or visible representation.",
     "Imprisonment up to 2 years, or fine, or both.",
     "defamation, slander, libel, false accusation, reputation harm, fake news about person"),

    ("IPC 503 / BNS 351",
     "Criminal Intimidation",
     "Whoever threatens another with injury to his person, reputation, or property to cause alarm.",
     "Imprisonment up to 2 years, or fine, or both.",
     "threat, threaten, intimidate, blackmail, coerce, terrorize, extort with threat"),

    ("IPC 506 / BNS 352",
     "Punishment for Criminal Intimidation",
     "Threatening with death or grievous hurt to cause alarm.",
     "Imprisonment up to 7 years, or fine, or both (if threat of death/grievous hurt).",
     "death threat, threaten to kill, serious threat, gun threat, criminal threat"),

    ("IPC 363 / BNS 137",
     "Kidnapping",
     "Whoever kidnaps any person from the lawful guardianship.",
     "Imprisonment up to 7 years and fine.",
     "kidnap, abduct, missing child, took away, forcefully taken, hostage"),

    ("IPC 366 / BNS 140",
     "Kidnapping / Abduction of Woman",
     "Kidnapping or abducting a woman to compel her to marry or for other wrongful purposes.",
     "Imprisonment up to 10 years and fine.",
     "abduct woman, forcefully taken woman, kidnap girl, forced marriage"),

    ("IPC 498A / BNS 85",
     "Dowry Harassment / Domestic Violence",
     "Husband or relative subjecting wife to cruelty for dowry or harassment.",
     "Imprisonment up to 3 years and fine.",
     "dowry harassment, domestic violence, marital cruelty, wife beating, torture by husband"),

    ("IT Act 66 / BNS 66",
     "Hacking / Computer-Related Offences",
     "If any person dishonestly or fraudulently does any act referred to in section 43, he shall be punishable.",
     "Imprisonment up to 3 years, or fine up to ₹5 lakh, or both.",
     "hacking, hack, cybercrime, unauthorized access, computer crime, data breach, cracked password"),

    ("IT Act 66C",
     "Identity Theft",
     "Fraudulent or dishonest use of electronic signature, password, or other unique identification feature.",
     "Imprisonment up to 3 years and fine up to ₹1 lakh.",
     "identity theft, fake identity, stolen credentials, account takeover, impersonation online"),

    ("IT Act 66D",
     "Cheating by Impersonation Using Computer",
     "Cheating by personating using a communication device or computer resource.",
     "Imprisonment up to 3 years and fine up to ₹1 lakh.",
     "online fraud, fake profile, impersonation, phishing, social engineering"),

    ("IT Act 67",
     "Publishing Obscene Material Online",
     "Publishing or transmitting or causing to be published in electronic form any obscene material.",
     "First conviction: imprisonment up to 3 years and fine up to ₹5 lakh.",
     "obscene content, pornography online, explicit content, objectionable material"),

    ("NDPS Act 20",
     "Drug Trafficking / Possession",
     "Possession, use, transportation or selling of narcotic drugs or psychotropic substances.",
     "Rigorous imprisonment 10 years to life and fine up to ₹1–2 lakh.",
     "drugs, narcotic, cocaine, heroin, ganja, marijuana, drug trafficking, possession of drugs"),

    ("IPC 304B / BNS 80",
     "Dowry Death",
     "Death of a woman caused by burns, bodily injury or under suspicious circumstances within 7 years of marriage.",
     "Imprisonment not less than 7 years, may extend to life.",
     "dowry death, bride burning, suspicious death after marriage, dowry murder"),
]


# ── Helper ─────────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


# ── Main creation routine ──────────────────────────────────────────────────────
def create_database():
    print(f"[DB] Creating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # ── Legal sections table ───────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS legal_sections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            section     TEXT NOT NULL,
            crime_name  TEXT NOT NULL,
            description TEXT NOT NULL,
            punishment  TEXT NOT NULL,
            keywords    TEXT NOT NULL
        )
    """)

    # ── Users table ────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'user',
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Reports table ─────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            input_text  TEXT NOT NULL,
            summary     TEXT,
            crime_types TEXT,
            ipc_sections TEXT,
            sentiment   TEXT,
            bias_score  REAL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Insert legal sections (skip if already populated) ─────────────────────
    cur.execute("SELECT COUNT(*) FROM legal_sections")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO legal_sections (section, crime_name, description, punishment, keywords) "
            "VALUES (?, ?, ?, ?, ?)",
            LEGAL_SECTIONS,
        )
        print(f"[DB] Inserted {len(LEGAL_SECTIONS)} legal sections.")
    else:
        print("[DB] Legal sections already exist – skipping insert.")

    # ── Create default admin account ──────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "admin"),
        )
        print("[DB] Default admin account created  (admin / admin123).")

    conn.commit()
    conn.close()
    print("[DB] Database ready.")


if __name__ == "__main__":
    create_database()
