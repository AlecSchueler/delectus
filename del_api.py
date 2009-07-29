#!/usr/bi/env python import urllib import re
import urllib
import re

def sgroup(regex,string):
    '''
    Returns only the term matched by a regex.
    '''
    return regex.search(string).group()

def parse_attr(attr_name,string):
    print string
    start= len(attr_name)+2 # id est 'attr_nam="'
    stop = -1
    
    return string[start:stop]

def api_time_to_epoch(time):
    

def parse_posts(xml):
    post  = re.compile("<post .*?>\\n")
    href  = re.compile("href=\".*?\"")
    title = re.compile("description=\".*?\"")
    tags  = re.compile("tag=\".*?\"")
    desc  = re.compile("extended=\".*?\"")
    time  = re.compile("time=\".*?\"")
    
    parsed = {}
    
    for p in post.findall(xml):
        parsed[parse_attr("description",sgroup(title,p))]=(
            parse_attr("href", sgroup( href,p)),
            parse_attr("tag", sgroup( tags,p)),
            parse_attr("extended", sgroup( desc,p)),
            parse_attr("time", sgroup( time,p))
        )
    return parsed

