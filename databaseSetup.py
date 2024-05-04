"""
Author: Kenechukwu Maduabum
Date: May 3th, 2024
Description:
This file contains everything necessary to create the schema for the 
database and tables along with inserting some rows into the necessary tables.
"""

import mysql.connector

# Create Connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kene1234"
)

# preparing a cursor object
cursor = mydb.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS ANIME_MANAGEMENT")
cursor.execute("USE ANIME_MANAGEMENT")

# Create ANIME table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ANIME (
    ID INT AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Status VARCHAR(16) CHECK(Status IN ('Not Aired Yet',
        'Currently Airing', 'Finished Airing')) DEFAULT 'Not Aired Yet',
    Synopsis VARCHAR(600),
    Season VARCHAR(6) CHECK(Season IN ('Winter', 'Spring', 'Summer', 'Fall')),
    Year INT CHECK (Year >= 1901 AND Year <= 2155),
    StreamPlatform VARCHAR(35),
    Studio VARCHAR(80) NOT NULL,
    PRIMARY KEY(ID)
)
""")

# Create EPISODE table
cursor.execute("""
CREATE TABLE IF NOT EXISTS EPISODE (
    ID INT AUTO_INCREMENT,
    Name VARCHAR(120) NOT NULL,
    Length TIME NOT NULL,
    Link VARCHAR(255),
    AnimeID INT NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (AnimeID) REFERENCES ANIME(ID)
)
""")

# Create ANIME_GENRES table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ANIME_GENRES (
    AnimeID INT,
    Genre VARCHAR(13) CHECK(Genre IN('Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
        'Mystery', 'School', 'Romance', 'Slice of Life', 'Supernatural', 'Isekai',
        'Psychological', 'Shoujo', 'Shounen', 'Sci-Fi', 'Time Travel', 'Video Game')),
    PRIMARY KEY (AnimeID, Genre),
    FOREIGN KEY (AnimeID) REFERENCES ANIME(ID)
)
""")


# Create CHARACTER table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ANIME_CHARACTER (
    ID INT AUTO_INCREMENT,
    Name VARCHAR(70) NOT NULL,
    Biography VARCHAR(600),
    VoiceActor VARCHAR(255),
    PRIMARY KEY (ID)
)
""")

# Create INCORPORATES table
cursor.execute("""
CREATE TABLE IF NOT EXISTS INCORPORATES (
    CharID INT,
    AnimeID INT,
    CharacterRole VARCHAR(10) NOT NULL CHECK (CharacterRole IN ('Main', 'Supporting')),
    PRIMARY KEY (CharID, AnimeID),
    FOREIGN KEY (CharID) REFERENCES ANIME_CHARACTER(ID),
    FOREIGN KEY (AnimeID) REFERENCES ANIME(ID)
)
""")

# Create USER table
cursor.execute("""
CREATE TABLE IF NOT EXISTS USER (
    ID INT AUTO_INCREMENT,
    Name VARCHAR(35) UNIQUE NOT NULL,
    JoinDate DATE NOT NULL,
    PRIMARY KEY (ID)
)
""")

# Create REVIEW table
cursor.execute("""
CREATE TABLE IF NOT EXISTS REVIEW (
    AnimeID INT,
    UserID INT,
    Rating INT NOT NULL CHECK (Rating >= 1 AND Rating <= 10),
    Comment VARCHAR(600),
    PRIMARY KEY (AnimeID, UserID),
    FOREIGN KEY (AnimeID) REFERENCES ANIME(ID),
    FOREIGN KEY (UserID) REFERENCES USER(ID)
)
""")

# Create LIST table
cursor.execute("""
CREATE TABLE IF NOT EXISTS LIST (
    ID INT AUTO_INCREMENT,
    Title VARCHAR(255),
    Description VARCHAR(100),
    UserID INT UNIQUE NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (UserID) REFERENCES USER(ID)
)
""")

# Create CONTAINS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS CONTAINS (
    ListID INT,
    AnimeID INT,
    WatchStatus VARCHAR(13) NOT NULL CHECK (WatchStatus IN ('Plan to Watch',
        'Watching', 'Completed', 'On-Hold', 'Dropped')) DEFAULT 'Plan to Watch',
    NumEpsWatched INT NOT NULL CHECK (NumEpsWatched >= 0) DEFAULT 0,
    PRIMARY KEY (ListID, AnimeID),
    FOREIGN KEY (ListID) REFERENCES LIST(ID),
    FOREIGN KEY (AnimeID) REFERENCES ANIME(ID)
)
""")

