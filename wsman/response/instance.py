"""
Instance response

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

from . import KeyResponse
from ..mixin.dictionary import DictionaryMixin


class Instance(KeyResponse, DictionaryMixin):
    """
    Instance response object
    """
    
    def __init__(self, name):
        """
        Constructor for the Instance class
        
        @param name: Name of the instance
        @type name: String
        """
                
        # Call the base class
        super(Instance, self).__init__()
        
        # Store the name of the class that this is an instance of. 
        self.__name = name
    
    def toString(self):
        """
        show the object in a reader friendly format
        """
        strs = [self.name]
        
        for k,v in self.items:
            #strs.append("\t%s = %s" % (k,','.join(v) if v else "" ))
            strs.append("\t%s=%s" % (k, ",".join(map(lambda x: x if x else "" ,v)) ))
        return "\n".join(strs)
        
        
    # Properties of this class    
    name = property(fget=lambda x: x.__name)
        