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
from wsman.transport.dummy import Dummy
from wsman.transport.process import Subprocess
from wsman.response.reference import Reference
from wsman.response.fault import Fault
from wsman.format.command import OutputFormatter
from wsman.loghandlers.HTMLHandler import HTMLHandler

from datetime import datetime
  
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

# Set up the text log
fmt = OutputFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(command)s %(output)s %(duration)fs', pretty=False)
fHandle = logging.FileHandler("test_raw.txt", mode="w")
fHandle.setFormatter(fmt)

# Set up the HTML log
html = HTMLHandler("test_raw.html", pretty=False)
log = logging.getLogger("")
log.setLevel(logging.DEBUG)
log.addHandler(fHandle)
log.addHandler(html)

# Remote object


# WSMan test
wsman = WSMan(transport=Dummy())
 
def invoke(ip, force_fault= False):
    
    remote = Remote(ip, 'root', 'calvin')
    r = Reference("DCIM_RAIDService")
    
    if force_fault:
        r.set_resource_uri("http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcM_RAIDService")
    else:
        r.set_resource_uri("http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_RAIDService")
        
    r.set("__cimnamespace","root/dcim")
    r.set("CreationClassName","DCIM_RAIDService")
    r.set("SystemName","DCIM:ComputerSystem")
    r.set("Name","DCIM:RAIDService")
    r.set("SystemCreationClassName","DCIM_ComputerSystem")
    
    s = wsman.invoke(r, "SetAttributes", "Set.xml", remote=remote)
    print "Result", s
    return s

def get(ip, force_fault=False):
    remote = Remote(ip, 'root', 'calvin')
    r = Reference("DCIM_RAIDService")
    
    if force_fault:
        r.set_resource_uri("http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_AIDService")
    else:
        r.set_resource_uri("http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDService")
        
    r.set("__cimnamespace","root/dcim")
    r.set("CreationClassName","DCIM_RAIDService")
    r.set("SystemName","DCIM:ComputerSystem")
    r.set("Name","DCIM:RAIDService")
    r.set("SystemCreationClassName","DCIM_ComputerSystem")
    
    s = wsman.get(r, "", remote=remote)
    print "Result", s
    return s

def set_test(ip):
    remote = Remote(ip, 'root', 'calvin')
    refs = wsman.enumerate_keys("DCIM_SystemInteger", "root/dcim", remote=remote)
    for ref in refs:
        if ref.get("InstanceID")[0] == "System.Embedded.1#ServerPwr.1#PowerCapValue":
            print ref.resource_uri
            
            # Show the properties of the system
            instance = wsman.get(ref, "", remote=remote)
            for k,v in instance.items:
                print k, v[0]
                
            # Set the value
            set_result = wsman.set(ref, "", properties={"CurrentValue": 133}, remote=remote)
            if isinstance(set_result, Fault):
                print set_result.toString() 
            
    

def test():
    r = invoke("172.26.4.55")
    r = invoke("172.26.4.55")
    r = invoke("172.26.4.55")
    r = invoke("172.26.4.55")
    #print "Invoke Cache Stats", wsman.invoke.cache_info()


def test_enumerate():
    remote = Remote("172.26.4.55", 'root', 'calvin')
    r = wsman.enumerate("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    print r
    r = wsman.enumerate("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    print r
    r = wsman.enumerate("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    print r
    
    remote = Remote("172.26.4.55", 'root', 'calvin')
    r = wsman.enumerate("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    print r
    
    print "Enumerate Cache Stats", wsman.enumerate.cache_info()


def store_enum():
    import shelve
    import ut
    
    remote = Remote("172.26.4.55", 'root', 'calvin')
    r = wsman.enumerate("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    r_ = wsman.enumerate_keys("DCIM_AggregationMetricDefinition", "root/dcim", remote=remote)
    
    ut.associate(r, r_)
    
    store = shelve.open("instances")
    store["CIL"] = r
    store.close()

def get_NICView():
    remote = Remote("172.26.4.55", 'root', 'calvin')
    results = wsman.enumerate_keys("DCIM_NICView", "root/dcim", remote=remote)
    
    # Find the reference we want a full GET on
    for reference in results:
        if reference.get("InstanceID")[0] == "NIC.Slot.2-2-4":
            break
    
    my_nic = wsman.get(reference, "", remote=remote)
    print "Found NIC", my_nic
        
    
if __name__ == "__main__":
    
    #test()
    #get_NICView()
    
    #set_test("172.26.4.55")
    #test_enumerate()
    
    r = invoke("172.26.4.55")
    print r
    for p in r.keys:
        print p, r.get(p)
    """
    remote = Remote("172.26.4.55", 'root', 'calvin')
    s = wsman.enumerate_keys("DCIM_iDRACCardString", "root/dcim", remote)
    print "Result", s
    
    
    s = wsman.get(r, "root/dcim",remote)
    print "Result", s
    try:
        log.debug("Results %d %s", len(s), s)
    except:
        log.debug("Got %s", type(s))
        log.debug(s.reason)
    """
     
    
    
    
        
    
    
    