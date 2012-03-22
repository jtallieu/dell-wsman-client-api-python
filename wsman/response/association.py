"""
Association class

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
from reference import Reference
from ..mixin.dictionary import DictionaryMixin


class Association(KeyResponse, DictionaryMixin):
    """
    Association class
    """
    
    def __init__(self, name):
        """
        Constructor for the association class
        
        @param name: Name of the instance
        @type name: String
        """
        
        # Call the base class
        super(Association, self).__init__()
        
        # Name of the reference 
        self.__name = name
    
    
    def toString(self, indent=0):
        s = [("\t" * indent) + self.name]
        
        for (k,v) in self.items:
            if isinstance(v[0], Reference):
                s.append(v[0].toString(indent + 1))
            else:
                s.append(("\t" * indent) + "\t%s=%s" % (k, ",".join(map(lambda x: x if x else "" ,v)) ))
        return "\n".join(s)
    
    def get_left_reference(self):
        for k,v in self.items:
            if isinstance(v,list) and len(v):
                ref = v[0]
                if isinstance(ref, Reference):
                    return (k,ref)
        return None
    
    def get_right_reference(self):
        foundLeft = False
        for k,v in self.items:
            if isinstance(v,list) and len(v):
                ref = v[0]
                if isinstance(ref, Reference):
                    if foundLeft:
                        return (k,ref)
                    else:
                        foundLeft = True
        return None
    
    def is_equal(self, assoc):
        """
        Tests this association instance for equalisty with the given associator
        
        @param assoc: The association class to compane with
        @type assoc: L{Association}
        """
        
        if isinstance(assoc, Association):
            for my_key, my_value in self.items:
                my_value = my_value[0] if my_value else None
                other_value = assoc.get(my_key, None)
                
                other_value = other_value[0] if other_value else None
                
                if isinstance(my_value, Reference):
                    if not isinstance(other_value, Reference):
                        # Cannot compare mixed types
                        print "Wrong type for key ", my_key, " expected Reference" 
                        return False
                    else:
                        # Compare the references
                        if not my_value.is_equal(other_value):
                            print "References are not equal"
                            return False
                elif my_value != other_value:
                    print "Key ", my_key, " not equal", my_value, " - ", other_value
                    return False
            return True
        else:
            print "Wrong type: expecting Association for comparison"
            return False
        
    
    # Properties of this class    
    name = property(fget=lambda x: x.__name)
    left_reference = property(fget=get_left_reference)
    right_reference = property(fget=get_right_reference)
     