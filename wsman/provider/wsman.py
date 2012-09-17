"""
Base WSMan provider

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

class WSManProvider(object):
    """
    WS-Management provider
    """
    
    
    def __init__(self, transport):
        """
        Constructor for the WSMan provider class.
        
        @param transport: Transport object to execute the constructed command
        @type transport: L{Transport}
        """
        
        # Transport for the provider
        self.__transport = transport
        
        
    def get_transport(self):
        """
        Get the transport for this provider.
        
        @return: Transport for the provider
        @rtype: L{Transport}
        """
        
        return self.__transport
    
    def identify(self, remote=None):
        """
        Identify WS-Man implementation
        
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        @return: L{Response} object or the raw XML response
        @rtype: L{Response}
        """
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    
    def enumerate(self, cim_class, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Enumerate the cim class.
        
        @param cim_class: CIM class to be enumerated
        @type cim_class: String
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumeration
        @rtype: List of L{Response} objects/ L{Fault}
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    
    def enumerate_keys(self, cim_class, cim_namespace, remote=None, uri_host=""):
        """        
        Enumerate the keys for the cim class.
        
        @param cim_class: CIM class for key enumeration
        @type cim_class: String
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumerating the keys
        @rtype: L{Reference}
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    def associators(self, instance, cim_namespace, remote=None, uri_host=""):
        """
        Do an associators operation for the instance
        
        @param instance: CIM instance response object
        @type instance: L{Instance}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    def references(self, instance, cim_namespace, remote=None, uri_host=""):
        """
        Do a references operation for the instance
        
        @param instance: CIM instance response object
        @type instance: L{Instance}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    def get(self, instance, cim_namespace, remote=None):
        """
        Do a get operation for the instance
        
        @param instance: CIM instance response object
        @type instance: L{Instance}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    
    
    def invoke(self, reference, command, arguments, remote=None):
        """
        Do a get operation for the instance
        
        @param reference: CIM reference response object
        @type reference: L{Reference}
        @param command: The command to invoke
        @type command: String
        @param arguments: A path to a file, or a dictionary of key/value paris used in the command
        @type arguments: String/dict
        @param remote: Remote configuration object
        @type remote: L{Remote}
        
        @return: Response object from the call, either a Reference, Fault, or an Result
        @rtype: L{Response}    
        """
        
        raise NotImplementedError("This method needs to be implemented in the derived class.")
    