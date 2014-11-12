#
# This program goes to USCF website get all CO tournaments. Then, calculates tour points for all
# CO players in these tournaments
# By Jackson Chen
#

import urllib
import os
import re
from datetime import datetime

START_DATE = datetime.strptime('2014-08-29', '%Y-%m-%d')
END_DATE = datetime.strptime('2015-09-01', '%Y-%m-%d')
TOUR_TOURNAMENTS_MAP = {
   '2014 COLORADO OPEN': 3,
}

class Tournament:
     def __init__(self, num_sec, t_date, link, name):
        self.nsec = num_sec
        self.date = t_date
        self.link = link
        self.name = name
        self.sections = dict()

class Section:
     def __init__(self, nrounds, name, playersMap, averagerating):
        self.name = name
        self.players = playersMap
        self.nrounds = nrounds
        self.avrating = averagerating

class Player:
     def __init__(self, id, name, rank, score, state, rating, points, ngames, accumrating, withdrew):
        self.name = name
        self.id = id
        self.rank = rank
        self.score = score
        self.state = state
        self.rating = rating
        self.points = points
        self.ngames = ngames
        self.accumrating = accumrating
        self.withdrew = withdrew

class TDParser:
    def __init__(self):
         self.startTr = False
         self.startTd = False
         self.getNextTag = False
         self.tdName = ""
         self.tdId = ""

    def parse(self, line1d):
        self.startTr = False
        self.startTd = False
        self.getNextTag = False
        for aline in line1d:
            if aline.find("<tr") >= 0:
                self.startTr = True
            elif aline.find("</tr>") >= 0:
                self.startTr = False
                self.getNextTag = False
            elif aline.find("<td") >= 0:
                self.startTd = True
            elif aline.find("</td>") >= 0:
                self.startTd = False
            elif self.startTr and self.startTd and "chief" in aline.lower() and "TD" in aline:
                self.getNextTag = True
                #print "aline:", aline
            elif self.startTr and self.startTd and self.getNextTag and aline.strip():
                #print "Found Data:", aline
                matchObj = re.match(r"<b>(.*)</b>.*<small>\((.*)\)</small>", aline, re.M)
                if matchObj:
                    self.tdName = matchObj.group(1)
                    self.tdId = matchObj.group(2)
                    #print "TD Name: ", self.tdName, ", TD ID: ", self.tdId

class RatingParser:
    def __init__(self, id):
         self.startTr = False
         self.startTd = False
         self.getNextTag = False
         self.tdId = id
         self.rating = 0
         self.url = ""

    def parse(self):
        self.url = "http://www.uschess.org/msa/MbrDtlMain.php?" + self.tdId
        line1d = readData(self.url)
        #print "Rating URL: ", self.url
        for aline in line1d:
            if aline.find("<tr") >= 0:
                self.startTr = True
            elif aline.find("</tr>") >= 0:
                self.startTr = False
                self.getNextTag = False
            elif aline.find("<td") >= 0:
                self.startTd = True
            elif aline.find("</td>") >= 0:
                self.startTd = False
            elif self.startTr and self.startTd and "regular rating" in aline.lower():
                self.getNextTag = True
                #print "aline:", aline
            elif self.startTr and self.startTd and self.getNextTag and aline.strip() and aline.find("<b>") < 0 and aline.find("</b>") < 0 and aline.find("/br>") < 0 and aline.find("<br>") < 0:
                #print "Found Data:", aline
                matchObj = re.match(r"(\d+).*", aline, re.M)
                if matchObj:
                    self.rating = matchObj.group(1)
                    #print "Rating: ", self.rating, ", TD ID: ", self.tdId


def readData(url):
    urllib.urlretrieve(url, "C:\\Jackson\\Server\\Apache24\\htdocs\\chess\\stats\\CO_Open.txt")

    file = open("C:\\Jackson\\Server\\Apache24\\htdocs\\chess\\stats\\CO_Open.txt", 'r')
    line1d = []
    while 1:
        line = file.readline()
        if not line:
           break
        line1d.append(line)
    file.close()
    return line1d

