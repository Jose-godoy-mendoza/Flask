from fastapi import FastAPI, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask_cors import CORS
from conf.db import Connection
from starlette.status import HTTP_400_BAD_REQUEST
from pydantic import BaseModel


class Draw_Menu(BaseModel):
    Username: str
    Menu: str


app = FastAPI()


@app.get("/")
def Index():
    return {"prueba": "test"}


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
    

