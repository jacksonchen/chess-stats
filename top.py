#
# This program goes to USCF website get all CO tournaments. Then, calculates tour porints for all
# CO players in these tournaments
# By Jackson Chen
#

import os
import re
from datetime import datetime
import urllib2
from HTMLParser import HTMLParser

class Player:
     def __init__(self, id, name, rating, date, title, gender, isJunior):
         self.name = name
         self.id = id
         self.rating = rating
         self.beforeRating = 0
         self.date = date
         self.title = title
         self.gender = gender
         self.junior = isJunior
         self.tournament = ""

class TokenParser(HTMLParser):
    def __init__(self, token):
         self.reset()
         self.startTr = False
         self.startTd = False
         self.getNextTag = False
         self.token = token
         self.value = ""

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.startTr = True
        if tag == "td":
            self.startTd = True
    def handle_endtag(self, tag):
        if tag == "tr":
            self.startTr = False
        if tag == "td":
            self.startTd = False
    def handle_data(self, data):
        #print "data: ", data
        dataWithoutNewLine = data.replace('\n', '')
        if self.startTr and self.startTd and self.token.lower() in dataWithoutNewLine.lower():
            self.getNextTag = True
        elif self.startTr and self.startTd and self.getNextTag and dataWithoutNewLine.strip() != "":
            self.value = data
            self.getNextTag = False

class TableParser(HTMLParser):
    def __init__(self, token):
         self.reset()
         self.startTable = False
         self.startTh = False
         self.startTr = False
         self.startTd = False
         self.token = token
         self.getNextRow = False
         self.foundToken = False
         self.headings = []
         self.array2d = []
         self.array1d = []
         self.link = []
         self.attr = ""
         self.tableIndex = 0
         self.trIndex = 0
         self.tdIndex = 0
         self.thIndex = 0

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.startTr = True
            self.trIndex += 1
            if self.getNextRow and len(self.array1d) > 0:
                self.array1d = []
        if tag == "td":
            self.startTd = True
            self.tdIndex += 1
        if tag == "th":
            self.startTh = True
            self.thIndex += 1
        if tag == "table":
            self.startTable = True
            self.tableIndex += 1
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.attr = value
            
    def handle_endtag(self, tag):
        if tag == "tr":
            if self.getNextRow and len(self.array1d) > 0:
                self.array2d.append(self.array1d)
                self.link.append(self.attr)
                #print "Add a row: ", self.array1d 
            if self.startTh or self.foundToken:
                self.getNextRow = True
            self.startTr = False
            self.startTh = False
            self.startTd = False
            self.thIndex = 0
            self.tdIndex = 0
        if tag == "td":
            self.startTd = False
        if tag == "table":
            self.startTable = False
            self.getNextRow = False
            self.foundToken = False
            self.trIndex = 0
            self.thIndex = 0
            self.tdIndex = 0

    def handle_data(self, data):
        #print "table: ", self.tableIndex, ", tr: ", self.trIndex, ", td: ", self.tdIndex, ", th: ", self.thIndex, ", data: ", data, ", th start: ", self.startTh, ", tr start: ", self.startTr, ", td start: ", self.startTd, ", table start: ", self.startTable, ", getNextRow: ", self.getNextRow
        if self.trIndex > 0:
            # Heading row
            dataWithoutNewLine = data.replace('\n', '').strip()
            if self.startTh and self.thIndex > 0:
                if len(self.headings) < self.thIndex:
                    self.headings.append([])
                if dataWithoutNewLine != "":
                    self.headings[self.thIndex-1].append(dataWithoutNewLine)
            # Data rows
            if self.getNextRow and self.tdIndex > 0:
                if len(self.array1d) < self.tdIndex:
                    self.array1d.append([])
                if dataWithoutNewLine != "":
                    self.array1d[self.tdIndex-1].append(dataWithoutNewLine)
                #print "Data: ", dataWithoutNewLine
            # find token
            if (dataWithoutNewLine != "") and self.token != "" and self.token in dataWithoutNewLine:
                self.foundToken = True

from PyPDF2 import PdfFileReader

def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
    # Collapse whitespace
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content
       
                
def readData(url):
        response = urllib2.urlopen(url)
        return response.read()

import sys

"""Main"""
#read all CO players from the table in USCF page and parse it into 2d-array
allTournaments = dict()
url = "http://main.uschess.org/datapage/top-players2.php?state=CO&limit=&maxcnt=1000&players=M&rtgsys=R&current=C"
line1d = readData(url)
line1d = line1d.replace("<td>&nbsp;</td>","<td> </td>")
parser = TableParser("")
parser.feed(line1d)
#print "HEADING: ", parser.headings

#convert 2d-array to a list of Player objects
allPlayers = []
for array1d in parser.array2d:
    id = array1d[1][0]
    name = array1d[3][0]
    rating = int(array1d[4][0]) if (array1d[4][0].isdigit()) else 0
    date = array1d[5][0]
    title = array1d[6][0] if (len(array1d[6]) > 0) else ""
    aPlayer = Player(id, name, rating, date, title, "M", False)
    allPlayers.append(aPlayer)
    #print "Player: id: ", aPlayer.id, ", name: ", aPlayer.name, ", rating, ", aPlayer.rating, ", date: ", aPlayer.date, ", title: ", aPlayer.title

