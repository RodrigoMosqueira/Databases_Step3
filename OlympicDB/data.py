
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
    ["CoachID", "Name", "Gender", "Type", "YearsOfExperience", "CountryID"],
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
    ["OfficialID", "Name", "Gender", "Type", "YearsOfExperience", "CountryID"],
  ),
]

queries = [
  (
    "Medal Count (Countries)",
    [],
    """List Countries - by name and count of Medals.
    Display the Countries in descending order of their count of Medals.
    """,
    """
    SELECT Cou.Name, COUNT(DISTINCT Com.EventID) AS CountOfMedals
    FROM Countries AS Cou
    INNER JOIN Athletes AS A ON Cou.CountryID = A.CountryID
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    WHERE Com.Result >= 3
    GROUP BY Cou.CountryID
    ORDER BY COUNT(DISTINCT Com.EventID) DESC;
    """,
    False,
    ),
  (
    "Medal Count (Athletes)",
    [],
    """
    List Athletes - by name and count of Medals.
    Display the Athletes in descending order of their count of Medals.
    Limit the output to 10 Athletes only.
    """,
    """
    SELECT A.Name, COUNT(C.EventID) AS CountOfMedals
    FROM Athletes AS A
    INNER JOIN Compete AS C ON A.AthleteID = C.AthleteID
    WHERE C.Result >= 3
    GROUP BY A.AthleteID
    ORDER BY COUNT(C.EventID) DESC
    LIMIT 10;
    """,
    False,
  ),
  (
    "Athletes Born After Year",
    ["Year", "Country"],
    """
    List Athletes - by name and Event name - born after {} (included) representing the Country {}.
    """,
    """
    SELECT A.Name AS AthleteName, E.Name AS EventName
    FROM Athletes AS A
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    INNER JOIN Events AS E ON Com.EventID = E.EventID
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    WHERE YEAR(A.DateOfBirth) >= %s AND Cou.Name = %s;
    """,
    False,
  ),
  (
    "Gold Medal Athletes Born Before Year",
    ["Year", "Country"],
    """
    List distinct Athletes - by name, date of birth, and Country name -
    who won gold Medals and were born before {} (excluded) representing the Country {}.
    """,
    """
    SELECT DISTINCT A.Name AS AthleteName, A.DateOfBirth, Cou.Name AS CountryName
    FROM Athletes AS A
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    INNER JOIN Events AS E ON Com.EventID = E.EventID
    WHERE Com.Result = 1 AND YEAR(A.DateOfBirth) < %s AND Cou.Name = %s;
    """,
    False,
  ),
  (
    "Gold Medal Athletes",
    [],
    """
    List Athletes - by name, Country name, and Event name - who won at least one gold Medal.
    """,
    """
    SELECT A.Name AS AthleteName, Cou.Name AS CountryName, E.Name AS EventName
    FROM Athletes AS A
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    INNER JOIN Compete AS COM ON A.AthleteID = Com.AthleteID
    INNER JOIN Events AS E ON Com.EventID = E.EventID
    WHERE Com.Result = 1;
    """,
    False,
  ),
  (
    "Event Dates",
    ["Country"],
    """
    List Events - by name and date - in which Athletes representing the Country {} participated in.
    Display the Events in ascending order of their dates.
    """,
    """
    SELECT E.Name, E.Date FROM Events AS E
    INNER JOIN Compete AS Com ON E.EventID = Com.EventID
    INNER JOIN Athletes AS A ON Com.AthleteID = A.AthleteID
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    WHERE Cou.Name = %s
    ORDER BY E.Date ASC;
    """,
    False,
  ),
  (
    "Average Official Experience",
    [],
    """
    List Countries - by name, count of Officials, and average years of experience of Officials.
    Only display Countries with at least 2 Officials (included). Display the Countries in descending
    order of the average years of experience of Officials.
    """,
    """
    SELECT C.Name, COUNT(O.OfficialID) AS CountOfOfficials, AVG(O.YearsOfExperience) AS AverageYearsOfExperienceOfOfficials
    FROM Countries AS C
    INNER JOIN Officials AS O ON C.CountryID = O.CountryID
    GROUP BY C.CountryID
    HAVING COUNT(O.OfficialID) >= 2
    ORDER BY AVG(O.YearsOfExperience) DESC;
    """,
    False,
  ),
  (
    "Host Venues",
    ["Event"],
    """
    List Venues - by name and city - that hosted the Event {}.
    """,
    """
    SELECT V.Name, V.City
    FROM Venues AS V
    INNER JOIN Events AS E ON V.VenueID = E.VenueID
    WHERE E.Name = %s;
    """,
    False,
  ),
  (
    "Above-Average Height",
    ["Country"],
    """
    List Athletes with height greater than the average height of Athletes representing the Country {}.
    """,
    """
    SELECT *
    FROM Athletes
    WHERE Height > (
      SELECT AVG(A.Height)
      FROM Athletes AS A
      INNER JOIN Countries AS C ON A.CountryID = C.CountryID
      WHERE C.Name = %s
    );
    """,
    False,
  ),
  (
    "All United States Participants",
    [],
    """
    List Athletes, Coaches, and Officials - by name - representing the Country United States.
    """,
    """
    (
      SELECT A.Name
      FROM Athletes AS A
      INNER JOIN Countries AS C ON A.CountryID = C.CountryID
      WHERE C.Name = \"United States\"
    ) UNION (
      SELECT Coa.Name
      FROM Coaches AS Coa
      INNER JOIN Countries AS Cou ON Coa.CountryID = Cou.CountryID
      WHERE Cou.Name = \"United States\"
    ) UNION (
      SELECT O.Name
      FROM Officials AS O
      INNER JOIN Countries AS C ON O.CountryID = C.CountryID
      WHERE C.Name = \"United States\"
    );
    """,
    False,
  ),
  (
    "Experienced Coaches",
    ["Years"],
    """
    List Coaches - by name, years of experience, and Country name -
    who have more than {} (included) years of experience.
    Display the Coaches in descending order of their years of experience.
    """,
    """
    SELECT Coa.Name AS CoachName, Coa.YearsOfExperience, Cou.Name AS CountryName
    FROM Coaches AS Coa
    INNER JOIN Countries AS Cou ON Coa.CountryID = Cou.CountryID
    WHERE Coa.YearsOfExperience >= %s
    ORDER BY Coa.YearsOfExperience DESC;
    """,
    False,
  ),
  (
    "Events in Large Venues",
    [],
    """
    List Events - by name and Venue name -
    that were hosted by Venues with a capacity between 20,000 (included) and 30,000 (included).
    """,
    """
    SELECT E.Name AS EventName, V.Name AS VenueName
    FROM Events AS E
    INNER JOIN Venues AS V ON E.VenueID = V.VenueID
    WHERE V.Capacity >= 20000 AND V.Capacity <= 30000;
    """,
    False,
  ),
  (
    "First and Last Day",
    [],
    """
    List Athletes - by athleteID and name -
    that competed in Events held on the first day of the Olympics (July 26)
    and the last day of the Olympics (August 11).
    """,
    """
    (
      SELECT A.AthleteID, A.Name
      FROM Athletes AS A
      INNER JOIN Compete AS C ON A.AthleteID = C.AthleteID
      INNER JOIN Events AS E ON C.EventID = E.EventID
      WHERE E.Date = 2024-07-26
    ) INTERSECT (
      SELECT A.AthleteID, A.Name
      FROM Athletes AS A
      INNER JOIN Compete AS C ON A.AthleteID = C.AthleteID
      INNER JOIN Events AS E ON C.EventID = E.EventID
      WHERE E.Date = 2024-08-11
    );
    """,
    False,
  ),
  (
    "Country Medalists",
    ["Country"],
    """
    List Athletes - by name, gender, and education level - representing the Country {} who won a Medal.
    """,
    """
    SELECT A.Name, A.Gender, A.EducationLevel
    FROM Athletes AS A
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    WHERE Com.Result >= 3 AND Cou.Name = %s;
    """,
    False,
  ),
  (
    "Only Gold",
    [],
    """
    List Athletes - by name and Country name -
    who won a gold Medal but did not win a silver Medal or a bronze Medal.
    """,
    """
    SELECT A.Name AS AthleteName, Cou.Name AS CountryName
    FROM Athletes AS A
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    WHERE Com.Result = 1 AND A.AthleteID NOT IN (
      SELECT AthleteID
      FROM Compete
      WHERE Result IN (2, 3)
    );
    """,
    False,
  ),
  (
    "A Lot of Athletes",
    ["Athletes"],
    """
    List Countries - by name, population, and number of Athletes representing them.
    Only display Countries with at least {} (included) Athletes representing them.
    """,
    """
    SELECT C.Name, C.Population, COUNT(A.AthleteID) AS NumberOfAthletes
    FROM Countries AS C
    INNER JOIN Athletes AS A ON C.CountryID = A.CountryID
    GROUP BY C.CountryID
    HAVING COUNT(A.AthleteID) >= %s;
    """,
    False,
  ),
  (
    "Outside Paris",
    [],
    """
    List Events - by name, Venue name, and Venue city -
    that were held in Venues located in cities that aren’t Paris.
    """,
    """
    SELECT E.Name AS EventName, V.Name AS VenueName, V.City
    FROM Events AS E
    INNER JOIN Venues AS V ON E.VenueID = V.VenueID
    WHERE V.City != \"Paris\";
    """,
    False,
  ),
  (
    "Athlete Attributes",
    ["Attributes"],
    """
    List Athletes - by {}.
    """,
    """
    SELECT {}
    FROM Athletes;
    """,
    True,
  ),
  (
    "North American Medalists",
    [],
    """
    List Athletes - by name and Country name -
    who represented the Countries USA, Mexico, or Canada and won a Medal.
    """,
    """
    SELECT A.Name AS AthleteName, Cou.Name AS CountryName
    FROM Athletes AS A
    INNER JOIN Countries AS Cou ON A.CountryID = Cou.CountryID
    INNER JOIN Compete AS Com ON A.AthleteID = Com.AthleteID
    WHERE Cou.Name IN (\"USA\", \"Mexico\", \"Canada\") AND Com.Result >= 3;
    """,
    False,
  ),
  (
    "First-Time Coach",
    [],
    """
    List Countries - by ID and name -
    who have a Coach that is coaching an event for the first time
    but do not have an Official that is officiating for the first time.
    """,
    """
    SELECT Countries.CountryID, Countries.Name
    FROM Countries
    INNER JOIN Coaches ON Countries.CountryID = Coaches.CountryID
    INNER JOIN Coach ON Coaches.CoachID = Coach.CoachID
    WHERE Coach.FirstTime = TRUE AND Countries.CountryID NOT IN (
      SELECT Officials.CountryID
      FROM Officials
      INNER JOIN Officiate ON Officials.OfficialID = Officiate.OfficialID
      WHERE Officiate.FirstTime = TRUE
    );
    """,
    False,
  ),
  (
    "All Athletes",
    [],
    """
    Display all Athletes
    """,
    """
    SELECT *
    FROM Athletes;
    """,
    False,
  ),
  (
    "All Countries",
    [],
    """
    Display all Countrie