# Anime-Watchlist-Management-System (AWMS)

**Description:** Database Application, TKinter, Python, MySQL
Implemented and utilized a dictionary to store a collection of languages and displayed their information on a GUI using JavaFX. The GUI allows for operations like searching for languages in the collection, playing their sounds, traversing to the next or previous languages, etc.

**Created By:** Kene Maduabum.

**How to Set Up & Run Database:**
1. Install python for your device.
2. Install pip through the command line:
  1. Type - /*curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py*/
  2. Type - /*python get-pip.py*/
3. Install MySQL server, MySQL workbench, and set up the password for a server instance.
4. Install MySQL-python connector through the command line:
  1. Type - /*pip install mysql-connector-python*/
5. Run "databaseSetup.py" through the command line (This file contains everything necessary to create the schema for the database and tables along with inserting some rows into the necessary tables):
  1. Type - /*cd path/to/directory/containing/file*/
  2. Type - /*python databaseSetup.py*/
6. Install the sv_ttk package for tkinter through the command line:
  1. Type - /*pip install sv-ttk*/
7. Run "animeWatchlistApp.py" through the command line (This is the source code ):
  1. Type - /*cd path/to/directory/containing/file*/
  2. Type - /*python animeWatchlistApp.py*/
 

**Future Work:**
- Give each anime their own separate display pages.
  - Implement the functionality of making reviews.
  - Display episode and character information.
- Expand on the list functionalities:
  - Remove
  - Update
  - Delete
  - Go to anime page from watchlist.
  - Remove from list while on page.
- Manage tkinter Toplevel windows better (through dropping current window and raising a new one) or implement a better way to transition between windows/pages.
- Add scrollbars to each listbox in the search page.
  - Change some filter options to single selection, comboboxes instead of listboxes.
- Fix bug with filtering with options other than genres.
- Research more efficient algorithms and queries for functions.
- Add more class and functions to organize code.
- Find a way to automate the process of filling tables. Maybe through web scraping?
