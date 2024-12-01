from flask import Flask, redirect, render_template, request

app = Flask(__name__)

queries = [
  (
    "Medal Count (Countries)",
    ["List Countries - by name and count of Medals. Display the Countries in descending order of their count of Medals."],
    [],
    ["SELECT Cou.Name COUNT(DISTINCT Com.EventID) FROM Countries AS Cou INNER JOIN Athletes AS A ON Cou.CountryID = A.CountryID INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID WHERE Com.Result >= 3 GROUP BY Cou.CountryID ORDER BY COUNT(DISTINCT Com.EventID) DESC;"],
    ),
  (
    "Medal Count (Athletes)",
    ["List Athletes - by name and count of Medals. Display the Athletes in descending order of their count of Medals. Limit the output to 10 Athletes only."],
    [],
    ["SELECT A.name, COUNT(C.EventID) FROM Athletes AS A INNER JOIN Compete AS C ON A.AthleteID = C.AthleteID WHERE C.Result >= 3 GROUP BY A.AthleteID ORDER BY COUNT(C.EventID) DESC LIMIT 10;"],
  ),
  (
    "Athletes Born After Year",
    ["List Athletes - by name and Event name - born after ", " (included) representing the Country ", "."],
    ["Year", "Country"],
    ["SELECT A.Name, E.Name FROM Athletes AS A INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID INNER JOIN Events AS E ON Com.EventID = E.EventID INNER JOIN Country AS Cou ON A.CountryID = Cou.CountryID WHERE YEAR(A.DateOfBirth) >= ", " AND Cou.Name = ", ";"],
  ),
  (
    "Gold Medal Athletes Born Before Year",
    ["List distinct Athletes - by name, date of birth, and Country name - who won gold Medals and were born before ", " (excluded) representing the Country ", "."],
    ["Year", "Country"],
    ["SELECT DISTINCT A.Name, A.DateOfBirth, Cou.Name FROM Athletes AS A INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID INNER JOIN Events AS E ON Com.EventID = E.EventID WHERE E.Result = 1 AND YEAR(A.DateOfBirth) < ", " AND Cou.Name = ", ";"],
  ),
  (
    "Gold Medal Athletes",
    ["List Athletes - by name, Country name, and Event name - who won at least one gold Medal."],
    [],
    [""],
  ),
  (
    "Event Dates",
    ["List Events - by name and date - in which Athletes representing the Country ", " participated in. Display the Events in ascending order of their dates."],
    ["Country"],
    ["SELECT E.Name, E.Date FROM Events AS E INNER JOIN Compete AS Com ON E.EventID = Com.EventID INNER JOIN Athletes AS A ON Com.AthleteID = A.AthleteID INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID WHERE Cou.Name = ", " ORDER BY E.Date ASC;"],
  ),
  (
    "Night Events",
    ["List Events - by name and Venue name - that took place after 6pm (included)."],
    [],
    ["SELECT E.Name, V.Name FROM Events AS E INNER JOIN Venues AS V ON E.VenueID = E.VenueID WHERE E.StartTime >= \"18:00:00\";"],
  ),
  (
    "Men's Basketball",
    ["List Venues - by name and city - that hosted the Event men’s basketball."],
    [],
    [""],
  ),
  (
    "Female Americans",
    ["List Athletes - by name and date of birth - who are female and represent the Country USA."],
    [],
    [""],
  ),
  (
    "All USA Participants",
    ["List Athletes, Coaches, and Officials - by name - representing the Country USA."],
    [],
    ["(SELECT A.Name FROM Athletes AS A INNER JOIN Countries AS C ON A.CountryID = C.CountryID WHERE C.Name = \"USA\") UNION (SELECT Coa.Name FROM Coaches AS Coa INNER JOIN Countries AS Cou ON Coa.CountryID = Cou.CountryID WHERE Country.Name = \"USA\") UNION (SELECT O.Name FROM Officials AS O INNER JOIN Country AS C ON O.CountryID = C.CountryID WHERE C.Name = \"USA\");"],
  ),
  (
    "Experienced Coaches",
    ["List Coaches - by name, years of experience, and Country name - who have more than ", " (included) years of experience. Display the Coaches in descending order of their years of experience."],
    ["Years"],
    ["SELECT Coa.Name, Coa.YearsOfExperience, Cou.Name FROM Coaches AS Coa INNER JOIN Countries AS Cou ON Coa.CountryID = Cou.CountryID WHERE Coa.YearsOfExperience >= ", " ORDER BY Coa.YearsOfExperience DESC;"],
  ),
  (
    "Events in Large Venues",
    ["List Events - by name and Venue name - that were hosted by Venues with a capacity between 20,000 (included) and 30,000 (included)."],
    [],
    ["SELECT E.name, V.name FROM Events AS E INNER JOIN Venues AS V ON E.VenueID = V.VenueID WHERE V.Capacity >= 20000 AND V.Capacity <= 30000;"],
  ),
  (
    "First and Last Day",
    ["List Athletes - by name - that competed in Events held on the first day of the Olympics (July 26) and the last day of the Olympics (August 11)."],
    [],
    [""],
  ),
  (
    "Country Medalists",
    ["List Athletes - by name, gender, and education level - representing the Country ", " who won a Medal."],
    ["Country"],
    ["SELECT A.Name, A.Gender, A.EducationLevel FROM Athletes AS A INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID WHERE Com.Result >= 3 AND Cou.Name = ", ";"],
  ),
  (
    "Only Gold Medalists",
    ["List Athletes - by name - who won a gold Medal but did not win a silver Medal or a bronze Medal."],
    [],
    [""],
  ),
  (
    "A Lot of Athletes",
    ["List Countries - by name, population, and number of Athletes representing them. Only display Countries with at least ", " (included) Athletes representing them."],
    ["Athletes"],
    ["SELECT C.Name, C.Population, COUNT(A.AthleteID) AS NumberOfAthletes FROM Countries AS C INNER JOIN Athletes AS A ON C.CountryID = A.CountryID GROUP BY C.CountryID HAVING COUNT(A.AthleteID) >= ", ";"],
  ),
  (
    "Outside Paris",
    ["List Events - by name - that were held in Venues located in cities that aren’t Paris."],
    [],
    [""],
  ),
  (
    "Athlete Attributes",
    ["List Athletes - by ", "."],
    ["Attributes"],
    ["SELECT ", " FROM Athletes;"],
  ),
  (
    "North American Medalists",
    ["List Athletes - by name - who represented the Countries USA, Mexico, or Canada and won a Medal."],
    [],
    [""],
  ),
  (
    "First-Time Coach",
    ["List Countries - by ID and name - who have a Coach that is coaching an event for the first time but do not have an Official that is officiating for the first time."],
    [],
    ["SELECT Countries.ID, Countries.Name FROM Countries INNER JOIN Coaches ON Countries.CountryID = Coaches.CountryID INNER JOIN Coach ON Coaches.CoachID = Coach.CoachID WHERE Coach.FirstTime = TRUE AND Countries.ID NOT IN (SELECT Officials.CountryID FROM Officials INNER JOIN Officiate ON Officials.OfficialID = Officiate.OfficialID WHERE Officiate.FirstTime = TRUE);"],
  ),
  (
    "All Athletes",
    ["Display all Athletes"],
    [],
    ["SELECT * FROM Athletes;"],
  ),
  (
    "All Countries",
    ["Display all Countries"],
    [],
    ["SELECT * FROM Countries;"],
  ),
  (
    "All Coaches",
    ["Display all Coaches"],
    [],
    ["SELECT * FROM Coaches;"],
  ),
  (
    "All Venues",
    ["Display all Venues"],
    [],
    ["SELECT * FROM Venues;"],
  ),
  (
    "All Events",
    ["Display all Events"],
    [],
    ["SELECT * FROM Events;"],
  ),
  (
    "All Officials",
    ["Display all Officials"],
    [],
    ["SELECT * FROM Officials;"],
  ),
]

