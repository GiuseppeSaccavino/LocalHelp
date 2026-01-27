from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from init_db import *

app = Flask(__name__)
app.secret_key = "chiave_super_segreta"  

# --- CONNESSIONE DB ---
def get_db():
    conn = sqlite3.connect("database.db", timeout=30) #la connessione aspetta 30 secondi se il DB è bloccato invece di dare subito errore
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # ATTIVA FK
    conn.execute("PRAGMA journal_mode=WAL;") #Permette più scritture contemporaneamente, migliora la concorrenza 
    return conn

def get_posts(id_assegnato=None, accettata=0, completato=0, self_id=None, uguale=0):
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT 
            p.id AS post_id,
            p.descrizione,
            u.email,
            u.tel,
            l.provincia,
            l.comune,
            l.via,
            u2.email AS assegnato_email
        FROM post p
        JOIN utente u ON p.id_utente = u.id_utente
        JOIN locazione l ON l.id_utente = u.id_utente
        LEFT JOIN utente u2 ON p.id_assegnato = u2.id_utente
        WHERE p.accettata = ?
        AND p.completato = ?
    """

    params = [accettata, completato]

    if id_assegnato == "NOT_NULL":
        query += " AND p.id_assegnato IS NOT NULL"
    elif id_assegnato is None:
        query += " AND p.id_assegnato IS NULL"
    else:
        query += " AND p.id_assegnato = ?"
        params.append(id_assegnato)

    if self_id is not None and uguale == 0:
        query += " AND p.id_utente != ?"
        params.append(self_id)
    elif self_id is not None and uguale == 1:
        query += " AND p.id_utente = ?"
        params.append(self_id)
        
    query += " ORDER BY p.id DESC"

    cur.execute(query, params)
    posts = cur.fetchall()

    # generi per ogni post
    cur.execute("""
        SELECT 
            pg.post_id,
            g.nome
        FROM post_genere pg
        JOIN genere g ON g.id = pg.genere_id
    """)
    righe_generi = cur.fetchall()
    
    conn.close()

    # mappa post_id -> lista generi
    generi_map = {}
    for r in righe_generi:
        post_id = r["post_id"]
        generi_map.setdefault(post_id, []).append(r["nome"])
    
    return posts, generi_map

# --- API dinamiche ---
@app.route("/province/<int:regione_id>")
def get_province(regione_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM province WHERE regione_id = ? ORDER BY nome", (regione_id,))
    province = [{"id": p["id"], "nome": p["nome"]} for p in cur.fetchall()]
    conn.close()
    return jsonify(province)

@app.route("/comuni/<int:provincia_id>")
def get_comuni(provincia_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM comuni WHERE provincia_id = ? ORDER BY nome", (provincia_id,))
    comuni = [{"id": c["id"], "nome": c["nome"]} for c in cur.fetchall()]
    conn.close()
    return jsonify(comuni)

# --- HOME ---
@app.route("/")
def index():
    if "id_utente" not in session:
        return redirect("/login")
    
    return redirect("/bacheca")


# --- REGISTRAZIONE ---
@app.route("/register", methods=["GET", "POST"])
def register():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, nome FROM regioni ORDER BY nome")
    regioni = cur.fetchall()
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        regione_id = request.form.get("regione")
        provincia_id = request.form.get("provincia")
        comune_id = request.form.get("comune")
        via = request.form.get("via")
        cap = request.form.get("cap")
        tel = request.form.get("tel")

        if not all([email, password, regione_id, provincia_id, comune_id, via, cap, tel]):
            conn.close()
            return "Errore: tutti i campi sono obbligatori."

        hashed = generate_password_hash(password)

        try:
            # Inserisce utente
            cur.execute("INSERT INTO utente (email, password, tel) VALUES (?, ?, ?)", (email, hashed, tel))
            conn.commit()
            cur.execute("SELECT id_utente FROM utente WHERE email = ?", (email,))
            id_utente = cur.fetchone()["id_utente"]

            # Recupera nomi da ID per locazione
            cur.execute("SELECT nome FROM regioni WHERE id = ?", (regione_id,))
            regione = cur.fetchone()["nome"]
            cur.execute("SELECT nome FROM province WHERE id = ?", (provincia_id,))
            provincia = cur.fetchone()["nome"]
            cur.execute("SELECT nome FROM comuni WHERE id = ?", (comune_id,))
            comune = cur.fetchone()["nome"]

            # Inserisce locazione
            cur.execute("""
                INSERT INTO locazione (id_utente, regione, provincia, comune, via, CAP)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_utente, regione, provincia, comune, via, cap))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Errore: email già registrata."
        finally:
            conn.close()
            
        return redirect("/login")
    
    return render_template("register.html", regioni=regioni)

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM utente WHERE email = ?", (email,))
        utente = cur.fetchone()
        conn.close()

        if utente and check_password_hash(utente["password"], password):
            session["id_utente"] = utente["id_utente"]
            session["email"] = utente["email"]
            return redirect("/bacheca")
        else:
            return "Credenziali errate."

    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- AGGIUNGI RICHIESTE ---
