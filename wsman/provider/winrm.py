"""
WinRM based provider

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

from pprint import pprint

from wsman import WSManProvider
from ..parsers import Parser
from ..response.fault import Fault
from ..response.instance import Instance
from ..response.reference import Reference
from ..response.association import Association
from exceptions import TypeError

import logging
log = logging.getLogger("WSMAN")



class WinRM(WSManProvider):
    """
    Windows based WS-Management provider.
    """
    
    def __init__(self, transport):
        """
        Constructor for the WSMan provider class.
        
        @param transport: Transport object to execute the constructed command
        @type transport: L{Transport}
        """
        
        # Call the base class 
        super(WinRM, self).__init__(transport)
        
        
    def extract(self, output):
        """
        Extract the results XML or the fault XML from the output 
        
        @param output: Output from the transport
        @type output: String
        @return: Result XML from the output
        @rtype: String
        """
        
        def extract_(tag):
            start = output.find('<%s' % tag)
            if start > -1:
                end = output.find('</%s>' % tag)
                if end > -1:
                    xml = output[start:end] + '</%s>' % tag
                    return xml            
            return None
        
        # Extract the XML from the output
        xml = extract_('wsman:Results')
        xml = extract_('s:Fault') if not xml else xml
        xml = extract_('f:WSManFault') if not xml else xml
        xml = extract_('wsmid:IdentifyResponse') if not xml else xml
              
        return xml
    
    
    def response_from_reference(self, name, node):
        """
        Construct the reference object from the node
        
        @param name: Name of this reference
        @type name: String
        @param node: XML reference dictionary
        @type node: Dictionary
        
        @return: Response object
        @rtype: L{Response}
        """
        
        # Reference object
        reference = Reference(name)
        
        # Get the selectors
        for child in node.get('children', []):
            
            # Set the resource URI for the reference
            if child.get('name', '') == 'ResourceURI':
                reference.set_resource_uri(child.get('value', ''))
                
            # Set the selector set                                
            elif child.get('name', '') == 'SelectorSet':
                for child_ in child.get('children', []):
                    if child_.get('name', '') == 'Selector':
                        key   = child_.get('attributes', {}).get('Name', '')
                        value = child_.get('value', None)
                                                                        
                        if key:
                            reference.set(key, value)                        
        return reference
    
    
    def is_association(self, node):
        """
        Check to see if this is an association node
        
        @param node: XML results node
        @type node: Dictionary
        """
        
        # Check if any of the node children have children
        if node and isinstance(node, dict):
            for child in node.get('children', []):
                if child.get('children', []):
                    return True
        return False    


    def response_from_identify(self, node):
        """
        Construct the response object from the results node dictionary
        
        @param node: XML results dictionary
        @type node: Dictionary
        
        @return: Response object parsed from the node
        @rtype: L{Response}
        """
        
        name = node.get("name",'')
        response = Instance(name)
        for child_ in node.get('children', []):
                    
            # Get the name and value
            key = child_.get('name', None)
            value = child_.get('value', None)
            
            # Construct the association
            if key and child_.get('children', []):
                if key == 'SecurityProfiles':
                    for child__ in child_.get('children', []):
                        if child__.get('name', '') == 'SecurityProfileNames':
                            response.set(key,child__.get('value', ''))
                     
            elif key:
                response.set(key, value)
            
        return response
        
    
    def response_from_results(self, node):
        """
        Construct the response object from the results node dictionary
        
        @param node: XML results dictionary
        @type node: Dictionary
        
        @return: List of Response objects parsed from the node
        @rtype: List of L{Response}
        """
        
        # Response objects
        responses = []
        
        # Decide if this is an Instance, Association or Reference
        for child in node.get('children', []):
            qname = child.get('type', '')
            name = child.get('name', '')
            
            # Response Object
            response = None
            
            # End point reference (EPR)
            if name == 'EndpointReference': 
                for child_ in child.get('children', []):
                    if child_.get('name', '') == 'ReferenceParameters':
                        response = self.response_from_reference(name, child_)
                       
            # Instance or Association
            else:
                
                response = Instance(name) if not self.is_association(child) else Association(name)                
                #print "PARSING", name, response
                # Build the instance attributes
                for child_ in child.get('children', []):
                    
                    # Get the name and value
                    key = child_.get('name', None)
                    value = child_.get('value', None)
                    
                    #print "Processing", key
                    # Construct the association
                    if key and child_.get('children', []):                                                
                        for child__ in child_.get('children', []):
                            #print "\tChild", child__.get("name",""), "of", key
                            if child__.get('name', '') == 'ReferenceParameters':
                                value = self.response_from_reference(key, child__)
                                
                            # Handle invoke responses with a non-standard format (Modular 12G) 
                            elif child__.get('name', '') == 'EndpointReference':
                                try:
                                    value = self.response_from_results(child_)[0]
                                except:
                                    value = Reference(child__.get('name', ''))
                    if key:
                        nilSet=False
                        for aKey_, aValue_ in child_.get("attributes",{}).items():
                            aKey_ = aKey_.split(":")[-1]
                            if aKey_ == "nil" and aValue_ == "true":
                                response.set(key, None)
                                nilSet = True
                                break                                
                        if not nilSet:
                            response.set(key, value)
                                                
            if response:
                responses.append(response)
                
        return responses
    
    
    def response_from_fault(self, node):
        """
        Construct the response object from the fault node dictionary
        
        @param node: XML fault dictionary
        @type node: Dictionary
        
        @return: Response object
        @rtype: L{Response}
        """
                
        code   = 'WinRM'
        reason = 'Internal Server Error (WinRM Provider)'
        detail = 'Internal Server Error (WinRM Provider)'
        
        try:
            for child in node.get('children', []):
                name = child.get('name', '')
                if name == 'Code':
                    for x in child.get('children', []):
                        if x.get('name') == 'Subcode':
                            for y in x.get('children', []):
                                if y.get('name') == 'Value':
                                    code = y.get('value', '')
                                                                                                        
                elif name == 'Reason':
                    for x in child.get('children', []):
                        if x.get('name') == 'Text':                        
                            reason = x.get('value', '')
                                  
                elif name == 'Detail':
                    for x in child.get('children', []):
                        if x.get('name') == 'FaultDetail':                        
                            detail = x.get('value', '')                            
        except:
            pass
            
        return Fault(code, reason, detail)
    
    
    def response_from_wsmanfault(self, node):
        """
        Construct the response object from the wsman fault node dictionary
        
        @param node: XML fault dictionary
        @type node: Dictionary
        
        @return: Response object
        @rtype: L{Response}
        """
                
        code   = 'WinRM'
        reason = 'Internal Server Error (WinRM Provider)'
        detail = 'Internal Server Error (WinRM Provider)'
        
        try:
            for child in node.get('children', []):
                log.info("Fault node message %s" % child.get("name"))
                if child.get('name') == 'Message':
                    code = node.get('attributes', {}).get('Code', code)
                    reason = child.get('value', reason)
        except:
            log.error("Error getting fault %s:%s" %(sys.exc_info()[1],sys.exc_info()[0]))
            pass
            
        return Fault(code, reason, detail)
        
        
    def parse(self, output):
        """
        Parse the output into one of the response formats.
        
        @param output: Output from the transport
        @type output: String
        """
        # Extract the XML from the output
        xml = self.extract(output)
        
        # Get the  dictionary representation of the extracted XML
        xml_dict = Parser().parse(xml) if xml else {}
        
        # If it is a results XML
        if xml_dict.get('name', '') == 'Results':
            return self.response_from_results(xml_dict)
        
        elif xml_dict.get('name', '') == 'IdentifyResponse':
            return self.response_from_identify(xml_dict)
        
        # WSMan Fault
        elif xml_dict.get('name', '') == 'WSManFault':
            return  self.response_from_wsmanfault(xml_dict)
    
        elif xml_dict.get('name', '') == 'Fault':
            return  self.response_from_fault(xml_dict)
        
        # Fault!
        else:
            try:
                return self.response_from_results(Parser().parse("<wsman:Results>%s</wsman:Results>" % output) if output else {})
            except:
                pass
            return self.response_from_fault(xml_dict)
        
        
        
    def remote_options(self, remote):
        """
        Generate the options for a remote command.
        
        @param remote: Remote configuration object
        @type remote: L{Remote}
        
        @return: Remote command line options
        @rtype: String
        """
        
        if not remote:
            return ''
        
        remote_  = '-u:%s ' % remote.username
        remote_ += '-p:%s ' % remote.password
        remote_ += '-r:https://%s/wsman ' % remote.ip
        remote_ += '-encoding:utf-8 -a:basic '
        
        return remote_
    
    def properties_argument(self, properties):
        """
        Builds the set argument for the set command
        
        @param properties: the properties to be set
        @type properties: dict
        
        @return: A string used to set properties of an instance in the form @{k1="v1";kn="vn"}
        @rtype: String
        """
        kv_strs=[]
        for k,v in properties.items():
            kv_strs.append("%s=\"%s\"" % (k,v))
        
        kv_strs = ";".join(kv_strs)
           
        return "@{%s}" % kv_strs
    
    
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
        # Construct the command
        command  = 'winrm id '
        command += self.remote_options(remote)        
        command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
        
        # Use the transport and execute the command
        output = self.get_transport().execute(command)        
        if raw: 
            return output
        else:
            # Parse the output into a response object
            return self.parse(output)
    
        
    def enumerate(self, cim_class, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Enumerate the CIM class.
        
        @param cim_class: CIM class to be enumerated
        @type cim_class: String
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response objects after enumeration
        @rtype: List of L{Response} objects/ L{Fault}
        """
        
        # Construct the command
        enumerate_command  = 'winrm e \"%s/wbem/wscim/1/cim-schema/2/%s?__cimnamespace=%s\" ' % (uri_host, cim_class, cim_namespace)
        enumerate_command += self.remote_options(remote)        
        enumerate_command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
        
        # Use the transport and execute the command
        output = self.get_transport().execute(enumerate_command)        
        if raw: 
            return output
        else:
            # Parse the output into a response object
            return self.parse(output)
    
    
    def enumerate_keys(self, cim_class, cim_namespace, remote=None, raw=False, uri_host=""):
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
        
        
        @return: Response objects after enumerating the keys
        @rtype: List of L{Reference} objects/ L{Fault}
        """
        
        # Construct the command
        enumerate_command  = 'winrm e \"%s/wbem/wscim/1/cim-schema/2/%s?__cimnamespace=%s\" ' % (uri_host, cim_class, cim_namespace)
        enumerate_command += self.remote_options(remote)
        enumerate_command += '-SkipCNcheck -SkipCAcheck -format:Pretty -ReturnType:EPR'
        
        # Use the transport and execute the command
        output = self.get_transport().execute(enumerate_command)
        
        if raw: 
            return output
        else:
            # Parse the output into a response object
            return self.parse(output)
    
    
    
    def set(self, reference, cim_namespace, remote=None, properties={}, raw=False):
        """
        Sets the properties of an instance using the properties argument.
        
        @param reference: CIM reference response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class (depricated: using the namespace from the reference)
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param properties: The properties and values to set
        @type properties: dict 
        
        @return: Instance object or Fault
        @rtype: L{Response}
        """
        
        # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
            isinstance(reference, Reference):
            
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            for (key, value) in reference.items:
                                        
                # Assemble the intermediate value since it is stored as a list
                # TODO: What if the value is an array? How do we assemble an array for a get query?
                value_ = value[0] if value else ''
                value_ = value_ if value_ else ''
                
                # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
                safe_value = value_
                pairs.append('%s=%s' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = '+'.join(pairs)
            classname = reference.classname
            
            # Construct the command
            get_command  = 'winrm s \"%s?%s\" ' % (reference.resource_uri, query)
            get_command += self.properties_argument(properties) + ' '
            get_command += self.remote_options(remote)
            get_command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
            
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
    
            if raw:
                return output
            
            else:
                # Note: (WinRM specific actions)
                # If it is not a fault then add the covers since get does not return
                # the results within the <wsman:Results> tag.
                if not self.extract(output):
                    output = '<wsman:Results>' + output + '</wsman:Results>'
                
                
                # Parse the output into a response object
                instance_or_fault = self.parse(output)
                log.debug("Got a %s response" % (type(instance_or_fault)))
                if not isinstance(instance_or_fault, Fault) and isinstance(instance_or_fault, list): 
                    if len(instance_or_fault) > 0:
                        return instance_or_fault[0]
                    else:
                        return Fault('WinRM','Error', "Invalid response")
                        
                    
                return instance_or_fault
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        # Generate a Fault
        return Fault('WinRM',\
                     'Set is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
    
        
    def associators(self, reference, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Do an associators operation for an instance
        
        @param reference: CIM reference(key) response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response objects after enumerating the keys
        @rtype: List of L{Reference} objects/ L{Fault}
        """
        # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
            isinstance(reference, Reference):
            
            pairs = []
            for (key, value) in reference.items:
                                        
                # Assemble the intermediate value since it is stored as a list
                # TODO: What if the value is an array? How do we assemble an array for a get query?
                value_ = value[0] if value else ''
                value_ = value_ if value_ else ''
                
                # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
                safe_value = value_
                pairs.append('%s=%s' % (key, safe_value))
        
            # Get the query parameter for command construction
            query = '+'.join(pairs)
            classname = reference.classname
            
            get_command = 'winrm e %s/wbem/wscim/1/cim-schema/2/* ' % (uri_host) 
            get_command += '-dialect:association -filter:{object=%s?%s} ' % (classname, query)
            get_command += self.remote_options(remote)
            get_command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
            
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
            
            if raw: 
                return output
            else:
                # Parse the output into a response object
                return self.parse(output)
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        
        # Generate a Fault
        return Fault('WinRM',\
                 'Get is not supported on this instance or the reference is not set or it returned an error.',\
                 'WinRM provider for WSMAN returned an error.')
    
    def references(self, reference, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Do a references operation for an instance
        
        @param reference: CIM reference(key) response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response objects after enumerating the keys
        @rtype: List of L{Reference} objects/ L{Fault}
        """
        # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
            isinstance(reference, Reference):
            
            pairs = []
            for (key, value) in reference.items:
                                        
                # Assemble the intermediate value since it is stored as a list
                # TODO: What if the value is an array? How do we assemble an array for a get query?
                value_ = value[0] if value else ''
                value_ = value_ if value_ else ''
                
                # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
                safe_value = value_
                pairs.append('%s=%s' % (key, safe_value))
        
            # Get the query parameter for command construction
            query = '+'.join(pairs)
            classname = reference.classname
            
            get_command = 'winrm e %s/wbem/wscim/1/cim-schema/2/* ' % (uri_host)
            get_command += '-dialect:association -associations -filter:{object=%s?%s} ' % (classname, query)
            get_command += self.remote_options(remote)
            get_command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
            
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
            
            if raw: 
                return output
            else:
                # Parse the output into a response object
                return self.parse(output)
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        
        # Generate a Fault
        return Fault('WinRM',\
                 'Get is not supported on this instance or the reference is not set or it returned an error.',\
                 'WinRM provider for WSMAN returned an error.')

    
            
    def get(self, reference, cim_namespace, remote=None, raw=False):
        """
        Do a get operation for a reference. 
        
        @param reference: CIM reference(key) response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
        
        # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
            isinstance(reference, Reference):
            
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            for (key, value) in reference.items:
                # Assemble the intermediate value since it is stored as a list
                # TODO: What if the value is an array? How do we assemble an array for a get query?
                value_ = value[0] if value else ''
                value_ = value_ if value_ else ''
                
                # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
                safe_value = value_
                pairs.append('%s=%s' % (key, safe_value))
        
            # Get the query parameter for command construction
            query = '+'.join(pairs)
            classname = reference.classname
            
            # Construct the command
            get_command  = 'winrm g \"%s?%s\" ' % (reference.resource_uri, query)
            get_command += self.remote_options(remote)
            get_command += '-SkipCNcheck -SkipCAcheck -format:Pretty'
            
            
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
        
            if raw:
                return output
            
            else:
                # Note: (WinRM specific actions)
                # If it is not a fault then add the covers since get does not return
                # the results within the <wsman:Results> tag.
                if not self.extract(output):
                    output = '<wsman:Results>' + output + '</wsman:Results>'
                
                # Parse the output into a response object
                instance_or_fault = self.parse(output)
                if not isinstance(instance_or_fault, Fault) and isinstance(instance_or_fault, list):                
                    if len(instance_or_fault) > 0:
                        return instance_or_fault[0]
                    else:
                        return Fault('WinRM',\
                                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                                     'WinRM provider for WSMAN returned an error.')
                    
                return instance_or_fault
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        # Generate a Fault
        return Fault('WinRM',\
                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
        
    
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
        
        @return: Response object from the call, either a Reference, Fault, or an Result
        @rtype: L{Response}    
        """
        
        
        if reference and isinstance(reference, Reference):
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            
            for (key, value) in reference.items:
                # Assemble the intermediate value since it is stored as a list
                # TODO: What if the value is an array? How do we assemble an array for a get query?
                value_ = value[0] if value else ''
                value_ = value_ if value_ else ''
                
                # JCT: used to wrap values with paces in double quotes - now we wrap the entire uri
                safe_value = value_
                pairs.append('%s=%s' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = '+'.join(pairs)
            classname = reference.classname
            
            # Construct the command
            get_command  = 'winrm i %s \"%s?%s\" ' % (command, reference.resource_uri, query)
            get_command += self.remote_options(remote)
            get_command += '-SkipCNcheck -SkipCAcheck -format:Pretty '
            
            # construct the options
            if isinstance(arguments, basestring):
                get_command += "-file:\"%s\"" % arguments
            elif isinstance(arguments, dict):
                get_command += " " + self.properties_argument(arguments)
             
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
            
            if raw:
                return output
            else:
                # Parse the output into a response object
                instance_or_fault = self.parse(output)
                if not isinstance(instance_or_fault, Fault) and isinstance(instance_or_fault, list):                
                    if len(instance_or_fault) > 0:
                        return instance_or_fault[0]
                    else:
                        return Fault('WinRM',\
                                     'Invoke is not supported on this instance or the reference is not set or it returned an error.',\
                                     'WinRM provider for WSMAN returned an error.')
                        
                    
                return instance_or_fault
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        # Generate a Fault
        return Fault('WinRM',\
                     'Invoke is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')