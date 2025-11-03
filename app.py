#!/usr/bin/env python
# Noemie Baudouin

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)


def edad_es_valido(edad):
    if edad == "":
        return ""
    try:
        edad = int(edad)
        if edad > 0 and int(edad) < 150:
            return ""
        return "Edad inválida"
    except ValueError:
        return "Edad corrupta"


@app.route("/borrar", methods=["GET", "POST"])
def borrar():
    borrar_id = request.form.get("borrar_id")
    # si recibe una peticion de borrar
    if borrar_id:
        with sqlite3.connect("users.db") as con:
            con.execute(
                "DELETE FROM usuarios WHERE id = ?",
                (borrar_id,),
            )
    mensaje = f"Usuario con ID {borrar_id} borrado!"
    return redirect(url_for("index", mensaje=mensaje))


@app.route("/modificar", methods=["GET", "POST"])
def modificar():
    modificar_id = request.form.get("modificar_id")
    # si recibe una peticion de modificar
    if modificar_id:
        with sqlite3.connect("users.db") as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM usuarios ORDER BY id DESC").fetchall()
            row_modificar = con.execute(
                f"SELECT * FROM usuarios WHERE id = ?",
                (modificar_id,),
            ).fetchone()

    return render_template("modificar.html", usuarios=rows, row_modificar=row_modificar)


@app.route("/hora_entrada", methods=["GET", "POST"])
def hora_entrada():
    dt = datetime.datetime.now()
    hora = dt.strftime("%H:%M:%S")
    entrada_id = request.form.get("entrada_id")
    # si recibe una peticion de fichar hora de entrada
    if entrada_id:
        with sqlite3.connect("users.db") as con:
            con.execute(
                "UPDATE usuarios SET entrada = ? WHERE id = ?",
                (hora, entrada_id),
            )
    mensaje = f"Usuario con ID {entrada_id} entrado!"
    return redirect(url_for("index", mensaje=mensaje))


@app.route("/hora_salida", methods=["GET", "POST"])
def hora_salida():
    dt = datetime.datetime.now()
    hora = dt.strftime("%H:%M:%S")
    salida_id = request.form.get("salida_id")
    # si recibe una peticion de fichar hora de salida
    if salida_id:
        with sqlite3.connect("users.db") as con:
            con.execute(
                "UPDATE usuarios SET salida = ? WHERE id = ?",
                (hora, salida_id),
            )
    mensaje = f"Usuario con ID {salida_id} salido!"
    return redirect(url_for("index", mensaje=mensaje))


@app.route("/", methods=["GET", "POST"])
def index():
    # crear la tabla de usuarios
    with sqlite3.connect("users.db") as con:
        con.executescript(
            """
                    PRAGMA foreign_keys = ON;

                    CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre NOT NULL,
                    email VARCHAR NOT NULL,
                    edad INTEGER,
                    entrada TEXT,
                    salida TEXT
                    );
        """
        )

    error = ""
    mensaje = ""
    # si recibe un mensaje, almacenarlo en una variable
    if request.method == "GET" and request.args.get("mensaje"):
        mensaje = request.args.get("mensaje")

    # si recibe un formulario de modificacion
    elif request.method == "POST" and request.form.get("id_modificar"):
        id_modificar = request.form.get("id_modificar")
        nombre_modificar = request.form.get("nombre_modificar")
        email_modificar = request.form.get("email_modificar")
        edad_modificar = request.form.get("edad_modificar")

        # para una mejor experiencia, quedarse en la pagina principal y hacer las verificaciones
        if edad_modificar:
            error = edad_es_valido(edad_modificar)
        if error == "":
            # permitir las modificaciones parciales
            if not nombre_modificar:
                with sqlite3.connect("users.db") as con:
                    nombre_modificar = con.execute(
                        "SELECT nombre FROM usuarios WHERE id = ?",
                        (id_modificar,),
                    ).fetchone()[0]
            if not email_modificar:
                with sqlite3.connect("users.db") as con:
                    email_modificar = con.execute(
                        "SELECT email FROM usuarios WHERE id = ?",
                        (id_modificar,),
                    ).fetchone()[0]
            if not edad_modificar:
                with sqlite3.connect("users.db") as con:
                    edad_modificar = con.execute(
                        "SELECT edad FROM usuarios WHERE id = ?",
                        (id_modificar,),
                    ).fetchone()[0]
            with sqlite3.connect("users.db") as con:
                con.execute(
                    "UPDATE usuarios SET (nombre, email, edad) = (?, ?, ?) WHERE id = ?",
                    (nombre_modificar, email_modificar, edad_modificar, id_modificar),
                )
            mensaje = f"Usuario con ID {id_modificar} modificado!"

    # si recibe un formulario de ingreso
    elif request.method == "POST" and not request.form.get("borrar_id"):
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        edad = request.form.get("edad")
        # verificaciones de integridad de datos
        if edad:
            error = edad_es_valido(edad)
        if not nombre and not email:
            error = "Faltan el nombre y el email también"
        elif not nombre:
            error = "Falta el nombre"
        elif not email:
            error = "Falta el email"
        elif error == "":
            with sqlite3.connect("users.db") as con:
                con.execute(
                    "INSERT INTO usuarios (nombre, email, edad) VALUES (?, ?, ?)",
                    (nombre, email, edad),
                )
            error = "Usuario registrado"
            return redirect("/")

    # en todos casos
    with sqlite3.connect("users.db") as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT * FROM usuarios ORDER BY id DESC").fetchall()
    return render_template("index.html", usuarios=rows, mensaje=mensaje, error=error)


# abrir con Flask si app.py llamada directamente
if __name__ == "__main__":
    app.run(debug=True)
