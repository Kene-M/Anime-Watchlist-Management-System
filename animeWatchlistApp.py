"""
Author: Kenechukeu Maduabum
Date: May 3th, 2024
Description:
Implemented a Database Application for allowing multiple users organize and track the anime they watch 
using MySQL and Python. The "tkinter" package of python is also to implement a GUI for the application.
"""

import tkinter
import sv_ttk
from tkinter import ttk # Used to create the GUI applications with the effects of
                # modern graphics which cannot be achieved using only tkinter.
from tkinter import messagebox
import mysql.connector # For connecting to mysql
from datetime import date # For fetching today's day.

# Create Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword"
)

# preparing a cursor object
cursor = mydb.cursor()
cursor.execute("USE ANIME_MANAGEMENT")

# Function 1: Search_Anime
# second_frame comes from open_searchpage
#def search_anime(second_frame, rating, genres, studios, statuses, seasons):
def search_anime(user_id, second_frame, rating_combo, genre_list, studio_list, status_list, season_list):
    # Retrieve values from comboxes and listboxes in second_frame
    rating = rating_combo.get()

    selected_indices = genre_list.curselection()
    genres = [genre_list.get(index) for index in selected_indices]
    if genres is None: genres = []

    selected_indices = studio_list.curselection()
    studios = [status_list.get(index) for index in selected_indices]
    if studios is None: studios = []

    selected_indices = status_list.curselection()
    statuses = [status_list.get(index) for index in selected_indices]
    if statuses is None: statuses = []

    selected_indices = season_list.curselection()
    seasons = [season_list.get(index) for index in selected_indices]
    if seasons is None: seasons = []

    genre_anime_id_set = set()
    if genres:
        # Step 1 & 2: Record AnimeIDs that include all specified genres
        query = f"""
            SELECT AnimeID
            FROM ANIME_GENRES
            WHERE Genre IN {tuple(genres)}
            GROUP BY AnimeID
            HAVING COUNT(Genre) = {len(genres)}"""

        cursor.execute(query)
        results = cursor.fetchall()
        #anime_ids = [row[0] for row in cursor.fetchall()]
        genre_anime_id_set.update(row[0] for row in results) # Iterates through the list, adds and eliminates duplicates

    # Step 3: Record AnimeIDs for specified studios
    studio_anime_id_set = set()
    for studio in studios:
        cursor.execute("SELECT ID FROM ANIME WHERE Studio = %s", (studio,))
        results = cursor.fetchall()
        studio_anime_id_set.update(row[0] for row in results)

    # Step 4: Record AnimeIDs for specified statuses
    status_anime_id_set = set()
    for status in statuses:
        cursor.execute("SELECT ID FROM ANIME WHERE Status = %s", (status,))
        results = cursor.fetchall()
        status_anime_id_set.update(row[0] for row in results)

    # Step 5: Record AnimeIDs for specified seasons
    season_anime_id_set = set()
    for season in seasons:
        season_and_year_list = season.split()
        cursor.execute("SELECT ID FROM ANIME WHERE Season = %s AND Year = %s", tuple(season_and_year_list))
        results = cursor.fetchall()
        season_anime_id_set.update(row[0] for row in results)

    # Step 6: Record AnimeIDs with average rating >= specified rating
    #TODO Build on this, need to find average rating of all anime -> filter each id using rating
    """if rating != "Select":
        query = "SELECT ID FROM REVIEW WHERE Rating >= %s"
        cursor.execute(query, (rating,))
        results = cursor.fetchall()
        for anime_id in results:
            anime_ids.add(anime_id[0])"""

    """filtered_anime_ids = set()
    for anime_id in anime_ids:
        cursor.execute("SELECT AVG(Rating) FROM REVIEW WHERE AnimeID = %s", (anime_id,))
        avg_rating = cursor.fetchone()[0]
        if avg_rating is not None and avg_rating >= rating:
            filtered_anime_ids.add(anime_id)"""

    # Step 7 & 8: Retrieve anime information for resulting AnimeIDs and sort by name.
    anime_ids = set() # Distinct anime_ids fitting filter requirements

    # Check if all are empty sets: Inersection is empty set
    if not genre_anime_id_set and not studio_anime_id_set and not status_anime_id_set and not season_anime_id_set:
        anime_ids = set()
    # Find intersection: If some are empty, exclude them from consideration
    else:
        # '&' is shortcut for intersection()
        if genre_anime_id_set:
            if not anime_ids:
                anime_ids = genre_anime_id_set 
        if studio_anime_id_set:
            if not anime_ids:
                anime_ids = studio_anime_id_set 
            elif not studio_anime_id_set:
                anime_ids = anime_ids & studio_anime_id_set
        if status_anime_id_set:
            if not anime_ids:
                anime_ids = status_anime_id_set 
            elif not status_anime_id_set:
                anime_ids = anime_ids & status_anime_id_set
        if season_anime_id_set:
            if not anime_ids:
                anime_ids = season_anime_id_set 
            elif not season_anime_id_set:
                anime_ids = anime_ids & season_anime_id_set
    
    anime_info = []
    for anime_id in anime_ids: 
        query = "SELECT ID, Name, Status, Studio FROM ANIME WHERE ID = %s ORDER BY Name"
        cursor.execute(query, (anime_id,))
        anime_info.append(cursor.fetchone())

    # Step 9: Display filtered anime information
    if not anime_info:
        label = ttk.Label(second_frame, text = "No results for the specified query")
        label.pack(padx = 2, pady = 5)
    else:
        new_frame = ttk.Frame(second_frame) 
        label = ttk.Label(new_frame, text = "") # Empty frame
        label.pack(pady = 5)
        label = ttk.Label(new_frame, text = "Title", width = 65) # 'width' sets the widget to X chars wide
        label.pack(side = "left", padx = 2, pady = 5)
        label = ttk.Label(new_frame, text = "Status of Completion", width = 25) 
        label.pack(side = "left", padx = 2, pady = 5)
        label = ttk.Label(new_frame, text = "Studio", width = 25)
        label.pack(side = "left", padx = 2, pady = 5)
        new_frame.pack(fill = "x")

        for (anime_id, name, status, studio) in anime_info:
            new_frame = ttk.Frame(second_frame) 
            label = ttk.Label(new_frame, text = f"{name}", width = 65) 
            label.pack(side = "left", padx = 2, pady = 5)
            label = ttk.Label(new_frame, text = f"{status}", width = 25) 
            label.pack(side = "left", padx = 2, pady = 5)
            label = ttk.Label(new_frame, text = f"{studio}", width = 25)
            label.pack(side = "left", padx = 2, pady = 5)

            # Pack a button for adding to list
            # NOTE lambda fucntion has default arguments to force early binding. Late binding (on button click) done if unspecified.
            button = ttk.Button(new_frame, text = "Add", command = lambda user_id = user_id, anime_id = anime_id: manage_list(user_id,
                            anime_id, rating=None, watch_status=None, num_eps_watched=None, operation="add"))
            button.pack(padx = 2, pady = 5)
            new_frame.pack(fill = "x")

