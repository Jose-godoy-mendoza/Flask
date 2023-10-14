from fastapi import FastAPI, Response, Form
from werkzeug.security import generate_password_hash, check_password_hash
#from datetime import timedelta
#from flask_cors import CORS
from conf.db import Connection
from conf.OracleConnection import OracleConnection
from starlette.status import HTTP_400_BAD_REQUEST
from pydantic import BaseModel, ValidationError
from datetime import datetime
import cx_Oracle



class Draw_Menu(BaseModel):
    Username: str
    Menu: str

class insert_transaction(BaseModel):
    #Beneficiario: str
    #Banco_Beneficiario: str
    #Monto: str
    Remitente: str
    Mensaje: str

class Delete_Transactions(BaseModel):
    IdTransaccion: str


class Insert_Bank(BaseModel):
    IdBank:str
    BankName:str

app = FastAPI()


@app.get("/")
def Index():
    return {"Pagina inicial": "index"}


@app.get("/api/prueba/<Username><Password>", response_model=Draw_Menu)
def Login(Username:str, Password:str):
    SQLConnection = Connection.cursor()
    GetRol = SQLConnection.execute("select * from Users where  Username ='"+Username+"';").fetchone()
    JPassword = GetRol[2]

    if GetRol is not None:
        if check_password_hash(JPassword, Password):
            print(JPassword)
            SQLConnection = Connection.cursor()

            HTMLString = "<nav><ul>"
            SQLResult = SQLConnection.execute("select * from Menu where  IdMenuPadre = 0 and IdRol ='"+ str(GetRol[3])+"';").fetchall()
            for Menu in SQLResult:
                idPadre = Menu[0]
                HTMLString+="<li class=\"liPadre\"><a href=\""+Menu[3]+"\">"+Menu[1]+"</a>"
                Menus = SQLConnection.execute("select * from Menu where  IdMenuPadre ='"+str(idPadre)+"' and IdRol ='"+ str(GetRol[3]) + "';").fetchall()

                HTMLString+="<ul>"
                for SubMenu in Menus:
                    HTMLString += "<li><a href=\""+SubMenu[3]+"\">"+SubMenu[1]+"</a></li>"
                    print(SubMenu)

                HTMLString +="</ul>\n</li>"
            HTMLString+="<li><a href=\"/salir\">Salir</a></li>"    
            HTMLString +="</ul></nav>"
            SQLConnection.close()
            return {"Username" : GetRol[1], "Menu":HTMLString}
        else:
            SQLConnection.close()
            return Response(status_code=HTTP_400_BAD_REQUEST) 
    else:
        SQLConnection.close()
        return Response(status_code=HTTP_400_BAD_REQUEST) 
    

@app.get("/list")
def list():
    Oracle_Connection = OracleConnection.cursor()
    Bank_List = Oracle_Connection.execute("select * from bancos ORDER BY IdBanco").fetchall()
    #print(Bank_List)
    HTMLString=""
    DropDown_Banks = ""
    if Bank_List is not None:
        
        for Banks in Bank_List:
            HTMLString+= "<tr>"
            HTMLString+="<td>"+str(Banks[0])+"</td>"
            HTMLString+="<td>"+Banks[1]+"</td>"
            HTMLString +="<td> <a class=\"btn btn-success\">Edit</a> | <a class=\"btn btn-danger\">Delete</a> </td>"
            HTMLString +="</tr>"

            DropDown_Banks += "<option>"+Banks[1]+"</option>"
            
        Oracle_Connection.close()
        return {"Id" : Banks[0], "Bank_List":HTMLString, "DropDown_Banks":DropDown_Banks}
    else:
        Oracle_Connection.close()
        return Response(status_code=HTTP_400_BAD_REQUEST)
    
@app.post("/api/insert_bank/<IdBank><BankName>", response_model=Insert_Bank)
def Insert_Bank(IdBank:str, BankName:str):
    try:
        Oracle_Connection = OracleConnection.cursor()
        Oracle_Connection.execute("insert into Bancos values ("+IdBank+", '"+BankName+"')")
        OracleConnection.commit()
    except cx_Oracle.DatabaseError as e:
        print("Error al ejecutar la consulta de inserción:", e)
    return {"IdBank":IdBank, "BankName":BankName}


