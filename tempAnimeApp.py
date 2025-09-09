"""
Author: Kenechukwu Maduabum
Date:
Description:
Implemented a Database Application for allowing multiple users organize and track the anime they watch using MySQL 
RDBMS and Python programming language. The "PyQt6" package of python is also to implement a GUI for the application.
"""
# NOTE: MAKE SYNOPSIS, etc BE 1500+ CHARS | ADD DEFAULT VALUE FOR SYNOPSIS (should still be NOT NULL)
#       Make Black Clover a shounen
#       Make self.ui.gridLayout_# names more meaningful (find-replace)

from PyQt6.QtWidgets import (
    QCheckBox, # Checkbox widget allowing mulliple clicks for selecton/deselection.
    QListWidget, # allows user to accept any number of options
    QListWidgetItem, # a QListWidget option
    QComboBox, # drop-down selection menu widget
    QStackedWidget, # Allows for easy switching between widgets (useful for multiple pages in application)
    QPushButton, #
    QLabel, #
    QLineEdit, # Allows the user to enter one line of input text.
    #QTextEdit,
    QSizePolicy, # .Policy.Expanding - For allowing a widget fill the entire space it was allocated
    QWidget, # Used as a container to pack other widgets in
    QMessageBox, #
    QGridLayout, # Allows for placing widgets in a grid format
    QVBoxLayout, # Allows for placing widgets in a vertical format
    QHBoxLayout, # Allows for placing widgets in a horizontal format
    QAbstractItemView, # QAbstractItemView.MultiSelection to enable multi selection for QListWidget
    QMainWindow, #
    QApplication # manages application-wide resources and settings.
)
from PyQt6.QtCore import (
    Qt # Qt.Alignment: Has alignment value for labels | Qt.CheckState: For checking state of QCheckBox 
        # | Qt.CursorShape: To change shape of cursor when hovering a button | Qt.TextElideMode: To elide text ("...") if it is too long
)
from PyQt6.QtGui import (
    QFont # For formatting the font of a label
)
import sys
import mysql.connector # For connecting to mysql
from datetime import date # For fetching today's day.
import math # For using ceil function

from animeAppUI import Ui_MainWindow # File/class containing template pages of the GUI

