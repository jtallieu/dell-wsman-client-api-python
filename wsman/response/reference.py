"""
Reference class

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
from ..mixin.dictionary import DictionaryMixin


class Reference(Response, DictionaryMixin):
    """
    Reference object for WSMan
    """
    
    def __init__(self, name):
        """
        Constructor for the Reference class
        
        @param name: Name of the instance
        @type name: String
        """
        
        # Call the base class
        super(Reference, self).__init__()
        
        # Name of the reference 
        self.__name = name
        
        # Resource URI
        self.__resource_uri = ''
    
    def toString(self, indent=0):
        s = [("\t" * indent) + self.name]
        s.append(("\t" * indent) + "\tReferenceParameters")
        s.append(("\t" * indent) + "\t\tResourceURI=%s" % self.resource_uri)
        s.append(("\t" * indent) + "\t\tSelectorSet")
        for k,v in self.items:
            s.append(("\t" * indent) + "\t\t\tSelector: %s=%s" % (k, ",".join(map(lambda x: x if x else "" ,v)) ))
            
        return "\n".join(s)
    
    def set_resource_uri(self, uri):
        """
        Set the resource URI for the reference response
        """
        
        self.__resource_uri = uri
        
        
    def get_class_from_uri(self):
        """
        Get the class name of this reference from the URI
        """
        
        if self.__resource_uri:
            return self.__resource_uri.split('/')[-1]
        
        return ''            
    
    def is_equal(self, reference):
        """
        Tests this association instance for equalisty with the given associator
        
        @param reference: The association class to compane with
        @type reference: L{Reference}
        """
        
        if isinstance(reference, Reference):
            for my_key, my_value in self.items:
                other_value = reference.get(my_key, None)
                if other_value != my_value:
                    print "Reference Key ", my_key, " not equal", my_value, " - ", other_value
                    return False
                else:
                    print "Reference Key ", my_key, " equal", my_value, " - ", other_value
            return True
        else:
            print "Wrong type: expecting Reference for comparison"
            return False
        
    def __repr__(self):
        """
        String representation of the object
        """
        pairs = []
        for (key, value) in self.items:
            # Assemble the intermediate value since it is stored as a list
            # TODO: What if the value is an array? How do we assemble an array for a get query?
            value_ = value[0] if value else ''
            value_ = value_ if value_ else ''
            
            # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
            safe_value = value_
            pairs.append('%s=\"%s\"' % (key, safe_value))
        
        # Get the query parameter for command construction
        query = '&'.join(pairs)
        return "%s?%s" % (self.resource_uri, query)
            
            
    def __cmp__(self, other):
        """
        Comparison function
        """
        if self.resource_uri != other.resource_uri:
            return 1
        
        for (key, value) in other.items:
            if not self.has_key(key) or value != self.get(key):
                return -1
        return 0

    def __hash__(self):
        """
        The hash function
        """
        return hash("%s" % self)
        
    # Properties of this class    
    name = property(fget=lambda x: x.__name)
    classname = property(fget=get_class_from_uri)
    resource_uri = property(fget=lambda x: x.__resource_uri)
        
        