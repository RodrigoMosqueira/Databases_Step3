"""
Run this file to generate processed data.Be sure change the password in line 9.
This will output processed data in .csv file starting with the file name 
'gnerated_'. The data will also be automatically inserted into mysql
"""


import mysql.connector
import csv
from datetime import datetime, timedelta, time
import random
import pandas as pd

myConnection = mysql.connector.connect(
    user = 'root',
    password = 'XXXXX', #replace with your password
    host = 'localhost')

cursor = myConnection.cursor()

cursor.execute("DROP DATABASE IF EXISTS Olympics")

cursor.execute("CREATE DATABASE IF NOT EXISTS Olympics")

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
        Kind VARCHAR(255),
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
        Kind VARCHAR(255),
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
        Result VARCHAR(25),
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



"""
Processing data to insert:
"""

# Adding country_id to athletes.csv
def add_country_id_to_csv(input_file_path, output_file_path):
    # Read the input CSV file
    with open(input_file_path, 'r') as input_file:
        reader = csv.DictReader(input_file)
        rows = list(reader)

    # Extract unique country names and assign unique CountryIDs
    countries = set(row["country"].strip() for row in rows if "country" in row and row["country"].strip())
    country_id_map = {country: idx + 1 for idx, country in enumerate(sorted(countries))}

    # Add a new "CountryID" column to each row
    for row in rows:
        country_name = row.get("country", "").strip()
        row["CountryID"] = country_id_map.get(country_name, None)

    # Write the updated data to the output CSV file
    with open(output_file_path, 'w', newline='') as output_file:
        fieldnames = reader.fieldnames + ["CountryID"]  # Add the new column to the header
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated CSV saved to {output_file_path}")

    # Generate and save a CSV with unique country-CountryID pairs
    unique_pairs_file_path = "Data/Paris2024/generated_country.csv"
    unique_country_pairs = sorted(set((row["country"].strip(), row["CountryID"]) for row in rows))
    
    # Write the unique country-CountryID pairs to a separate CSV
    with open(unique_pairs_file_path, 'w', newline='') as unique_file:
        writer = csv.writer(unique_file)
        writer.writerow(["Country", "CountryID"])  # Header
        writer.writerows(unique_country_pairs)

    print(f"Unique country-CountryID pairs saved to {unique_pairs_file_path}")


# File paths
input_csv_path = "Data/Paris2024/athletes.csv"  # Replace with the path to your input CSV file
output_csv_path = "Data/Paris2024/generated_athletes_with_country_id.csv"  # Replace with the desired output file path
# Add CountryID and save the updated CSV
add_country_id_to_csv(input_csv_path, output_csv_path)


