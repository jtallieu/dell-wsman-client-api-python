"""
Transport for WS-Management

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


class Transport(object):
    """
    The Transport class is responsible for executing the
    constructed command.    
    """
    
    def __init__(self, **kwargs):
        """
        Constructor for the transport
        """
        
        # controls if the transport should write anything to the console
        self.__quiet = False
        pass
    
    
    def execute(self, command):
        """
        Execute the command and return the output.
        
        @param command: The command constructed by the provider.
        @type command: String
        
        @return: The output from the command execution 
        @rtype: String
        """
        
        raise NotImplementedError("This method needs to be implemented by the derived class.")
    
    def __set_quiet_mode(self, value):
        """
        Set verbosity of the transport
        """
        
        if isinstance(value, bool):
            self.__quiet = value
        else:
            pass
        
    
    quiet = property(fget=lambda x: x.__quiet, fset=__set_quiet_mode)    
        
    
    