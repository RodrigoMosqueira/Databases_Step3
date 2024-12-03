import mysql.connector

myConnection = mysql.connector.connect(
    user = 'root',
    password = 'romoa5068', #replace with your password
    host = 'localhost')

cursor = myConnection.cursor()

cursor.execute("CREATE DATABASE Olympics")

cursor.execute("USE Olympics")

cursor.execute("""
    CREATE TABLE Countries (
        CountryID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        Population INT,
        PRIMARY KEY (CountryID)
    );
""")

cursor.execute("""
    CREATE TABLE Athletes (
        AthleteID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        Gender VARCHAR(10), 
        Height DECIMAL(10,2), 
        Weight DECIMAL(10,2), 
        DateofBirth DATE, 
        EducationLevel VARCHAR(100), 
        CountryID INT,
        PRIMARY KEY (AthleteID),
        FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
    );
""")

cursor.execute("""
    CREATE TABLE Coaches (
        CoachID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        Gender VARCHAR(10), 
        Type VARCHAR(255),
        YearsOfExperience INT,
        CountryID INT,
        PRIMARY KEY (CoachID),
        FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
    );
""")

cursor.execute("""
    CREATE TABLE Venues (
        VenueID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        Capacity INT,
        City VARCHAR(100),
        PRIMARY KEY (VenueID)
    );
""")

cursor.execute("""
    CREATE TABLE Events (
        EventID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        StartTime TIME, 
        EndTime TIME,
        Date DATE,
        VenueID INT,
        PRIMARY KEY (EventID),
        FOREIGN KEY (VenueID) REFERENCES Venues(VenueID)
    );
""")

cursor.execute("""
    CREATE TABLE Officials (
        OfficialID INT NOT NULL, 
        Name VARCHAR(255) NOT NULL, 
        Gender VARCHAR(10),
        Type VARCHAR(255),
        YearsOfExperience INT, 
        CountryID INT,
        PRIMARY KEY (OfficialID),
        FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
    );
""")

cursor.execute("""
    CREATE TABLE Compete (
        AthleteID INT NOT NULL, 
        EventID INT NOT NULL,
        Result INT,
        PRIMARY KEY (AthleteID, EventID),
        FOREIGN KEY (AthleteID) REFERENCES Athletes(AthleteID),
        FOREIGN KEY (EventID) REFERENCES Events(EventID)
    );
""")

cursor.execute("""
    CREATE TABLE Coach (
        CoachID INT NOT NULL, 
        EventID INT NOT NULL,
        FirstTime BOOL,
        PRIMARY KEY (CoachID, EventID),
        FOREIGN KEY (CoachID) REFERENCES Coaches(CoachID),
        FOREIGN KEY (EventID) REFERENCES Events(EventID)
    );
""")

cursor.execute("""
    CREATE TABLE Officiate (
        OfficialID INT NOT NULL, 
        EventID INT NOT NULL,
        FirstTime BOOL,
        PRIMARY KEY (OfficialID, EventID),
        FOREIGN KEY (OfficialID) REFERENCES Officials(OfficialID),
        FOREIGN KEY (EventID) REFERENCES Events(EventID)
    );
""")