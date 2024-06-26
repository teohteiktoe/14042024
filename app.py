from flask import Flask, request, render_template
import datetime
import sqlite3
from flask import Markup
import replicate
import os
from flask import redirect
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

app = Flask(__name__)

dashboard = Dash(__name__, server=app, url_base_pathname="/dash/", external_stylesheets=[dbc.themes.CYBORG])
dashboard.layout = html.Div(
        [
            html.Div(id='live-update-text'),
            dcc.Interval(id='interval-component')
        ],
        style={"display":"flex", "justify-content": "center", "align-items": "center"}
)

name_flag = 0
name=""

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    global name_flag,name
    if name_flag==0:
        name = request.form.get("name")
        name_flag=1
        conn = sqlite3.connect("log.db")
        c = conn.cursor()
        timestamp = datetime.datetime.now()
        c.execute("insert into employee (name,timestamp) values(?,?)",(name,timestamp))
        conn.commit()
        c.close()
        conn.close()
    return(render_template("main.html",name=name))

@app.route("/ethical_test",methods=["GET","POST"])
def ethical_test():
    return(render_template("ethical_test.html"))

@app.route("/query",methods=["GET","POST"])
def query():
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("select * from employee")
    r=""
    for row in c:
        r=r+str(row)+"<br>"
    print(r)
    r = Markup(r)
    c.close()
    conn.close()
    return(render_template("query.html",r=r))

@app.route("/delete",methods=["GET","POST"])
def delete():
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("delete from employee;")
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete.html"))

@app.route("/answer",methods=["GET","POST"])
def answer():
    ans = request.form["options"]
    print(ans)
    if ans == "true":
        return(render_template("wrong.html"))
    else:
        return(render_template("correct.html"))

@app.route("/food_exp",methods=["GET","POST"])
def food_exp():
    return(render_template("food_exp.html"))

@app.route("/prediction",methods=["GET","POST"])
def prediction():
    print("prediction")
    income = float(request.form.get("income"))
    print(income)
    return(render_template("prediction.html",r=(income * 0.485)+147))

@app.route("/music",methods=["GET","POST"])
def music():
    return(render_template("music.html"))

@app.route("/music_generator",methods=["GET","POST"])
def music_generator():
    q = request.form.get("q")
    r = replicate.run(
        "meta/musicgen:7be0f12c54a8d033a0fbd14418c9af98962da9a86f5ff7811f9b3423a1f0b7d7",
        input={
            "prompt": q,
            "duration" : 5
        }
    )
    return(render_template("music_generator.html",r=r))

@app.route('/dashboard',methods=["GET","POST"])
def dashboard():
  return redirect('/dash')


@callback(Output('live-update-text', 'children'),
          Input('interval-component', 'n_intervals'))
def update_metrics(n):

  conn = sqlite3.connect(
      "log.db")
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM employee")
  count = cursor.fetchone()[0]
  cursor.close()
  conn.close()
  return [
        dbc.Card(
            dbc.CardBody([
                 html.H2("Name Count {0}".format(count)),
            ]),
        ),
        html.Br(),
        dbc.Button(
            "Go Back", id="back", className="back", external_link=True, href="/main",
        ),
    ]

@app.route("/end",methods=["GET","POST"])
def end():
    return(render_template("end.html"))

if __name__ == "__main__":
    app.run()

