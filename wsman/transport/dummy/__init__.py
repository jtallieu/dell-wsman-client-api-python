"""
Dummy transport 

@copyright: 2010-2012
@author: Joseph Tallieu <joseph_tallieu@dell.com>
@author: Vijay Halaharvi <vijay_halaharvi@dell.com>
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


import os
import sys
import time
import random
import logging

log = logging.getLogger("WSMAN.transport")
from .. import Transport


class Dummy(Transport):
    """
    Dummy transport
    """
    
    def execute(self, command):
        """
        Execute the command and return the output.
        
        @param command: The command constructed by the provider.
        @type command: String
        
        @return: The output from the command execution 
        @rtype: String
        """
        start = time.time()
        
        # You could parse the command line here and send the appropriate file
        # but the parser needs to handle all of these formats. This transport
        # picks the file randomly. 
        
        files = ['wsmanfault.txt', 'epr.txt', 'get.txt', 'fault.txt', 'instance.txt', 'instances.txt', 'invoke_resp.txt', 'invoke_result.txt']                
        #files = ['invoke_resp.txt', 'invoke_result.txt']
        files = ['get.txt', 'instance.txt', 'instances.txt', 'wsmanfault.txt']
        #files = ['fault.txt']
        #files = ['large_response.txt']
        
        filename = random.choice(files)
        basename = os.path.dirname(__file__)
        provider = 'winrm' if (sys.platform == 'win32') else 'wsmancli'
        #provider = 'winrm'
        path = os.path.join(basename, 'responses', provider, filename)
        print path
        
        duration = time.time() - start
        output = open(path, "r").read()
        log.info("Command Completed in %0.3f s" % duration, extra={'command': command, 'output': output, 'duration':duration})
        return output
    
