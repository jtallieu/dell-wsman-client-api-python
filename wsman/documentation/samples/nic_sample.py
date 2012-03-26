"""
Test WSMan

@copyright: 2010-2012
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

from wsman import WSMan
from wsman.provider.remote import Remote
from wsman.transport.process import Subprocess
from wsman.format.command import OutputFormatter
from wsman.loghandlers.HTMLHandler import HTMLHandler
  
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

# Set up the text log
fmt = OutputFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(command)s %(output)s %(duration)fs', pretty=True)
fHandle = logging.FileHandler("test.txt", mode="w")
fHandle.setFormatter(fmt)

# Set up the HTML log
html = HTMLHandler("test.html", pretty=True)
log = logging.getLogger("")
log.setLevel(logging.DEBUG)
log.addHandler(fHandle)
log.addHandler(html)

# Remote object

# WSMan test
wsman = WSMan(transport=Subprocess())

remote = Remote("172.26.4.55", 'root', 'calvin')
results = wsman.enumerate_keys("DCIM_NICView", "root/dcim", remote=remote)

# Find the reference we want a full GET on
for reference in results:
    if reference.get("InstanceID")[0] == "NIC.Slot.2-2-4":
        break
my_nic = wsman.get(reference, "", remote=remote)

for property in my_nic.keys:
    print property, ":", my_nic.get(property) 
print "Found NIC", my_nic
    
    
    
        
    
    
    