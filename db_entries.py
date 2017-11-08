import sqlite3 as sql

# we only need the function datetime.datetime.now; we can now reference it as 
# dt.now
from datetime import datetime as dt

def none_to_null(s = None) :
    if s is None :
        return "Null"
    else :
        return '"{}"'.format(s)

###############################################################################
# Generate an id for a db entry                                               #
###############################################################################

def generate_id(db, date) :
    '''Generate a new unique ID in the budgeter on the database. An ID is an 
    integer with 8 digits, where the first digit are based on the date and the 
    last two digits are a serial number.

    Keyword arguments:
        db   -- the database the id is generated for
        date -- the date on which the ID should be based

    Example: 
        If date==DateTime('2017-08-17') and the database contains the IDs 
        2017081701, 2017081702, 2017081703 and 2017081705, then the id 
        2017081704 is returned.

    Exceptions:
        IndexError - if all 99 possible serial numbers (01-99) have already 
                     been distributed.

        N.B. Could also Except, if the Database Call raises an exception.
    '''
    date_int = int(date.strftime('%Y%m%d00'))
    crsr = db.cursor()
    crsr.execute('SELECT id FROM money_events WHERE id BETWEEN ' +
                 '{} AND {}'.format(date_int, date_int + 99))
    results = [row[0] for row in crsr.fetchall()]

    current_id = date_int + 1
    while current_id in results :
        current_id += 1
    if current_id > date_int + 99 :
        raise IndexError(
            'Encountered to many ids for the date {}'.format(date))

    return current_id
###############################################################################
# Create related db entries from data                                         #
###############################################################################

def create_money_event(db, event_type, description, date) :
    the_id = generate_id(db, date)
    crsr = db.cursor() 
    crsr.execute('INSERT INTO money_events VALUES '
                 '({}, "{}", "{}", "{}");'.format(the_id, event_type, 
                                                  description, date))
    db.commit()
    return the_id

def add_database_event(db, the_id, comment, entry_type = 'Erstellung') :
    crsr = db.cursor()
    crsr.execute(
        'INSERT INTO database_events VALUES ({}, "{}", "{}", "{}");'.format(
            the_id, entry_type, dt.now().strftime('%Y-%m-%d'), comment))
    db.commit()

def add_budget_event(db, the_id, budget_pot, amount, additional_descr = None, 
                     budget_effect_date = None) :
    crsr = db.cursor() 
    crsr.execute('INSERT INTO budget_events VALUES ' +
                 '({}, "{}", {}, {}, {});'.format(
                     the_id, budget_pot, amount, none_to_null(additional_descr),
                     none_to_null(budget_effect_date)))
    db.commit()


def put_budget_event_into_database(
        db, date, description, amount, budget_pot, comment, given_id = None, 
        event_type = None) :

    if given_id is None :
        if event_type is None :
            raise ValueError('If no id is provided it is assumed, that a ' +
                             'money event has to be created. In this case ' +
                             'an event_type must be supplied.')
        given_id = create_money_event(db, event_type, description, date)

    add_budget_event(db, given_id, budget_pot, amount)
    add_database_event(db, given_id, comment)

    return the_id

def add_payment(db, the_id, money_pot, amount, 
                additional_descr = None, effect_date = None) :
    crsr = db.cursor() 
    crsr.execute( 'INSERT INTO payments VALUES ({}, "{}", {}, {}, {});'.format(
            the_id, money_pot, amount, none_to_null(additional_descr),
            none_to_null(effect_date)))
    db.commit()
        
def put_payment_into_database(
        db, date, description, amount, money_pot, 
        comment, given_id = None, event_type = None, budget_pot = None) :
    if given_id is None :
        if event_type is None :
            raise ValueError('If no id is provided it is assumed, that a ' +
                             'money event has to be created. In this case ' +
                             'an event_type must be supplied.')
        given_id = create_money_event(db, event_type, description, date)

    add_payment(db, given_id, money_pot, amount) 

    if budget_pot is not None :
        add_budget_event(db, given_id, budget_pot, amount)

    add_database_event(db, given_id, comment)

    return the_id

def add_transfer(db, the_id, money_pot_source, money_pot_sink, amount, 
                 additional_descr = None, effect_date = None) :
    crsr = db.cursor() 
    crsr.execute('INSERT INTO payments VALUES ' + 
                 '({}, "{}", "{}", {}, {}, {});'.format(
                     the_id, money_pot_source, money_pot_sink, amount, 
                     none_to_null(additional_descr), none_to_null(effect_date)))
    db.commit()

def add_recieving(db, the_id, money_pot, amount, 
                 additional_descr = None, effect_date = None) :
    crsr = db.cursor() 
    crsr.execute('INSERT INTO recievings VALUES ({}, "{}", {}, {}, {});'.format(
        the_id, money_pot, amount, none_to_null(additional_descr),
        none_to_null(effect_date)))
    db.commit()

def put_transfer_into_database(
        db, date, description, amount, money_pot_source, money_pot_sink, comment, 
        effect_date = None, given_id = None, event_type = None) :
    if given_id is None :
        if event_type is None :
            raise ValueError('If no id is provided it is assumed, that a ' +
                             'money event has to be created. In this case ' +
                             'an event_type must be supplied.')
        given_id = create_money_event(db, event_type, description, date)

    add_transfer(db, given_id, money_pot_source, money_pot_sink, amount,
                 effect_date=effect_date) 
    add_database_event(db, given_id, comment)

    return the_id
