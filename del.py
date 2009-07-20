#!/usr/bin/env python

'''Backup delicious.com bookmarks in a variety of formats.'''

#Script is not in working oder, but may be useful to someone already

from urllib import urlopen
import re

def contents(string, element_name):
    '''
    strips out and returns the contents of an xml element.
    
    >>> print contents("<p>Hello, World!</p>,"p")
    Hello, World!
    '''
    length = len(element_name)+2 #i.e. `len("<" + elem_name +">" )`

    return string[ length : 0-(length+1) ]

def fetch_rss_url(username, count=0):
    '''
       Returns the url for the feed, filling in the parameters for
       username and count. Count is the number of items we ask to
       be included in the feed. When no value for count is given,
       we first scrape the users homepage to see their total number
       of bookmarks, and use that as count.
    '''  
    if not count:
        tagScopeCount   = re.compile(r'tagScopeCount">.*?<')
        #The span id containing the overall number of bookmarks    
        users_bookmarks = urlopen('http://delicious.com/%s' % username).read()

        count = tagScopeCount.search( users_bookmarks ).group()
        count = count[15:-1] #cut out everything but the number    

    return 'http://feeds.delicious.com/v2/rss/%s?count=%s' % (username,count)

def parse_feed(feed_url):
    '''
        Parse the feed and return it as a dictionary in the form:
            {
            title = link,
                    description, #if applicable
            title...
            }
    '''
    #todo: it may well be prudent to create a feed class with this 
    #as its __init__ function, so we can call e.g. feed.print_as...
    rss  = urlopen(feed_url).read()

    #todo: replace many <x>.*?</x> with a function that takes x and
    #returns the compiled <x>.*?</x>, with the DOTALL flag.        

    #These are the regecies for the various elements of the feed.
    item        = re.compile(r'<item>.*?</item>'              ,re.DOTALL)
    title       = re.compile(r'<title>.*?</title>'            ,re.DOTALL)
    link        = re.compile(r'<link>.*?</link>'              ,re.DOTALL)
    pubdate     = re.compile(r'<pubdate>.*?</pubdate>'        ,re.DOTALL)
    description = re.compile(r'<description>.*?</description>',re.DOTALL)

    items = item.findall( rss )
    parsed_feed={}

    for i in items:
        #todo: instead of having x.search(i).group() called a lot,  
        #have a function which takes x and returns x.search(i).group
        #todo: set link before testing for descriptiong.
        if 'description' in i:
            parsed_feed[title.search(i).group()] = (link.search(i).group(),
                                               description.search(i).group())
        else:
            parsed_feed[title.search(i).group()] =(link.search(i).group())

    return parsed_feed
