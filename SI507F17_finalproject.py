import requests
import json
import webbrowser
import psycopg2
import psycopg2.extras
import csv
from bs4 import BeautifulSoup
from bs4 import Tag
from config import *
import plotly
from plotly.graph_objs import Scatter, Layout

#caching setup
CACHE_FNAME = 'footbal_seasons_cache_file.json'
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

# function definitions
def get_connection_and_cursor(): # NOTE - Code taken from section 11 in class assignment
    try:
        if db_password != "":
            db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
            print("Success connecting to database")
        else:
            db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
    except:
        print("Unable to connect to the database. Check server and credentials.")
        sys.exit(1) # Stop running program if there's no db connection.

    db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return db_connection, db_cursor

def setup_database():

    # Create Coaches table
    cur.execute("DROP TABLE IF EXISTS Seasons CASCADE")
    cur.execute("DROP TABLE IF EXISTS Coaches CASCADE")
    cur.execute("""CREATE TABLE Coaches(
    	ID SERIAL PRIMARY KEY,
    	School TEXT,
    	Name VARCHAR(40) UNIQUE,
    	Season_count INTEGER,
    	Years_active TEXT,
    	Overall_record NUMERIC(8,3)
    	)""")

    # Create Seasons table
    cur.execute("""CREATE TABLE Seasons(
    	ID SERIAL PRIMARY KEY,
    	Year INTEGER,
    	School TEXT,
    	Conference TEXT,
    	Wins INTEGER,
    	Losses INTEGER,
    	Ties INTEGER,
    	Win_percent NUMERIC(8,3),
    	Simple_rating_score NUMERIC(8,3), 
    	Strength_of_schedule NUMERIC(8,3), 
    	Highest_rank INTEGER, 
    	Coach VARCHAR REFERENCES Coaches(Name), 
    	Bowl_game VARCHAR(128))  
    	""")
    conn.commit()
    print('Setup database complete')

def execute_and_print(query, number_of_results=100):
    cur.execute(query)
    results = cur.fetchall()
    for r in results[:number_of_results]:
        print(r)
    # print('--> Result Rows:', len(results))
    print()

def plotly_1(years_list, win_list, win_pct_list, teamname1):
	teamname1 = teamname1
	percentage = Scatter(
		x=years_list, 
		y=win_pct_list,
		mode = 'lines',
		name='Single Season Win%'
		)
	wintotal = Scatter(
		x=years_list, 
		y=win_list,
		mode = 'lines',
		name='Single Season Win Total'
		)
	plotly.offline.plot({
	    "data": [percentage, wintotal],
	    "layout": Layout(title="Football Seasons Summary for "+teamname1)
		})


def plotly_2(years_list1, win_list1, win_pct_list1, years_list2, win_list2, win_pct_list2,teamname1, teamname2):
	teamname1 = teamname1
	teamname2 = teamname2
	percentage_1 = Scatter(
		x=years_list1, 
		y=win_pct_list1,
		mode = 'lines',
		name=teamname1+' Single Season Win%'
		)
	wintotal_1 = Scatter(
		x=years_list1, 
		y=win_list1,
		mode = 'lines',
		name=teamname1+' Single Season Win Total'
		)
	percentage_2 = Scatter(
		x=years_list2, 
		y=win_pct_list2,
		mode = 'lines',
		name=teamname2+' Single Season Win%'
		)
	wintotal_2 = Scatter(
		x=years_list2, 
		y=win_list2,
		mode = 'lines',
		name=teamname2+' Single Season Win Total'
		)

	plotly.offline.plot({
	    "data": [percentage_1, wintotal_1, percentage_2, wintotal_2],
	    "layout": Layout(title="Football Seasons Summary for "+teamname1 +" and "+teamname2)
		})

#class definitions
class SeasonObject(object): #single season  class
	def __init__(self, single_season_object, school):
		
		self.year = single_season_object.find("td", {"data-stat":"year_id"}).text
		self.conference = single_season_object.find("td", {"data-stat":"conf_id"}).text
		self.wins = single_season_object.find("td", {"data-stat":"wins"}).text
		self.losses = single_season_object.find("td", {"data-stat":"losses"}).text
		self.ties =  single_season_object.find("td", {"data-stat":"ties"}).text
		self.win_percent = single_season_object.find("td", {"data-stat":"win_loss_pct"}).text
		self.simple_rating_score = single_season_object.find("td", {"data-stat":"srs"}).text
		self.strength_of_schedule = single_season_object.find("td", {"data-stat":"sos"}).text
		if single_season_object.find("td", {"data-stat":"coaches"}).text != "":
			self.coach = single_season_object.find("td", {"data-stat":"coaches"}).text
		else:
			self.coach = "no coach data available"
		if single_season_object.find("td", {"data-stat":"rank_min"}).text != "":
			self.highest_ap_rank = single_season_object.find("td", {"data-stat":"rank_min"}).text
		else:
			self.highest_ap_rank = 0
		if single_season_object.find("td", {"data-stat":"bowl_name"}).text != "":
			self.bowl = single_season_object.find("td", {"data-stat":"bowl_name"}).text
		else:
			self.bowl = "No Bowl"
		self.school = school

	def pretty_coachname(self):
		mycoach = self.coach
		if self.coach == "no coach data available":
			current_final_coach = self.coach
		else:
			coach_pretty = self.coach.split()
			current_final_coach = coach_pretty[0]+" "+coach_pretty[1]
		return current_final_coach
	

	def season_csv_str(self):
		final_str = ""
		final_str+=str(self.year)+","+self.conference+","+str(self.wins)+","+str(self.losses)+","+str(self.ties)+","+str(self.win_percent)+","+str(self.simple_rating_score)+","+str(self.strength_of_schedule)+","+str(self.highest_ap_rank)+","+self.pretty_coachname()+","+self.bowl+"\n"
		return final_str

	def __repr__(self):
		return "Year: {}, for School: {} ".format(self.year, self.school)

	def __contains__(self,coach):
		if coach in self.coach:
			return True
		else:
			return False

