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
from SI507F17_finalproject import final_function,input_and_run,main_process,CoachObject,SeasonObject, plotly_2,plotly_1,execute_and_print,setup_database,get_connection_and_cursor
import unittest 


class TestFinalProject(unittest.TestCase):
	def setUp(self):
		try:
			self.conn, self.cur = get_connection_and_cursor()
			self.verifier = "yes"
		except:
			self.verifier = "no"

		self.badger_data  = requests.get('https://www.sports-reference.com/cfb/schools/wisconsin/').text
		self.badgersoup = BeautifulSoup(self.badger_data, 'html.parser')
		self.badger_seasons_table = self.badgersoup.find("tbody")

		# self.testrow ='<tr><th class="right " csk="107" data-stat="ranker" scope="row">107</th><td class="right " data-stat="year_id"><a href="/cfb/schools/wisconsin/1911.html">1911</a></td><td class="left " data-stat="conf_id"><a href="/cfb/conferences/western/1911.html">Western</a></td><td class="right " data-stat="wins">5</td><td class="right " data-stat="losses">1</td><td class="right " data-stat="ties">1</td><td class="right " data-stat="win_loss_pct">.786</td><td class="right " data-stat="srs">14.93</td><td class="right " data-stat="sos">1.79</td><td class="center " csk="999.1911" data-stat="rank_pre"></td><td class="center " csk="999.1911" data-stat="rank_min"></td><td class="center " csk="999.1911" data-stat="rank_final"></td><td class="left " csk="Richards,J.R..1911" data-stat="coaches"><a href="/cfb/coaches/jr-richards-1.html">J.R. Richards</a> (5-1-1)</td><td class="left " csk="ZZZ.1911" data-stat="bowl_name"></td><td class="left " data-stat="notes"></td></tr>'
		# final_function(question="1", teamnamex="Wisconsin", teamnamey="Michigan", number_coaches1=1, number_coaches2=1)
		self.testlist = []
		for season in self.badger_seasons_table:
			self.testlist.append(SeasonObject(season,'wisconsin'))

		self.wisco_years, self.wisco_win_pct,self.wisco_win_total = main_process('wisconsin')
		
		self.query = "SELECT Coaches.Name, Coaches.season_count, Coaches.years_active, Coaches.overall_record from Coaches WHERE coaches.school LIKE '%wisconsin%'"
		self.cur.execute(self.query)
		self.results = self.cur.fetchall()
		self.testcoach = CoachObject('Jacob Haspiel','wisconsin')

	def test_mainprocess_output(self):
		self.assertTrue(type(self.wisco_years) == list)
		self.assertTrue(type(self.wisco_win_pct) == list)
		self.assertTrue(type(self.wisco_win_total) == list)

	def test_years(self):
		self.assertTrue(type(self.wisco_years[0]) == str)

	def test_win_pct(self):
		self.assertTrue(type(self.wisco_win_pct[0]) == str)

	def test_win(self):
		self.assertTrue(type(self.wisco_win_total[0]) == str)

	def test_query_term(self):
		self.assertTrue(self.results[0]['name']=='Paul Chryst (wisconsin)')
	def test_results_return(self):
		self.assertTrue(len(self.results)==27)

	def test_conn_cur(self):
		self.assertTrue(self.verifier =="yes")

	def test_coach_class_init(self):
		self.assertTrue(self.testcoach.coachname =='Jacob Haspiel')
		self.assertTrue(self.testcoach.school =='wisconsin')


	# def test_cache_diction(self):
	# 	self.assertTrue(type(self.cache)==dict)



class TestPlotting(unittest.TestCase):
	def setUp(self):
		self.testyearslist1 = [2014,2015,2016]
		self.testteamname1 = 'orcs'
		self.testwinlist1 = [10,12,14]
		self.testwinpctlist1 = [.83,.89,.96]
		self.testyearslist2 = [2014,2015,2016]
		self.testteamname2 = 'elves'
		self.testwinlist2 = [7,6,5]
		self.testwinpctlist2 = [.25,.31,.29]
		self.plotly1= plotly_1(self.testyearslist1, self.testwinlist1,self.testwinpctlist1,self.testteamname1)
		self.plotly2= plotly_2(self.testyearslist1, self.testwinlist1,self.testwinpctlist1,self.testyearslist2, self.testwinlist2,self.testwinpctlist2,self.testteamname1,self.testteamname2)
	

	def test_plotly1_type(self):
		self.assertTrue(type(self.plotly1)==dict)
	def test_plotly1_wins(self):
		self.assertEqual(len(self.plotly1['data']),2)
	def test_plotly1_title(self):
		print(self.plotly1['layout']['title'])
		self.assertTrue(self.testteamname1 in self.plotly1['layout']['title'])

	def test_plotly2_type(self):
		self.assertTrue(type(self.plotly2)==dict)
	def test_plotly2_wins(self):
		self.assertEqual(len(self.plotly2['data']),4)
	def test_plotly2_title(self):
		self.assertTrue(self.testteamname1, self.testteamname2 in self.plotly2['layout']['title'])

	
# \


unittest.main(verbosity=2)