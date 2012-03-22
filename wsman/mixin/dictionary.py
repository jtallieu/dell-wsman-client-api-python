"""
Dictionary Mix-in

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

from pprint import pformat

class DictionaryMixin(object):
    """
    Dictionary Mixin class
    """
    
    def __init__(self):
        """
        Constructor for the Dictionary Mixin
        """
        
        super(DictionaryMixin, self).__init__()
        
        # Dictionary
        self.__mapping = {}
        
        # Case insensitive dictionary
        self.__lower_mapping = {}
        
        
    def set(self, key, value):
        """
        Add/Edit a dictionary mapping
        
        Example Output:
        <..>
        <n1:IdentifyingDescriptions>CIM:GUID</n1:IdentifyingDescriptions>
        <n1:IdentifyingDescriptions>CIM:Tag</n1:IdentifyingDescriptions>
        <n1:IdentifyingDescriptions>DCIM:ServiceTag</n1:IdentifyingDescriptions>
        <..>
        
        IdentifyingDescriptions is an array cause it is repeated so we need to store
        all of its values hence the value for a key is stored as a list
        
        @param key: Key for the mapping
        @type key: String
        @param value: Value of the mapping
        @type value: String                 
        """
        
        if self.__mapping.has_key(key):
            self.__mapping[key].append(value)
            self.__lower_mapping[key.lower()].append(value)
        else:
            self.__mapping[key] = [value]
            self.__lower_mapping[key.lower()] = [value]
                 
        return True
        
        
    def get(self, key, default=None):
        """
        Get the value of the key from the mapping
        
        @param key: Key for the mapping
        @type key: String
        @param default: Default value in case the mapping does not exist
        @type default: L{object}
        
        @return: The value of the mapping if it exists else default.
        @rtype: String or L{object}        
        """
        
        #return self.__mapping.get(key, default)
        return self.__lower_mapping.get(key.lower(), default)
    
    def has_key(self, key):
        """
        Checks if a key is set/defined
        
        @param key: Key for the mapping
        @type key: String
        
        @return: True if defined
        @rtype: boolean
        """
        
        #return self.__mapping.has_key(key)
        return self.__lower_mapping.has_key(key.lower())
    
    def dump(self):
        try:
            return pformat(self.__mapping)
        except:
            return str(self)    
        
    # Properties 
    keys    = property(fget=lambda x: x.__mapping.keys()) 
    values  = property(fget=lambda x: x.__mapping.values())
    items   = property(fget=lambda x: x.__mapping.items())
    