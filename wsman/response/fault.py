"""
Fault response

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


from . import Response

class Fault(Response):
    """
    Fault response
    """
    
    def __init__(self, code, reason, detail):
        """
        Constructor for the Fault response
        
        @param code: Fault code
        @type code: String
        @param reason: Reason for the fault
        @type reason: String
        @param detail: URL for the fault details
        @type detail: String
        """
        
        # Call the base class
        super(Fault, self).__init__()
        
        # Fault attributes
        self.__code     = code
        self.__reason   = reason
        self.__detail   = detail
    
    def toString(self):
        """
        show the object in a reader friendly format
        """
        s = "Fault:\n\tCode: %s\n\tReason: %s\n\tDetail: %s" % (self.code, self.reason, self.detail)
        return s
        
        
        
        
    # Fault properties
    code    = property(fget=lambda x: x.__code)
    reason  = property(fget=lambda x: x.__reason)
    detail  = property(fget=lambda x: x.__detail)
    