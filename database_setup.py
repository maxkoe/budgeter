### ToDo
# Set more things NOT NULL


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

crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS event_types (
        category TEXT,
        type TEXT PRIMARY KEY,
        description TEXT,
        abbreviation TEXT UNIQUE
    );
''')

crsr.execute('''
    INSERT INTO event_types
    VALUES ('Zahlung', 'Barzahlung', 'bares Bezahlen', 'B'),
           ('Zahlung', 'Kartenzahlung', 'Zahlen mit Visa oder Girokarte', 'K'),
           ('Zahlung', 'Überweisung', 'Rechnungsbegleichung durch Überweisen', 'U'),
           ('Zahlung', 'Dauerauftrag', 'automatische (regelmäßige) Rechnungsbegleichung durch Dauerauftrag', 'D'),
           ('Zahlung', 'SEPA-Mandat', 'automatische (regelmäßige) Rechnungsbegleichung durch direkten Bankeinzug', 'S'),
           ('Zahlung', 'Bankeinzug', 'Rechnungsbegleichung durch direkten Bankeinzug', 'BE'),
           ('Transfer', 'Abheben', 'Geldabheben', 'A'),
           ('Transfer', 'Aufladen', 'Aufladen auf eine Chipkarte', 'AU'),
           ('Transfer', 'Kontotransfer', 'Transger von Geld zwischen zwei Konten', 'KT'),
           ('Transfer', 'Bargeldtransfer', 'Transfer von Bargeld zwischen zwei baren Geldtöpfen', 'BT'),
           ('Recieving', 'Einnahme', 'reguläre Geldeinnahme', 'E'),
           ('Recieving', 'Geldfund', 'unerwartete Geldeinnahme, z.B. Geldfund', 'GF');
''')

db.commit()

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

crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS money_events (
        id INTEGER PRIMARY KEY,
        type TEXT,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (type) REFERENCES event_types (type)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER,
        money_pot TEXT,
        amount REAL,
        additional_description TEXT,
        effect_date TEXT, 
        FOREIGN KEY (id) REFERENCES money_events(id),
        FOREIGN KEY (money_pot) REFERENCES money_pots (key)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''CREATE TABLE IF NOT EXISTS recievings (
        id INTEGER,
        money_pot TEXT,
        amount REAL,
        additional_description TEXT,
        budget_effect_date TEXT, 
        FOREIGN KEY (id) REFERENCES money_events(id),
        FOREIGN KEY (money_pot) REFERENCES money_pots (key)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''CREATE TABLE IF NOT EXISTS transfers (
        id INTEGER,
        money_pot_source TEXT,
        money_pot_sink TEXT,
        amount REAL,
        additional_description TEXT,
        effect_date TEXT, 
        FOREIGN KEY (id) REFERENCES money_events(id),
        FOREIGN KEY (money_pot_source) REFERENCES money_pots (key),
        FOREIGN KEY (money_pot_sink) REFERENCES money_pots (key)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS budget_events (
        id INTEGER,
        budget_pot TEXT NOT NULL,
        amount REAL NOT NULL,
        additional_description TEXT,
        budget_effet_date TEXT,
        FOREIGN KEY (id) REFERENCES money_events (id),
        FOREIGN KEY (budget_pot) REFERENCES budget_pots (key)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS event_groups (
        group_id INTEGER PRIMARY KEY,
        description TEXT NOT NULL
    );
''')


crsr.execute('''
    INSERT INTO event_groups(description)
    VALUES ('Miete'),
           ('Haftpflichtversicherung'),
           ('Berufsunfähigkeitsversicherung'),
           ('Rechtsschutzversicherung'),
           ('Strom'),
           ('Vodafone'),
           ('Drillisch Paul'),
           ('Drillisch Max'),
           ('Apple Music Paul'),
           ('Spotify Max'),
           ('Backblaze'),
           ('Semestergebühr Paul'),
           ('Semestergebühr Max'),
           ('Sportjahresgebühr'),
           ('Sport'),
           ('GEW'),
           ('GEZ'),
           ('Miete FFM'),
           ('Probebahncard 100'),
           ('MyBahncard 50 Paul');
''')

crsr.execute('''
    CREATE TABLE IF NOT EXISTS event_in_group (
        group_id INTEGER,
        event_id TEXT UNIQUE,
        FOREIGN KEY (group_id) REFERENCES event_groups (group_id),
        FOREIGN KEY (event_id) REFERENCES money_events (id)
    );
''')

db.commit()

crsr = db.cursor()

crsr.execute('''
    CREATE TABLE IF NOT EXISTS database_event_types (
        type TEXT PRIMARY KEY,
        description TEXT
    );
''')

crsr.execute('''
    INSERT INTO database_event_types
    VALUES ('Erstellung', 'Erstellung eines Eintrages'),
           ('Update', 'Hinzufügen von Information'),
           ('Korrektur', 'Korrigieren eines Eintrages'),
           ('Löschung', 'Löschen eines Eintrages');
''')

crsr.execute('''
    CREATE TABLE IF NOT EXISTS database_events (
        id INTEGER,
        type TEXT,
        date TEXT,
        description TEXT,
        FOREIGN KEY (id) REFERENCES money_events (id),
        FOREIGN KEY (type) REFERENCES database_event_types (type)
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