@app.route("/aggiungi",  methods=["GET", "POST"])
def aggiungi():
    if "id_utente" not in session:
        return redirect("/login")
    
    if request.method == "POST":
        descrizione = request.form.get("descrizione")
        generi = request.form.getlist("genere[]")
        
        if not generi:
            error = "Bisogna selezionare almeno un tipo di aiuto."
            return render_template("aggiungi.html", error=error)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO post (descrizione, id_utente) VALUES (?, ?);", (descrizione, session['id_utente']))
        id_post = cur.lastrowid
        conn.commit()
        
        for gen in generi:
            cur.execute("SELECT id FROM genere WHERE nome=?", (gen,))
            row = cur.fetchone()
            
            if row:
                id_genere = row[0]
            else:
                cur.execute("INSERT INTO genere (nome) VALUES (?)", (gen,))
                id_genere = cur.lastrowid

            cur.execute("INSERT INTO post_genere (post_id, genere_id) VALUES (?, ?)",(id_post, id_genere))
        
        conn.commit()
        return "Richiesta aggiunta con successo <a href='richieste'>Torna Alle mie Richieste</a>"

    return render_template("aggiungi.html")

# --- ATTIVITÀ ---
@app.route("/attivita")
def attivita():
    if "id_utente" not in session:
        return redirect("/login")
    
    attivita_in_corso, generi_map_in = get_posts(session["id_utente"], 1, 0, None)
    attivita_completate, generi_map_ok = get_posts(session["id_utente"], 1, 1, None)

    return render_template(
        "attivita.html",
        title="Le mie attività",
        attivita_in_corso=attivita_in_corso,
        generi_map_in = generi_map_in,
        attivita_completate=attivita_completate,
        generi_map_ok = generi_map_ok
    )

# --- RICHIESTE ---
@app.route("/richieste")
def richieste():
    if "id_utente" not in session:
        return redirect("/login")
    
    attivita_in_corso, generi_map_in = get_posts("NOT_NULL", 1, 0, session["id_utente"],1)
    attivita_completate, generi_map_ok = get_posts("NOT_NULL", 1, 1, session["id_utente"],1)
    attivita_non_accettate, generi_map_non = get_posts(None, 0, 0, session["id_utente"],1)

    return render_template(
        "richieste.html",
        title="Le mie richieste",
        attivita_in_corso=attivita_in_corso,
        generi_map_in = generi_map_in,
        attivita_completate=attivita_completate,
        generi_map_ok = generi_map_ok,
        attivita_non_accettate=attivita_non_accettate,
        generi_map_non=generi_map_non
    )

# --- BACHECA / ACCETTA POST ---
@app.route("/bacheca")
def bacheca():
    if "id_utente" not in session:
        return redirect("/login")
    try:
        posts, generi_map = get_posts(None, 0, 0, session["id_utente"])
    except Exception as e:
        print("Errore nella bacheca: ", e)
        return redirect("/login")

    return render_template(
        "bacheca.html",
        title="Richieste disponibili",
        posts=posts,
        generi_map=generi_map
    )

# --- ACCETTA ---
@app.route("/accetta/<int:id_post>", methods=["POST"])
def accetta_post(id_post):
    if "id_utente" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE post
        SET accettata = 1,
            id_assegnato = ?
        WHERE id = ?
          AND accettata = 0
    """, (session["id_utente"], id_post))

    conn.commit()
    conn.close()

    return redirect("/bacheca")

# --- CANCELLA RICHISTA---
@app.route("/cancella/<int:id_post>", methods=["POST"])
def cancella(id_post):
    if "id_utente" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        DELETE FROM post
        WHERE id = ?
        AND id_utente = ?
    """, (id_post, session["id_utente"]))

    conn.commit()
    conn.close()
    
    return redirect("/richieste")

# --- COMPLETA RICHIESTA ---
@app.route("/completa/<int:id_post>", methods=["POST"])
def completa(id_post):
    if "id_utente" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    # Aggiorna solo se l'utente loggato ha accettato il post
    cur.execute("""
        UPDATE post
        SET completato = 1
        WHERE id = ?
          AND id_utente = ?
          AND completato = 0
    """, (id_post, session["id_utente"]))

    conn.commit()
    conn.close()

    return redirect("/richieste")


if __name__ == "__main__":
    DB_FILE = "database.db"

    if not os.path.exists(DB_FILE):
        create_table(DB_FILE)
        insert_RPC(DB_FILE)
    
    app.run(port=8000, debug=True, host='0.0.0.0')

