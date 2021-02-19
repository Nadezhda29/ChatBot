# подключение к БД
driver = 'DRIVER={SQL Server}'
server = 'SERVER=LAPTOP-T5S647EI'
db = 'DATABASE=Students'
user = 'UID=Nadezhda'
password = 'PWD=12345'
tru_conn = 'trusted_connection=yes'
conn_str = ';'.join([driver, server, db, user, password, tru_conn])