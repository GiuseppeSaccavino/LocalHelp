CREATE TABLE IF NOT EXISTS utente(
    id_utente INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL, 
    password TEXT NOT NULL,
    tel TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS locazione(
    id_locazione INTEGER PRIMARY KEY AUTOINCREMENT,
    regione TEXT NOT NULL,
    provincia TEXT NOT NULL,
    comune TEXT NOT NULL,
    via TEXT NOT NULL,
    CAP TEXT NOT NULL,
    id_utente INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (id_utente) REFERENCES utente(id_utente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS regioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS province (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    sigla TEXT,
    regione_id INTEGER,
    UNIQUE(nome, regione_id),
    FOREIGN KEY (regione_id) REFERENCES regioni(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comuni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    provincia_id INTEGER,
    UNIQUE(nome, provincia_id),
    FOREIGN KEY (provincia_id) REFERENCES province(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descrizione TEXT,
    accettata INTEGER NOT NULL DEFAULT 0 CHECK (accettata IN (0,1)),
    completato INTEGER NOT NULL DEFAULT 0 CHECK (completato IN (0,1)),
    id_utente INTEGER NOT NULL,
    id_assegnato INTEGER,
    FOREIGN KEY (id_utente) REFERENCES utente(id_utente) ON DELETE CASCADE,
    FOREIGN KEY (id_assegnato) REFERENCES utente(id_utente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS genere(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS post_genere (
    post_id INTEGER NOT NULL,
    genere_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, genere_id),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (genere_id) REFERENCES genere(id) ON DELETE CASCADE
);
