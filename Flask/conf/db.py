import pyodbc

# Definir los parámetros de conexión
server = 'DESKTOP-LNOKM7P\SQLEXPRESS'
database = 'DesarrolloWeb'
username = 'Banco_DBA'
password = 'Banco_DBA'

# Crear una cadena de conexión
ConnectionString = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Intentar establecer la conexión
try:
    Connection = pyodbc.connect(ConnectionString)
    print("Conexión exitosa a SQL Server")

    # Aquí puedes realizar operaciones en la base de datos

    # Cerrar la conexión cuando hayas terminado
   
except Exception as e:
    print(f"Error al conectar a SQL Server: {str(e)}")
