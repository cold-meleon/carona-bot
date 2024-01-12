import sqlite3 
import numpy as np

paid_status =   "PAID"
pending_status = "PENDING"

# SCHEDULE TABLE
CREATE_TABLE_SCHEDULE = """CREATE TABLE schedule (
                            chat_id INT,
                            message_times TEXT
                            );"""
INSERT_TRAVEL_TIMES = """INSERT INTO schedule (
                            chat_id,
                            message_times
                            ) VALUES (?, ?);"""
GET_MESSAGE_TIMES = "SELECT * FROM schedule WHERE chat_id = ?;"
DELETE_CHAT_SCHEDULE = "DELETE FROM schedule WHERE chat_id = ?;"

# CARONAS TABLE
CREATE_TABLE_CARONAS = """CREATE TABLE caronas (
                           chat_id INT,
                           user_id INT,
                           first_name TEXT,
                           last_name TEXT,
                           date TEXT,
                           num_caronas INT,
                           status TEXT
                           );"""
INSERT_CARONA = """INSERT INTO caronas (
                            chat_id,
                            user_id,
                            first_name,
                            last_name,
                            date,
                            num_caronas,
                            status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?);"""
GET_CARONA_BY_NAME = "SELECT * FROM caronas WHERE chat_id = ? AND user_id = ? AND status = ?;"                            
GET_CARONA_BY_DATE = "SELECT * FROM caronas WHERE chat_id = ? AND date = ? AND status = ?;"
DELETE_CARONA_BY_USER = "DELETE FROM caronas WHERE chat_id = ? AND user_id = ? AND status = ?;"
UPDATE_CARONA_STATUS_BY_USER = f"""UPDATE caronas 
                                SET status = \"{paid_status}\", num_caronas = 0
                                WHERE status = \"{pending_status}\" AND chat_id = ? AND user_id = ?;"""
GET_ALL_USERS = "SELECT * FROM caronas WHERE chat_id = ? AND status = ?;"  

# DATABASES
CARONAS = "caronas.db"
SCHEDULE = "schedule.db"


# GLOBAL DATABASE FUNCTIONS
def connect(database):
    return sqlite3.connect(database)

def create_tables(connection, cursor, table_format):
    with connection:
        cursor.execute(table_format)



# SCHEDULE DATABASE FUNCTIONS
def add_schedule(connection, cursor, chat_id, message_times):
    with connection:
        cursor.execute(INSERT_TRAVEL_TIMES, (chat_id, message_times))

def get_chat_schedule(connection, cursor, chat_id):
    with connection:
        return cursor.execute(GET_MESSAGE_TIMES, (chat_id,)).fetchall()

def remove_chat_schedule(connection, cursor, chat_id):
    with connection:
        cursor.execute(DELETE_CHAT_SCHEDULE, (chat_id,))

def update_chat_schedule(connection, cursor, chat_id, message_times):
    remove_chat_schedule(connection, cursor, chat_id)
    add_schedule(connection, cursor, chat_id, message_times)


# CARONAS DATABASE FUNCTIONS
def add_carona(connection, cursor, chat_id, user_id, first_name, last_name, date, num_caronas=1, status=paid_status):
    with connection:
        cursor.execute(INSERT_CARONA, (chat_id, user_id, first_name, last_name, date, num_caronas, status))
        
def get_carona_by_user(connection, cursor, chat_id, user_id, status):
    with connection:
        return cursor.execute(GET_CARONA_BY_NAME, (chat_id, user_id, status)).fetchall()
        
def get_carona_by_date(connection, cursor, chat_id, date, status):
    with connection:
        return cursor.execute(GET_CARONA_BY_DATE, (chat_id, date, status)).fetchall()

def update_user_caronas_status(connection, cursor, chat_id, user_id):
    with connection:
        cursor.execute(UPDATE_CARONA_STATUS_BY_USER, (chat_id, user_id))

def remove_user_caronas(connection, cursor, chat_id, user_id, status):
    with connection:
        cursor.execute(DELETE_CARONA_BY_USER, (chat_id, user_id, status))

# returns a dict such as:  user_id : [first_name, last_name]
def get_carona_users(connection, cursor, chat_id, status=pending_status):
    users_dict = {}
    # data posistion in the tuple
    user_id = 1
    first_name = 2
    last_name = 3
    with connection:
        all_items = cursor.execute(GET_ALL_USERS, (chat_id, status)).fetchall()
        for item in all_items:
            users_dict[item[user_id]] = [item[first_name], item[last_name]]
        return users_dict
            
            



# CODE TESTING
        
conn = connect(CARONAS)
c = conn.cursor()
# create_tables(conn, c, CREATE_TABLE_SCHEDULE)

# add_schedule(conn, c, '2083012766', "20h30,16h00")
# print(get_chat_schedule(conn, c, '2083012766'))


# add_carona(conn, c, '2083012766', '2083012766', 'Pedro', 'Schnarndorf', '11/01/24 15:38:10', 1, pending_status)
# add_carona(conn, c, '2083012766', '2083012766', 'Y', 'TESTE', '11/01/24 15:38:10', 1, paid_status)
# add_carona(conn, c, '2083012766', '2083012765', 'Z', 'TESTE', '11/01/24 15:38:10', 1, pending_status)
# print(get_carona_by_user(conn, c, '2083012766', '2083012766', pending_status))

# print(get_carona_by_date(connection, c, '2083012766', '11/01/24 15:38:10'))
# remove_user_caronas(connection, c, '2083012766', '2083012766')

# update_user_caronas_status(conn, c, '2083012766', '2083012766')
# print(get_carona_by_user(conn, c, '2083012766', '2083012766', paid_status))
print(get_carona_users(conn, c, '2083012766', pending_status))