# Function 2: Manage_List
def manage_list(user_id, anime_id, rating=None, watch_status=None, num_eps_watched=None, operation="add"):
    # Step 1: Retrieve list ID for user
    cursor.execute("SELECT ID FROM LIST WHERE UserID = %s", (user_id,))
    list_id = cursor.fetchone()[0]

    if operation == "add":
        # Step 2: Insert new anime entry in CONTAINS table

        # Check if anime entry already in list
        query = "SELECT ListID, AnimeID FROM CONTAINS WHERE ListID = %s AND AnimeID = %s"
        cursor.execute(query, (list_id, anime_id))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Failure", "Anime already in watchlist.")

        else:
            query = "INSERT INTO CONTAINS (ListID, AnimeID, WatchStatus, NumEpsWatched) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (list_id, anime_id, watch_status or "Plan to Watch", num_eps_watched or 0))
            mydb.commit()

            # Step 2ii: If rating specified, add row to REVIEW table
            if rating is not None:
                cursor.execute("INSERT INTO REVIEW (UserID, AnimeID, Rating) VALUES (%s, %s, %s)",
                               (user_id, anime_id, rating))
            mydb.commit()
            messagebox.showinfo("Success", "Anime added to watchlist.")

    elif operation == "remove":
        # Step 3: Remove specified anime entry from CONTAINS table
        cursor.execute("DELETE FROM CONTAINS WHERE ListID = %s AND AnimeID = %s", (list_id, anime_id))
        # Step 3ii: Remove corresponding review from REVIEW table
        cursor.execute("DELETE FROM REVIEW WHERE UserID = %s AND AnimeID = %s", (user_id, anime_id))
        db.commit()
        messagebox.showinfo("Success", "Anime removed from watchlist.")

    elif operation == "update":
        # Step 4i: Update rating in REVIEW table
        if rating is not None:
            cursor.execute("UPDATE REVIEW SET Rating = %s WHERE UserID = %s AND AnimeID = %s",
                           (rating, user_id, anime_id))
        # Step 4ii: Update watch status in CONTAINS table
        if watch_status is not None:
            cursor.execute("UPDATE CONTAINS SET WatchStatus = %s WHERE ListID = %s AND AnimeID = %s",
                           (watch_status, list_id, anime_id))
            # Step 4ii-1: If Completed status, update NumEpsWatched
            if watch_status == "Completed":
                cursor.execute("SELECT MAX(Episode.ID) FROM EPISODE INNER JOIN ANIME ON EPISODE.AnimeID = ANIME.ID WHERE ANIME.ID = %s", (anime_id,))
                max_eps = cursor.fetchone()[0]
                cursor.execute("UPDATE CONTAINS SET NumEpsWatched = %s WHERE ListID = %s AND AnimeID = %s",
                               (max_eps, list_id, anime_id))
        # Step 4iii: Update number of episodes watched in CONTAINS table
        if num_eps_watched is not None:
            cursor.execute("SELECT MAX(Episode.ID) FROM EPISODE INNER JOIN ANIME ON EPISODE.AnimeID = ANIME.ID WHERE ANIME.ID = %s", (anime_id,))
            max_eps = cursor.fetchone()[0]
            if max_eps >= num_eps_watched:
                cursor.execute("UPDATE CONTAINS SET NumEpsWatched = %s WHERE ListID = %s AND AnimeID = %s",
                               (num_eps_watched, list_id, anime_id))
            else:
                messagebox.showerror("Error", "Number of episodes watched exceeds total episodes.")
                return
        db.commit()
        messagebox.showinfo("Success", "Watchlist updated.")

    elif operation == "display":
        # Step 5i: Retrieve anime information for specified list ID
        cursor.execute("SELECT ANIME.Name, CONTAINS.WatchStatus, CONTAINS.NumEpsWatched, REVIEW.Rating FROM ANIME "
                       "INNER JOIN CONTAINS ON ANIME.ID = CONTAINS.AnimeID "
                       "LEFT JOIN REVIEW ON ANIME.ID = REVIEW.AnimeID "
                       "WHERE CONTAINS.ListID = %s", (list_id,))
        anime_info = cursor.fetchall()

        # Create the list window
        list_window = tkinter.Toplevel(window)
        list_window.title ("Anime Watchlist Management System")
        list_window.geometry("1000x475")
        #scroll_bar = ttk.Scrollbar(list_window) 
        #scroll_bar.pack(side = tkinter.RIGHT, fill = tkinter.Y)

        # Create a main frame
        main_frame = ttk.Frame(list_window)
        main_frame.pack(fill=tkinter.BOTH, expand=1)

        # Create a canvas inside the main frame.
        my_canvas = tkinter.Canvas(main_frame)
        my_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

        # Add a scrollbar to the main frame
        my_scrollbar = ttk.Scrollbar(main_frame, orient=tkinter.VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Configure the canvas to use the scroll bar
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind(
            '<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all"))
        )
        # Create ANOTHER frame INSIDE the canvas
        second_frame = ttk.Frame(my_canvas) # Will add all further widgets to this.

        # Add the new frame to a window inside the canvas
        my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        # Give option to go back to profile
        profile_button = ttk.Button(second_frame, text = "Go to profile", command = lambda: report_statistics(user_id))
        profile_button.pack(pady = 5)

        # Give option to go to search page/Add anime
        search_button = ttk.Button(second_frame, text = "Add to List (Go to Search)", command = lambda: open_searchpage(user_id))
        search_button.pack(pady = 5)

        # Display the information: Header info
        cursor.execute("SELECT Title FROM LIST WHERE ID = %s", (list_id,))
        title = cursor.fetchone()[0]
        label = ttk.Label(second_frame, text = f"{title.center(100)}")
        label.pack(pady = 10)
        cursor.execute("SELECT JoinDate FROM USER WHERE ID = %s", (user_id,))
        join_date = cursor.fetchone()[0]
        label = ttk.Label(second_frame, text = f"Join Date: {join_date}")
        label.pack(pady = 10)

            # Create another frame to fill a horizontal row (for each entry)
        new_frame = ttk.Frame(second_frame) 
        label = ttk.Label(new_frame, text = "Title", width = 65) # 'width' sets the widget to X chars wide
        label.pack(side = "left", padx = 2, pady = 5)
        label = ttk.Label(new_frame, text = "Status", width = 20) 
        label.pack(side = "left", padx = 2, pady = 5)
        label = ttk.Label(new_frame, text = "Episodes", width = 15)
        label.pack(side = "left", padx = 2, pady = 5)
        label = ttk.Label(new_frame, text = "Score", width = 15)
        label.pack(side = "left", padx = 2, pady = 5)
        new_frame.pack(fill = "x")

        # Display the information: List entry info
        for (name, status, num_eps_watched, rating) in anime_info:
            new_frame = ttk.Frame(second_frame)
            label = ttk.Label(new_frame, text = f"{name}", width = 65)
            label.pack(side = "left", padx = 2, pady = 5)
            label = ttk.Label(new_frame, text = f"{status}", width = 20)
            label.pack(side = "left", padx = 2, pady = 5)
            label = ttk.Label(new_frame, text = f"{num_eps_watched}", width = 15)
            label.pack(side = "left", padx = 2, pady = 5)
            label = ttk.Label(new_frame, text = f"{rating}", width = 15)
            label.pack(side = "left", padx = 2, pady = 5)
            new_frame.pack(fill = "x")

        list_window.mainloop()

# Function 3: Review_Anime
def review_anime(user_id, anime_id, rating=None, comment=None, operation="create"):
    pass

# Function 4: Report_Statistics
def report_statistics(user_id):
    # Create user profile window
    user_window = tkinter.Toplevel(window)
    user_window.title ("Anime Watchlist Management System")
    user_window.geometry("1000x475")
    #scroll_bar = ttk.Scrollbar(user_window) 
    #scroll_bar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    
    # Give option to go back to search page/add anime
    search_button = ttk.Button(user_window, text = "Add to List (Go to Search)", command = lambda: open_searchpage(user_id))
    search_button.pack(pady = 5)

    # Give option to view watchlist
    search_button = ttk.Button(user_window, text = "View Watchlist", command = lambda: manage_list(user_id, None, operation = "display"))
    search_button.pack(pady = 5)

    # Step 1: Retrieve list ID for user
    query = "SELECT ID FROM LIST WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    list_id = cursor.fetchone()[0]

    # Step 2: Display total number of anime watched
    query = "SELECT COUNT(*) FROM CONTAINS WHERE ListID = %s"
    cursor.execute(query, (list_id,))
    total_anime_watched = cursor.fetchone()[0]

    # Step 3: Display total number of watched episodes
    query = "SELECT SUM(NumEpsWatched) FROM CONTAINS WHERE ListID = %s"
    cursor.execute(query, (list_id,))
    total_eps_watched = cursor.fetchone()[0]

    # Step 4: Display average rating
    query = "SELECT AVG(Rating) FROM REVIEW WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    avg_rating = cursor.fetchone()[0]

    # Step 5: Display watch status of anime in list
    query = "SELECT WatchStatus, COUNT(*) FROM CONTAINS WHERE ListID = %s GROUP BY WatchStatus"
    cursor.execute(query, (list_id,))
    watch_status_info = cursor.fetchall() # Fetch a list of tuples

    # Step 6: Display statistics
    label = ttk.Label(user_window, text = "Statistics")
    label.pack()
    label = ttk.Label(user_window, text = f"Total number of anime entries: {total_anime_watched}")
    label.pack()
    label = ttk.Label(user_window, text = f"Total number of watched episodes: {total_eps_watched}")
    label.pack()
    label = ttk.Label(user_window, text = f"Average rating: {avg_rating}")
    label.pack()

    # TODO USE A DICTIONARY TO INCLUDE ALL STATUS PROMPTS WHEN None (Use season, year above as a reference)


    if not watch_status_info:
        status_prompt = "Watching: None\nCompleted: None\nOn-Hold: None\nDropped: None"
        label = ttk.Label(user_window, text = status_prompt)
        label.pack()

    for (status, count) in watch_status_info:
        label = ttk.Label(user_window, text = f"{status}: {count}")
        label.pack()

    user_window.mainloop()
    
# Function to create a new Toplevel window for searching anime.
def open_searchpage(user_id):
    # Create window.
    search_window = tkinter.Toplevel(window)
    search_window.title ("Anime Watchlist Management System")
    search_window.geometry("1000x475")
    #scroll_bar = ttk.Scrollbar(search_window) 
    #scroll_bar.pack(side = tkinter.RIGHT, fill = tkinter.Y) 

    # Create a main frame
    main_frame = ttk.Frame(search_window)
    main_frame.pack(fill=tkinter.BOTH, expand=1)

    # Create a canvas inside the main frame.
    my_canvas = tkinter.Canvas(main_frame)
    my_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

    # Add a scrollbar to the main frame
    my_scrollbar = ttk.Scrollbar(main_frame, orient=tkinter.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    # Configure the canvas to use the scroll bar
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind(
        '<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all"))
    )
    # Create ANOTHER frame INSIDE the canvas
    second_frame = ttk.Frame(my_canvas) # Will add all further widgets to this.

    # Add the new frame to a window inside the canvas
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    profile_button = ttk.Button(second_frame, text = "Go to profile", command = lambda: report_statistics(user_id))
    profile_button.pack(pady = 5) # pady for giving some vertical border space.

    # Get input for searches.
    label = ttk.Label(second_frame, text = "Please specify the minimum rating you want to use as a filter: ")
    label.pack(pady=10) 

    # Create a Combobox widget (drop-down selection menu) to get rating.
    rating_combo = ttk.Combobox(second_frame, values=["Select", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    rating_combo.pack(pady=5)
    rating_combo.set("Select") # Set default value

    # Create a listbox (allows user to accept any number of options) to get selection of genres.
    # (exportselection = "False") makes clicking other listboxes not deselect this listbox option.
    label = ttk.Label(second_frame, text = "Please specify all the genres you want to use as a filter: ")
    label.pack(pady=10)
    genre_list = tkinter.Listbox(second_frame, selectmode="multiple", height = 8, exportselection = "False")
    genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
        'Mystery', 'School', 'Romance', 'Slice of Life', 'Supernatural', 'Isekai',
        'Psychological', 'Shoujo', 'Shounen', 'Sci-Fi', 'Time Travel', 'Video Game']

    for genre in genres: 
        # Insert values into the listbox
        genre_list.insert(tkinter.END, genre)
    genre_list.pack(pady=5)

    # Create a listbox to get selection of studios.
    label = ttk.Label(second_frame, text = "Please specify all the studios you want to use as a filter: ")
    label.pack(pady=10)
    studio_list = tkinter.Listbox(second_frame, selectmode="multiple", height = 8, exportselection = "False")
    query = "SELECT DISTINCT Studio FROM ANIME"
    cursor.execute(query)
    studios = cursor.fetchall()

    for studio in studios:
        studio_list.insert(tkinter.END, studio)
    studio_list.pack(pady=5)

    # Create a listbox to get selection of statuses.
    label = ttk.Label(second_frame, text = "Please specify all the statuses you want to use as a filter: ")
    label.pack(pady=10)
    status_list = tkinter.Listbox(second_frame, selectmode="multiple", height = 3, exportselection = "False")

    for status in ["Not Aired Yet", "Currently Airing", "Finished Airing"]:
        status_list.insert(tkinter.END, status)
    status_list.pack(pady=5)

    # Create a listbox to get selection of seasons.
    label = ttk.Label(second_frame, text = "Please specify all the aired seasons you want to use as a filter: ")
    label.pack(pady=10)
    season_list = tkinter.Listbox(second_frame, selectmode="multiple", height = 8, exportselection = "False")
    #seasons = ["Winter", "Spring", "Summer", "Fall"]
    query = "SELECT DISTINCT Season, Year FROM ANIME ORDER BY Year DESC"
    cursor.execute(query)
    seasons = cursor.fetchall()
    
    season_dict = {}
    for season, year in seasons: 
        if year in season_dict:
            season_dict[year].append(season)
        else:
            season_dict[year] = season
    for year, seasons in season_dict.items(): # Order the seasons within years by descending order
        if "Fall" in seasons:
            season_list.insert(tkinter.END, f"Fall {year}")
        if "Summer" in seasons:
            season_list.insert(tkinter.END, f"Summer {year}")
        if "Spring" in seasons:
            season_list.insert(tkinter.END, f"Spring {year}")
        if "Winter" in seasons:
            season_list.insert(tkinter.END, f"Winter {year}")
    season_list.pack(pady=5)

    # Retrieve all the user's specified information, and define the search button event.

    # Button to filter based on provided information.
    search_button = ttk.Button(second_frame, text = "Search", 
                    command = lambda: search_anime(user_id, second_frame, rating_combo, genre_list, studio_list, status_list, season_list))
    search_button.pack()

    # Listen for events until closed manually.
    search_window.mainloop()

# Function 5: validate login (upon button click)
def validate_login():
    # Check if the provided username exists in the database
    username = entry1.get() # Get text from entry
    query = "SELECT Name FROM USER WHERE Name = %s"
    cursor.execute(query, (username,))

    # Fetch the result
    result = cursor.fetchone() 

    # If the user exists, then it is a login
    if result:
        username = result[0] #'0' because a singelton tuple is fetched.
        messagebox.showinfo("Login Successful", f"Login Successful\nWelcome, {username}!")
    
    # If the user doesn't exist, then it is an account creation.
    else:
        insertion = "INSERT INTO USER (Name, JoinDate) VALUES (%s, %s)"
        today = date.today() # Extract today's date.
        cursor.execute(insertion, (username, today))
        mydb.commit()

        messagebox.showinfo("Account Creation Successful", f"Account Created\nWelcome, {username}!")

    # Get the user id.
    query = "SELECT ID FROM USER WHERE Name = %s"
    cursor.execute(query, (username,))
    user_id = cursor.fetchone()[0]

    # Transition windpws
    open_searchpage(user_id)

# Create a (root) window
window = tkinter.Tk()
window.title ("Anime Watchlist Management System")
window.geometry("1000x475") # Make the initial window bigger

num_windows = 0 # TODO later, to manage multiple windows

# Create a Label widget as a child to the root window.
greeting = ttk.Label(window, text="Welcome to AWMS!")
greeting.pack(pady = 5) # add the button to the window

namePrompt = ttk.Label(window, text = "Please enter your username: ")
namePrompt.pack(pady = 5) #

# Create an entry - for user text input.
entry1 = ttk.Entry(window)
entry1.pack(pady = 5) # pady for giving some vertical border space.

# Create a Button widget. Command is a function that defines the button click.
# Define an anonymous function (using lambda) that calls a function to handle the button click event.
button = ttk.Button(window, text = "Login", command = lambda: validate_login())
button.pack(pady = 5) # add the button to the window

# Set the modern, dark theme of the GUI
sv_ttk.set_theme("dark")

# Listen for events like button clicks.
window.mainloop()



"""
# Make root/login window unvisible
#window.withdraw()
# Make root/login window visible
#window.deiconify()

# Destroy window
#window.destroy()

# Keep track of open Toplevel windows
open_windows = []

def on_closing():
    global open_windows
    root.quit()  # Stop the main event loop

def open_login_window():
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    open_windows.append(login_window)  # Add the new window to the list

    # Add widgets and layouts for the login window
    # ...

    login_window.grab_set()

    # Bind the close event to remove the window from the list
    login_window.protocol("WM_DELETE_WINDOW", lambda: remove_window(login_window))

    # Hide the root window
    root.withdraw()

def remove_window(window):
    global open_windows
    open_windows.remove(window)  # Remove the window from the list
    window.destroy()  # Destroy the window

    # If this was the last open window, stop the main event loop
    if not open_windows:
        root.quit()
"""