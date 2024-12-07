
import mysql.connector

from data import inserts, queries
from flask import abort, Flask, redirect, render_template, request

app = Flask(__name__)

myConnection = mysql.connector.connect(
  user = "root",
  password = "password",
  host = "localhost",
  database = "Olympics",
)

cursorObject = myConnection.cursor()

@app.route("/")
def show_home():
  return render_template("home.html")

@app.route("/query")
def show_queries():
  return render_template("queries.html", queries=queries)

@app.route("/query/<int:query_id>")
def show_query(query_id):
  if query_id > len(queries):
    abort(404)

  userInputs = queries[query_id - 1][1]

  for userInput in userInputs:
    if userInput not in request.args or not request.args[userInput]:
      error = "Please make sure to provide values for all inputs."
      return render_template("error.html", error=error)

  values = []
  for i, userInput in enumerate(userInputs):
    values.append(request.args[userInput])
  values = tuple(values)
  
  query = queries[query_id - 1][2].format(*values)

  formatSql = queries[query_id - 1][4]
  if formatSql:
    sql = queries[query_id - 1][3].format(*values)
    values = []
  else:
    sql = queries[query_id - 1][3]
  
  try:
    cursorObject.execute(sql, values)
    result = cursorObject.fetchall()
    columnNames = tuple([description[0] for description in cursorObject.description])
    result.insert(0, columnNames)
  except Exception as e:
    print(e)
    error = "There was an error while running the query. Please make sure your inputs look OK."
    return render_template("error.html", error=error)
    
  return render_template("query.html", queries=queries, query_id=query_id, query=query, result=result)

@app.route("/insert")
def show_insert():
  return render_template("insert.html", inserts=inserts)

@app.route("/insert/<int:insert_id>", methods=["POST"])
def insert_data(insert_id):
  tableName = inserts[insert_id - 1][0]
  query = "INSERT INTO " + tableName + " VALUES "
  columns = inserts[insert_id - 1][1]
  
  values = []
  for column in columns:
    if column not in request.form or not request.form[column]:
      error = "Please make sure to provide values for all inputs."
      return render_temp