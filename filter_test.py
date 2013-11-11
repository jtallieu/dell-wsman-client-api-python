"""
Test WSMan Filtering

@copyright: 2010-2015
@author: Joseph Tallieu <joseph_tallieu@dell.com>
@organization: Dell Inc. - PG Validation
@license: GNU LGLP v2.1
"""
#    This file is part of WSManAPI.
#
#    WSManAPI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 2.1 of the License, or
#    (at your option) any later version.
#
#    WSManAPI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with WSManAPI.  If not, see <http://www.gnu.org/licenses/>.

import sys
from wsman import WSMan
from wsman.provider.remote import Remote
from wsman.transport.dummy import Dummy
from wsman.transport.process import Subprocess
from wsman.response.reference import Reference
from wsman.response.fault import Fault
from wsman.format.command import OutputFormatter
from wsman.loghandlers.HTMLHandler import HTMLHandler
from wsman.filter import SelectorFilter, XPathFilter, CQLFilter, WQLFilter

from datetime import datetime
  
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

# Set up the text log
fmt = OutputFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(command)s %(output)s %(duration)fs', pretty=False)
fHandle = logging.FileHandler("test_raw2.txt", mode="w")
fHandle.setFormatter(fmt)

# Set up the HTML log
html = HTMLHandler("test_raw2.html", pretty=False)
log = logging.getLogger("")
log.setLevel(logging.INFO)
log.addHandler(fHandle)
log.addHandler(html)

# Remote object


# WSMan test
wsman = WSMan(transport=Subprocess())

CLASSNAME = "DCIM_NICView"

def test_enumerate(ip):
    remote = Remote(ip, 'root', 'calvin')
    print "Enumerating SelLog"
    r = wsman.enumerate(CLASSNAME, "root/dcim", remote=remote)
    total_count = len(r)
    print "Found %d Unfiltered instances" % len(r)

    print "XPath Query"
    try:    
        query = XPathFilter(query='../%s[WWN="78:2B:CB:4B:CD:9E"]' % CLASSNAME)
        r = wsman.enumerate(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"


    print "CQL Query"
    try:
        query = CQLFilter(query='select * from %s where WWN = "78:2B:CB:4B:CD:9E"' % CLASSNAME)
        r = wsman.enumerate(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"
    
    print "WQL Query"
    try:
        query = WQLFilter(query='select * from %s where WWN = "78:2B:CB:4B:CD:9E"' % CLASSNAME)
        r = wsman.enumerate(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"

    print "Selector Query"
    try:
        query = SelectorFilter(query='{DeviceNumber = "0"}') 
        r = wsman.enumerate(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"



    print "Testing enumerate_keys"
    print "XPath Query"
    try:    
        query = XPathFilter(query='../%s[WWN="78:2B:CB:4B:CD:9E"]' % CLASSNAME)
        r = wsman.enumerate_keys(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"


    print "CQL Query"
    try:
        query = CQLFilter(query='select * from %s where WWN = "78:2B:CB:4B:CD:9E"' % CLASSNAME)
        r = wsman.enumerate_keys(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"
    
    print "WQL Query"
    try:
        query = WQLFilter(query='select * from %s where WWN = "78:2B:CB:4B:CD:9E"' % CLASSNAME)
        r = wsman.enumerate_keys(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"

    print "Selector Query"
    try:
        query = SelectorFilter(query='{WWN = "78:2B:CB:4B:CD:9E"}')
        r = wsman.enumerate_keys(CLASSNAME, "root/dcim", remote=remote, query=query)
        print "Found %d instances" % len(r)
    except:
        print "Error"
    
    """
    


    r = wsman.enumerate_keys("DCIM_SELLogEntry", "root/dcim", remote=remote, query=query)
    print "Found %d instances" % len(r)
    """
if __name__ == "__main__":
    test_enumerate(sys.argv[1])


