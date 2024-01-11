import sqlite3

CREATE_TABLE = """CREATE TABLE caronas (
                           chat_id TEXT,
                           user_id TEXT,
                           date TEXT,
                           num_caronas INT
                           );"""
INSERT_CARONA = """INSERT INTO caronas (
                            chat_id,
                            user_id,
                            date,
                            num_caronas
                            ) VALUES (?, ?, ?, ?);"""
GET_CARONA_BY_NAME = "SELECT * FROM caronas WHERE chat_id = ? AND user_id = ?;"                            
GET_CARONA_BY_DATE = "SELECT * FROM caronas WHERE chat_id = ? AND date = ?;"
DELETE_CARONA_BY_USER = "DELETE FROM caronas WHERE "

def connect():
    return sqlite3.connect("caronas.db")

def create_tables(connection):
    with connection:
        connection.execute(CREATE_TABLE)
        
def add_carona(connection, chat_id, user_id, date, num_caronas):
    with connection:
        connection.execute(INSERT_CARONA, (chat_id, user_id, date, num_caronas))
        
def get_carona_by_user(connection, chat_id ,user_id):
    with connection:
        return connection.execute(GET_CARONA_BY_NAME, (chat_id, user_id)).fetchall()
        
def get_carona_by_date(connection, chat_id, date):
    with connection:
        return connection.execute(GET_CARONA_BY_DATE, (chat_id, date)).fetchall()
    
def remove_user_caronas(connection, chat_id, user_id):
    with connection:
        connection.execute(DELETE_CARONA_BY_USER, (chat_id, user_id))
        
get_carona_by_user(connect, '2083012766', '2083012766')