# Create a trigger to create a LIST for all new users.
insert_user_list = """
CREATE TRIGGER IF NOT EXISTS insert_user_list
AFTER INSERT ON USER
FOR EACH ROW
BEGIN
    INSERT INTO LIST (Title, Description, UserID)
    VALUES (CONCAT(NEW.Name, "'s List"),
        CONCAT('Personal watchlist for user: ', NEW.Name), NEW.ID);
END
"""
cursor.execute(insert_user_list)

# Insert data into ANIME table
insert_query = "INSERT INTO ANIME (Name, Status, Synopsis, Season, Year, StreamPlatform, Studio) VALUES (%s, %s, %s, %s, %s, %s, %s)"
anime_data = [
    ("Attack on Titan", "Finished Airing", "Humanity's last safe haven lies behind...", "Spring", 2013, "Crunchyroll", "Wit Studio"),
    ("Re:ZERO -Starting Life in Another World-", "Finished Airing", "Subaru immediately reawakens to a familiar scene...", "Spring", 2016, "Crunchyroll", "White Fox"),
    ("One Piece", "Currently Airing", "Gol D. Roger was known as the 'Pirate King'...", "Fall", 1999, "Netflix", "Toei Animation"),
    ("Black Clover", "Finished Airing", "Asta and Yuno were abandoned at the same church on the same day...", "Fall", 2017, "Crunchyroll", "Pierrot"),
    ("Kaguya-sama: Love is War", "Finished Airing", "At the renowned Shuchiin Academy, Miyuki Shirogane and Kaguya Shinomiya are the student body's top representatives...", "Winter", 2019, "Crunchyroll", "A-1 Pictures"),
    ("My Hero Academia", "Finished Airing", "The appearance of 'quirks,' newly discovered super powers, has been steadily increasing...", "Spring", 2016, "Crunchyroll", "Bones")
]
cursor.executemany(insert_query, anime_data)

# Commit changes.
mydb.commit()

# Insert data into ANIME_CHARACTER table
insert_query = "INSERT INTO ANIME_CHARACTER (Name, Biography, VoiceActor) VALUES (%s, %s, %s)"
character_data = [
    ("Eren Yeager", "Eren is Shingeki no Kyojin's protagonist.", "Yuki Kaji"),
    ("Mikasa Ackerman", "Mikasa is Eren's childhood friend, along with Armin.", "Ishikawa, Yui"),
    ("Levi Ackerman", "Levi is known as humanity's most powerful soldier.", "Kamiya, Hiroshi"),

    ("Emilia", "She is a silver-haired half-elf girl who is one of the candidates to become the next ruler in the royal election.", "Rie Takahashi"),
    ("Rem", "Rem is one of the twin maids working for Roswaal L Mathers.", "Inori Minase"),

    ("Luffy Monkey", "Luffy is the captain of the Straw Hat Pirates and is best friends with all of them and values them over all else.", "Mayumi Tanaka"),
    
    ("Asta", "Asta is an orphan who was left under the care of a church in the village of Hage.", "Shun Horie"),
    ("Yami Sukehiro", "Yami is the captain of the Black Bulls of the Magic Knights", "Junichi Suwabe"),

    ("Kaguya Shinomiya", "Vice president of the student council of Shuchiin Academy", "Aoi Koga"),
    ("Yuu Ishigami", "He is the treasurer of the student council of the Shuchiin Academy.", "Ryouta Suzuki"),
    ("Shouto Todoroki", "Shouto Todoroki is a student at Yuuei training to become a Pro Hero.\nQuirk: Half-Cold Half-Hot.", "Yuuki Kaji")
]
cursor.executemany(insert_query, character_data)

# Commit changes.
mydb.commit()

# Insert data into ANIME_GENRES table
insert_query = "INSERT INTO ANIME_GENRES (AnimeID, Genre) VALUES (%s, %s)" # Can also use f-strings
genres_data = [
    (1, "Action"), (1, "Fantasy"), (1, "Mystery"), (1, "Shounen"),
    (2, "Drama"), (2, "Fantasy"), (2, "Isekai"), (2, "Psychological"), (2, "Time Travel"),
    (3, "Shounen"), (3, "Action"), (3, "Adventure"), (3, "Fantasy"),
    (4, "Action"), (4, "Comedy"), (4, "Fantasy"),
    (5, "Romance"), (5, "Comedy"), (5, "School"), (5, "Psychological"),
    (6, "Action"), (6, "School"), (6, "Shounen")
]
cursor.executemany(insert_query, genres_data)

