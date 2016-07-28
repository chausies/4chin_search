from bs4 import BeautifulSoup as BS
from urllib import urlopen
import json
import progressbar as pbar
import re

from math import log as mlog
class InvFileTransferSpeed(pbar.Widget):
  'Widget for showing the transfer speed (useful for file transfers).'

  format = '%6.2f %ss/%s'
  prefixes = ' kMGTPEZY'
  __slots__ = ('unit', 'format')

  def __init__(self, unit='loop'):
    self.unit = unit

  def update(self, bar):
    'Updates the widget with the current SI prefixed speed.'

    if bar.seconds_elapsed < 2e-10 or bar.currval < 2e-10: # =~ 0
      scaled = power = 0
    else:
      speed = bar.seconds_elapsed / bar.currval 
      power = int(mlog(speed, 1000))
      scaled = speed / 1000.**power

    return self.format % (scaled, self.prefixes[power], self.unit)

try:
  html = urlopen("http://pokemondb.net/pokedex/all").read()
except:
  print "Couldn't open pokemon database. Check internet connection"
  exit()

Pokemon = dict()
soup = BS(html, "lxml")
table = map(
    lambda tr : tr.find_all("td"),
    soup.table.find_all("tr")[1:]
    )
for row in table:
  pokemon = dict()
  pokemon["PKDX#"] = int(row[0].text)
  pokemon["Types"] = [ t.text for t in row[2].find_all("a") ]
  pokemon["HP"]    = int(row[4].text)
  pokemon["Atk"]   = int(row[5].text)
  pokemon["Def"]   = int(row[6].text)
  pokemon["SpAtk"] = int(row[7].text)
  pokemon["SpDef"] = int(row[8].text)
  pokemon["Spd"]   = int(row[9].text)
  pokemon["info"]  = "http://pokemondb.net" + row[1].a["href"]
  name = list(row[1].children)[-1].text
  Pokemon[name] = pokemon

widgets = ['Progress: ', pbar.Percentage(), ' ', pbar.Bar(),
           ' ', pbar.ETA(), ' ', InvFileTransferSpeed()] 
bar = pbar.ProgressBar(widgets=widgets, maxval=len(Pokemon))
bar.start()
for i, (pokemon, data) in enumerate(Pokemon.iteritems()):
  bar.update(i)
  success = False
  url = data["info"]
  j = 0
  while not success:
    j += 1
    try:
      html = urlopen(url).read()
      success = True
    except:
      if j > 20:
        print "Couldn't open %s after 20 tries" % url
        print "Check internet connection and try again"
        exit()
  soup = BS(html, "lxml")
  tab_num ,= [ j 
      for j, li in enumerate(
        soup.find("ul", {"class":"svtabs-tab-list"}).find_all("li")
        )
      if li.text == pokemon
      ]
  main_table = soup.find("ul", {"class":"svtabs-panel-list"}) \
    .find_all("li", recursive=False)[tab_num].table.find_all("tr")
  data["Height"] = float(
        re.findall(
          r'\(.*?m', 
          main_table[3].text
        )[0][1:-1]
      )
  data["Weight"] = float(
        re.findall(
          r'.* lbs', 
          main_table[4].text
        )[0][:-4]
      )
  data["Abilities"] = [ a.text for a in main_table[5].find_all("a") ]
  data["Evolutions"] = map(
      lambda x : x.text,
      soup.find("div", {"id": "dex-evolution"})\
          .parent.find_all("a", {"class":"ent-name"})
      )
  li = soup.find("li", {"id" : "svtabs_moves_14"})
  if li.find("div", {"class": "tabset-moves-game-form"}):
    tab_num ,= [ j 
        for j, l in enumerate(
          li.find("ul", {"class":"svtabs-tab-list"}).find_all("li")
          )
        if l.text == pokemon
        ]
    rows = li.find("ul", {"class":"svtabs-panel-list"}) \
        .find_all("li")[tab_num].table.find_all("tr")[1:]
  else:
    rows = li.find("table").find_all("tr")[1:]
  # move_tables = li.find_all("table")
  # move_categories = li.find_all("h2")[:len(move_tables)]
  # for category, table in zip(move_categories, move_tables):
  category = "Moves learnt by level up"
  moves = []
  for row in rows:
    cols = row.find_all("td")
    move = dict()
    move["name"] = cols[1].text
    move["Type"] = cols[2].text
    move["Category"] = cols[3].text
    move["Power"] = float(cols[4].text.replace('-', 'nan'))
    move["Accuracy"] = float(cols[5].text\
        .replace('-', 'nan')\
        .replace(u'\u221e', 'inf')
        )
    moves += [move]
  data[category] = moves

bar.finish()

with open("pokedata.json", "w") as f:
  json.dump(Pokemon, f)
