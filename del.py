#!/usr/bin/env python

'''Backup delicious.com bookmarks in a variety of formats.'''

#Script is not in working oder, but may be useful to someone already

#todo:  check if user exists
#       print out to file   
#       commandline options 
#       tag support         
from urllib import urlopen
from time   import mktime, time
import re


# - Utility functions
#   Defined as a function instead of lambdas
#   for the sake of readability.            
def contents(string, element_name):
    '''
    strips out and returns the contents of an xml element.
    note: presumes no attributes are given

    >>> print contents("<p>Hello, World!</p>,"p")
    Hello, World!
    '''
    length = len(element_name)+2 #i.e. `len("<" + elem_name +">" )`

    return string[ length : 0-(length+1) ]

def sgroup(regex,string):
    '''
    Returns only the term matched by a regex.
    '''
    return regex.search(string).group()

months = {"Jan":0,"Feb":1,"Mar":2,
          "Apr":3,"May":4,"Jun":5,
          "Jul":6,"Aug":7,"Sep":8,
          "Oct":9,"Nov":10,"Dec":11}
def pubDate_to_epoch(pubDate):      #bound to be a better way to do this...
    '''\
        Takes the RSS "pubDate" and converts it to epoch seconds.
    '''
    global months

    pubDate=pubDate.split(" ")
    clock  =pubDate[4].split(":")
    #"Mon, 20 Jul 2009 09:55:01 +0000"
    parsed = (pubDate[3],
              months [pubDate[2]],
              pubDate[1],
              clock  [0],
              clock  [1],
              clock  [2],
              0,0,-1)
    return int(mktime(tuple(int(i) for i in parsed))) #todo: delispify this line

def re_compile(element_name):
    '''
    Takes the name of an xml element and returns a compiled regex object to match
    it and its contents.
    '''
    return re.compile('<%s>.*?</%s>' % (element_name,element_name), re.DOTALL)

def tag_strip(category_string):
    global username
    return category_string[42+len(username):-11]


# - Main functions
# - init functions for fetching and parsing the feed
def fetch_rss_url(username, count=0):
    '''
    Returns the url for the feed, filling in the parameters for
    username and count. Count is the number of items we ask to
    be included in the feed. When no value for count is given,
    we first scrape the users homepage to see their total number
    zof bookmarks, and use that as count.
    '''  
    if not count:
        tagScopeCount   = re.compile(r'tagScopeCount">.*?<')
        #The span id containing the overall number of bookmarks    
        users_bookmarks = urlopen('http://delicious.com/%s' % username).read()

        count = sgroup(tagScopeCount,users_bookmarks)
        count = count[15:-1] #cut out everything but the number    

    return 'http://feeds.delicious.com/v2/rss/%s?count=%s' % (username,count)

def parse_feed(feed_url):
    '''
        Parse the feed and return it as a dictionary in the form:
            {
            title :(link,
                    pubDate,
                    description), #if applicable
            title...
            }
    '''
    #todo: it may well be prudent to create a feed class with this 
    #as its __init__ function, so we can call e.g. feed.print_as...
    #pros: readability                                             
    #cons: awkward if using the script as a module                 
    rss  = urlopen(feed_url).read()

    #These are the regecies for the various elements of the feed. 
    item        = re_compile("item")
    title       = re_compile("title")
    link        = re_compile("link")
    pubDate     = re_compile("pubDate")
    description = re_compile("description")
    category    = re.compile('<category.*?>.*?</category>')

    items = item.findall( rss )
    parsed_feed={}

    for i in items:
        #todo:test for desc, set it accordingly, then add everything
        #todo:test if we already have an item with the same title   
        pub_epoch = pubDate_to_epoch( contents( sgroup(pubDate,i),"pubDate" ) )

        if 'description' in i:
            parsed_feed[ contents( sgroup( title,i),"title")] =\
                                         (contents(sgroup(link,i),"link"),

                                          pub_epoch,

                                          contents(sgroup(description,i),
                                                   "description"),

                                          tuple(tag_strip(c)
                                                for c in category.findall(i)))
        else:
            parsed_feed[ contents( sgroup( title,i),"title")] =\
                                         (contents(sgroup(link,i),"link"),

                                          pub_epoch,

                                          "",#no description

                                          tuple(tag_strip(c)
                                                for c in category.findall(i)))

    return parsed_feed

# - conversion functions for outputting the bookmarks with the new filetype
def convert_html(feed_dict):
    '''
        Iterates through the dictionary created with parse_feed(),
        and prints out a netscape-bookmark-file-1 html file using
        the values therein.
    '''
    print """\
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Bookmarks</title>
<h1>Bookmarks</h1>

<dt><h3 add_date="%s" last_modified="%s">Delicious Bookmarks</h3>\
""" %(int(time()),
      int(time()))

    for title in iter(feed_dict):
        print """\
    <dt>
        <a href="%s" last_visit="" add_date="%s" tags="%s">%s</a>
    <dd>%s""" % (feed_dict[title] [0], # url        
                 feed_dict[title] [1], # pubDate    
        ",".join(feed_dict[title] [3]),# tags       
                 title,                # <-         
                 feed_dict[title] [2]) # description
        print

def convert_adr(feed_dict):
    print """\
Opera Hotlist version 2.0
Options: encoding = utf8, version=3

#FOLDER
    NAME=Delicious Bookmarks"""

    for title in iter(feed_dict):
        print """
#URL
    NAME=%s
    URL=%s
    CREATED=%s
    DESCRIPTION=%s""" % (title,               # <-     
                         feed_dict[title] [0],# ur     
                         feed_dict[title] [1],# pubDate
                         feed_dict[title] [2])# description

if __name__ == "__main__":
    username = "SuperlativeHors" # test
    x = convert_adr(parse_feed(fetch_rss_url("SuperlativeHors",10)))
