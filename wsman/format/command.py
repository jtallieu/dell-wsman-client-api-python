"""
WSMan Command Log Handler

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

import sys
import logging

from ..provider.winrm import WinRM
from ..provider.wsmancli import WSManCLI

from ..response.fault import Fault
from ..response.instance import Instance
from ..response.reference import Reference
from ..response.association import Association


def indent_output(record):
    """
    Formats command records based on the command
    
    @param record: A log record object that must have a command and output property
    
    @returns: String
    """
    if record.command.split(' ')[0] == 'winrm':
        provider = WinRM(None)
    else:
        provider = WSManCLI(None)
    
    # cast all responses to an iterable
    response = provider.parse(record.output)
    if not isinstance(response,list):
        response = [response]
    
    # build the string
    strs = []
    for i in response:
        strs.append(i.toString())
    return '\n'.join(strs)
        
    
    

class OutputFormatter(logging.Formatter):
    """
    Formats WSMan command output suitable for use with 
    logging.Handlers
    """
    
    def __init__(self, fmt=None, dateFmt=None, pretty=False):
        """
        Constructor
        
        @param pretty: Set to true to get indented output
        """
        self.pretty = pretty
        logging.Formatter.__init__(self, fmt, dateFmt)
        
        
    def format(self, record):
        """
        Formats the record
        """
        
        try:
            output = record.output
        except:
            output = False    
            
        if output:
            if self.pretty:
                command = record.command
                record.output = indent_output(record) + '\n'
                record.command = '\n' + record.command + '\n'
                msg = logging.Formatter.format(self, record)
                record.output = output
                record.command = command
                return msg
            else:
                command = record.command
                record.command = '\n' + record.command + '\n'
                msg = logging.Formatter.format(self, record)
                record.command = command
                return msg
        else:
            record.command = ""
            record.output = ""
            record.duration = 0.0
            msg = logging.Formatter.format(self, record)
            del record.command
            del record.output
            del record.duration
            return msg
            
     
     
        
        