def parseTournamentData(line1d):
        tournaments = []
        for aline in line1d:
           a_line = aline

           #1st line of tournaments is merged with heading line. have to separate them
           matchObj = re.match(r"<tr><td>Event ID</td><td>Sec</td><td>State</td><td>City</td><td>Dates</td><td>Plr</td><td>Event Name</td>(.*)",a_line, re.M)
           if matchObj:
                a_line = matchObj.group(1)
#
# A sample line:
#</tr><tr><td>201209254192 &nbsp;&nbsp;&nbsp;</td><td>1 &nbsp;&nbsp;&nbsp;</td><td>CO &nbsp;&nbsp;&nbsp;</td><td>FORT COLLINS &nbsp;&nbsp;&nbsp;</td><td>2012-09-04  - 09-25 &nbsp;&nbsp;&nbsp;</td><td>9 &nbsp;&nbsp;&nbsp;</td><td><a href=http://www.uschess.org/msa/XtblMain.php?201209254192 target='_blank'>FCCC SEPT 2012 G70</a></td>
#
           matchObj = re.match(r"[\S\s]+<tr><td>(\d+)\s+\S+</td><td>(\d+)\s+\S+</td><td>CO\s+\S+</td><td>([\w\s]+)\s+\S+</td><td>(\d\d\d\d-\d\d-\d\d)[\s\S]+</td><td>(\d+)\s+\S+</td><td><a href=(\S+)\s+\S+>([\w\s]+)</a></td>", a_line, re.M)
           if matchObj:
               numOfSections = matchObj.group(2)
               tournamentDateStr = matchObj.group(4)
               tournamentDate = datetime.strptime(tournamentDateStr, '%Y-%m-%d')
               tournamentLink = matchObj.group(6)
               tournamentName = matchObj.group(7)
               if (tournamentDate > START_DATE and tournamentDate < END_DATE):
                 hit = 0;
                 for item in TOUR_TOURNAMENTS_MAP.keys():
                    if tournamentName.find(item) != -1:
                        hit = 1
                        break
                 if hit:
                     tournament = Tournament(TOUR_TOURNAMENTS_MAP[tournamentName], tournamentDate, tournamentLink, tournamentName)
                     tournaments.append(tournament)
                     print ("event: ", matchObj.group(1), ", no of section: ", tournament.nsec, ", city: ", matchObj.group(3), ", date: ", tournament.date, ", link: ", tournament.link , ", name: ", tournament.name)

        return tournaments

