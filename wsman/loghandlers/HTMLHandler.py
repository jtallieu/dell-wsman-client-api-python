"""
HTML Log Handler

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

import os
import logging

from ..format.command import indent_output

from ..provider.winrm import WinRM
from ..provider.wsmancli import WSManCLI

from ..response.fault import Fault
from ..response.instance import Instance
from ..response.reference import Reference
from ..response.association import Association


def html_render(value):
    return value.replace('<', '&#60;').replace('>', '&#62;').replace('\r\n', '\r\n<br/>').replace('\n', '\n<br/>').replace('\t','&nbsp;' * 8)


class HTMLHandler(logging.FileHandler):
    """
    Log handler that generates html command logs
    
    This handler only logs records that have a command, duration, and output property
    """
    
    def __init__(self, filename, encoding=None, delay=0, title="Command Log", pretty=False):
        """
        The constructor
        
        @param pretty: Determines if the output is formatted in a readable format or in raw XML
        @type pretty: boolean
        """
        self.title = title
        self.pretty = pretty
        
        # load the template files
        self.__preamble = open(os.path.dirname(__file__) + os.sep + 'templates' + os.sep + 'preamble.html').read()
        self.__tail = open(os.path.dirname(__file__) + os.sep + 'templates' + os.sep + 'tail.html').read()
        self.__command_template = open(os.path.dirname(__file__) + os.sep + 'templates' + os.sep + 'command.html').read()
        
        logging.FileHandler.__init__(self, filename, 'w', encoding, delay)
    
    def _open(self):
        """
        Internal open of the stream
        """
        stream = logging.FileHandler._open(self)
        log = self.__preamble % self.title
        log = log.replace('%%','%')
        stream.write(log)
        stream.write(self.__tail)
        stream.flush()
        return stream
    
    
    def emit(self, record):
        """
        Emit the message
        """
        
        # Only handle commands
        try:
            hasCommand = record.command
        except:
            hasCommand = False
        
        if hasCommand:
            
            # Set the pointer to the end of the command section
            if self.stream is None:
                self.stream = self._open()
            self.stream.seek(-len(self.__tail),2)
            
            if record.command.split(' ')[0] == 'winrm':
                provider = WinRM(None)
            else:
                provider = WSManCLI(None)
            
            # cast all responses to an iterable
            response = provider.parse(record.output)
            extra_class = "pass"
            if isinstance(response, Fault):
                extra_class = "fail"
                
            # generate the output
            if not self.pretty:
                entry = self.__command_template % (str(record.command), record.duration, extra_class, html_render(record.output))
            else:
                output =  indent_output(record)
                entry = self.__command_template % (str(record.command), record.duration, extra_class, html_render(output))
            
            # put out the message    
            self.stream.write(entry)
            self.stream.write(self.__tail)
            self.stream.flush()
            