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
    Bank_List = Oracle_Connection.execute("select * from bancos").fetchall()
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

@app.post("/api/insert/<Beneficiario><Banco_Beneficiario><Monto><Remitente><Mensaje>", response_model=insert_transaction)
def list(Beneficiario: str, Banco_Beneficiario: str, Monto: str, Remitente: str, Mensaje: str):
    #Current_Date = datetime.now().strftime("%Y%m%d")
    try:
        CurrentDate = "10/10/2023"
        try:
            Oracle_Connection = OracleConnection.cursor()
            GetBankId = str(Oracle_Connection.execute("select idbanco from bancos where nombre='"+str(Banco_Beneficiario)+"'").fetchone()).replace(",","").replace("(","").replace(")","")
            
            print("******----",GetBankId,"----*****")
            Oracle_Connection.execute("insert into transacciones values ('1', '"+Monto+"', '1','"+Beneficiario+"','"+GetBankId+"','" +Remitente+"', '1','"+str(CurrentDate)+"','" +str(Mensaje)+"')")
            OracleConnection.commit()
            print("funciona")
        except cx_Oracle.DatabaseError as e:
            print("Error al ejecutar la consulta de inserción:", e)
        return {"Remitente":Remitente, "Mensaje":Mensaje}
    except ValidationError as exc:
        print(repr(exc.errors()[0]['type']))