def parsePlayerData(line1d):
        playersMap = dict()
        sectionName = ""
        nrounds = 0
        averagerating = 0
        for aline in line1d:
           #find section name
           #<b>Section 1 - CHAMPIONSH</b>
           matchObj = re.match(r"<b>Section\s+(\d+)\s+-\s+(.*)</b>",aline, re.M)
           if matchObj:
               sectionNum = matchObj.group(1)
               sectionName = matchObj.group(2)

           #find number of rounds and number of players in the section
           #<b>5 Rounds,&nbsp; 48 Players;  &nbsp;K Factor: F  &nbsp;Rating Sys: R  &nbsp;Tnmt Type: S  <br>Time Control: Round 1: G/90;d5, Round 2: G/90;d5, Round 3: G/90;+30, Round 4: G/90;+30, Round 5: G/90;+30</b>
           matchObj = re.match(r"<b>(\d+) Rounds[\S\s]*\s(\d+)\s+Players[\S\s]*Rating Sys[\S\s]*Tnmt Type[\S\s]*</b>",aline, re.M)
           if matchObj:
               nrounds = int(matchObj.group(1))
               nplayers = matchObj.group(2)

           #find players
           #    <a href=XtblPlr.php?201309013042-001-12805139>4</a> | <a href=MbrDtlMain.php?12805139>ZACHARY ALLAN BEKKEDAHL</a>        |4.0  |W  36|H    |H    |W  15|W  17|
           matchObj = re.match(r"\s+<a\s+href=\S+\?\d+-\d+-(\d+)>(\d+)</a>\s+\|\s+<a\s+href=\S+\?\d+>(.*)</a>\s+\|(\d+\.\d+)\s+\|(.*)",aline, re.M)
           if matchObj:
               playerId = matchObj.group(1)
               playerRank = matchObj.group(2)
               playerName = matchObj.group(3)
               playerScore = float(matchObj.group(4))
               playerGames = matchObj.group(5)
               playerGamesArray = playerGames.split('|')
               playerGameNum = 0
               playerUCount = 0
               for i in range(len(playerGamesArray)):
                   if playerGamesArray[i].find("W")>-1:
                       playerGameNum += 1
                   if playerGamesArray[i].find("L")>-1:
                       playerGameNum += 1
                   if playerGamesArray[i].find("D")>-1:
                       playerGameNum += 1
                   if playerGamesArray[i].find("B")>-1:
                       playerGameNum += 1
                   if playerGamesArray[i].find("X")>-1:
                       playerGameNum += 1
                   if playerGamesArray[i].find("H")>-1:
                       playerScore -= 0.5
                   if playerGamesArray[i].find("U")>-1:
                       playerUCount += 1

               #def __init__(self, id, name, rank, score, state, rating, points, ngames, accumrating, withdrew):
               player = Player(playerId, playerName, playerRank, playerScore, "", 0, 0, playerGameNum, 0, playerUCount)
               if playerId in playersMap:
                   if playersMap[playerId].withdrew > player.withdrew:
                       pass
                   else:
                       continue
               else:
                   playersMap[playerId] = player

           #find player state and rating
           #   SD | 12812673 / R: 2353   ->2369    |N:M  |     |     |     |     |     |
           matchObj = re.match(r"\s+(\w+)\s+\|\s+(\d+)\s+/\s+R\:\s*(\S+)\s*->\s*(\S+)\s*\|[\S\s]*",aline, re.M)
           if matchObj:
               playerState = matchObj.group(1)
               playerId = matchObj.group(2)
               playerRatingBefore = matchObj.group(3)
               playerRatingAfter = matchObj.group(4)
               playersMap[playerId].state = playerState
               playersMap[playerId].rating = playerRatingBefore
               if playersMap[playerId].rating.lower() == "unrated":
                  playersMap[playerId].rating = playerRatingAfter
                  m = re.match(r"(\d+)P\d+", playersMap[playerId].rating, re.M)
                  if m:
                      playersMap[playerId].rating = int(m.group(1))
                  else:
                      playersMap[playerId].rating = int(playersMap[playerId].rating)
               else: 
                  m = re.match(r"(\d+)P\d+", playersMap[playerId].rating, re.M)
                  if m:
                      playersMap[playerId].rating = int(m.group(1))
                  else:
                      averagerating += int(playerRatingBefore)
                      playersMap[playerId].rating = int(playersMap[playerId].rating)
               playersMap[playerId].accumrating = playersMap[playerId].ngames * playersMap[playerId].rating
        averagerating = averagerating/len(playersMap)
        return nrounds, sectionName, playersMap, averagerating