@app.delete("/api/delete_Bancos/<IdBanco>")
def Delete_Bank(IdBanco:str):
    try:
        Oracle_Connection = OracleConnection.cursor()
        Oracle_Connection.execute("delete from Bancos where IdBanco= '"+IdBanco+"'")
        OracleConnection.commit()
    except cx_Oracle.DatabaseError as e:
        print("Error al ejecutar la consulta de delete:", e)


@app.post("/api/update_bancos/<IdBanco><Nombre>")
def Update_Bank(IdBanco:str, Nombre:str):
    try:
        Oracle_Connection = OracleConnection.cursor()
        Oracle_Connection.execute("update bancos set nombre = '"+Nombre+"' where idbanco= '"+IdBanco+"'")
        OracleConnection.commit()
    except cx_Oracle.DatabaseError as e:
        print("Error al ejecutar la consulta de delete:", e)


@app.post("/api/insert/<Beneficiario><Banco_Beneficiario><Monto><Remitente><Mensaje>", response_model=insert_transaction)
def list(Beneficiario: str, Banco_Beneficiario: str, Monto: str, Remitente: str, Mensaje: str):
    CurrentDate = datetime.now().strftime("%d%m%Y")
    try:
        #CurrentDate = "10/10/2023"
        try:
            Oracle_Connection = OracleConnection.cursor()
            GetBankId = str(Oracle_Connection.execute("select idbanco from bancos where nombre='"+str(Banco_Beneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            Bank_Account = str(Oracle_Connection.execute("select idbanco from cuentas where idcuenta='"+str(Beneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetSaldoRemitente = str(Oracle_Connection.execute("select saldo from cuentas where idcuenta='"+str(Remitente)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            print("Remitente: ",GetSaldoRemitente, " enviado: ", Monto)
            print("*-*-*-*- ",Bank_Account)
            


            if int(GetSaldoRemitente) >= int(Monto):
                print("SI HAY FONDOS SUFIENTES, saldo enviado: ",Monto)
                print("REMITENTE: ",Remitente, " monto a tansferir: ", Monto)
                if str(Beneficiario) != str(Remitente):
                    print("DIFERENTES CUENTAS")
                    if Bank_Account == GetBankId:
                        print("BANCOS COINCIDEN, APROVADO")
                        Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+str(Monto)+" WHERE idcuenta = '"+str(Remitente)+"'")
                        OracleConnection.commit()
                        Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+str(Monto)+" WHERE idcuenta = '"+str(Beneficiario)+"'")
                        OracleConnection.commit()
                        Oracle_Connection.execute("insert into transacciones values ('1', '"+Monto+"', '1','"+Beneficiario+"','"+GetBankId+"','" +Remitente+"', '1','"+str(CurrentDate)+"','" +str(Mensaje)+"')")
                        OracleConnection.commit()
                    else:
                        print("NO COINCIDEN, DENEGADO")
                else:
                    print("NO SE PUEDE TRANSFERIR A LA MISMA CUENTA")
            else:
                print("NO HAY FONDOS, saldo en cuenta: ", GetSaldoRemitente)
                
            
        except cx_Oracle.DatabaseError as e:
            print("Error al ejecutar la consulta de inserción:", e)
        return {"Remitente":Remitente, "Mensaje":Mensaje}
    except ValidationError as exc:
        print(repr(exc.errors()[0]['type']))


@app.get("/api/show_transactions")
def show_transactions():
    Oracle_Connection = OracleConnection.cursor()
    Transaction_list = Oracle_Connection.execute("""
    SELECT transacciones.idtransaccion, tipo_transaccion.Descripcion, transacciones.Cuenta_Beneficiaria, 
    Bancos.Nombre, transacciones.monto, transacciones.idcuenta_remitente, 
    estados.descripcion, transacciones.comentario
    FROM transacciones
    INNER JOIN tipo_transaccion
    ON transacciones.idtipo_transaccion = tipo_transaccion.idtipo_transaccion
    INNER JOIN Bancos
    ON transacciones.IDBANCO_BENEFICIARIO = bancos.idbanco
    INNER JOIN estados
    ON transacciones.IDESTADO = ESTADOS.IDESTADO ORDER BY transacciones.idtransaccion
                                          """).fetchall()
    
    HTMLString=""
    if Transaction_list is not None:
        
        for Trx in Transaction_list:
            HTMLString+= "<tr>"
            HTMLString+="<td>"+str(Trx[0])+"</td>"
            HTMLString+="<td>"+str(Trx[1])+"</td>"
            HTMLString+="<td>"+str(Trx[2])+"</td>"
            HTMLString+="<td>"+str(Trx[3])+"</td>"
            HTMLString+="<td>"+str(Trx[4])+"</td>"
            HTMLString+="<td>"+str(Trx[5])+"</td>"
            HTMLString+="<td>"+str(Trx[6])+"</td>"
            HTMLString+="<td>"+str(Trx[7])+"</td>"
            HTMLString +="<td> <a class=\"btn btn-success\">Edit</a> | <a href=\"/Delete_Transaction\" class=\"btn btn-danger\">Delete</a> </td>"
            HTMLString +="</tr>"            
        Oracle_Connection.close()
        return {"Transactions_List":HTMLString}
    else:
        Oracle_Connection.close()
        return Response(status_code=HTTP_400_BAD_REQUEST)
    

@app.delete("/api/trx_Delete/<IdTransaction>", response_model=Delete_Transactions)
def Delete_Transaction(IdTransaccion:str):
    try:
        Oracle_Connection = OracleConnection.cursor()

        GetBeneficiario = str(Oracle_Connection.execute("select Cuenta_Beneficiaria from Transacciones where IDtransaccion ='"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
        print("BENEFICIARIO: ", GetBeneficiario)
        GetRemitente = str(Oracle_Connection.execute("select IDCUENTA_REMITENTE from Transacciones where IDtransaccion ='"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
        print("remitente: ", GetRemitente)
        GetSaldo_Beneficiario = str(Oracle_Connection.execute("select saldo from cuentas where idcuenta='"+str(GetBeneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
        print("SALDO: ", GetSaldo_Beneficiario)
        GetSaldo_Trx = str(Oracle_Connection.execute("select monto from transacciones where idtransaccion='"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
        print("monto de transaccion", GetSaldo_Trx)
        
        if int(GetSaldo_Beneficiario) >= int(GetSaldo_Trx):
            Oracle_Connection.execute("DELETE FROM transacciones where IdTransaccion='"+str(IdTransaccion)+"'")
            OracleConnection.commit()
            print("COMPLETADO")
            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+GetSaldo_Trx+" WHERE idcuenta = '"+GetBeneficiario+"'")
            OracleConnection.commit()
            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+GetSaldo_Trx+" WHERE idcuenta = '"+GetRemitente+"'")
            OracleConnection.commit()
            
            
            
        else:
            print("NO PODEMOS RETIRAR EL MONTO, CUENTA QUEDARÁ EN NEGATIVO")

    except cx_Oracle.DatabaseError as e:
        print("Error al ejecutar la consulta de delete:", e)
    return {"IdTransaccion":IdTransaccion}


@app.post("/api/Update/<IdTransaccion><Beneficiario><Banco_Beneficiario><Monto><Remitente><Comentario>", response_model=insert_transaction)
def Update(IdTransaccion: str, Beneficiario: str, Banco_Beneficiario: str, Monto: str, Remitente: str, Comentario: str):
    CurrentDate = datetime.now().strftime("%d%m%Y")
    try:
        try:
            Oracle_Connection = OracleConnection.cursor()
            GetOld_AccountBeneficiario = str(Oracle_Connection.execute("select CUENTA_BENEFICIARIA from transacciones where idtransaccion = '"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetOld_BalanceBeneficiario = str(Oracle_Connection.execute("select saldo from cuentas where idcuenta='"+str(GetOld_AccountBeneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetOld_AccountRemitente = str(Oracle_Connection.execute("select IDCUENTA_REMITENTE from transacciones where idtransaccion = '"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetOld_BalanceRemitente = str(Oracle_Connection.execute("select saldo from cuentas where idcuenta='"+str(GetOld_AccountBeneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            
            GetSaldoRemitente = str(Oracle_Connection.execute("select saldo from cuentas where idcuenta='"+str(Remitente)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetOld_TrxAmount = str(Oracle_Connection.execute("select monto from transacciones where idtransaccion='"+str(IdTransaccion)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            
            NewBank_AccountBeneficiario = str(Oracle_Connection.execute("select idbanco from cuentas where idcuenta='"+str(Beneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            GetNew_Bank = str(Oracle_Connection.execute("select idbanco from bancos where nombre='"+str(Banco_Beneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            
            
            print("Old Account: ",GetOld_AccountBeneficiario, " Sent: ", GetOld_TrxAmount)
            print("New Account: ",Beneficiario," new amt: ", Monto)
            AdjustedAmt = 0
            if int(GetOld_TrxAmount) > int(Monto):
                AdjustedAmt = int(GetOld_TrxAmount) - int(Monto)
            elif int(GetOld_TrxAmount) < int(Monto):
                AdjustedAmt = int(Monto) - int(GetOld_TrxAmount)
            else:
                AdjustedAmt = Monto


            if (str(Beneficiario) != str(GetOld_AccountBeneficiario)) or (str(Beneficiario) == str(GetOld_AccountBeneficiario) and GetOld_BalanceBeneficiario != AdjustedAmt):
                print("Diferente beneficiario o diferente cantidad con mismo beneficiario")
                if int(GetOld_BalanceBeneficiario) >= int(AdjustedAmt):
                    print("la cuenta antigua cuenta con balance para reversar la transaccion")
                    if NewBank_AccountBeneficiario == GetNew_Bank:
                        print("Bancos coinciden, podemos seguir")
                        if str(Beneficiario) != str(GetOld_AccountBeneficiario):
                            print("Cantidades iguales o diferentes, diferente beneficiario")
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+str(Monto)+" WHERE idcuenta = '"+str(Beneficiario)+"'")
                            OracleConnection.commit()
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+str(GetOld_TrxAmount)+" WHERE idcuenta = '"+str(GetOld_AccountBeneficiario)+"'")
                            OracleConnection.commit()
                        
                        elif int(Monto) > int(GetOld_TrxAmount):
                            print("new amount is higher that trx amt")
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+str(AdjustedAmt)+" WHERE idcuenta = '"+str(GetOld_AccountBeneficiario)+"'")
                            OracleConnection.commit()
                            
                        elif int(Monto) < int(GetOld_TrxAmount):
                            print("old trx amt mayor")
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+str(AdjustedAmt)+" WHERE idcuenta = '"+str(GetOld_AccountBeneficiario)+"'")
                            OracleConnection.commit()
                        
                        else:
                            print("nada")

                        if str(GetOld_AccountRemitente) != str(Remitente):
                            print("Diferente cuenta remitente")
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+str(GetOld_TrxAmount)+" WHERE idcuenta = '"+str(GetOld_AccountRemitente)+"'")
                            OracleConnection.commit()
                            Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+str(GetOld_TrxAmount)+" WHERE idcuenta = '"+str(Remitente)+"'")
                            OracleConnection.commit()
                        elif (str(GetOld_AccountRemitente) == str(Remitente) and GetOld_BalanceBeneficiario != AdjustedAmt):
                            if int(Monto) > int(GetOld_TrxAmount):
                                print("Misma cuenta pero transfiriendo mas")
                                Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo - "+str(AdjustedAmt)+" WHERE idcuenta = '"+str(GetOld_AccountRemitente)+"'")
                                OracleConnection.commit()
                            elif int(Monto) < int(GetOld_TrxAmount):
                                print("Misma cuenta pero reduciendo transferencia")
                                Oracle_Connection.execute("UPDATE Cuentas SET saldo = saldo + "+str(AdjustedAmt)+" WHERE idcuenta = '"+str(GetOld_AccountRemitente)+"'")
                                OracleConnection.commit()
                            else:
                                print("Misma cantidad")
                        else:
                            print("Misma Cuenta Remitente")
                        Oracle_Connection.execute(""" 
                        UPDATE Transacciones SET Monto ="""+str(Monto)+""", cuenta_beneficiaria = '"""+str(Beneficiario)+"""', 
                        idbanco_beneficiario = """+str(NewBank_AccountBeneficiario)+""", idcuenta_remitente = '"""+str(Remitente)+"""', Fecha = '"""+str(CurrentDate)+"""', 
                        Comentario='"""+str(Comentario)+"""' where idtransaccion = """+str(IdTransaccion)+"""
                        """)
                        OracleConnection.commit()
                    else:
                        print("Bancos no coinciden")
                else:
                    print("Balance insuficiente, no podemos reversar la transaccion")
            else:
                print("Mismo beneficiario")         
            
        except cx_Oracle.DatabaseError as e:
            print("Error al ejecutar la consulta de inserción:", e)
        return {"Remitente":Remitente, "Mensaje":Comentario}
    except ValidationError as exc:
        print(repr(exc.errors()[0]['type']))