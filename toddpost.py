from bs4 import BeautifulSoup as BS
from os import popen
import codecs
import progressbar as pbar
import re
from Queue import PriorityQueue as PQ

# from math import log as mlog
# class InvFileTransferSpeed(pbar.Widget):
#   'Widget for showing the transfer speed (useful for file transfers).'
#
#   format = '%6.2f %ss/%s'
#   prefixes = ' kMGTPEZY'
#   __slots__ = ('unit', 'format')
#
#   def __init__(self, unit='loop'):
#     self.unit = unit
#
#   def update(self, bar):
#     'Updates the widget with the current SI prefixed speed.'
#
#     if bar.seconds_elapsed < 2e-10 or bar.currval < 2e-10: # =~ 0
#       scaled = power = 0
#     else:
#       speed = bar.seconds_elapsed / bar.currval 
#       power = int(mlog(speed, 1000))
#       scaled = speed / 1000.**power
#
#     return self.format % (scaled, self.prefixes[power], self.unit)

try:
  html = popen("curl -s http://boards.4chan.org/v/archive").read()
except:
  print "Couldn't open 4chan. Check internet connection"
  exit()

soup = BS(html, "lxml")
table = map(
    lambda tr : tr.find_all("td"),
    soup.table.find_all("tr")[1:]
    )
table = [ row for row in table if int(row[3].text)>=100 ]
new_table = PQ()
print "Getting todd posts..."
widgets = ['Progress: ', pbar.Percentage(), ' ', pbar.Bar(),
           ' ', pbar.AdaptiveETA(), ' ', pbar.AdaptiveTransferSpeed()] 
bar = pbar.ProgressBar(widgets=widgets, maxval=len(table))
bar.start()
for i, row in enumerate(table):
  bar.update(i)
  link = "http://boards.4chan.org" + row[-1].a['href']
  htmlp = popen("curl -s " + link).read()
  n = len(list(re.finditer("todd", htmlp.lower())))
  if n > 0:
    new_table.put_nowait((-n, row))
bar.finish()
new_table = new_table.queue
posts = "   ID#   \t# of posts\t# of todd\tPost Title/Text\n"
for n, post in new_table:
  n = -n
  posts += "%s\t%s\t%s\t%s\n" % (post[0].text, post[3].text, n, post[2].text)

with codecs.open("toddposts.txt", "w", "utf-8") as f:
  f.write(posts)