inserts = [
  (
    "Athletes",
    ["AthleteID", "Name", "Gender", "Height", "Weight", "DateOfBirth", "EducationLevel", "CountryID"],
  ),
  (
    "Countries",
    ["CountryID", "Name", "Population"],
  ),
  (
    "Coaches",
    ["CoachID", "Name", "Gender", "Function", "YearsOfExperience", "CountryID"],
  ),
  (
    "Venues",
    ["VenueID", "Name", "Capacity", "City"],
  ),
  (
    "Events",
    ["EventID", "Name", "StartTime", "EndTime", "Date", "VenueID"],
  ),
  (
    "Officials",
    ["OfficialID", "Name", "Gender", "Function", "YearsOfExperience", "CountryID"],
  ),
]

sample_result = [
  ("Name", "Age", "Event", "Result"),
  ("Baker Mayfield", 27, "Men's 100m Dash", 1),
  ("Geno Smith", 25, "Men's Basketball", 2),
  ("Josh Jacobs", 29, "Men's Shotput", 4),
  ("CeeDee Lamb", 28, "Men's Figure Skating", 1),
]

@app.route("/")
def show_home():
  return render_template("home.html", queries=queries)

@app.route("/query")
def show_queries():
  return render_template("queries.html", queries=queries)

@app.route("/query/<int:query_id>")
def show_query(query_id):

  flag = False
  for key in queries[query_id - 1][2]:
    if key not in request.args:
      flag = True
  
  query = ""
  if not flag:
    query += queries[query_id - 1][1][0]
    index = 1
    for key in queries[query_id - 1][2]:
      query += request.args[key]
      query += queries[query_id - 1][1][index]
      index += 1
  
  sql = ""
  if not flag:
    sql += queries[query_id - 1][3][0]
    index = 1
    for key in queries[query_id - 1][2]:
      sql += request.args[key]
      sql += queries[query_id - 1][3][index]
      index += 1
  
  print(sql)
    
  return render_template("query.html", queries=queries, query_id=query_id, query=query, flag=flag, result=sample_result)

@app.route("/insert")
def show_insert():
  return render_template("insert.html", inserts=inserts)

@app.route("/insert/<int:insert_id>", methods=["POST"])
def insert_data(insert_id):
  query = "INSERT INTO " + inserts[insert_id - 1][0] + " (" + ", ".join(inserts[insert_id - 1][1]) + ")" + " VALUES "
  
  values = []
  for key in inserts[insert_id - 1][1]:
    values.append(request.form[key])
  
  query += "(" + ", ".join(values) + ")"

  return redirect(f"/query/{20 + insert_id}")
