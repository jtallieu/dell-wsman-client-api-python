"""
Test WSMan identify command

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


# WSMan test
wsman = WSMan(transport=Dummy())



if __name__ == "__main__":
    remote = Remote("172.23.200.13", 'root', 'calvin')
    results = wsman.identify(remote=remote, raw=False)
    print results
    if not isinstance(results, list):
      results = [results]
      
    for result in results:
      print result.toString()
    
    
    