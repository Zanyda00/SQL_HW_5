import psycopg2
from config import database, user, password


def create_database_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(30) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(80) UNIQUE NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
            phone_id SERIAL PRIMARY KEY,
            phone_number VARCHAR(30) UNIQUE,
            client_id INTEGER NOT NULL REFERENCES client(client_id)
        );
        """)
    conn.commit()


def add_new_client(conn, first_name, last_name, email, phone_number=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client (first_name, last_name, email) VALUES(%s, %s, %s) RETURNING client_id;
        """, (first_name, last_name, email))
        id = cur.fetchone()[0]
        if phone_number is not None:
            cur.execute("""
            INSERT INTO phone (phone_number, client_id) VALUES(%s, %s);
            """, (phone_number, id))
        else:
            print(f'Клиент с ID {id} не предоставил номер телефона')
    conn.commit()


def droptable(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE phone;
        DROP TABLE client;
        """)
    conn.commit()


def add_phone_number(conn, phone_number, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phone (phone_number, client_id) VALUES(%s, %s);
        """, (phone_number, client_id))
    conn.commit()


def change_data_client(conn, client_id, fist_name=None, last_name=None, email=None, phone_number=None):
    with conn.cursor() as cur:
        if fist_name is not None:
            cur.execute("""UPDATE client SET first_name=%s WHERE client_id=%s;""", (fist_name,client_id))
            print(f'Информация об имени клиента с ID: {client_id} изменена')
        if last_name is not None:
            cur.execute("""UPDATE client SET last_name=%s WHERE client_id=%s;""", (last_name, client_id))
            print(f'Информация о фамилии клиента с ID: {client_id} изменена')
        if email is not None:
            cur.execute("""UPDATE client SET email=%s WHERE client_id=%s;""", (email, client_id))
            print(f'Информация об электронной почте клиента с ID: {client_id} изменена')
        if phone_number is not None:
            cur.execute("""SELECT COUNT(phone_number) FROM phone WHERE client_id=%s;""", (client_id,))
            quantity = cur.fetchone()[0]
            if quantity == 0:
                cur.execute("""
                            INSERT INTO phone (phone_number, client_id) VALUES(%s, %s);
                            """, (phone_number, client_id))
            else:
                cur.execute("""SELECT phone_id, phone_number FROM phone WHERE client_id=%s;""",(client_id,))
                print('Выберите ID номера телефона который хотите изменить')
                for i in cur.fetchall():
                    print(f'ID: {i[0]}, Номер телефона: {i[1]}')
                phone_id = int(input('Введите ID: '))
                cur.execute("""UPDATE phone SET phone_number=%s WHERE phone_id=%s;""", (phone_number, phone_id))
                print(f'Информация о номере телефона клиента с ID: {client_id} изменена')
    conn.commit()


def delet_phone_number(conn, phone_number, client_id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone WHERE phone_number=%s AND client_id=%s;""",(phone_number,client_id))
    conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phone WHERE client_id=%s;""", (client_id,))
        cur.execute("""DELETE FROM client WHERE client_id=%s;""",(client_id,))
    conn.commit()
    print()
    print('Вся информация о клиенте удалена')
    print()



def find_client(conn, first_name=None, last_name=None, email=None, phone_number=None):
    with conn.cursor() as cur:
        if first_name is not None:
            cur.execute("""SELECT * FROM client WHERE first_name=%s;""",(first_name,))
            data_client = cur.fetchone()
            print(f'По имени ({first_name}) найден клиент:')
        if last_name is not None:
            cur.execute("""SELECT * FROM client WHERE last_name=%s;""",(last_name,))
            data_client = cur.fetchone()
            print(f'По фамилии ({last_name}) найден клиент:')
        if email is not None:
            cur.execute("""SELECT * FROM client WHERE email=%s;""",(email,))
            data_client = cur.fetchone()
            print(f'По электроной почте ({email}) найден клиент:')
        if phone_number is not None:
            cur.execute("""SELECT client_id FROM phone WHERE phone_number=%s;""",(phone_number,))
            client_id = cur.fetchone()[0]
            cur.execute("""SELECT * FROM client WHERE client_id=%s;""",(client_id,))
            data_client = cur.fetchone()
            print(f'По номеру ({phone_number}) найден клиент:')
        print(f'ID: {data_client[0]}, Имя: {data_client[1]}, Фамилия: {data_client[2]}, email: {data_client[3]}')
    conn.commit()

with psycopg2.connect(database=database, user=user, password=password ) as conn:
    droptable(conn)
    create_database_table(conn)
    add_new_client(conn, 'Вась', 'Вась', 'вась@вась.com', '+11111111')
    add_new_client(conn, 'Петь', 'Петь', 'петь@петь.com')
    add_new_client(conn, 'Лёнь', 'Лёнь', 'лёнь@лёнь.com', '+22222222')
    add_new_client(conn, 'Жень', 'Жень', 'жень@жень.com', '+99999999')
    add_phone_number(conn, '+33333333', 1)
    add_phone_number(conn, '+44444444', 1)
    add_phone_number(conn, '+55555555', 3)
    change_data_client(conn, 2, email='ПЕТЬ@ПЕТЬ.ru')
    change_data_client(conn, 1, phone_number='+12345678')
    change_data_client(conn,4, 'Евгений', 'Евгеньевич' )
    delet_phone_number(conn, '+11111111', 1)
    delete_client(conn, 3)
    find_client(conn, phone_number='+33333333')
    find_client(conn, email='ПЕТЬ@ПЕТЬ.ru')

conn.close()

