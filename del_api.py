#!/usr/bi/env python
#todo: use a global "usage..." var
#todo: docstrings
#todo: set useragent string
from time import mktime, time
from os import popen
import urllib
import re
import sys

class urlopener(urllib.URLopener):
    try:
        arch = popen("uname -m") # system architecture
        kern = popen("uname -s") # kernel name
        version = "Delectus/1.0 (%s; %s; N)" %\
                  (kern.read().strip("\n"),  arch.read().strip("\n"))
    finally:
        arch.close()
        kern.close()


def api_url(username,password,count=0):
    if not count:
        return "https://%s:%s@api.del.icio.us/v1/posts/all"%(
            username,password)
    return "https://%s:%s@api.del.icio.us/v1/posts/recent?count=%s"%(
        username,password,count)


def get_xml(url):
    global del_opener
    try:
        xml_sock = del_opener.open(url)
        xml      = xml_sock.read()
    finally:
        xml_sock.close()
        return xml


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

    #todo: tidy this up
    for p in post.findall(xml):
        parsed[parse_attr("description",sgroup(title,p))]=(
            parse_attr("href", sgroup( href,p)),
            api_time_to_epoch(parse_attr("time", sgroup( time,p))),
            parse_attr("extended", sgroup( desc,p)),
            tuple(parse_attr("tag", sgroup( tags,p)).split(' '))
        )
    return parsed


def convert_html(feed_dict):
    '''
        Iterates through the dictionary created with parse_feed(),
        and prints out a netscape-bookmark-file-1 html file using
        the values therein.
    '''
    global target
    target.write("""\
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Bookmarks</title>
<h1>Bookmarks</h1>

<dt><h3 add_date="%s" last_modified="%s">Delicious Bookmarks</h3>
""" %(int(time()),
      int(time()))
    )

    for title in iter(feed_dict):
        target.write("""
    <dt>
        <a href="%s" last_visit="" add_date="%s" tags="%s">%s</a>
    <dd>%s\n"""%(feed_dict[title] [0], # url        
                 feed_dict[title] [1], # pubDate    
        ",".join(feed_dict[title] [3]),# tags       
                 title,                # <-         
                 feed_dict[title] [2]) # description
                    )


def convert_adr(feed_dict):
    '''
        Iterates through the dictionary created wit parse_feed(),
        and prints out an Opera ADR bookmark file, version 3, using
        the values therein.
    '''
    global target
    target.write("""\
Opera Hotlist version 2.0
Options: encoding = utf8, version=3

#FOLDER
    NAME=Delicious Bookmarks""")

    for title in iter(feed_dict):
        target.write("""
#URL
    NAME=%s
    URL=%s
    CREATED=%s
    DESCRIPTION=%s\n"""% (title,              # <-     
                         feed_dict[title] [0],# ur     
                         feed_dict[title] [1],# pubDate
                         feed_dict[title] [2])# description
                    )


def convert_xbel(feed_dict):
    '''
        Iterates through the dictionary created wit parse_feed(),
        and prints out an XBEL file, version 1.0, as defined by
        the Python XML Special Interest Group, using the values
        therein.
    '''
    global target
    target.write("""\
<?xml version="1.0"?>
<!DOCTYPE xbel
  PUBLIC "+//IDN python.org//DTD XML Bookmark Exchange Language 1.0//EN//XML"
         "http://www.python.org/topics/xml/dtds/xbel-1.0.dtd">
<xbel version="1.0">
    <info>This XBEL document was generated automatically using a conversion
          script for delicious.com  bookmarks.  For more information please
          visit http://github.com/AlecSchueler/Delectus/
    </info>

    <folder folded="yes">
        <title>Delicious Bookmarks</title>""")

    for title in iter(feed_dict):
        target.write("""
            <bookmark href="%s">
                <title>%s</title>
                <info>Tags: %s</info>
                <desc>
                    %s
                </desc>
            </bookmark>""" % (feed_dict[title][0],
                              title,
                     ",".join(feed_dict[title][3]),
                              feed_dict[title][2])
                     )
    target.write("\t</folder>\n</xbel>\n")


def convert(parsed_xml):
    global options
    if options.HTM:
        convert_html(parsed_xml)

    elif options.ADR:
        convert_adr(parsed_xml)

    elif options.XBEL:
        convert_xbel(parsed_xml)


if __name__ == "__main__":
    from optparse import OptionParser,OptionValueError
    import getpass
    del_opener = urlopener()
    Usage = "usage: delectus -u USERNAME [options]"

    oparser = OptionParser(usage=Usage)

    oparser.add_option("-u","--user",dest="USER",# should be a positional arg
                       action="store",type="str",
                       help="Delicious username")
    oparser.add_option("-p","--pass",dest="PASS",#<- for use in scripts
                       action="store",type="str")
    oparser.add_option("-f","--file",dest="FILE",default=sys.stdout,
                       action="store",type="str",
                       help="File to write to. Default is stdout")
    oparser.add_option("-c","--count",dest="COUNT",
                       action="store",type="int",default=0,
                       help="""Number of bookmarks to retrieve
                                0 means all (default)""")
    oparser.add_option("-a","--adr",dest="ADR",
                       action="store_true",default=False,
                       help="Whether to use Opera's ADR format")
    oparser.add_option("-n","--html",dest="HTM",
                       action="store_true",default=False,
                       help="Whether to use Netscape's HTML format")
    oparser.add_option("-x","--xbel",dest="XBEL",
                       action="store_true",default=True,
                       help="Whether to use the PXSIG's XBEL format (default)")
    #todo: add a resolve case for filetypes

    (options, args) = oparser.parse_args()

    if not options.USER:
        print Usage
        exit(1)
    else:
        username=options.USER
    if not options.PASS:
        password=getpass.getpass()

    url = api_url(username,password,options.COUNT)
    xml = get_xml(url)

    if options.FILE !=sys.stdout:
        target = file(options.FILE,"w")
        close=1#whether or not to close the file before exit
    else:
        target=sys.stdout
        close=0

    if close:
        try:convert(parse_posts(xml))
        finally:target.close()
    else:
        convert(parse_posts(xml))
    exit(0)