# Generate Table Countries in mysql
def process_and_insert_countries(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        countries_data = []

        # Extract unique countries from the CSV
        unique_countries = {}
        for row in reader:
            country_id = int(row["CountryID"])
            country_name = row["country"].strip()
            if country_id not in unique_countries:
                unique_countries[country_id] = country_name

        # Generate random populations and prepare data for insertion
        for country_id, country_name in unique_countries.items():
            population = random.randint(500_000, 150_000_000)  # Random population
            countries_data.append((country_id, country_name, population))

        # Insert data into the Countries table
        insert_query = """
        INSERT INTO Countries (CountryID, Name, Population)
        VALUES (%s, %s, %s)
        """
        cursor.executemany(insert_query, countries_data)
        myConnection.commit()

        print(f"Inserted {len(countries_data)} rows into the Countries table.")

process_and_insert_countries("Data/Paris2024/generated_athletes_with_country_id.csv")


# Athletes
def process_and_insert_athletes(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        athletes_data = []

        for row in reader:
            # Generate or clean up the data
            athlete_id = int(row.get("code"))
            # athlete_id = int(row.get("code", random.randint(1000, 9999)))  # Use 'code' for AthleteID
            name = row.get("name", "Unknown").strip()  # Default to "Unknown" if missing
            gender = row.get("gender", random.choice(["Male", "Female"]))
            height = float(row.get("height", random.uniform(150.0, 200.0))) if row.get("height") else None
            weight = float(row.get("weight", random.uniform(50.0, 100.0))) if row.get("weight") else None

            # Generate random Date of Birth if missing
            dob = row.get("birth_date")
            if dob:
                try:
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    dob = None
            if not dob:  # Generate random date if missing or invalid
                start_date = datetime.now() - timedelta(days=365 * 40)  # Up to 40 years ago
                random_days = random.randint(0, 365 * 30)  # Random age between 10 and 40
                dob = (start_date + timedelta(days=random_days)).date()

            # Generate logical random education level if missing
            education_level = row.get("education_level")
            if not education_level:
                if dob.year > 2005:  # Younger athletes likely in school
                    education_level = random.choice(["High School", "Undergraduate"])
                else:  # Older athletes likely have higher education
                    education_level = random.choice(["Undergraduate", "Postgraduate", "Vocational"])

            country_id = int(row.get("CountryID"))

            athletes_data.append(
                (athlete_id, name, gender, height, weight, dob, education_level, country_id)
            )


        # Insert data into the Athletes table
        insert_query = """
        INSERT INTO Athletes (AthleteID, Name, Gender, Height, Weight, DateOfBirth, EducationLevel, CountryID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, athletes_data)
        myConnection.commit()

csv_file_path_athletes = "Data/Paris2024/generated_athletes_with_country_id.csv"
process_and_insert_athletes(csv_file_path_athletes)


# Venues
def process_and_save_venues(input_file_path, output_file_path, cursor):
    """
    Process the venues.csv file, save the extracted and generated venue information
    into a new CSV file, and insert the data into the Venues MySQL table.

    Parameters:
    input_file_path (str): Path to the input venues.csv file.
    output_file_path (str): Path to the output CSV file to save the processed venue information.
    cursor (MySQLCursor): MySQL cursor object for executing queries.
    """
    venues_data = []
    venue_ids = set()  # To keep track of unique VenueIDs

    with open(input_file_path, 'r') as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            # Generate a unique VenueID
            # print(row)
            while True:
                venue_id = random.randint(1000, 9999)  # Random VenueID
                if venue_id not in venue_ids:  # Ensure it's unique
                    venue_ids.add(venue_id)
                    break
            
            # Extract information from CSV
            name = row.get("venue", "Unknown Venue").strip()
            capacity = random.randint(5000, 80000)  # Logical random capacity
            city = row.get(" city", "Unknown City").strip()

            # Append the data for CSV file and SQL insertion
            venues_data.append({
                "VenueID": venue_id,
                "Name": name,
                "Capacity": capacity,
                "City": city
            })

            # Insert into the Venues table
            insert_query = """
            INSERT INTO Venues (VenueID, Name, Capacity, City)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (venue_id, name, capacity, city))

    # Commit the insertion into the database
    myConnection.commit()

    # Save the processed data into a new CSV file
    with open(output_file_path, 'w', newline='') as output_file:
        fieldnames = ["VenueID", "Name", "Capacity", "City"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(venues_data)

    print(f"Processed venue data has been saved to {output_file_path}")
    print("Data has also been inserted into the Venues table.")

input_file_path = "Data/Paris2024/venues.csv"
output_file_path = "Data/Paris2024/generated_venues.csv"

process_and_save_venues(input_file_path, output_file_path, cursor)


# Events
def generate_and_insert_events(events_file, venues_file, cursor):
    events_df = pd.read_csv(events_file)
    venues_df = pd.read_csv(venues_file)

    # Extract venue IDs from the venues data
    venue_ids = venues_df['VenueID'].tolist()

    # Define the start and end date of the 2024 Paris Olympics
    olympics_start_date = datetime(2024, 7, 26).date()
    olympics_end_date = datetime(2024, 8, 11).date()

    # Function to generate random datetime for each event
    def generate_event_date():
        random_date = olympics_start_date + timedelta(days=random.randint(0, (olympics_end_date - olympics_start_date).days))
        random_start_time = time(random.randint(9, 22), random.randint(0, 59))  # Random time between 9 AM to 10 PM
        random_end_time = (datetime.combine(datetime.today(), random_start_time) + timedelta(hours=random.randint(1, 3))).time()  # Duration of 1 to 3 hours
        return random_date, random_start_time, random_end_time

    # Generate EventID and assign VenueID
    event_data = []
    event_id = 1
    for index, row in events_df.iterrows():
        event_name = f"{row['event']} {row['sport']}"
        date, start_time, end_time = generate_event_date()
        venue_id = random.choice(venue_ids)
        
        event_data.append({
            "EventID": event_id,
            "Name": event_name,
            "StartTime": start_time,
            "EndTime": end_time,
            "Date": date,
            "VenueID": venue_id
        })
        
        event_id += 1  # Increment the EventID for each event

    # Convert to DataFrame
    event_table_df = pd.DataFrame(event_data)

    # Save to a new CSV file
    event_table_df.to_csv('Data/Paris2024/generated_events.csv', index=False)

    print("Event data generated and saved to 'generated_events.csv'.")

    # Prepare SQL Insert statement
    insert_query = """
        INSERT INTO Events (EventID, Name, StartTime, EndTime, Date, VenueID) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    # Insert the events into the database
    for event in event_data:
        cursor.execute(insert_query, (event['EventID'], event['Name'], event['StartTime'], event['EndTime'], event['Date'], event['VenueID']))
    
    # Commit the transaction
    myConnection.commit()


events_file = "Data/Paris2024/events.csv"
venues_file = "Data/Paris2024/generated_venues.csv"
generate_and_insert_events(events_file, venues_file, cursor)


# Coaches
def generate_coach_data(coaches_file, countries_file, cursor):
    # Load the coaches data (adjust the path to your actual file location)
    coaches_df = pd.read_csv(coaches_file)

    # Load the countries data (adjust the path to your actual file location)
    countries_df = pd.read_csv(countries_file)

    # Create a dictionary of CountryID mapped to country names
    country_dict = dict(zip(countries_df['Country'], countries_df['CountryID']))

    # Function to generate random years of experience
    def generate_years_of_experience():
        return random.randint(0, 20)  # Random experience between 2 and 20 years

    # Prepare the data for insertion into the 'Coaches' table
    coach_data = []

    for index, row in coaches_df.iterrows():
        coach_id = row['code']  # Use 'code' as CoachID
        name = row['name']
        gender = row['gender']
        kind = row['function']
        years_of_experience = generate_years_of_experience()

        # Assign a random CountryID (if country information is missing)
        random_country = random.choice(list(country_dict.values()))
        country_id = random_country

        coach_data.append({
            "CoachID": coach_id,
            "Name": name,
            "Gender": gender,
            "Kind": kind,
            "YearsOfExperience": years_of_experience,
            "CountryID": country_id
        })

    # Convert the prepared data into a DataFrame
    coach_table_df = pd.DataFrame(coach_data)

    # Save to a new CSV file
    coach_table_df.to_csv("Data/Paris2024/generated_coaches.csv", index=False)

    print(f"Coach data generated and saved to Data/Paris2024/generated_coaches.csv.")

    # Prepare SQL Insert statement for the 'Coaches' table
    insert_query = """
        INSERT INTO Coaches (CoachID, Name, Gender, Kind, YearsOfExperience, CountryID) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    # Insert each row from the DataFrame into MySQL
    for index, row in coach_table_df.iterrows():
        cursor.execute(insert_query, tuple(row))

    myConnection.commit()  # Commit the transaction
    
    print(f"{len(coach_table_df)} rows inserted into the Coaches table successfully!")

coaches_file = 'Data/Paris2024/coaches.csv'
countries_file = 'Data/Paris2024/generated_country.csv'

generate_coach_data(coaches_file, countries_file, cursor)

# Coaching
def generate_coaching_event_data(events_file, coaches_file, output_path, cursor):
    # Load Events and Coaches datasets
    events_df = pd.read_csv(events_file)
    coaches_df = pd.read_csv(coaches_file)

    # Initialize an empty list to store the coaching data
    coaching_data = []
    
    # Create a list of all EventIDs and CoachIDs
    event_ids = events_df['EventID'].tolist()
    coach_ids = coaches_df['CoachID'].tolist()
    
    # Initialize a dictionary to track how many events each coach is assigned to
    coach_event_count = {coach_id: 0 for coach_id in coach_ids}

    # Initialize a dictionary to track how many coaches are assigned to each event
    event_coach_count = {event_id: 0 for event_id in event_ids}

    # Set to track combinations of (EventID, CoachID) to ensure no duplicates
    existing_combinations_set = set()

    # 1. Ensure all events have at least one coach
    for event_id in event_ids:
        # First assign 1 coach to every event (this ensures all events are covered)
        available_coaches = [coach_id for coach_id in coach_ids if coach_event_count[coach_id] < 6]
        
        if available_coaches:
            selected_coach = random.choice(available_coaches)
            coaching_data.append({
                "EventID": event_id,
                "CoachID": selected_coach,
                "FirstTime": coaches_df[coaches_df['CoachID'] == selected_coach]['YearsOfExperience'].iloc[0] < 5
            })
            coach_event_count[selected_coach] += 1
            event_coach_count[event_id] += 1
            existing_combinations_set.add((event_id, selected_coach))

    # 2. Now ensure that each coach is assigned to at least one event
    for coach_id in coach_ids:
        if coach_event_count[coach_id] == 0:
            # If a coach has not been assigned to any event, assign them to a random event
            available_events = [event_id for event_id in event_ids if event_coach_count[event_id] < 6]
            if available_events:
                selected_event = random.choice(available_events)
                coaching_data.append({
                    "EventID": selected_event,
                    "CoachID": coach_id,
                    "FirstTime": coaches_df[coaches_df['CoachID'] == coach_id]['YearsOfExperience'].iloc[0] < 5
                })
                coach_event_count[coach_id] += 1
                event_coach_count[selected_event] += 1
                existing_combinations_set.add((selected_event, coach_id))

    # 3. Randomly assign additional coaches to events, ensuring no more than 6 coaches per event
    for event_id in event_ids:
        # Each event can have at most 6 coaches
        num_coaches = random.randint(1, 6)  # Randomly assign between 1 and 6 coaches
        assigned_coaches = []
        
        while event_coach_count[event_id] < num_coaches:
            # Randomly select a coach who has been assigned to less than 6 events and this event has space
            available_coaches = [coach_id for coach_id in coach_ids if coach_event_count[coach_id] < 6 and event_coach_count[event_id] < 6]
            
            if not available_coaches:
                break  # Exit if no available coaches

            selected_coach = random.choice(available_coaches)
            if (event_id, selected_coach) not in existing_combinations_set:
                coaching_data.append({
                    "EventID": event_id,
                    "CoachID": selected_coach,
                    "FirstTime": coaches_df[coaches_df['CoachID'] == selected_coach]['YearsOfExperience'].iloc[0] < 5
                })
                coach_event_count[selected_coach] += 1
                event_coach_count[event_id] += 1
                existing_combinations_set.add((event_id, selected_coach))

    # Convert to DataFrame
    coaching_df = pd.DataFrame(coaching_data)
    
    # Save to a new CSV file
    coaching_df.to_csv(output_path, index=False)

    print(f"Coaching data generated and saved to {output_path}.")


    # Prepare the SQL Insert statement
    insert_query = """
        INSERT INTO Coach (EventID, CoachID, FirstTime) 
        VALUES (%s, %s, %s)
    """

    # Insert each row into the MySQL table
    for index, row in coaching_df.iterrows():
        cursor.execute(insert_query, (row['EventID'], row['CoachID'], row['FirstTime']))

    # Commit the transaction
    myConnection.commit()
    print(f"Coaching-Events data successfully inserted into the MySQL table.")

generate_coaching_event_data('Data/Paris2024/generated_events.csv', 
                            'Data/Paris2024/generated_coaches.csv', 
                            'Data/Paris2024/generated_coaching_events.csv', 
                            cursor)


# Officials
def process_and_insert_officials(file_path_officials, file_path_countries, output_path, cursor):
    # Load countries data to map CountryID
    country_data = pd.read_csv(file_path_countries)
    country_map = dict(zip(country_data["Country"], country_data["CountryID"]))
    
    officials_data = []
    unique_officials = set()  # To ensure unique officials by ID
    
    with open(file_path_officials, "r") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            official_name = row.get("name", "Unknown").strip()
            gender = row.get("gender", "Unknown").strip()
            kind = row.get("function", "Unknown").strip()
            organisation = row.get("organisation", "").strip()
            country_id = country_map.get(organisation, random.choice(list(country_map.values())))
            years_of_experience = random.randint(1, 20)  # Generate random years of experience
            
            # Ensure unique OfficialID
            official_id = int(row.get("code", random.randint(1000000, 1999999)))
            while official_id in unique_officials:
                official_id = random.randint(1000000, 1999999)
            unique_officials.add(official_id)
            
            # Append the processed data
            officials_data.append({
                "OfficialID": official_id,
                "Name": official_name,
                "Gender": gender,
                "Kind": kind,
                "YearsOfExperience": years_of_experience,
                "CountryID": country_id
            })
    
    # Save processed data to a new CSV file
    officials_df = pd.DataFrame(officials_data)
    officials_df.to_csv(output_path, index=False)
    print(f"Officials data saved to {output_path}.")

    # Insert data into MySQL table
    insert_query = """
        INSERT INTO Officials (OfficialID, Name, Gender, Kind, YearsOfExperience, CountryID)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for index, row in officials_df.iterrows():
        cursor.execute(
            insert_query, (
            row["OfficialID"], row["Name"], row["Gender"], row["Kind"],
            row["YearsOfExperience"], row["CountryID"]
                )
            )
    
    myConnection.commit()
    print("Officials data inserted into MySQL table.")

process_and_insert_officials(
    file_path_officials="Data/Paris2024/technical_officials.csv",
    file_path_countries="Data/Paris2024/generated_country.csv",
    output_path="Data/Paris2024/generated_officials.csv",
    cursor=cursor
)


# Officiate
def generate_and_insert_officiate_data(officials_file_path, events_file_path, output_path, cursor):
    # Load the officials and events data
    officials_file = pd.read_csv(officials_file_path)
    events_file = pd.read_csv(events_file_path)

    # Track how many events each official has been assigned to
    official_event_count = {official_id: 0 for official_id in officials_file['OfficialID']}

    # Prepare a list to hold the officiate data
    officiate_data = []

    # Iterate through each event
    for event_id in events_file['EventID'].tolist():
        # Randomly select between 1 to 4 officials for the event
        num_officials = random.randint(1, 4)
        
        # Get a list of officials who can still be assigned to events (max 4 events per official)
        available_officials = [official_id for official_id in officials_file['OfficialID'] 
                               if official_event_count[official_id] < 4]

        # If there are fewer than num_officials available, adjust the selection count
        if len(available_officials) < num_officials:
            num_officials = len(available_officials)

        # Randomly select the officials
        selected_officials = random.sample(available_officials, num_officials)

        # For each selected official, generate FirstTime based on YearsOfExperience
        for official_id in selected_officials:
            official = officials_file[officials_file['OfficialID'] == official_id].iloc[0]
            years_of_experience = official['YearsOfExperience'] if 'YearsOfExperience' in official else random.randint(0, 10)

            # FirstTime based on YearsOfExperience
            first_time = True if years_of_experience < 5 else False

            # Add the generated officiate record with EventID first
            officiate_data.append({
                "EventID": event_id,
                "OfficialID": official_id,
                "FirstTime": first_time
            })

            # Update the count of how many events the official has been assigned to
            official_event_count[official_id] += 1

    # Convert the officiate data to a DataFrame
    officiate_df = pd.DataFrame(officiate_data)

    # Reorder columns to put EventID first
    officiate_df = officiate_df[['EventID', 'OfficialID', 'FirstTime']]

    # Save the data to the specified output path (CSV file)
    officiate_df.to_csv(output_path, index=False)

    print(f"Officiate data generated and saved to '{output_path}'.")

# Prepare insert query
    insert_query = """
    INSERT INTO Officiate (EventID, OfficialID, FirstTime)
    VALUES (%s, %s, %s)
    """
    
    # Insert data into the table
    for _, row in officiate_df.iterrows():
        cursor.execute(insert_query, (row['EventID'], row['OfficialID'], row['FirstTime']))
    
    # Commit the connection
    myConnection.commit()

# Specify file paths for officials, events, and countries
officials_file_path = "Data/Paris2024/generated_officials.csv"
events_file_path = "Data/Paris2024/generated_events.csv"
output_path = "Data/Paris2024/generated_officiating.csv"

generate_and_insert_officiate_data(officials_file_path, events_file_path, output_path, cursor)


# Compete
def generate_athlete_event_data(athletes_file, events_file, output_path, cursor):
    # Load data
    athletes_df = pd.read_csv(athletes_file)
    events_df = pd.read_csv(events_file)

    # Prepare athlete-event assignment
    athlete_event_data = []
    athlete_ids = athletes_df['code'].tolist()
    event_ids = events_df['EventID'].tolist()

    # Shuffle athlete and event IDs for randomness
    random.shuffle(athlete_ids)
    random.shuffle(event_ids)

    # Assign at least two athletes to each event
    for event_id in event_ids:
        assigned_athletes = random.sample(athlete_ids, min(2, len(athlete_ids)))
        for athlete_id in assigned_athletes:
            result = random.choice(["Gold", "Silver", "Bronze", "No medals"])
            athlete_event_data.append({
                "EventID": event_id,
                "AthleteID": athlete_id,
                "Result": result
            })

    # Ensure every athlete is assigned to at least one event
    for athlete_id in athlete_ids:
        if not any(ae["AthleteID"] == athlete_id for ae in athlete_event_data):
            event_id = random.choice(event_ids)
            result = random.choice(["Gold", "Silver", "Bronze", "No medals"])
            athlete_event_data.append({
                "EventID": event_id,
                "AthleteID": athlete_id,
                "Result": result
            })

    # Convert to DataFrame
    athlete_event_df = pd.DataFrame(athlete_event_data)

    # Save to a new CSV file
    athlete_event_df.to_csv(output_path, index=False)

    print(f"Athlete-event data generated and saved to {output_path}.")

    # Prepare SQL Insert statement
    insert_query = """
        INSERT INTO Compete (EventID, AthleteID, Result)
        VALUES (%s, %s, %s)
    """

    # Insert data into MySQL
    for _, row in athlete_event_df.iterrows():
        cursor.execute(insert_query, (row['EventID'], row['AthleteID'], row['Result']))
    
    # Commit the connection
    myConnection.commit()
    print("Data inserted into the Compete table.")

athletes_file = 'Data/Paris2024/generated_athletes_with_country_id.csv'
events_file = 'Data/Paris2024/generated_events.csv'
output_path = 'Data/Paris2024/generated_compete.csv'

generate_athlete_event_data(athletes_file, events_file, output_path, cursor)
