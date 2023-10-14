import cx_Oracle
from datetime import datetime


#try:
#    OracleConnection = cx_Oracle.connect(
#        user = 'Banco_DBA',
#        password = 'Banco_DBA',
#        dsn = 'localhost/xe',
#        encoding = 'UTF-8'
#    )
#    print("Connectado a Oracle, version: ", OracleConnection.version)
#except Exception as ex:
#    print(ex)

try:
    OracleConnection = cx_Oracle.connect(user='Banco_DBA', password='Banco_DBA', dsn='localhost/xe')
    print("Conexión exitosa a Oracle")

except Exception as e:
    print(f"Error al conectar a Oracle: {str(e)}")

Oracle_Connection = OracleConnection.cursor()
#Oracle_Connection.execute("insert into Bancos values (14, 'asdfasfsd')")
#OracleConnection.commit()
#Current_Date = datetime.now().strftime("%d%m%Y")
#print(Current_Date)
#Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - 10 WHERE idcuenta = 102030")
#OracleConnection.commit()
