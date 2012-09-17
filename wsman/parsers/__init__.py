"""
Parser class for XML to dictionary

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

import xml.parsers.expat as expat

class Parser(object):
    """
    XML to dictionary Parser
    """
    
    def __init__(self):
        """
        Constructor for the parser
        """
        
        # Stack for the elements
        self.__stack = []
        
        # Current element
        self.__current = None
        
        
    def reset(self):
        """
        Reset the markers 
        """
        
        self.__stack = []
        self.__current = None
        
        
    def element(self):
        """
        Get a new element for a node
        
        @return: Dictionary representation of the XML Node
        @rtype: Dictionary
        """
        
        return {'type':'', 'name':'', 'value':None, 'children':[], 'attributes':{}}
        
        
    def start(self, name, attributes):
        """
        Start tag handler for the node
        
        @param name: Name of the XML Node
        @type name: String
        @param attributes: Attributes of the XML Node
        @type attributes: Dictionary
        """
        
        # Get the qualifier and the name from the tag
        qname, tname = name.split(':')
        
        # If there is a current element then push it onto the stack
        if self.__current:
            self.__stack.append(self.__current)
        
        # Create a new element for this Node and set the properties
        self.__current               = self.element()
        self.__current['type']       = qname
        self.__current['name']       = tname
        self.__current['attributes'] = attributes
                    
    
    def character(self, data):
        """
        Character data handler of the XML node
        
        @param data: Node data
        @type data: String
        """
        
        if self.__current:
            
            # If the value is none, make it a string so we can append
            # - it's buffered data
            if not self.__current['value']:
                self.__current['value'] = ""
            
            self.__current['value'] += data
        
        
    def end(self, name):
        """
        End tag handler for the XML node
        """
        
        # Get the qualifier and the name from the tag
        qname, tname = name.split(':')
        
        # Get the parent if it exists
        parent = self.__stack.pop() if len(self.__stack) > 0 else None
        
        # Add it to the parent if it exists    
        if parent:
            parent['children'].append(self.__current)
            self.__current = parent
        
        
    def parse(self, xml):
        """
        Parse an XML string and return a dictionary representation.
        
        @param xml: XML string
        @type xml: String
        
        @return: Dictionary representation of the XML
        @rtype: Dictionary 
        """
        
        # Reset the stack and the current element
        self.reset()
        
        # Create the parser
        parser = expat.ParserCreate()
        
        parser.buffer_text = True
        
        # Set the handlers
        parser.StartElementHandler  = self.start
        parser.CharacterDataHandler = self.character
        parser.EndElementHandler    = self.end
        
        # Parse the XML        
        parser.Parse(xml)
        
        return self.__current
    