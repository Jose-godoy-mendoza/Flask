import cx_Oracle

try:
    OracleConnection = cx_Oracle.connect(
        user = 'Banco_DBA',
        password = 'Banco_DBA',
        dsn = 'localhost/xe',
        encoding = 'UTF-8'
    )
    print("Connectado a Oracle, version: ", OracleConnection.version)
except Exception as ex:
    print(ex)


test = OracleConnection.cursor()
test.execute('select * from Bancos')
result = test.fetchall()
print(result)
test.close()
OracleConnection.close()