# Anime-Watchlist-Management-System (AWMS)

**Description:** Implemented a Database Application for allowing multiple users organize and track the anime they watch using MySQL RDBMS and Python programming language. The "tkinter" and "sv_ttk" packages of python are also to implement a GUI for the application.

**Created By:** Kene Maduabum.

**How to Set Up & Run Database:**
1. Install python for your device.
2. Install pip through the command line:
    1. Type - *curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py*
    2. Type - *python get-pip.py*
3. Install MySQL server, MySQL workbench, then set up the password for a server instance in the workbench.
4. Install MySQL-python connector through the command line:
    1. Type - *pip install mysql-connector-python*
5. Run "databaseSetup.py" through the command line (This file contains everything necessary to create the schema for the database and tables along with inserting some rows into the necessary tables):
    1. Type - *cd path/to/directory/containing/file*
    2. Type - *python databaseSetup.py*
6. Install the sv_ttk package through the command line (This is a package that uses tkinter, and is used by the source code to create the dark-themed modern GUI):
    1. Type - *pip install sv-ttk*
7. Run "animeWatchlistApp.py" through the command line (This is the source code for the database application itself):
    1. In line 21, change "yourpassword" to the password set for the MySQL server workbench. Check to ensure the "host" and "user" values correspond to the server being used.
    2. Type - *cd path/to/directory/containing/file*
    3. Type - *python animeWatchlistApp.py*
 

**Future Work:**
- Give each anime their own separate display pages.
  - Implement the functionality of making reviews, along with viewing the statistics for other user profiles.
  - Display episode and character information.
- Expand on some watchlist functionalities:
  - Remove
  - Update
  - Go to anime page from watchlist.
  - Remove from list while on page.
  - May decide to allow users to have multiple lists, and control the accessibility of each list.
- Add password functionalities to the application, and some constraints on the length of usernames.
- Manage tkinter Toplevel windows better (through dropping current window and raising a new one) or implement a better way to transition between windows/pages.
- Add scrollbars to each listbox in the search page.
  - Change some filter options to single selection, comboboxes instead of listboxes.
- Fix bug concerning filtering with options other than genres.
- Research more efficient algorithms and queries for functions.
- Add more classes and functions to organize code.
- Research ways of automating the process of filling tables. Maybe through web scraping?

**Notes on pyqt6**
- Install pyqt6 through the command line:
  - Type - *pip3 install pyqt6*
- Install Qt Designer to drag and drop widgets + generate py codes of the window.
- Install the qdarktheme package through the command line
  - Type - *pip install pyqtdarktheme*
- How to convert .ui file (from Qt Designer) to .py file: 
  - Type - *cd path/to/directory/containing/.uifile*
  - Type - *python -m PyQt6.uic.pyuic filename.ui -o newFilename.py*