def htmldisplay(title, ntop, playerArray, tieflag):
    file_handle.write("<table border=\"1\" cellpadding=\"2\" cellspacing=\"0\" width=\"400\"> \n")
    file_handle.write("<tr><td align=\"left\" colspan=\"5\"><a name=\"active\"></a><b>"+title+"</b></td></tr> \n")
    file_handle.write("<tr><th>&nbsp;</th><th align=\"left\">Name</th><th>Rating</th><th>Points</th><th>Games</th></tr> \n")
    rank = 1
    for ii in range(len(playerArray)):
        player = playerArray[ii]
        if ii>0 and tieflag == 1 and playerArray[ii].points != playerArray[ii-1].points:
            rank = ii+1
        if ii>0 and tieflag == 2 and playerArray[ii].ngames != playerArray[ii-1].ngames:
            rank = ii+1
        if rank >= ntop+2:
            break
        file_handle.write("<tr><td align=\"right\">"+str(rank)+"&nbsp;</td><td>"+player.name+"&nbsp;</td><td align=\"right\">"+str(player.rating)+"&nbsp;</td><td align=\"right\">"+str(round(player.points, 2))+"&nbsp;</td><td align=\"right\">"+str(player.ngames)+"&nbsp;</td></tr>\n")
        
    file_handle.write("</table>\n")
    file_handle.write("<br>\n")

"""Main"""
#read all CO tournaments
#line1d = readData("http://www.uschess.org/datapage/event-search.php?name=&state=CO&city=&date_from=&date_to=&order=D&minsize=&mode=Find");
#http://www.uschess.org/datapage/event-search.php?name=&state=CO&city=&date_from=2011-08-30&date_to=2013-08-30&order=L&minsize=&mode=Find
allTournaments = dict()
num_of_get = 3
time_diff = END_DATE - START_DATE
for time_index in range(0, num_of_get):
    from_date = START_DATE + time_diff/num_of_get*time_index
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date = from_date + time_diff/num_of_get
    if to_date > END_DATE:
        to_date = END_DATE
    to_date_str = to_date.strftime('%Y-%m-%d')
    url = "http://www.uschess.org/datapage/event-search.php?name=&state=CO&city=&date_from="+from_date_str+"&date_to="+to_date_str+"&order=D&minsize=&mode=Find"
    line1d = readData(url);
    #print "url: ", url, ", time difference: ", time_diff.days
    tournaments = parseTournamentData(line1d);
    for tournament in tournaments:
        allTournaments[tournament.name] = tournament

#read each tournament
for tournament_name in allTournaments.keys():
    tournament = allTournaments[tournament_name]
    url = tournament.link
    for i in range(0, tournament.nsec):
        if tournament.nsec > 1:
           url = tournament.link + "." + str(i+1);
        line1d = readData(url);
        nrounds, sectionName, playersMap, averagerating = parsePlayerData(line1d)
        averagerating = averagerating + 100

		#creates section and adds PlayersMap to the section, and adds section to tournament
        section = Section(nrounds, sectionName, playersMap, averagerating)
        tournament.sections[sectionName] = section
        
        print ("Section name: ", section.name, ", number of players: ", len(section.players), ", Tournament: ", tournament_name)
    
    #parse chief TD
    parser = TDParser()
    line1d = readData(url);
    parser.parse(line1d)
    #print ("===== CHIEF TD is: ", parser.tdName, " TD ID: ", parser.tdId, " URL: ", url)
    rParser = RatingParser(parser.tdId)
    rParser.parse()
    #print ("===== CHIEF TD Rating is: ", rParser.rating, " TD ID: ", rParser.tdId, " TOURNAMENT NAME: ", tournament_name)
    tddeterminer = []

	#Determines TD section (according to rating)
    for key in tournament.sections.keys():
        tddeterminer.append(int(rParser.rating) - tournament.sections[key].avrating)
    tdsection = min(abs(i) for i in tddeterminer)
    tdplayer = Player(parser.tdId, parser.tdName, 0, nrounds/2, "CO", rParser.rating, 0, nrounds, int(nrounds) * int(rParser.rating), 0)

	#Determines TD player's section
    foundTDsection = ""
    for key in tournament.sections.keys():
        if parser.tdId in tournament.sections[key].players:
            foundTDsection = key

	#creates and adds TD player to proper section
    if foundTDsection == "":
        for key in tournament.sections.keys():
            if tournament.sections[key].avrating == tdsection + int(rParser.rating) or tournament.sections[key].avrating == (-1)*tdsection + int(rParser.rating):
                tournament.sections[key].players[parser.tdId] = tdplayer
                break
    else:
		if tdplayer.withdrew < tournament.sections[foundTDsection].players[parser.tdId].withdrew:
			tournament.sections[foundTDsection].players[parser.tdId] = tdplayer


