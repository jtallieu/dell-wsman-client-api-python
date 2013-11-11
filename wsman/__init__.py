"""
WSManAPI

@copyright: 2010-2012
@author: Joseph Tallieu <joseph_tallieu@dell.com>
@author: Vijay Halaharvi <vijay_halaharvi@dell.com>
@organization: Dell Inc. - PG Validation
@license: GNU LGLP v2.1
"""
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 2.1 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cache

from transport.process import Subprocess
from provider import WSManProviderFactory


class WSMan(object):
    """WS-management class"""
    
    def __init__(self, transport=Subprocess()):
        """
        Constructor for the WSMan class.
        
        @param transport: The L{transport} instance that will handle WSMan requests.  (default=L{Subprocess}) 
        @type transport: L{transport} 
        """
        
        # Store the transport
        self.__transport = transport
        
        # Provider
        self.__provider = WSManProviderFactory(self.__transport).get_provider()
    
    
    def identify(self, remote=None, raw=False):
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
        return self.__provider.identify(remote, raw)
    
    @cache.lru_cache(maxsize=20)    
    def enumerate(self, cim_class, cim_namespace, remote=None, raw=False, uri_host="http://schemas.dmtf.org", query=None):
        """
        Enumerate a CIM class. 
        
        @attention: Uses LRU Cache - set keyword argument I{cache} to "I{no}", "I{false}", or "I{off}" to bypass the cache.
        
        @param cim_class: CIM class to be enumerated
        @type cim_class: String
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: A list of L{Instance} objects or the raw XML response
        @rtype: list or string
        """
        args = {"cim_class": cim_class,
                "cim_namespace": cim_namespace,
                "remote": remote,
                "raw": raw,
                "uri_host": uri_host,
                "dialect": "",
                "query": ""}

        if query:
            args.update(query(self.__provider, args)) 

        return self.__provider.enumerate(**args)
    
    @cache.lru_cache(maxsize=20)
    def enumerate_keys(self, cim_class, cim_namespace, remote=None, raw=False, uri_host="http://schemas.dmtf.org", query=None):
        """        
        Enumerate the keys for a CIM class.
        
        @attention: Uses LRU Cache - set keyword argument I{cache} to "I{no}", "I{false}", or "I{off}" to bypass the cache.
        
        @param cim_class: CIM class for key enumeration
        @type cim_class: String
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: A list of L{Instance} objects or the raw XML response
        @rtype: list or string
        """
        args = {"cim_class": cim_class,
                "cim_namespace": cim_namespace,
                "remote": remote,
                "raw": raw,
                "uri_host": uri_host,
                "dialect": "",
                "query": ""}

        if query:
            args.update(query(self.__provider, args)) 

        return self.__provider.enumerate_keys(**args)
    
    @cache.lru_cache(maxsize=20)
    def associators(self, instance, cim_namespace, remote=None, raw=False, uri_host="http://schemas.dmtf.org"):
        """
        Do an associators operation for the instance
        
        @attention: Uses LRU Cache - set keyword argument I{cache} to "I{no}", "I{false}", or "I{off}" to bypass the cache.
        
        @param instance: CIM instance response object
        @type instance: L{Instance}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: A list of L{Reference} objects or the raw XML response
        @rtype: list or string         
        """
                
        return self.__provider.associators(instance, cim_namespace, remote, raw, uri_host)
    
    @cache.lru_cache(maxsize=20)
    def references(self, instance, cim_namespace, remote=None, raw=False, uri_host="http://schemas.dmtf.org"):
        """
        Do a references operation for the instance
        
        @attention: Uses LRU Cache - set keyword argument I{cache} to "I{no}", "I{false}", or "I{off}" to bypass the cache.
        
        @param instance: CIM instance response object
        @type instance: L{Instance}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: A list of L{Reference} objects or the raw XML response
        @rtype: list or string         
        """
                
        return self.__provider.references(instance, cim_namespace, remote, raw, uri_host)
    
    def set(self, reference, cim_namespace, remote=None, properties={}, raw=False):
        """
        Sets the properties of an instance using the properties argument.
        
        @param reference: CIM reference response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param properties: The properties and values to set
        @type properties: dict 
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        
        @return: L{Response} object or the raw XML response
        @rtype: L{Response}
        """
        return self.__provider.set(reference, cim_namespace, remote, properties, raw)
    
    def get(self, reference, cim_namespace, remote=None, raw=False):
        """
        Do a get operation for the instance
        
        @param reference: CIM reference response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        
        @return: L{Instance} object or the raw XML response
        @rtype: L{Instance}         
        """
                
        return self.__provider.get(reference, cim_namespace, remote, raw)
    
    
    def invoke(self, reference, command, arguments, remote=None, raw=False):
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
        @param raw: Determines if the method should return the XML output from the transport, or a L{Response} object.
                    If you want to do your own parsing of the XML output, then set this parameter to True. (default=False)
        @type raw: bool
        
        @return: L{Response} object or the raw XML response
        @rtype: L{Response}    
        """
        
        return self.__provider.invoke(reference, command, arguments, remote, raw)
    
    def __set_quiet(self, value):
        """
        Sets the transport's verbosity
        """
        self.__transport.quiet = value
    
    # Property to control the verbosity of the transport
    quiet = property(fset=__set_quiet)
        