"""
Process transport based on subprocess

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
import logging
import subprocess
from .. import Transport

log = logging.getLogger("WSMAN.transport")

class Subprocess(Transport):
    """
    Subprocess based transport
    """
    
    def __init__(self):
        """
        Constructor for the CLI-mate transport
        """
        
        # Base class
        super(Subprocess, self).__init__()
        
    
    def shell(self):
        """
        Return the shell based on the operating system.
        
        @return: The shell command
        @rtype: String
        """
        
        if sys.platform == 'win32':
            return 'cmd.exe'        
        return 'sh'
    
    
    def delimiter(self):
        """
        Delimiter for the shell based on the operating system
        
        @return: The delimiter for the shell commands
        @rtype: String
        """
        
        if sys.platform == 'win32':
            return '\r\n'        
        return '\n'
    
    
    def execute(self, command):
        """
        Execute the command and return the output.
        
        @param command: The command constructed by the provider.
        @type command: String
        
        @return: The output from the command execution 
        @rtype: String
        """
        start = time.time() 
        process = subprocess.Popen(command,\
                                   stdout=subprocess.PIPE,\
                                   stderr=subprocess.PIPE,\
                                   shell=True)
        (stdout, stderr) = process.communicate()
        duration = time.time() - start        
        output =  stdout + stderr
        log.info("Command Completed in %0.3f s" % duration, extra={'command': command, 'output': output, 'duration':duration})
        return output
        