# Commit changes.
mydb.commit()

# Insert data into INCORPORATES table
insert_query = "INSERT INTO INCORPORATES (CharID, AnimeID, CharacterRole) VALUES (%s, %s, %s)"
incorporates_data = [
    (1, 1, "Main"), (2, 1, "Main"), (3, 1, "Supporting"),
    (4, 2, "Main"), (5, 2, "Supporting"),
    (6, 3, "Main"),
    (7, 4, "Main"), (8, 4, "Supporting"),
    (9, 5, "Main"), (10, 5, "Main"),
    (11, 6, "Supporting")
]
cursor.executemany(insert_query, incorporates_data)

# Commit changes.
mydb.commit()

# Insert data into EPISODE table
insert_query = "INSERT INTO EPISODE (Name, Length, Link, AnimeID) VALUES (%s, %s, %s, %s)"
episode_data = [
    # Attack on Titan 
    ("To You, in 2000 Years: The Fall of Shiganshina, Part 1", "00:24:09", "https://www.crunchyroll.com/watch/GR49GM4W6/to-you-2000-years-in-the-future--the-fall-of-zhiganshina-1", 1),
    ("That Day: The Fall of Shiganshina, Part 2", "00:24:09", "https://www.crunchyroll.com/watch/GRJQK1ZEY/that-day---the-fall-of-zhiganshina-2", 1),
    ("A Dim Light Amid Despair: Humanity's Comeback, Part 1", "00:24:09", "https://www.crunchyroll.com/watch/GRK5KXZ46/a-dim-light-in-the-darkness-of-despair---humanity-rises-again-1", 1),

    # Re:ZERO -Starting Life in Another World-
    ("The End of the Beginning and the Beginning of the End", "00:50:01", "https://www.crunchyroll.com/rezero-starting-life-in-another-world-/episode-1-re-start-of-this-world-696247", 2),
    ("Reunion with the Witch", "00:24:58", "https://aniwave.to/watch/rezero-starting-life-in-another-world.jv78/ep-1", 2),
    ("Starting Life from Zero in Another World", "00:25:07", "https://aniwave.to/watch/rezero-starting-life-in-another-world.jv78/ep-3", 2),

    # One Piece
    ("Romance Dawn", "00:24:07", "https://www.netflix.com/", 3),

    # Black Clover
    ("Asta and Yuno", "00:23:55", "https://www.crunchyroll.com/watch/G50UZ4E20/asta-and-yuno", 4),
    ("The Boys' Promise", "00:23:55", "https://www.crunchyroll.com/watch/GWDU8KPPV/the-boys-promise", 4),
    ("To the Royal Capital of the Clover Kingdom!", "00:23:55", "https://www.crunchyroll.com/watch/GG1U2EDD5/to-the-royal-capital-of-the-clover-kingdom", 4),

    # Kaguya-sama: Love is War
    ("I Will Make You Invite Me to a Movie / Kaguya Wants to Be Stopped / Kaguya Wants It", "00:24:33", "https://www.crunchyroll.com/watch/GD9UVWXGX/i-will-make-you-invite-me-to-a-movie--kaguya-wants-to-be-stopped--kaguya-wants-it", 5),
    ("Kaguya Wants to Trade / Chika Wants to Go Somewhere / Miyuki Wants to Hide His Ignorance", "00:24:00", "https://www.crunchyroll.com/watch/G0DUN08NG/kaguya-wants-to-trade--chika-wants-to-go-somewhere--miyuki-wants-to-hide-his-ignorance", 5),
    ("Miyuki Shirogane Still Hasn't Done It / Kaguya Wants to Be Figured Out / Kaguya Wants to Walk", "00:23:59", "https://www.crunchyroll.com/watch/G14U4EM4Z/miyuki-shirogane-still-hasnt-done-it--kaguya-wants-to-be-figured-out--kaguya-wants-to-walk", 5),

    # My Hero Academia
    ("Izuku Midoriya: Origin", "00:24:33", "https://www.crunchyroll.com/watch/G31UXQ3NP/izuku-midoriya-origin", 6),
    ("What It Takes to Be a Hero", "00:24:33", "https://www.crunchyroll.com/watch/GPWUKE590/what-it-takes-to-be-a-hero", 6),
    ("Roaring Muscles", "00:24:33", "https://www.crunchyroll.com/watch/G8WUNEWJE/roaring-muscles", 6)
]
cursor.executemany(insert_query, episode_data)

# Commit changes.
mydb.commit()

# Disconnect from the server
cursor.close()
mydb.close()
