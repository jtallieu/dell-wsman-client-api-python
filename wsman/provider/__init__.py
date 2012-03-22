"""
WS-Management provider

@copyright: 2010-2012
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

import sys
from winrm import WinRM
from wsmancli import WSManCLI

# Factory for the WSMan Provider
class WSManProviderFactory(object):
    """
    Factory for the WSMan provider
    """
    
    def __init__(self, transport):
        """
        Initialize the factory with the transport.
        
        @param transport: Transport object to execute the constructed command
        @type transport: L{Transport}
        """
        
        # Set the transport
        self.__transport = transport    
    
    
    def get_provider(self):
        """
        Get the provider based on the specified criterion.
        
        @return: WSManProvider that matches the specified criterion.
        @rtype: L{WSManProvider}
        """
        
        if sys.platform == 'win32':
            return WinRM(self.__transport)
        
        return WSManCLI(self.__transport) 

