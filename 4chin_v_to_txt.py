from bs4 import BeautifulSoup as BS
from os import popen

try:
  html = html = popen("curl http://boards.4chan.org/v/archive").read()
except:
  print "Couldn't open 4chan. Check internet connection"
  exit()

soup = BS(html, "lxml")
table = map(
    lambda tr : map(
      lambda td : td.text,
      tr.find_all("td")),
    soup.table.find_all("tr")[1:]
    )
table = [ row for row in table if int(row[3])>=100 ]
posts = "   ID#   \t# of posts\tPost Title/Text\n"
for post in table:
  posts += "%s\t%s\t%s\n" % (post[0], post[3], post[2])

with open("4chin.txt", "w", "utf-8") as f:
  f.write(posts)
