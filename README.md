# SI507-FinalProject
final project for SI507 UMSI 2017
author Jacob Haspiel
12/11/2017
VERSION == PYTHON 3.6

Hello! Outlined below is the documentation for my app using data from https://www.sports-reference.com/cfb/schools/

Project Goals:
- [ ] Create Git Repository
- [ ] Using BeautifulSoup - pull Data from sports-reference.com E.G. on football seasons for a given team
    - Coach
    - Record
    - Year
    - Bowl Game 
    - Conference
    - ETC
- [ ] Create and implement Caching System for Beautiful Soup Data 
- [ ] Allow user input
- [ ] Create class for a single season of football
- [ ] Create class for a single coach
- [ ] Create 1 Table for Coaches
- [ ] Create 1 Table for Seasons
	- Join occurs on coach name across tables
- [ ] Create tests to ensure types, side effects, class etc working correctly.
- [ ] Ensure Readme is formatted/informative and correct
- [ ] Include Collaborators
- [ ] Create VirtualENV - ensure it is updated
- [ ] Requirements.txt file present and correct
- [ ] Show data for team or teams via plotly
- [ ] Print coach data.
- [ ] Create .csv files for team
- [ ] Ensure all credit given to sources



***INSTRUCTIONS***
VERSION == PYTHON 3.6

*** Once you have cloned this repository - navigate to the git repository: SI507-FinalProject

1. Ensure your local host server is running with the following command: pg_ctl -D /usr/local/var/postgres start 

2. In the attached config.py file you will want to change the db_name and db_username and if applicable db_password to your own credentials. Save the file

3. In your terminal create the DB corresponding the the DB_name you have just selected in config.py e.g: createdb haspiel_507projectfinal

4. Open a virtual environment and pip3 install -r requirements.txt

5. run the file! python3 SI507F17_finalproject.py
This app allows the user to pull and visualize data on their favorite (or most hated!) football teams, E.G. Michigan or.... Ohio State.
	Step 1: The program will prompt you for creation of the DB- if this is your first time running the program enter "Y". Otherwise hit any other key
	Step 2: Choose whether you would like to look at football season data for 1 team or 2 ('1' or '2')
	Step 3: Enter your team or teams (not case-sensitive)
	Step 4: Choose how many coaches for each team or teams you would like to see data for (queries database for coach data)
	Step 5: sit back and enjoy!

6. The program does the following:
	1. Creates/rewrites DB if user wants.
	2. Using a cache system attempts to pull the requested HTML data for a given team from the cache. If that team does not have data in the cache the program pulls data from the relevant https://www.sports-reference.com/cfb/schools/{TEAM} page for TEAM.
	3. Creates a BS object from the HTML for the given team
	4. Creates an instance of class SeasonObject for each given season in the BS data.
	5. Creates an instance of class CoachObject for each coach if one does not already exist
	6. Inserts season data into Seasons table in the DB
	7. Inserts coach data into Coaches table in the DB
	8. Creates a .csv file for each team summarizing all seasons if that team does not already have a .csv file
	9. Queries the DB for the # of coaches selected for each team and prints out in the console
	10. Creates a plotly html file visualizing data for the team or teams over all active years. Shows win totals and win %s.
	11. Prompts user to run again or quit!


TO TEST:
1. Run the SI507F17_finalproject_tests file.
2. Enjoy