class CoachObject(object):
	def __init__(self, coachname,school,number_seasons = 0):
		# try:
		self.coachname = coachname
		self.coach_seasons = number_seasons
		self.school = school

	def get_overall_percent(self, all_seasons_list):
		totalpct = 0.0
		for season in all_seasons_list:
			if self.coachname in season.coach:
				totalpct += float(season.win_percent)
		totalpct = str(totalpct/self.coach_seasons)
		finalpct = totalpct[0:5]

		return finalpct

	def get_years_coached(self, all_seasons_list):
		years_list_coached = []
		for season in all_seasons_list:
			if self.coachname in season.coach:
				years_list_coached.append(season.year)
		max_year = max(years_list_coached)
		min_year = min(years_list_coached)
		years_coached_final = str(min_year)+"-"+str(max_year)
	
		return years_coached_final


#Caching System
# teamname = "wisconsin"

def main_process(teamname):
	teamname = teamname
	teamstripped = teamname.replace(" ","-")
	lower_team = teamstripped.lower()
	final_team = lower_team +"/"
	url_base = 'https://www.sports-reference.com/cfb/schools/'
	current_team_url = url_base+lower_team

	if current_team_url in CACHE_DICTION:
		badger_data = CACHE_DICTION[current_team_url]
	else:
		badger_data  = requests.get(current_team_url).text
		CACHE_DICTION[current_team_url] = badger_data
		with open(CACHE_FNAME, 'w') as cache_file:
			cache_json = json.dumps(CACHE_DICTION)
			cache_file.write(cache_json)

	teamlink = lower_team+"_link"
	badgersoup = BeautifulSoup(badger_data, 'html.parser')
	badger_seasons = badgersoup.find("span", {"id":teamlink})
	badger_seasons_table = badgersoup.find("tbody")

	#Lists for use
	all_seasons_list = []
	all_coaches_list = []
	coach_objects_list = []

	#Compile all seasons 
	doorway = 'open'
	try:
		for row in badger_seasons_table:
			if isinstance(row, Tag):
				try:
					all_seasons_list.append(SeasonObject(row, lower_team))
				except:
					current = ""
	except:
		doorway = 'closed'
		print("Could not find the name of "+teamname+ " check spelling and try again!")

	#Compile all coaches 
	for season in all_seasons_list:
		if season.__contains__(season.year) == True:
			print (yes)
		coach = season.coach
		if season.coach == "no coach data available":
			final_coach = season.coach
		else:
			coach_pretty = coach.split()
			final_coach = coach_pretty[0]+" "+coach_pretty[1]
		if final_coach not in all_coaches_list:
			all_coaches_list.append(final_coach)

	#Create list of coach objects
	for current_coach in all_coaches_list:
		seasons_count = 0
		for season in all_seasons_list:
			if current_coach in season.coach:
				seasons_count+=1
		coach_objects_list.append(CoachObject(current_coach,teamstripped,seasons_count))

	try:
		cur.execute("SELECT School FROM Coaches WHERE Coaches.School = %s", (lower_team,))
		testteam = cur.fetchone()
		termconfirm = testteam['school']

	except:
		for current_coach in coach_objects_list:
			cur.execute(""" INSERT INTO Coaches (Name, School, Season_count, Years_active, Overall_record) values (%s, %s, %s, %s, %s)""",(current_coach.coachname + " (" + current_coach.school+")", current_coach.school, current_coach.coach_seasons, current_coach.get_years_coached(all_seasons_list), current_coach.get_overall_percent(all_seasons_list)))
			conn.commit()

		for current_season in all_seasons_list:
			cur.execute(""" INSERT INTO Seasons (Year, School, Conference, Wins, Losses, Ties, Win_percent, Simple_rating_score, Strength_of_schedule, Highest_rank, Coach, Bowl_game) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(current_season.year, current_season.school, current_season.conference, current_season.wins, current_season.losses, current_season.ties, current_season.win_percent, current_season.simple_rating_score, current_season.strength_of_schedule, current_season.highest_ap_rank, current_season.pretty_coachname()+" (" +current_season.school+")", current_season.bowl))
			conn.commit()

	working_football_csv = teamstripped+'football_seasons.csv'

	#write a CSV file for the specific team
	if doorway == 'open':
		try:
		    open(working_football_csv, 'r')
		except:
			columnheaders = ("Year,Conference,Wins,Losses,Ties, Win_Percent, Simple_Rating_Score, Strength_of_schedule, Highest_rank, Coach, Bowl\n")
			fcsv = open(working_football_csv, 'a') #write a new line, do not write over existing data
			fcsv.write(columnheaders)
			for current_season in all_seasons_list:
				fcsv.write(current_season.season_csv_str())
			fcsv.close()

	years_list =[]
	win_pct_list =[]
	win_total_list = []
	for year in all_seasons_list:
		years_list.append(year.year)
		win_pct_list.append(year.win_percent)
		win_total_list.append(year.wins)


	return years_list, win_pct_list, win_total_list


def input_and_run():
	print("Welcome to the football index. Take a look at one team to view their wins and win percent over time. Choose 2 teams to compare them!")
	question = "1"
	question = input("Look at 1 FBS/FCS Football team or 2?: (1/2):    ")
	teamname1 = ""
	teamname2 = ""
	team1_years = []
	number_coaches2 = 0
	if question == "1":
		teamnamex = input('Enter an FBS or FCS College Football School Such as: Wisconsin, Michigan , Michigan State:  ')
		try:
			number_coaches1 = int(input("For "+teamnamex +" How many coaches do you want to see data for? (e.g. 5):    "))
		except:
			number_coaches1 = 10
		teamname1 = teamnamex.lower()
		print("")
		team1_years, team1_win_pct, team1_win_list = (main_process(teamname1))
	elif question == "2":
		teamnamex = input('Enter Team 1: FBS or FCS College Football School Such as: Wisconsin, Michigan , Michigan State:  ')
		teamnamey = input('Enter Team 2:   ')
		try:
			number_coaches1 = int(input("For "+teamnamex +" How many coaches do you want to see data for? (e.g 5):    "))
		except:
			number_coaches1 = 10
		try:
			number_coaches2 = int(input("For "+teamnamey +" How many coaches do you want to see data for? (e.g. 5):    "))
		except:
			number_coaches2 = 10
		teamname1 = teamnamex.lower()
		teamname2 = teamnamey.lower()
		team2_years, team2_win_pct, team2_win_list = (main_process(teamname2))
		team1_years, team1_win_pct, team1_win_list = (main_process(teamname1))

	if team1_years != []:
		if question == "1":
			plotly_1(team1_years, team1_win_pct, team1_win_list, teamname1)
		elif question == "2":
			plotly_2(team1_years, team1_win_pct, team1_win_list, team2_years, team2_win_pct, team2_win_list, teamname1, teamname2)
		if teamname2 != "":	
			return teamname1, teamname2, number_coaches1, number_coaches2
		else:
			return teamname1, teamname1, number_coaches1, number_coaches2


def final_function():
	try:
		teamname1, teamname2, number_coaches1, number_coaches2 = input_and_run()
		teamstr1 = "'%"+teamname1+"'"
		teamstr2 = "'%"+teamname2+"'"
		if teamname1 == teamname2:	
			# number_coaches1 = int(input("For "+teamname1 +" How many coaches do you want to see data for? (1,2,10) "))
			query1 = 'SELECT Coaches.Name, Coaches.season_count, Coaches.years_active, Coaches.overall_record from Coaches WHERE coaches.school LIKE'+teamstr1
			print("Coach Summary for "+teamname1)
			execute_and_print(query1,number_coaches1)
		elif teamname1 != teamname2:
			# number_coaches1 = int(input("For "+teamname1 +" How many coaches do you want to see data for? (1,2,10) "))
			query1 = 'SELECT Coaches.Name, Coaches.season_count, Coaches.years_active, Coaches.overall_record from Coaches WHERE coaches.school LIKE'+teamstr1
			print("Coach Summary for "+teamname1)
			execute_and_print(query1,number_coaches1)
			# number_coaches2 = int(input("For "+teamname2 +" How many coaches do you want to see data for? (1,2,10) "))
			query2 = 'SELECT Coaches.Name, Coaches.season_count, Coaches.years_active, Coaches.overall_record from Coaches WHERE coaches.school LIKE'+teamstr2
			print("Coach Summary for "+teamname2)
			execute_and_print(query2,number_coaches2)
		if teamname1 == teamname2:
			print(".CSV file created for "+teamname1)
		else:
			print(".CSV files created for "+teamname1+" and "+teamname2)
	except:
		print('Could not complete request')

conn, cur = get_connection_and_cursor()
rewrite = 'Y'
rewrite = input("Initialize / Re-Write the DB? Careful, cannot be undone! enter 'Y' for yes, any other key for No:    ")
if rewrite == 'Y':
	setup_database()
go_again = 'Y'
while go_again != 'q':
	final_function()
	go_again = input('Type "q" to quit, or hit any other key to run the program again:    ')


