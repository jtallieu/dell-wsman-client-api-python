"""
Response classes

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


class Response(object):
    """
    Response class for command output
    """
    
    def __init__(self):
        """
        Constructor for the response class
        """
        
        super(Response, self).__init__()
    
    def toString(self):
        return "%s" % self    

        
class KeyResponse(Response):
    """
    Response that has a keys attribute
    """
    
    def __init__(self):
        """
        Constructor for the response class
        """
        
        super(KeyResponse, self).__init__()
        
        # Add a key reference
        self.reference = None
        
        