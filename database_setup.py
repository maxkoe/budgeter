import sqlite3 as sql
import pandas as pd
import sys

db_filename = sys.argv[1] if len(sys.argv) > 1 else 'my-budget-default.sqlite'

db = sql.connect(db_filename)
print('Creating an an empty database as "{}"'.format(db_filename))

# create table list of all places where money can lie
crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS money_pots (
        key TEXT PRIMARY KEY,
        description TEXT,
        liquid TEXT
    );
''')

crsr.execute('''
    INSERT INTO money_pots
    VALUES ('KG', 'gemeinsames Konto', 'Yes'),
           ('KE', 'Extrakonto zum gemeinsamen Konto', 'Yes'),
           ('KM', 'Konto Max', 'Yes'),
           ('KP', 'Konto Paul', 'Yes'),
           ('KB', 'Konto Bundesbank', 'Yes'),
           ('KC', 'Consorsbankkonto', 'No'),
           ('BM', 'Bargeld Max', 'Yes'),
           ('BP', 'Bargeld Paul', 'Yes'),
           ('CB', 'Chipkarte Bundesbank', 'Semi'),
           ('CT', 'Chipkarte Trianon', 'Semi'),
           ('CM', 'Chipkarte Mensa Potsdam', 'Semi'),
           ('GM', 'Geldkarte Max', 'Semi'),
           ('SB', 'Schatulle Berlin', 'Yes'),
           ('SF', 'Schatulle Frankfurt', 'Yes');
''')

# create table list of all actions that can be undertaken with funds

crsr.execute('''
    CREATE TABLE IF NOT EXISTS event_types (
        type TEXT PRIMARY KEY,
        description TEXT,
        abbreviation TEXT UNIQUE
    );
''')

crsr.execute('''
    INSERT INTO event_types
    VALUES ('Festsetzung', 'Festsetzen des zu einem Zeitpunkt vorhanden Betrag in einem Geldtopf', 'Fe'),
           ('Kontrolle', 'positive Überprüfung des theoretischen Geldbetrag in einem Geldtopf', 'Ko'),
           ('Differenz', 'Korrektur des theoretischen Geldbetrag in einem Geldtopf auf den realen Wert', 'Di'),
           ('Transfer', 'Übertragung von Geld zwischen zwei Geldtöpfen', 'T'),
           ('Barzahlung', 'bares Bezahlen', 'B'),
           ('Kartenzahlung', 'Zahlen mit Visa oder Girokarte', 'K'),
           ('Bankeinzug', 'Rechnungsbegleichung durch direkten Bankeinzug', 'BE'),
           ('Überweisung', 'Rechnungsbegleichung durch Überweisen', 'U'),
           ('SEPA-Mandat', 'automatische (regelmäßige) Rechnungsbegleichung durch direkten Bankeinzug', 'S'),
           ('Dauerauftrag', 'automatische (regelmäßige) Rechnungsbegleichung durch Dauerauftrag', 'D'),
           ('Einnahme', 'reguläre Geldeinnahme', 'E'),
           ('Geldfund', 'unerwartete Geldeinnahme, z.B. Geldfund', 'GF');
''')

# create table list of all actions that can be undertaken with funds

crsr.execute('''
    CREATE TABLE IF NOT EXISTS budget_pots (
        key TEXT PRIMARY KEY,
        description TEXT,
        type TEXT
    );
''')

crsr.execute('''
    INSERT INTO budget_pots
    VALUES ('L', 'Lebensmittel', NULL),
           ('A', 'Ausgehen Restaurant', NULL),
           ('AE', 'Ausgehen Eis, Cafe', 'A'),
           ('AB', 'Ausgehen Döner, Bistro, ...', 'A'),
           ('AM', 'Mensa, Kantine, Kasino', NULL),
           ('S', 'Langlebige Produkte', NULL),
           ('SK', 'Klamotten', 'S'),
           ('R', 'regelmäßige und budgetierte Ausgaben', NULL),
           ('RM', 'Mietzahlungen', 'R'),
           ('RV', 'Versicherungs- und Vertragsbeträge', 'R'),
           ('RP', 'Pflichtbeiträge', 'R'),
           ('D', 'Driogerieprodukte', NULL),
           ('DA', 'Arzeneimittel','D'), 
           ('M', 'Miscellaneous', NULL),
           ('T', 'Transportkosten','M');
''')

crsr.execute('''
    CREATE TABLE IF NOT EXISTS money_events (
        id INTEGER PRIMARY KEY,
        type TEXT,
        description TEXT NOT NULL,
        creation_date TEXT NOT NULL,
        modification_dates BLOB,
        comments TEXT,
        complete TEXT,
        FOREIGN KEY (type) REFERENCES event_types (type)
    );
''')

crsr.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER,
        money_pot TEXT,
        amount REAL,
        additional_description TEXT, 
        modification_dates BLOB,
        comments TEXT,
        complete TEXT,
        FOREIGN KEY (id) REFERENCES money_events(id),
        FOREIGN KEY (money_pot) REFERENCES money_pots (key)
    );
''')

crsr.execute('''
    CREATE TABLE IF NOT EXISTS budget_events (
        id INTEGER,
        budget_pot TEXT NOT NULL,
        amount REAL NOT NULL,
        additional_description TEXT,
        budget_effect_date TEXT,
        modification_dates BLOB,
        comments TEXT,
        complete TEXT,
        FOREIGN KEY (id) REFERENCES money_events (id)
        FOREIGN KEY (budget_pot) REFERENCES budget_pots (key)
    );
''')

db.commit()

print('Completed creating the database scheme. It looks as follows:')

## control setup
display(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", db))

crsr = db.cursor()
crsr.execute("SELECT name FROM sqlite_master WHERE type='table';")
for table in crsr.fetchall() :
    print('The table {}: '.format(table[0]))
    display(pd.read_sql_query('SELECT * FROM {};'.format(table[0]), db))

db.close()
