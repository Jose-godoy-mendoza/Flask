import pyodbc

# Definir los parámetros de conexión
server = 'DESKTOP-LNOKM7P\SQLEXPRESS'
database = 'DesarrolloWeb'
username = 'Banco_DBA'
password = 'Banco_DBA'

ConnectionString = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'


try:
    Connection = pyodbc.connect(ConnectionString)
    print("Conexión exitosa a SQL Server")

except Exception as e:
    print(f"Error al conectar a SQL Server: {str(e)}")
