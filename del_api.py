#!/usr/bi/env python import urllib import re
from time import mktime
import urllib
import re

def sgroup(regex,string):
    '''
    Returns only the term matched by a regex.
    '''
    return regex.search(string).group()

def parse_attr(attr_name,string):
    start= len(attr_name)+2 # id est 'attr_nam="'
    stop = -1
    
    return string[start:stop]

def api_time_to_epoch(time):
    global months
    #2009-06-19T17:28:55Z
    parsed = (time[0:4],
              time[5:6],
              time[8:10],
              time[-9:-7],
              time[-6:-4],
              time[-3:-1],
              0,0,-1)
    return int(mktime(tuple(int(i) for i in parsed)))

def parse_posts(xml):
    post  = re.compile("<post .*?>\\n")
    href  = re.compile("href=\".*?\"")
    title = re.compile("description=\".*?\"")
    tags  = re.compile("tag=\".*?\"")
    desc  = re.compile("extended=\".*?\"")
    time  = re.compile("time=\".*?\"")
    
    parsed = {}

    #todo: order
    for p in post.findall(xml):
        parsed[parse_attr("description",sgroup(title,p))]=(
            parse_attr("href", sgroup( href,p)),
            tuple(parse_attr("tag", sgroup( tags,p)).split(' ')),
            parse_attr("extended", sgroup( desc,p)),
            api_time_to_epoch(parse_attr("time", sgroup( time,p)))
        )
    return parsed