class MainWindow(QMainWindow):
    def __init__(self):
        # Initialize QMainWindow features for this class, and set up the UI file window as an instance attribute.
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Define the Qt StyleSheet (QSS - similar to CSS) for all the buttons - underline text when hovered over.
        stylesheet = """
        QPushButton:hover {
            color: inherit;
            text-decoration: underline;
        }
        """
        # Apply the stylesheet to the window
        self.setStyleSheet(stylesheet)

        # Define a signal and slot for handilng the button click event for username submission (the signal is "clicked", the slot is the function/handler)
        # Define an anonymous function (using lambda) that calls a function to handle the button click event.
        self.ui.login_button.clicked.connect(lambda: self.validate_login())

        # Alternatively handle username submission when enter key is pressed from the QLineEdit
        self.ui.user_entry.returnPressed.connect(lambda: self.validate_login())  # The signal is "returnPressed".

        # Set up necessary widgets
        self.pagination_widget = QWidget() # Widget to set up pagination when displaying filtered anime searches
        self.ui.gridLayout_5.addWidget(self.pagination_widget, 11, 0, 1, 7)
        self.pagination_layout = QVBoxLayout()
        self.pagination_widget.setLayout(self.pagination_layout)
        self.anime_display_widget = None # Widget containing information of filtered anime searches

        # -------------FUTURE-----------------------------
        # Enable copying from all elements of QMainWindow
        # Add password label and LineEdit
        # setEchoMode() FOR PASSWORD BLUR.
        # Add more constraints and checking for username and password (too short, too long, already exists, etc.)
        # QMessageMox features (like new user found - account creation Y/N popup)

        # Show the main window
        self.show()
        #self.showMaximized() # Full screen with title bar

    # Function to validate user login (upon button click).
    def validate_login(self):
        # Check if the provided username exists in the database
        username = self.ui.user_entry.text() # Get text from LineEdit (allows user to enter line of text)
        query = "SELECT Name FROM USER WHERE Name = %s"
        cursor.execute(query, (username,))

        # Fetch the result
        result = cursor.fetchone() 

        # If the user exists, then it is a login
        if result:
            username = result[0] #'[0]' because a singelton tuple is fetched.
            #messagebox.showinfo("Login Successful", f"Login Successful\nWelcome, {username}!")

        # If the user doesn't exist, then it is an account creation.
        else:
            insertion = "INSERT INTO USER (Name, JoinDate) VALUES (%s, %s)"
            today = date.today() # Extract today's date.
            cursor.execute(insertion, (username, today))
            mydb.commit()

            #messagebox.showinfo("Account Creation Successful", f"Account Created\nWelcome, {username}!")

        # Get the user id.
        query = "SELECT ID FROM USER WHERE Name = %s"
        cursor.execute(query, (username,))
        self.user_id = cursor.fetchone()[0]

        # Get the list id.
        query = "SELECT ID FROM LIST WHERE UserID = %s"
        cursor.execute(query, (self.user_id,))
        self.list_id = cursor.fetchone()[0]

        # Transition pages
        self.open_search_page(True)

    # This function transitions to the search page by changing the current widget of the stacked widget.
    def open_search_page(self, after_login = False):
        self.ui.stackedWidget.setCurrentWidget(self.ui.search_page)

        # Ensure that widgets are created and added to search page only after login.
        if not after_login: return

        # Add the button to go the profile page, and define a signal-slot handler.
        self.ui.profile_button.setFixedSize(100, 50)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.ui.profile_button.setFont(font)
        self.ui.profile_button.clicked.connect(lambda: self.report_statistics())
        self.ui.gridLayout_5.addWidget(self.ui.profile_button, 0, 6, 1, 1) # (row, col, rowspan, colspan)

        # Create a label
        label = QLabel("Filters", alignment = Qt.AlignmentFlag.AlignLeft)
        # OR label.setText("Filters") -> label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        self.ui.gridLayout_5.addWidget(label, 1, 0, 1, 7)

        # Get input for searches.
        
        # Create a QComboBox widget to get selected rating.
        label = QLabel("Rating")
        label.setFixedWidth(100)
        self.ui.gridLayout_5.addWidget(label, 2, 0)
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["Select", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.rating_combo.setFixedWidth(100)
        self.ui.gridLayout_5.addWidget(self.rating_combo, 2, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        # Create a QComboBox widget to get selected status.
        label = QLabel("Status")
        label.setFixedWidth(100)
        self.ui.gridLayout_5.addWidget(label, 3, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Select", "Not Aired Yet", "Currently Airing", "Finished Airing"])
        self.status_combo.setFixedWidth(120)
        self.ui.gridLayout_5.addWidget(self.status_combo, 3, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        # Create a QListWidget to get selection of studios.
        label = QLabel("Studios", alignment = Qt.AlignmentFlag.AlignTop)
        label.setFixedWidth(110)
        self.ui.gridLayout_5.addWidget(label, 4, 0)
        self.studio_list = QListWidget()
        self.studio_list.setWordWrap(True) # Enable word wrapping for every item in list

            # Set the selection mode to allow multiple selections
        self.studio_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        query = "SELECT DISTINCT Studio FROM ANIME ORDER BY Studio"
        cursor.execute(query)
        studios = cursor.fetchall()

        for studio in studios:
            listWidgetItem = QListWidgetItem(studio[0]) # OR x = QListWidgetItem(studio[0], parent = self.studio_list)
            self.studio_list.addItem(listWidgetItem)    #

            # Restrict the height - Calculate the total height for visible items
        item_height = self.studio_list.sizeHintForRow(0) # Get the height of a single item
        total_height = item_height * 6
        self.studio_list.setFixedSize(250, total_height)
        self.ui.gridLayout_5.addWidget(self.studio_list, 4, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        # Create a QListWidget to get selection of seasons.
        label = QLabel("Seasons", alignment = Qt.AlignmentFlag.AlignTop)
        label.setFixedWidth(100)
        self.ui.gridLayout_5.addWidget(label, 5, 0)
        self.season_list = QListWidget()
        
            # Set the selection mode to allow multiple selections
        self.season_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        #seasons = ["Winter", "Spring", "Summer", "Fall"]
        query = "SELECT DISTINCT Season, Year FROM ANIME ORDER BY Year DESC"
        cursor.execute(query)
        seasons = cursor.fetchall()
    
        season_dict = {}
        for season, year in seasons: # Add the distinct season, year in dict
            if year in season_dict:
                season_dict[year].append(season)
            else:
                season_dict[year] = season
        for year, seasons in season_dict.items(): # Order the seasons within years by descending order
            if "Fall" in seasons:
                listWidgetItem = QListWidgetItem(f"Fall {year}", parent = self.season_list)
            if "Summer" in seasons:
                listWidgetItem = QListWidgetItem(f"Summer {year}", parent = self.season_list)
            if "Spring" in seasons:
                listWidgetItem = QListWidgetItem(f"Spring {year}", parent = self.season_list)
            if "Winter" in seasons:
                listWidgetItem = QListWidgetItem(f"Winter {year}", parent = self.season_list)
        
            # Restrict the height - Calculate the total height for visible items
        item_height = self.season_list.sizeHintForRow(0) # Get the height of a single item
        total_height = item_height * 6
        self.season_list.setFixedSize(100, total_height)
        self.ui.gridLayout_5.addWidget(self.season_list, 5, 1, alignment = Qt.AlignmentFlag.AlignLeft)

        # Group QCheckBoxes to get inclusive/exclusive selection of genres.
            # Group checkboxes in a widget
        self.genre_widget = QWidget()
        self.genre_layout = QGridLayout()

        label = QLabel("Genres")
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        self.ui.gridLayout_5.addWidget(label, 6, 0)
        label = QLabel("Click once to exclude, twice to include")
        self.ui.gridLayout_5.addWidget(label, 7, 0, 1, 7)
      
        self.genre_options = ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
            'Mystery', 'School', 'Romance', 'Slice of Life', 'Supernatural', 'Isekai',
            'Psychological', 'Shoujo', 'Shounen', 'Sci-Fi', 'Time Travel', 'Video Game']
        self.genre_checkboxes = []
        row = 0
        col = 0

            # Create a QCheckBox for each genre
        for genre in self.genre_options: 
            checkbox = QCheckBox(genre)
            checkbox.setTristate(True) # Enabling trisatate gives the checkbox 3 selection modes (inclusive/exclusive/neither)
            self.genre_checkboxes.append(checkbox)
            self.genre_layout.addWidget(checkbox, row, col)
            col += 1

            if col == 5:
                row += 1
                col = 0
        self.genre_widget.setLayout(self.genre_layout)
        self.ui.gridLayout_5.addWidget(self.genre_widget, 9, 0, 1, 7)

        # Retrieve all the user's specified information, and define the search button signal/slot.

        # Button to filter based on provided information.
        self.ui.filter_button.setFixedSize(80, 40)
        font = QFont()
        font.setPointSize(14)
        self.ui.filter_button.setFont(font)
        self.ui.filter_button.clicked.connect(lambda: self.search_anime())
        self.ui.gridLayout_5.addWidget(self.ui.filter_button, 10, 0, 1, 7, alignment=Qt.AlignmentFlag.AlignCenter) # Center button within colspan

    # This function displays a list of anime information, based off the user provided filters. 
    def search_anime(self):
        # Create a widget within the scroll area widget of search page to display anime information.
            # QStackedWidget allows for overriding previous display widget, when button clicked multiple times.
        """if self.anime_display_widget is not None:
            self.anime_stacked_widget.removeWidget(self.anime_display_widget)
        self.anime_display_widget = QWidget()
        self.anime_stacked_widget.addWidget(self.anime_display_widget)
        self.anime_stacked_widget.setCurrentWidget(self.anime_display_widget) # Transition to a new widget
        self.filter_layout = QGridLayout(parent = self.anime_display_widget)"""
        """ OR self.anime_display_widget = QWidget()
        self.filter_layout = QGridLayout(parent = self.anime_display_widget)
        self.ui.gridLayout_5.addWidget(self.anime_display_widget, 11, 0, 1, 7)"""

        # Retrieve values from comboxes, listwidgets, and checkboxes from search page.
        rating = self.rating_combo.currentText() # Get text of selected item in QComboBox
        if rating == "Select": rating = ""
        
        status = self.status_combo.currentText()
        if status == "Select": status = ""

        selected_items = self.studio_list.selectedItems() # Get the selected items from QListWidget
        studios = [item.text() for item in selected_items] # Extract the text of each selected item

        selected_items = self.season_list.selectedItems() 
        seasons = [item.text() for item in selected_items]

        included_genres = []
        excluded_genres = []
        for checkbox in self.genre_checkboxes: 
            state = checkbox.checkState()
            # Check if genre (checkbox) is checked as included: append the genre.
            if state == Qt.CheckState.Checked:
                included_genres.append(checkbox.text())
            # Check if genre (checkbox) is checked as excluded
            elif state == Qt.CheckState.PartiallyChecked: 
                excluded_genres.append(checkbox.text())

        # Retrieve all anime ids in the database. Will remove elements not meeting filter requirements.
        anime_ids = set()
        cursor.execute("SELECT ID FROM ANIME")
        anime_id_list = cursor.fetchall()
        anime_ids.update(item[0] for item in anime_id_list)

        # Record AnimeIDs for specified statuses
        if status:
            status_anime_id_set = set()
            cursor.execute("SELECT ID FROM ANIME WHERE Status = %s", (status,))
            results = cursor.fetchall()
            status_anime_id_set.update(row[0] for row in results) # Iterates through the list, eliminates duplicates and adds others

            # Intersect both id sets to filter.
            anime_ids = anime_ids & status_anime_id_set # '&' is shortcut for intersection()
       
        # Record AnimeIDs for specified studios
        if studios:
            studio_anime_id_set = set()
            for studio in studios:
                cursor.execute("SELECT ID FROM ANIME WHERE Studio = %s", (studio,))
                results = cursor.fetchall()
                studio_anime_id_set.update(row[0] for row in results)
            # Intersect both id sets to filter.
            anime_ids = anime_ids & studio_anime_id_set

        # Record AnimeIDs for specified seasons
        if seasons:
            season_anime_id_set = set()
            for season in seasons:
                # Query for (season, year) simultaneously, but separately
                season_and_year_list = season.split() 
                cursor.execute("SELECT ID FROM ANIME WHERE Season = %s AND Year = %s", tuple(season_and_year_list))
                results = cursor.fetchall()
                season_anime_id_set.update(row[0] for row in results)

            # Intersect both id sets to filter.
            anime_ids = anime_ids & season_anime_id_set

        # Record AnimeIDs that include all specified genres
        if included_genres:
            in_genre_anime_id_set = set()
            query = None
            # Find anime that has the single specified genre (and account for singleton tuple)
            if len(included_genres) == 1:
                query = f"""
                    SELECT AnimeID FROM ANIME_GENRES
                    WHERE Genre = '{included_genres[0]}'
                    GROUP BY AnimeID"""
            # For each anime, check if the anime has at least one matching genre, then filter anime by checking if 
            # the number of matching genres are equal to the specified amount (need anime with that includes all genres).
            else:
                query = f"""
                    SELECT AnimeID FROM ANIME_GENRES
                    WHERE Genre IN {tuple(included_genres)}
                    GROUP BY AnimeID
                    HAVING COUNT(Genre) = {len(included_genres)}"""
            cursor.execute(query)
            results = cursor.fetchall()
            in_genre_anime_id_set.update(row[0] for row in results)

            # Intersect both id sets to filter.
            anime_ids = anime_ids & in_genre_anime_id_set

        # Record AnimeIDs that exclude all specified genres
        if excluded_genres:
            # Find anime that has at least one matching genre and filter it from the list (need to remove anime ).
            ex_genre_anime_id_set = set()

            # Account for singleton tuple
            if len(excluded_genres) > 1:
                query = f"""
                    SELECT AnimeID FROM ANIME_GENRES
                    WHERE Genre IN {tuple(excluded_genres)}
                    GROUP BY AnimeID"""
                cursor.execute(query)
            else:
                query = f"""
                    SELECT AnimeID FROM ANIME_GENRES
                    WHERE Genre = '{excluded_genres[0]}'
                    GROUP BY AnimeID"""
                cursor.execute(query)
            results = cursor.fetchall()
            ex_genre_anime_id_set.update(row[0] for row in results)

            # Perform 'A' difference 'B' to remove excluded genre anime ids 'B' from 'A' to filter.
            anime_ids = anime_ids - ex_genre_anime_id_set # '-' is shortcut set difference

        # Record AnimeIDs with average rating >= specified rating
        anime_to_rating = None
        if rating:
            if anime_ids: # Check if any filter matches were found.
                # Retrieve the id and average score of each filtered anime id that has 
                # an average score >= specified rating. Associate them with each other.
                anime_to_rating = dict()

                # Account for singleton tuple
                if len(anime_ids) > 1:
                    query = f"""
                        SELECT AnimeID, AVG(Rating) AS AverageScore
                        FROM REVIEW
                        WHERE AnimeID IN {tuple(anime_ids)}
                        GROUP BY AnimeID
                        HAVING AVG(Rating) >= {rating}"""
                    cursor.execute(query)
                else:
                    query = f"""
                        SELECT AnimeID, AVG(Rating) AS AverageScore
                        FROM REVIEW
                        WHERE AnimeID = '{tuple(anime_ids)[0]}'
                        GROUP BY AnimeID
                        HAVING AVG(Rating) >= {rating}"""
                    cursor.execute(query)
                results = cursor.fetchall()

                # Associate them with each other.
                rating_anime_id_set = set()  # OR set(anime_id for (anime_id, score) in results)
                for (anime_id, score) in results: 
                    anime_to_rating[anime_id] = score
                    rating_anime_id_set.add(anime_id)

                anime_ids = anime_ids & rating_anime_id_set # Intersect both id sets to filter.

        # Retrieve the id and average score of each filtered anime id. Associate them with each other.
        else:
            if anime_ids: # Check if any filter matches were found.
                anime_to_rating = dict()
                
                # Account for singleton tuple
                if len(anime_ids) > 1:
                    query = f"""
                        SELECT AnimeID, AVG(Rating) AS AverageScore
                        FROM REVIEW
                        WHERE AnimeID IN {tuple(anime_ids)}
                        GROUP BY AnimeID"""
                    cursor.execute(query)
                else:
                    query = f"""
                        SELECT AnimeID, AVG(Rating) AS AverageScore
                        FROM REVIEW
                        WHERE AnimeID = '{tuple(anime_ids)[0]}'
                        GROUP BY AnimeID"""
                    cursor.execute(query)
                results = cursor.fetchall()

                # Associate them with each other.
                for (anime_id, score) in results:
                    anime_to_rating[anime_id] = score


        """ FOR TESTING
        print(f"anime_ids: {anime_ids}\nanime_to_rating: {anime_to_rating}")
        print(f"rating: {rating}\nstatus: {status}\nstudios: {studios}\nseasons: {seasons}\nincluded_genres: {included_genres}\nexcluded_genres: {excluded_genres}")"""


        # Display filtered anime information.
            # Check if any filter matches were found - remove and replace current widget with text.
        if not anime_ids: 
            label = QLabel("No results for the specified query.", alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) # '|' to separate multiple alignments
            self.filter_layout.addWidget(label, 0, 0, 1, 4)
        else:
            # Retrieve the information for all remaining animes.
                # Account for singleton tuples
            if len(anime_ids) > 1:
                query = f"""
                    SELECT ID, Name, Synopsis, Status, Studio
                    FROM ANIME WHERE ID IN {tuple(anime_ids)} 
                    ORDER BY Name"""
                cursor.execute(query)
            else:
                query = f"""
                    SELECT ID, Name, Synopsis, Status, Studio
                    FROM ANIME WHERE ID = '{tuple(anime_ids)[0]}'
                    ORDER BY Name"""
                cursor.execute(query)
            anime_info = cursor.fetchall() * 220

            # Create a page system to display 20 anime info per widget. Dynamically load only one widget at a time.
            self.init_pagination_bar(anime_info, anime_to_rating)

    # This function creates and sets up a pagination system for displaying filtered anime results.
    def init_pagination_bar(self, anime_info, anime_to_rating):
        self.anime_info = anime_info
        self.anime_to_rating = anime_to_rating

        # Calculate the total number of pages
        self.items_per_page = 20
        self.num_pages = math.ceil(len(self.anime_info) / self.items_per_page)

        # Create a QStackedWidget to manage different pages
        if self.anime_display_widget is None:
            self.anime_stacked_widget = QStackedWidget()
            self.pagination_layout.addWidget(self.anime_stacked_widget)

            # Create a pagination bar with navigation buttons and a page input
            pagination_bar = QHBoxLayout()
            self.prev_button = QPushButton("Previous")
            self.next_button = QPushButton("Next")
            self.page_input = QLineEdit()
            self.page_input.setPlaceholderText("Enter page number")
            self.page_label = QLabel(f"Page 1 of {self.num_pages}")

            # Connect button signals to slots (functions)
            self.prev_button.clicked.connect(self.show_previous_page) #Function reference used instead of lambda
            self.next_button.clicked.connect(self.show_next_page)
            self.page_input.returnPressed.connect(self.go_to_page) # When enter is pressed for the line edit

            # Add widgets to the pagination bar layout
            pagination_bar.addWidget(self.prev_button)
            pagination_bar.addWidget(self.page_input)
            pagination_bar.addWidget(self.page_label)
            pagination_bar.addWidget(self.next_button)

            # Add the pagination bar layout to the pagination widget (nest layouts)
            self.pagination_layout.addLayout(pagination_bar)
        else:
            self.anime_stacked_widget.removeWidget(self.anime_display_widget)
            self.anime_display_widget.deleteLater()

        self.page_label.setText(f"Page 1 of {self.num_pages}")

        # Track loaded pages and current page index
        self.loaded_pages = [False] * self.num_pages
        self.page_index = 0

        # Load the first page initially
        self.load_page(0)
        self.update_button_states()

    # Load content for a specific page if not already loaded (Dynamically load only one widget at a time).
    def load_page(self, page_index):
        self.page_index = page_index
        if not self.loaded_pages[page_index]:
            self.construct_page() # Create and display the page.
            self.loaded_pages[page_index] = True

    # Unload content for a specific page to free up memory and improve performance.
    def unload_page(self):
        if self.loaded_pages[self.page_index]:
            self.anime_stacked_widget.removeWidget(self.anime_display_widget)
            self.anime_display_widget.deleteLater()
            self.loaded_pages[self.page_index] = False

    # Slot to handle navigation to the previous page.
    def show_previous_page(self):
        if self.page_index > 0:
            self.unload_page()
            self.load_page(self.page_index - 1)
            self.update_page_label()
            self.update_button_states()

    # Slot to handle navigation to the next page.
    def show_next_page(self):
        if (self.page_index < self.num_pages - 1):
            self.unload_page()
            self.load_page(self.page_index + 1)
            self.update_page_label()
            self.update_button_states()

    # Slot to handle navigation to a specific page entered in the line edit.
    def go_to_page(self):
        try:
            page_number = int(self.page_input.text()) - 1
            if 0 <= page_number < self.num_pages:
                self.unload_page()
                self.load_page(page_number)
                self.update_page_label()
                self.update_button_states()
        except ValueError:
            # Ignore invalid input (non-integer)
            pass
        finally:
            # Clear focus from line edit after pressing Enter
            self.page_input.clearFocus()

    # Update the label displaying the current page number.
    def update_page_label(self):
        self.page_label.setText(f"Page {self.page_index + 1} of {self.num_pages}")
        
    # Update the enabled state of navigation buttons.
    def update_button_states(self):
        # Disable the "Previous" button if on the first page
        self.prev_button.setEnabled(self.page_index > 0)

        # Disable the "Next" button if on the last page
        self.next_button.setEnabled(self.page_index < self.num_pages - 1)

    # Function to create and display the current page's widget contents.
    def construct_page(self):
        self.anime_display_widget = QWidget()
        self.anime_stacked_widget.addWidget(self.anime_display_widget)
        self.anime_stacked_widget.setCurrentWidget(self.anime_display_widget) # Transition to a new widget
        self.filter_layout = QGridLayout(parent = self.anime_display_widget)

        # Calculate indices of the items to display on the page
        start = self.page_index * self.items_per_page
        end = min(start + self.items_per_page, len(self.anime_info)) # Ensures the end index does not exceed the total number of items

        # Add borders and reduce spacing between cells to display data in a tabular form.
        self.anime_display_widget.setStyleSheet("*{border: 1px solid gray;}")
        self.filter_layout.setHorizontalSpacing(0)
        self.filter_layout.setVerticalSpacing(0)
        self.filter_layout.setContentsMargins(0, 0, 0, 0) # removes any margins around the edges of the layout.

        row = 0
        label = QLabel("Title", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        self.filter_layout.addWidget(label, row, 0, 1, 3)

        label = QLabel("Status", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        self.filter_layout.addWidget(label, row, 3, 1, 1)

        label = QLabel("Studio", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        self.filter_layout.addWidget(label, row, 4, 1, 1)

        label = QLabel("Score", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        self.filter_layout.addWidget(label, row, 5, 1, 1)

        button = None
        height = 80

        # Create labels and buttons with fixed height, for each anime repeatedly
        row += 1
        for i in range(start, end):
            (anime_id, title, synopsis, status, studio) = self.anime_info[i]

            # Image
            image = QLabel("Image?", alignment = Qt.AlignmentFlag.AlignCenter)
            image.setFixedSize(60, height)
            image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.filter_layout.addWidget(image, row, 0, 2, 1)

            # Title - Pack a button for visiting anime page
            visit_anime_button = QPushButton()
                # Elide ("...") text if it's too long
            fm = visit_anime_button.fontMetrics()
            elided_text = fm.elidedText(title, Qt.TextElideMode.ElideRight, visit_anime_button.width() - 10)  # Adjust width for padding
            visit_anime_button.setText(elided_text)
                # Set tooltip to show full text on hover
            visit_anime_button.setToolTip(title) 
                # Set font, size, and style.
            font = QFont()
            font.setBold(True)
            visit_anime_button.setFont(font)
            visit_anime_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            visit_anime_button.setMaximumWidth(1000)
            visit_anime_button.setFixedHeight(20)
            visit_anime_button.setStyleSheet("border: None; color: blue;")
                # Set the cursor to a pointing hand cursor when hovering over the button
            visit_anime_button.setCursor(Qt.CursorShape.PointingHandCursor)
                # NOTE lambda function has default arguments to force early binding. Late binding (on button click) done if unspecified.
            visit_anime_button.clicked.connect(lambda anime_id = anime_id: self.open_anime_page(anime_id))
            self.filter_layout.addWidget(visit_anime_button, row, 1, 1, 1, alignment = Qt.AlignmentFlag.AlignLeft)
    
            # Synopsis
                # Show the first 250 characters of the text, and an ellipsis (if too long)
            short_synopsis = ""
            limit = 250
            short_synopsis = synopsis[:limit] + "..." if len(synopsis) > limit else synopsis
                # Create label and specifications
            label = QLabel(short_synopsis, alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setMaximumWidth(1000)
            label.setFixedHeight(60)
            label.setStyleSheet("border: None; border-bottom: 1px solid gray;")
                # Enable word wrap
            label.setWordWrap(True)
                # Set tooltip to show full text on hover
            label.setToolTip(synopsis)
            self.filter_layout.addWidget(label, (row + 1), 1, 1, 1)

            # Manage list button
                # Retrieve the user's watch status of the current anime
            query = f"SELECT WatchStatus FROM CONTAINS WHERE ListID = {self.list_id} AND AnimeID = {anime_id}"
            cursor.execute(query)
            watch_status = cursor.fetchone()

            if watch_status:
                list_button = QPushButton(watch_status[0])
                list_button.clicked.connect(lambda anime_id = anime_id, watch_status = watch_status:
                                      self.open_list_dialog(anime_id, watch_status[0])) # Force early binding
            else:
                list_button = QPushButton("Add")
                list_button.clicked.connect(lambda anime_id = anime_id: self.open_list_dialog(anime_id, None)) # Force early binding

            list_button.setStyleSheet("background-color: lightblue; border: None; border-bottom: 1px solid black;")
            list_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            list_button.setFixedSize(80, height)
            list_button.setCursor(Qt.CursorShape.PointingHandCursor) # Set the cursor to a pointing hand cursor when hovering over the button
            self.filter_layout.addWidget(list_button, row, 2, 2, 1)

            # Status
            label = QLabel(status, alignment = Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(90, height)
            self.filter_layout.addWidget(label, row, 3, 2, 1)

            # Studio
            label = QLabel(studio, alignment = Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(85, height)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                # Elide ("...") text if it's too long
            fm = label.fontMetrics()
            elided_text = fm.elidedText(studio, Qt.TextElideMode.ElideRight, label.width())
            label.setText(elided_text)
                # Set tooltip to show full text on hover
            label.setToolTip(studio)
            self.filter_layout.addWidget(label, row, 4, 2, 1)

            # Rating
                # Check if anime has no reviews.
            rating = None
            if anime_id in self.anime_to_rating:
                rating = f"{anime_to_rating[anime_id]: .2f}"
            else:
                rating = "N/A"
            label = QLabel(rating, alignment = Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(50, height)
            self.filter_layout.addWidget(label, row, 5, 2, 1)

            row += 2

            
         #************************************************************************************************
         #************ User profile styling and slots [SET UP STACKED WIDGET TO AVOID OVERLAP???]
         #************ Display of list page (only)
         #************************************************************************************************


    # This function transitions to an anime page by changing the current widget of the stacked widget.
    def open_anime_page(self, anime_id):
        self.ui.stackedWidget.setCurrentWidget(self.ui.anime_page)

        # Enable listening to events for transitioning to other pages.
        self.ui.profile_button_2.clicked.connect(lambda: self.report_statistics())
        self.ui.search_button.clicked.connect(lambda: self.open_search_page())

    #
    def review_anime(self):
        pass

    # This function creates and displays a dialog box to allow users to manage their lists.
    def open_list_dialog(self, anime_id, watch_status):
        pass

    # This function opens the user profile page, which reports statistics based on their anime viewing history.
    def report_statistics(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)

        # Add the button to go the search page, and define a signal-slot handler.
        self.ui.search_button_2.setFixedSize(140, 50)
        font = QFont() 
        font.setPointSize(14)
        font.setBold(True)
        self.ui.search_button_2.setFont(font)
        self.ui.search_button_2.clicked.connect(lambda: self.open_search_page())
        self.ui.gridLayout_profile.addWidget(self.ui.search_button_2, 0, 0, 1, 3, alignment = Qt.AlignmentFlag.AlignRight)

        # Retrieve and display the user's name
        query = f"SELECT Name FROM USER WHERE ID = {self.user_id}"
        cursor.execute(query)
        username = cursor.fetchone()[0]
        label = QLabel(f"{username}'s Profile", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont() 
        font.setPointSize(15)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("border: 0px; border-bottom: 2px solid gray;")
        label.setFixedHeight(40)
        self.ui.gridLayout_profile.addWidget(label, 1, 0, 1, 3)

        # Retrieve and display the user's join date.
        cursor.execute(f"SELECT JoinDate FROM USER WHERE ID = {self.user_id}")
        join_date = cursor.fetchone()[0]
        label = QLabel(f"Joined: {join_date: %B %d, %Y}", alignment = Qt.AlignmentFlag.AlignLeft) # Format in Month/Day/Year and state the month name
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        label.setFont(font)
        label.setFixedHeight(30)
        self.ui.gridLayout_profile.addWidget(label, 2, 0)

        # Add and create a button to view the user's review history
        user_review_history_button = QPushButton("Reviews")
        font = QFont() 
        font.setPointSize(12)
        font.setBold(True)
        user_review_history_button.setFont(font)
        user_review_history_button.setStyleSheet("color: blue;")
        #user_review_history_button.setFixedHeight(20)
        #self.user_review_history_button.clicked.connect(lambda: self.display_reviews())
        self.ui.gridLayout_profile.addWidget(user_review_history_button, 3, 0, alignment = Qt.AlignmentFlag.AlignLeft)

        # Add the button to option to user's view watchlist page.
        font = QFont() 
        font.setPointSize(12)
        font.setBold(True)
        self.ui.list_button.setFont(font)
        self.ui.list_button.setStyleSheet("color: blue;")
        #self.ui.list_button.setFixedHeight(20)
        self.ui.list_button.clicked.connect(lambda: self.open_list_page())
        self.ui.gridLayout_profile.addWidget(self.ui.list_button, 4, 0, alignment = Qt.AlignmentFlag.AlignLeft)

        # Determine the total number of anime watched
        query = f"SELECT COUNT(*) FROM CONTAINS WHERE ListID = {self.list_id}"
        cursor.execute(query)
        total_anime_watched = cursor.fetchone()[0]
        if not total_anime_watched: total_anime_watched = 0

        # Determine the total number of watched episodes
        query = f"SELECT SUM(NumEpsWatched) FROM CONTAINS WHERE ListID = {self.list_id}"
        cursor.execute(query)
        total_eps_watched = cursor.fetchone()[0]
        if not total_eps_watched: total_eps_watched = 0

        # Determine the average rating
        query = f"SELECT AVG(Rating) FROM REVIEW WHERE UserID = {self.user_id}"
        cursor.execute(query)
        avg_rating = cursor.fetchone()[0]
        if not avg_rating: avg_rating = 0.00
        
        # Determine the watch status of all anime in list
        query = f"SELECT WatchStatus, COUNT(*) FROM CONTAINS WHERE ListID = {self.list_id} GROUP BY WatchStatus"
        cursor.execute(query)
        watch_status_info = cursor.fetchall() # Fetch a list of tuples
        watch_status_dict = {}

            # Convert the list of tuples to a dictionary.
        for status, count in watch_status_info: 
            watch_status_dict[status] = count

            # If status is not in dictionary, add it and set its count to 0.
        if 'Watching' not in watch_status_dict: watch_status_dict['Watching'] = 0
        if 'Completed' not in watch_status_dict: watch_status_dict['Completed'] = 0
        if 'On-Hold' not in watch_status_dict: watch_status_dict['On-Hold'] = 0
        if 'Dropped' not in watch_status_dict: watch_status_dict['Dropped'] = 0
        if 'Plan to Watch' not in watch_status_dict: watch_status_dict['Plan to Watch'] = 0

        # Display statistics
            # Header label
        label = QLabel(f"Statistics", alignment = Qt.AlignmentFlag.AlignCenter)
        font = QFont() 
        font.setPointSize(13)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("border: 0px; border-bottom: 1px solid gray;")
        label.setFixedHeight(40)
        self.ui.gridLayout_profile.addWidget(label, 2, 1, 1, 2)

            # Watching
        label = QLabel(f"Watching: {watch_status_dict['Watching']}") 
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 3, 1)

            # Completed
        label = QLabel(f"Completed: {watch_status_dict['Completed']}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 4, 1)

            # On-Hold
        label = QLabel(f"On-Hold: {watch_status_dict['On-Hold']}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 5, 1)

            # Dropped
        label = QLabel(f"Dropped: {watch_status_dict['Dropped']}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 6, 1)

            # Plan to Watch
        label = QLabel(f"Plan to Watch: {watch_status_dict['Plan to Watch']}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 7, 1)

            # Total Entries
        label = QLabel(f"Total Entries: {total_anime_watched}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 3, 2)

            # Average score
        label = QLabel(f"Average score: {avg_rating:.2f}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 4, 2)

            # Episodes
        label = QLabel(f"Episodes: {total_eps_watched}")
        label.setFixedHeight(20)
        self.ui.gridLayout_profile.addWidget(label, 5, 2)


    # This function transitions to the list page by changing the current widget of the stacked widget.
    def open_list_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.list_page)

        # Enable listening to events for transitioning to other pages.
        self.ui.search_button_3.clicked.connect(lambda: self.open_search_page())
        self.ui.profile_button_3.clicked.connect(lambda: self.report_statistics())

    #
    def manage_list(self):
        pass

def main():
    # Create connection to the database
    global mydb # Global variable
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kene1234"
    )

    # Prepare a cursor object (for writing statements to the mysql)
    global cursor # Declare the cursor to be a global variable
    cursor = mydb.cursor()
    cursor.execute("USE ANIME_MANAGEMENT")

    # Instantiate and assign QApplication obj required to run the mainloop.
    app = QApplication(sys.argv) # sys.argv - handles command-line arguments specific to the application.
    window = MainWindow() 
    sys.exit(app.exec()) # mainloop the window to listen for events (like button clicks).

if __name__ == '__main__':
    main()

"""
QApplication - manages application-wide resources and settings.
sys.argv - handles command-line arguments specific to the application.
QMainWindow - 
QLineEdit - Allows to read only one line of text from the user.
"""

""" ******************** NON PAGINATED WIDGET CREATION **********************
# Add borders and reduce spacing between cells to display data in a tabular form.
            self.anime_display_widget.setStyleSheet("*{border: 1px solid gray;}")
            self.filter_layout.setHorizontalSpacing(0)
            self.filter_layout.setVerticalSpacing(0)
            self.filter_layout.setContentsMargins(0, 0, 0, 0) # removes any margins around the edges of the layout.

            row = 0
            label = QLabel("Title", alignment = Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            label.setFont(font)
            self.filter_layout.addWidget(label, row, 0, 1, 3)

            label = QLabel("Status", alignment = Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            label.setFont(font)
            self.filter_layout.addWidget(label, row, 3, 1, 1)

            label = QLabel("Studio", alignment = Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            label.setFont(font)
            self.filter_layout.addWidget(label, row, 4, 1, 1)

            label = QLabel("Score", alignment = Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(11)
            font.setBold(True)
            label.setFont(font)
            self.filter_layout.addWidget(label, row, 5, 1, 1)

            button = None
            height = 80

            # Create labels and buttons with fixed height, for each anime repeatedly
            row += 1
            for (anime_id, title, synopsis, status, studio) in anime_info:
                # Image
                image = QLabel("Image?", alignment = Qt.AlignmentFlag.AlignCenter)
                image.setFixedSize(60, height)
                image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.filter_layout.addWidget(image, row, 0, 2, 1)

                # Title - Pack a button for visiting anime page
                visit_anime_button = QPushButton()
                    # Elide ("...") text if it's too long
                fm = visit_anime_button.fontMetrics()
                elided_text = fm.elidedText(title, Qt.TextElideMode.ElideRight, visit_anime_button.width() - 10)  # Adjust width for padding
                visit_anime_button.setText(elided_text)
                    # Set tooltip to show full text on hover
                visit_anime_button.setToolTip(title) 
                    # Set font, size, and style.
                font = QFont()
                font.setBold(True)
                visit_anime_button.setFont(font)
                visit_anime_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                visit_anime_button.setMaximumWidth(1000)
                visit_anime_button.setFixedHeight(20)
                visit_anime_button.setStyleSheet("border: None; color: blue;")
                    # Set the cursor to a pointing hand cursor when hovering over the button
                visit_anime_button.setCursor(Qt.CursorShape.PointingHandCursor)
                    # NOTE lambda function has default arguments to force early binding. Late binding (on button click) done if unspecified.
                visit_anime_button.clicked.connect(lambda anime_id = anime_id: self.open_anime_page(anime_id))
                self.filter_layout.addWidget(visit_anime_button, row, 1, 1, 1, alignment = Qt.AlignmentFlag.AlignLeft)
                
                # Synopsis
                    # Show the first 250 characters of the text, and an ellipsis (if too long)
                short_synopsis = ""
                limit = 250
                short_synopsis = synopsis[:limit] + "..." if len(synopsis) > limit else synopsis
                    # Create label and specifications
                label = QLabel(short_synopsis, alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                label.setMaximumWidth(1000)
                label.setFixedHeight(60)
                label.setStyleSheet("border: None; border-bottom: 1px solid gray;")
                    # Enable word wrap
                label.setWordWrap(True)
                    # Set tooltip to show full text on hover
                label.setToolTip(synopsis)
                self.filter_layout.addWidget(label, (row + 1), 1, 1, 1)
                """"""text_edit = QTextEdit()
                text_edit.setPlainText(synopsis)
                text_edit.setReadOnly(True)  # Make it read-only if you don't want editing
                text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                text_edit.setMaximumWidth(1000)
                text_edit.setFixedHeight(60)
                text_edit.setStyleSheet("border: None; border-bottom: 1px solid gray;")
                    # Enable automatic line wrapping
                text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)  
                    # Set tooltip to show full text on hover
                text_edit.setToolTip(synopsis)
                self.filter_layout.addWidget(text_edit, (row + 1), 1, 1, 1, alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)""""""

                # Manage list button
                    # Retrieve the user's watch status of the current anime
                query = f"SELECT WatchStatus FROM CONTAINS WHERE ListID = {self.list_id} AND AnimeID = {anime_id}"
                cursor.execute(query)
                watch_status = cursor.fetchone()

                if watch_status:
                    list_button = QPushButton(watch_status[0])
                    list_button.clicked.connect(lambda anime_id = anime_id, watch_status = watch_status:
                                          self.open_list_dialog(anime_id, watch_status[0])) # Force early binding
                else:
                    list_button = QPushButton("Add")
                    list_button.clicked.connect(lambda anime_id = anime_id: self.open_list_dialog(anime_id, None)) # Force early binding

                list_button.setStyleSheet("background-color: lightblue; border: None; border-bottom: 1px solid black;")
                list_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                list_button.setFixedSize(80, height)
                list_button.setCursor(Qt.CursorShape.PointingHandCursor) # Set the cursor to a pointing hand cursor when hovering over the button
                self.filter_layout.addWidget(list_button, row, 2, 2, 1)

                # Status
                label = QLabel(status, alignment = Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(90, height)
                self.filter_layout.addWidget(label, row, 3, 2, 1)

                # Studio
                label = QLabel(studio, alignment = Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(85, height)
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    # Elide ("...") text if it's too long
                fm = label.fontMetrics()
                elided_text = fm.elidedText(studio, Qt.TextElideMode.ElideRight, label.width())
                label.setText(elided_text)
                    # Set tooltip to show full text on hover
                label.setToolTip(studio)
                self.filter_layout.addWidget(label, row, 4, 2, 1)

                # Rating
                    # Check if anime has no reviews.
                rating = None
                if anime_id in anime_to_rating:
                    rating = f"{anime_to_rating[anime_id]: .2f}"
                else:
                    rating = "N/A"
                label = QLabel(rating, alignment = Qt.AlignmentFlag.AlignCenter)
                label.setFixedSize(50, height)
                self.filter_layout.addWidget(label, row, 5, 2, 1)

                row += 2
"""

""" ******************** PAGINATION BAR ***********************
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit


# Class for widgets that display items on multiple pages.
class PaginationWidget(QWidget):
    def __init__(self, parent=None, num_pages = 0):
        super().__init__(parent)

        # Set up the layout for the pagination widget
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QStackedWidget to manage different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Create a pagination bar with navigation buttons and a page input
        pagination_bar = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Enter page number")
        self.page_label = QLabel(f"Page 1 of {num_pages}")

        # Connect button signals to slots (functions)
        self.prev_button.clicked.connect(self.show_previous_page)
        self.next_button.clicked.connect(self.show_next_page)
        self.page_input.returnPressed.connect(self.go_to_page)

        # Add widgets to the pagination bar layout
        pagination_bar.addWidget(self.prev_button)
        pagination_bar.addWidget(self.page_input)
        pagination_bar.addWidget(self.page_label)
        pagination_bar.addWidget(self.next_button)

        # Add the pagination bar layout to the pagination widget
        layout.addLayout(pagination_bar)

        # Track loaded pages and current page index
        self.loaded_pages = [False] * num_pages
        self.current_page_index = 0

        # Load the first page initially
        self.load_page(0)
        self.update_button_states()

    # Load content for a specific page if not already loaded.
    def load_page(self, page_index):
        if not self.loaded_pages[page_index]:
            page = QWidget()
            label = QLabel(f"Content of page {page_index + 1}")
            page_layout = QVBoxLayout(page)
            page_layout.addWidget(label)
            self.stacked_widget.insertWidget(page_index, page)
            self.loaded_pages[page_index] = True

    # Unload content for a specific page to free up memory.
    def unload_page(self, page_index):
        if self.loaded_pages[page_index]:
            widget = self.stacked_widget.widget(page_index)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
            self.loaded_pages[page_index] = False

    # Slot to handle navigation to the previous page.
    def show_previous_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.unload_page(current_index)
            self.load_page(current_index - 1)
            self.stacked_widget.setCurrentIndex(current_index - 1)
            self.update_page_label()
            self.update_button_states()

    # Slot to handle navigation to the next page.
    def show_next_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index < len(self.loaded_pages) - 1:
            self.unload_page(current_index)
            self.load_page(current_index + 1)
            self.stacked_widget.setCurrentIndex(current_index + 1)
            self.update_page_label()
            self.update_button_states()

    # Slot to handle navigation to a specific page entered in the line edit.
    def go_to_page(self):
        try:
            page_number = int(self.page_input.text()) - 1
            if 0 <= page_number < len(self.loaded_pages):
                self.unload_page(self.stacked_widget.currentIndex())
                self.load_page(page_number)
                self.stacked_widget.setCurrentIndex(page_number)
                self.update_page_label()
                self.update_button_states()
        except ValueError:
            # Ignore invalid input (non-integer)
            pass
        finally:
            # Clear focus from line edit after pressing Enter
            self.page_input.clearFocus()

    # Update the label displaying the current page number.
    def update_page_label(self):
        current_index = self.stacked_widget.currentIndex()
        self.page_label.setText(f"Page {current_index + 1} of {len(self.loaded_pages)}")
        
    # Update the enabled state of navigation buttons.
    def update_button_states(self):
        current_index = self.stacked_widget.currentIndex()
        # Disable the "Previous" button if on the first page
        self.prev_button.setEnabled(current_index > 0)
        # Disable the "Next" button if on the last page
        self.next_button.setEnabled(current_index < len(self.loaded_pages) - 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set up the layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create other content widget
        other_content = QWidget()
        other_content_label = QLabel("Other content goes here.")
        other_content_layout = QVBoxLayout(other_content)
        other_content_layout.addWidget(other_content_label)

        # Create pagination widget and add to main layout
        pagination_widget = PaginationWidget()
        layout.addWidget(other_content)
        layout.addWidget(pagination_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
"""


""" ***************** SCROLLAREA TUTORIAL *******************
from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtWidgets, uic
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        for i in range(1,50):
            object = QLabel("TextLabel")
            self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

        return

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()"""
