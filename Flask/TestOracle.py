from conf.OracleConnection import OracleConnection

Oracle_Connection = OracleConnection.cursor()
Bank_List = Oracle_Connection.execute("select * from bancos").fetchall()

#print(Bank_List)