allPlayersMap = dict()
#calculate tour points
for tournament_name in allTournaments.keys():
    tournament = allTournaments[tournament_name]
    for section_name in tournament.sections.keys():
        section = tournament.sections[section_name]
        for player_name in section.players.keys():
           player = section.players[player_name]
           player.points = len(section.players) * (1 + float(player.score))/section.nrounds
           if(player.state == "CO"):
               if player.id in allPlayersMap:
                  allPlayersMap[player.id].points += player.points
                  allPlayersMap[player.id].ngames += player.ngames
                  allPlayersMap[player.id].accumrating += player.accumrating
                  #if player.id == "13383565":
                  #    print "jackson", allPlayersMap["13383565"].ngames, tournament_name, section_name, player_name
               else:
                  allPlayersMap[player.id]=player
                  allPlayersMap[player.id].ngames = player.ngames
                  #if player.id == "13383565":
                  #    print "jackson", allPlayersMap["13383565"].ngames, tournament_name, section_name, player_name


#put players into their rating bucket
allPlayers = []
aPlayers = []
bPlayers = []
cPlayers = []
dPlayers = []
ePlayers = []
expertPlayers = []
unratedPlayers = []
activePlayers = []
for playerId in allPlayersMap.keys():
    player = allPlayersMap[playerId]
    player.rating = int(player.accumrating/player.ngames)
    allPlayers.append(player)
    activePlayers.append(player)
    if player.rating == 0:
        unratedPlayers.append(player)
    elif int(player.rating) < 1200:
        ePlayers.append(player)
    elif int(player.rating) < 1400:
        dPlayers.append(player)
    elif int(player.rating) < 1600:
        cPlayers.append(player)
    elif int(player.rating) < 1800:
        bPlayers.append(player)
    elif int(player.rating) < 2000:
        aPlayers.append(player)
    elif int(player.rating) < 2200:
        expertPlayers.append(player)

