from flask import Flask
from flask import render_template, session, request, redirect
from conf.db import Connection

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'random'

@app.route("/")
def Index():
    return render_template("Login.html")

@app.route("/Login", methods=["post"])
def Login():
    Username = request.form["username"]
    Password = request.form["password"]
    SQLConnection = Connection.cursor()
    SQLResult = SQLConnection.execute("select * from Users where  Username ='"+Username+"' and password = '"+Password+"';").fetchone()
    Message = ""

    if SQLResult is not None:
        Message = "Bienvenido"
        session["IdRol"] = SQLResult[3]
        return redirect("Menu")
    else:
        Message = "Error"
    SQLConnection.close()
    return render_template("Login.html", msg = Message)

@app.route("/Menu")
def Menu():
    IdRol = session.get("IdRol")

    SQLConnection = Connection.cursor()

    HTMLString = "<nav><ul>"
    SQLResult = SQLConnection.execute("select * from Menu where  IdMenuPadre = 0 and IdRol ='"+ str(IdRol)+"';").fetchall()
    for Menu in SQLResult:
        idPadre = Menu[0]
        HTMLString+="<li class=\"liPadre\"><a href=\""+Menu[3]+"\">"+Menu[1]+"</a>"
        Menus = SQLConnection.execute("select * from Menu where  IdMenuPadre ='"+str(idPadre)+"' and IdRol ='"+ str(IdRol) + "';").fetchall()

        HTMLString+="<ul>"
        for SubMenu in Menus:
            HTMLString += "<li><a href=\""+SubMenu[3]+"\">"+SubMenu[1]+"</a></li>"
            print(SubMenu)

        HTMLString +="</ul>\n</li>"
    HTMLString+="<li><a href=\"/salir\">Salir</a></li>"    
    HTMLString +="</ul></nav>"


    return render_template("testindex.html", pintar = HTMLString)

@app.route("/salir")
def Exit():
    session.clear()
    return redirect("/")


@app.route("/caja")
def caja():
    return render_template("cajas.html")



if __name__ == "__main__":
    app.run(debug=True)