#read CO Scholastic tournament PDF file
#coScholasticPdf = getPDFContent("2013CSCAStateFinalStandings.pdf").encode("ascii", "ignore")
coScholasticPdf = getPDFContent("C:\\Jackson\\Server\\Apache24\\htdocs\\chess\\stats\\2013CSCAStateFinalStandings.pdf").encode("ascii", "ignore")
coScholasticPdf = coScholasticPdf.lower()
scholasticPlayerList = "DANIEL ZHOU, Isaac Martinez"
scholasticPlayerList = scholasticPlayerList.lower()
nonScholasticPlayerList = "ALEXA E LASLEY"
nonScholasticPlayerList = nonScholasticPlayerList.lower()

# fill in rating, gender for each player
for aPlayer in allPlayers:
    playerUrl = "http://www.uschess.org/msa/MbrDtlMain.php?" + aPlayer.id
    print ("playerUrl: ", playerUrl)
    line1d = readData(playerUrl);

    # get Female and Junior
    playerFemaleParser = TokenParser("Female")
    playerFemaleParser.feed(line1d)
    if playerFemaleParser.value != "":
        aPlayer.gender = "F"

    #check if a scholastic player
    modifiedName = aPlayer.name.replace("IM ", "").strip()
    modifiedName = modifiedName.replace(" JR", "").strip()
    nameArray = modifiedName.split(" ")
    nameWithMiddleInitial = modifiedName
    if len(nameArray) == 3:
        modifiedName = nameArray[0] + " " + nameArray[2]
        nameWithMiddleInitial = nameArray[0] + " " + nameArray[1][0] + " " + nameArray[2]
    print ("nameArray: ", nameArray)
    if aPlayer.name.lower() in coScholasticPdf or modifiedName.lower() in coScholasticPdf or nameWithMiddleInitial.lower() in coScholasticPdf or aPlayer.name.lower() in scholasticPlayerList or modifiedName.lower() in scholasticPlayerList or nameWithMiddleInitial.lower() in scholasticPlayerList:
        aPlayer.junior = True
    if aPlayer.name.lower() in nonScholasticPlayerList or modifiedName.lower() in nonScholasticPlayerList or nameWithMiddleInitial.lower() in nonScholasticPlayerList:
        aPlayer.junior = False
    print ("modifiedName: ", modifiedName, ", scholastic: ", aPlayer.junior)

    #get most recent rating and date
    playerUrl = "http://www.uschess.org/msa/MbrDtlTnmtHst.php?" + aPlayer.id
    print ("player tournament history Url: ", playerUrl)
    line1d = readData(playerUrl);
    line1d = line1d.replace("<td>&nbsp;</td>","<td> </td>")
    historyParser = TableParser("Reg Rtg")
    # for aline in line1d:
        # a_line = aline
        # matchObj = re.match(r"<td width=\d+><a href=(\S+)>.*",a_line, re.M)
        # if matchObj:
            # aline = matchObj.group(1)
            # print "======================================================================"
            # print a_line
    historyParser.feed(line1d)
    count = 0
    for row in historyParser.array2d:
        print ("Row: ", row)
        if len(row[2]) > 0 and row[2][0].strip() != "":
            date = row[0][0]
            tournament = row[1][0] + "/" + row[1][1] if len(row[1]) > 1 else row[1][0]
            tournament = "<a href=http://www.uschess.org/msa/" + historyParser.link[count] + " target='_blank'>" + tournament + "</a>"
            beforeRatingStr = row[2][0]
            beforeRatingArray = beforeRatingStr.split(" ")
            afterRatingStr = row[2][1]
            afterRatingArray = afterRatingStr.split(" ")
            aPlayer.date = date
            aPlayer.beforeRating = int(beforeRatingArray[0]) if beforeRatingArray[0].isdigit() else 0
            aPlayer.rating = int(afterRatingArray[0])
            aPlayer.tournament = tournament
            #print "date: ", date, ", tournament: ", tournament, ", rating: ", ratingStr
            break
        count += 1

# create female and scholastic players list
femalePlayers = []
scholasticPlayers = []
for aPlayer in allPlayers:
    if aPlayer.junior:
        scholasticPlayers.append(aPlayer)
    if aPlayer.gender == "F":
        femalePlayers.append(aPlayer)

# sort
allPlayers.sort(key=lambda x: x.rating, reverse=True)
femalePlayers.sort(key=lambda x: x.rating, reverse=True)
scholasticPlayers.sort(key=lambda x: x.rating, reverse=True)

print ("Done")

now = datetime.now()
ntop = 20
nscholastic = 20
nfemale = 15