#sort players by points
allPlayers.sort(key=lambda x: x.points, reverse=True)
aPlayers.sort(key=lambda x: x.points, reverse=True)
bPlayers.sort(key=lambda x: x.points, reverse=True)
cPlayers.sort(key=lambda x: x.points, reverse=True)
dPlayers.sort(key=lambda x: x.points, reverse=True)
ePlayers.sort(key=lambda x: x.points, reverse=True)
expertPlayers.sort(key=lambda x: x.points, reverse=True)
activePlayers.sort(key=lambda x: x.ngames, reverse=True)
print ("-----------------------------------------------")
print ("Tour winner overall: name: ", allPlayers[0].name, ", rating: ", allPlayers[0].rating, ", points: ", allPlayers[0].points)
print ("Tour winner A: name: ", aPlayers[0].name, ", rating: ", aPlayers[0].rating, ", points: ", aPlayers[0].points)
print ("Tour winner B: name: ", bPlayers[0].name, ", rating: ", bPlayers[0].rating, ", points: ", bPlayers[0].points)
print ("Tour winner C: name: ", cPlayers[0].name, ", rating: ", cPlayers[0].rating, ", points: ", cPlayers[0].points)
print ("Tour winner D: name: ", dPlayers[0].name, ", rating: ", dPlayers[0].rating, ", points: ", dPlayers[0].points)
print ("Tour winner E: name: ", ePlayers[0].name, ", rating: ", ePlayers[0].rating, ", points: ", ePlayers[0].points)
print ("Tour winner Expert: name: ", expertPlayers[0].name, ", rating: ", expertPlayers[0].rating, ", points: ", expertPlayers[0].points)
#output HTML file
ntop = 10
file_handle = open("C:\\Jackson\\Server\\Apache24\\htdocs\\chess\\stats\\tour.html", 'w')
outStr1="""
<!doctype html>
 
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Top 10 Colorado Chess</title>
  <link rel="icon" type="image/png" href="favicon.png">
  <link rel="stylesheet" href="css/style.css" />
  <link rel="stylesheet" href="css/toptour.css" />
  <script src="js/toptour.js"></script>
  <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
  <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
  <script>
  $(function() {
    $( "#tabs" ).tabs();
  });
  </script>
</head>
<body>
<h2><a href="index.html" id="title" onmouseover="underline()" onmouseout="leave()">2014-2015 Colorado Tour</a></h2>
<div id="tabs">
  <ul>
    <li><a href="#tabs-1">Top 10 Overall</a></li>
    <li><a href="#tabs-2">Top 10 Active</a></li>
    <li><a href="#tabs-3">Top 10 Expert</a></li>
    <li><a href="#tabs-4">Top 10 A</a></li>
    <li><a href="#tabs-5">Top 10 B</a></li>
    <li><a href="#tabs-6">Top 10 C</a></li>
    <li><a href="#tabs-7">Top 10 D</a></li>
    <li><a href="#tabs-8">Top 10 E</a></li>
    <li><a href="#tabs-9">Full Standings</a></li>
	<li><a href="#tabs-10">Tournaments</a></li>

  </ul>
"""
tournStr1="""
<div id='tabs-10'>
<u>Completed Tournaments</u>
	<ul>
		<li>Colorado Open (August 30-31, 2014)</li>
	</ul>
<br>
<u>Upcoming Tournaments</u>
	<ul>
		<li>Winter Springs Open (December 6-7, 2014)</li>
		<li>Boulder Open (March 27-29, 2015)</li>
	</ul>
</div>
"""

file_handle.write(outStr1)
# expert
file_handle.write("<div id='tabs-3'>")
htmldisplay("Top "+str(ntop)+" Expert", ntop-1, expertPlayers, 1)
file_handle.write("</div>")
# class A
file_handle.write("<div id='tabs-4'>")
htmldisplay("Top "+str(ntop)+" Class A", ntop-1, aPlayers, 1)
file_handle.write("</div>")
# class B
file_handle.write("<div id='tabs-5'>")
htmldisplay("Top "+str(ntop)+" Class B", ntop-1, bPlayers, 1)
file_handle.write("</div>")
# class C
file_handle.write("<div id='tabs-6'>")
htmldisplay("Top "+str(ntop)+" Class C", ntop-1, cPlayers, 1)
file_handle.write("</div>")
# class D
file_handle.write("<div id='tabs-7'>")
htmldisplay("Top "+str(ntop)+" Class D", ntop-1, dPlayers, 1)
file_handle.write("</div>")
# class E
file_handle.write("<div id='tabs-8'>")
htmldisplay("Top "+str(ntop)+" Class E", ntop-1, ePlayers, 1)
file_handle.write("</div>")
# overall
file_handle.write("<div id='tabs-1'>")
htmldisplay("Top "+str(ntop)+" Overall", ntop-1, allPlayers, 1)
file_handle.write("</div>")
# active
file_handle.write("<div id='tabs-2'>")
htmldisplay("Top "+str(ntop)+" Active", ntop-1, activePlayers, 2)
file_handle.write("</div>")
# all
file_handle.write("<div id='tabs-9'>")
htmldisplay("Full Standing", len(allPlayers), allPlayers, 1)
file_handle.write("</div>")

file_handle.write(tournStr1)

file_handle.write("</div>")
file_handle.write("</body>\n")
file_handle.write("</html>\n")
file_handle.close()