outStr1 = """
<!doctype html>
 
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Top """ + str(ntop) + """ Colorado Chess</title>
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
<h2><a href="index.html" id="title" onmouseover="underline()" onmouseout="leave()">Colorado Chess Top """ + str(ntop) + """ Ratings</a></h2>
<div id="tabs">
  <ul>
    <li><a href="#tabs-1">Top """ + str(ntop) + """ General</a></li>
    <li><a href="#tabs-2">Top """ + str(nscholastic) + """ Scholastic</a></li>
    <li><a href="#tabs-3">Top """ + str(nfemale) + """ Female</a></li>
    <li><a href="#tabs-4">About</a></li>
  </ul>

  <div id="tabs-1">
<p>Updated """ + str(now) + """</p>
    <table>
<tr>
<th class="general">Rank</th>
<th class="general">Title</th>
<th class="general">Name</th>
<th class="general">Rating</th>
<th class="general">+/-</th>
<th class="general">Recent Tournament</th>
<th class="general">Date</th>
</tr>
""" 

#<tr>
#<td class="rank">1</td>
#<td class="rankchange"></td>
#<td class="title">IM</td>
#<td class="name">Michael Mulyar</td>
#<td class="rating">2541</td>
#<td class="ratingchange">0</td>
#<td class="tournament">Colorado Open</td>
#<td class="date">9/01/13</td>
#</tr>
outStr2 = ""
for ii in range(min(ntop, len(allPlayers))):
    player = allPlayers[ii]
    outStr2 += "\n<tr>\n<td class=\"rank\">"+str(ii+1)+"</td>\n<td class=\"title\">"+player.title+"</td>\n<td class=\"name\">"+player.name+"</td>\n<td class=\"rating\">"+str(player.rating)+"</td>\n<td class=\"ratingchange\">"+str(player.rating-player.beforeRating)+"</td>\n<td class=\"tournament\">"+player.tournament+"</td>\n<td class=\"date\">"+player.date+"</td>\n</tr>\n"

outStr3 = """
</table>
  </div>

  <div id="tabs-2">
<p>Updated """ + str(now) + """</p>
<table>
<tr>
<th class="scholastic">Rank</th>
<th class="scholastic">Title</th>
<th class="scholastic">Name</th>
<th class="scholastic">Rating</th>
<th class="scholastic">+/-</th>
<th class="scholastic">Recent Tournament</th>
<th class="scholastic">Date</th>
</tr>
""" 

outStr4 = ""
for ii in range(min(nscholastic, len(scholasticPlayers))):
    player = scholasticPlayers[ii]
    outStr4 += "\n<tr>\n<td class=\"rank\">" + str(ii+1) + "</td>\n<td class=\"title\">"+player.title+"</td>\n<td class=\"name\">"+player.name+"</td>\n<td class=\"rating\">"+str(player.rating)+"</td>\n<td class=\"ratingchange\">"+str(player.rating-player.beforeRating)+"</td>\n<td class=\"tournament\">"+player.tournament+"</td>\n<td class=\"date\">"+player.date+"</td>\n</tr>\n"

outStr5 =  """
</table>
  </div>

<div id="tabs-3">
<p>Updated """ + str(now) + """</p>
<table>
<tr>
<th class="female">Rank</th>
<th class="female">Title</th>
<th class="female">Name</th>
<th class="female">Rating</th>
<th class="female">+/-</th>
<th class="female">Recent Tournament</th>
<th class="female">Date</th>
</tr>
""" 

outStr6 = ""
for ii in range(min(nfemale, len(femalePlayers))):
    player = femalePlayers[ii]
    outStr6 += "\n<tr>\n<td class=\"rank\">" + str(ii+1) + "</td>\n<td class=\"title\">"+player.title+"</td>\n<td class=\"name\">"+player.name+"</td>\n<td class=\"rating\">"+str(player.rating)+"</td>\n<td class=\"ratingchange\">"+str(player.rating-player.beforeRating)+"</td>\n<td class=\"tournament\">"+player.tournament+"</td>\n<td class=\"date\">"+player.date+"</td>\n</tr>\n"

outStr7 = """
</table>
</div>
<div id="tabs-4">
<p>This website is a live rating site for the highest rated Colorado chess players in three categories. This website is updated daily.</p>
<p>The source of this data comes from the USCF, from this <a href="http://main.uschess.org/datapage/top-players2.php?state=CO&limit=&maxcnt=500&players=M&rtgsys=R&current=C">link</a>.</p>
<p>Players who haven't played a standard tournament within 1 year of the update date will not be included on the list.</p>
<p>If you have any suggestions or corrections (like players that I missed), feel free to fill out the form below.</p>
<iframe src="https://docs.google.com/forms/d/1tpNaTKqCeCZq0utf3oevdUvyrbBlZd8I_BSsjahbnPI/viewform?embedded=true" width="760" height="500" frameborder="0" marginheight="0" marginwidth="0">Loading...</iframe>
<p>Made by and maintained by Jackson Chen.</p>
</div>
</div>
 
 
</body>
</html>
"""

outStr = outStr1 + outStr2 + outStr3 + outStr4 + outStr5 + outStr6 + outStr7
file_handle = open("C:\\Jackson\\Server\\Apache24\\htdocs\\chess\\stats\\top.html", 'w')
file_handle.write(outStr)
file_handle.close()

