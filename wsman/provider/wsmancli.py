"""
WSManCLI based provider

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

import sys

from wsman import WSManProvider

from ..parsers import Parser
from ..response.fault import Fault
from ..response.instance import Instance
from ..response.reference import Reference
from ..response.association import Association
from exceptions import TypeError

import logging
log = logging.getLogger("WSMAN")

def find_children(name, node):
    """
    Finds direct children of a node by name
    
    @param name: The name of the node to find
    @type name: string
    
    @param node: the dict node
    @type node: dict
    """
    
    nodes = []
    try:
        for child in node.get('children',[]) if node else []:
            if child.get('name','') == name:
                nodes.append(child)
    except:
        pass
    return nodes 


def find_child(name, node):
    """
    Finds a direct child by name
    
    @param name: The node name to find (aka the Tag)
    @type name: string
    
    @param node: The dict node
    @type node: dict
    """
    try:
        for child in node.get('children',[]) if node else []:
            if child.get('name','') == name:
                return child
    except:
        pass
    return None
            

class WSManCLI(WSManProvider):
    """
    Unix based WS-Management provider.
    """
    
    def __init__(self, transport):
        """
        Constructor for the WSMan provider class.
        
        @param transport: Transport object to execute the constructed command
        @type transport: L{Transport}
        """
        
        # Call the base class 
        super(WSManCLI, self).__init__(transport)
    
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
    
    
    def generate_response(self, node):
        """
        Construct the response object from the results node dictionary
        
        @param node: XML results dictionary
        @type node: Dictionary
        
        @return: List of Response objects parsed from the node
        @rtype: List of L{Response}
        """
        item_nodes = []
        
        if not node:
            return Fault('WSManCLI', 
                         'Internal Server Error(WSManCLI Provider)', 
                         'Invalid response format')
            
        # Response objects
        responses = []
        
        fault = find_child("WSManFault", node)
        if fault:
            return self.response_from_fault(fault)
        
        # Iterate over the envelopes - may be more than one (see PullResponse)
        # to get the items
        envelopes = find_children("Envelope", node)
        if not envelopes:
            return Fault('WSManCLI', 
                         'Internal Server Error(WSManCLI Provider)', 
                         'Invalid response format - no Envelope tag')
        
        # for each envelope get the body
        for envelope in envelopes:
            body = find_child("Body", envelope)
            if not body:
                return Fault('WSManCLI', 
                         'Internal Server Error(WSManCLI Provider)', 
                         'Invalid response format - no Body tag in Envelope')
            
            # Aggregate items from both the EnumerateResponse and the PullResponse
            items = find_child("Items", find_child("EnumerateResponse", body))
            if items: 
                item_nodes.append(items)
            else:    
                items = find_child("Items", find_child("PullResponse", body))
                if items: 
                    item_nodes.append(items)
                else:
                    item_nodes.append(body)
            
        
        for item in item_nodes:
            # Decide if this is an Instance, Association or Reference, or Fault
            for child in item.get('children', []):
                qname = child.get('type', '')
                name = child.get('name', '')
                
                log.debug ("Got %s" %  name)
                # Response Object
                response = None
                
                # End point reference (EPR)
                if name == 'EndpointReference':                
                    for child_ in child.get('children', []):
                        if child_.get('name', '') == 'ReferenceParameters':
                            response = self.response_from_reference(name, child_)
                
                
                elif name == "Fault" or name == "WSManFault":
                    return self.response_from_fault(child)
                
                elif name == "IdentifyResponse":
                    return self.response_from_identify(child)
                           
                # Instance or Association
                else:
                    response = Instance(name) if not self.is_association(child) else Association(name)                
                    
                    # Build the instance attributes
                    for child_ in child.get('children', []):
                        
                        # Get the name and value
                        key = child_.get('name', None)
                        value = child_.get('value', None)
                        
                        # Construct the association
                        if key and child_.get('children', []):                                                
                            for child__ in child_.get('children', []):
                                if child__.get('name', '') == 'ReferenceParameters':
                                    value = self.response_from_reference(key, child__)
                                elif child__.get('name', '') == 'EndpointReference': # Change in XML structure so that Reference Params and Endpoint References can occur at the same level
                                    for child___ in child__.get('children',[]):
                                        if child___.get('name', '') == 'ReferenceParameters':
                                            value = self.response_from_reference(key, child___)                                                                        
                        if key:                                
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
        
        code   = 'WSManCLI'
        reason = 'Internal Server Error (WSManCLI Provider)'
        detail = 'Internal Server Error (WSManCLI Provider)'
        
        log.debug ("Generating a fault from response %s" % node.get('name', ''))
        try:
            for child in node.get('children', []):
                name = child.get('name', '')
                if name == 'Code':
                    for x in child.get('children', []):
                        if x.get("name", '') == 'Subcode':
                            for y in x.get('children', []):
                                if y.get("name", '') == 'Value':
                                    code = y.get('value', '')                                                                    
                elif name == 'Reason':
                    for x in child.get('children', []):
                        if x.get("name", '') == 'Text':                        
                            reason = x.get('value', '')
                            
                elif name == 'Detail':
                    for x in child.get('children', []):
                        if x.get("name", '') == 'FaultDetail':                        
                            detail = x.get('value', '')
        except:
            log.warn("Error processing FAULT %s, %s" % (sys.exc_info()[0],sys.exc_info()[0]))
            pass
                        
        return Fault(code, reason, detail)        
    
    

        
    def get_response(self,node):
        """
        Gets a response object from parsed output.  Calls generate_response
        with a specific starting node.  This method tries to find where the 
        generate_response method should start processing. 
        
        @param node: dict representation of XML output
        @type node: dict
        
        @return: Response object
        @rtype: L{Response}
        """
        
        return self.generate_response(node)
        
    
    def parse(self, output):
        """
        Parse the output into one of the response formats.
        
        @param output: Output from the transport
        @type output: String
        """
        #print "---> Size of output", len(output)
        
        # Strip out the XML decl elements by pushing anything before the XML DECL and examining the tail
        output_frags = []
        tail = output
        found_decl = False
        
        while len(tail) > 0:
            
            start = tail.find("<?xml ")
            end = -1
            
            #print "SPLICE: len", len(tail), "start", start
            
            # a xml decl element was found
            if start > -1:
                end = tail.find("?>")
                
                if found_decl:
                    output_frags.append(tail[0:start])
                    
                found_decl = True
                tail = tail[end + 2 : ]
                
            else:
                # xml decl NOT found in the tail - append the tail to the output frags
                output_frags.append(tail)
                tail = ""
                
        output = " ".join(output_frags)
        
        #print "---> Size of spliced output", len(output)
        
        # put our own wrapper on around it
        output = "<climate:env>" + output + "</climate:env>"
        
        #print "\nParsing \n", output[0:40],"...",output[-20:],"\n"

        # Get the  dictionary representation of the extracted XML
        xml_dict = Parser().parse(output) if output else {}
        
        # Hold on to the body node - all responses have a body node
        return self.get_response(xml_dict)
        
        
        
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
        remote_  = '-u %s ' % remote.username
        remote_ += '-p %s ' % remote.password
        remote_ += '-h %s ' % remote.ip
        remote_ += '-P 443 -j utf-8 -y basic -V -v -c Dummy '
        return remote_
    
    
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
        command = 'wsman identify -o -m 512 '
        command += self.remote_options(remote)
        
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
        
        
        @return: Response object after enumeration
        @rtype: List of L{Response} objects/ L{Fault}
        """
        
        # Construct the command
        enumerate_command = 'wsman -o -m 512 '
        enumerate_command += self.remote_options(remote)
        enumerate_command += '-N %s enumerate %s/wbem/wscim/1/cim-schema/2/%s' % (cim_namespace, uri_host, cim_class)
        
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
        enumerate_command = 'wsman -M epr -o -m 512 '
        enumerate_command += self.remote_options(remote)
        enumerate_command += '-N %s enumerate %s/wbem/wscim/1/cim-schema/2/%s' % (cim_namespace, uri_host, cim_class)
       
        log.debug ("Executing command %s" % enumerate_command)
        # Use the transport and execute the command
        output = self.get_transport().execute(enumerate_command)
        
        if raw:
            return output
        else:
            # Parse the output into a response object
            return self.parse(output)
        
    
    def associators(self, reference, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Do a associators operation for an instance.
        
        @param reference: CIM instance response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
         # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
              isinstance(reference,Reference):
                
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            for (key, value) in reference.items:
                if key != '__cimnamespace': # Ignore this key
                                        
                    # Assemble the intermediate value since it is stored as a list
                    # TODO: What if the value is an array? How do we assemble an array for a get query?
                    value_ = value[0] if value else ''
                    value_ = value_ if value_ else ''
                    
                    # If there are any spaces in the value then we need to single quote the string
                    safe_value = '\"%s\"' % value_ if value_.find(' ') > 0 else value_
                    pairs.append('%s=%s' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = ','.join(pairs) + ' '
            
            # Construct the command
            get_command = 'wsman -o -m 512 '
            get_command += self.remote_options(remote)
            get_command += '-N %s associators %s/wbem/wscim/1/* ' % (uri_host, reference.get("__cimnamespace",[cim_namespace])[0])
            get_command += '--filter %s?%s --dialect http://schemas.dmtf.org/wbem/wsman/1/cimbinding/associationFilter' % (reference.resource_uri, query)
            
            log.debug ("Executing command %s" % get_command)
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
        return Fault('WSManCLI',\
                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
    
    def references(self, reference, cim_namespace, remote=None, raw=False, uri_host=""):
        """
        Do a references operation for an instance.
        
        @param reference: CIM instance response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        @param uri_host: The host portion of the resource URI
        @type uri_host: L{String}
        
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
         # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
              isinstance(reference,Reference):
                
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            for (key, value) in reference.items:
                if key != '__cimnamespace': # Ignore this key
                                        
                    # Assemble the intermediate value since it is stored as a list
                    # TODO: What if the value is an array? How do we assemble an array for a get query?
                    value_ = value[0] if value else ''
                    value_ = value_ if value_ else ''
                    
                    # If there are any spaces in the value then we need to single quote the string
                    safe_value = '\"%s\"' % value_ if value_.find(' ') > 0 else value_
                    pairs.append('%s=%s' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = ','.join(pairs) + ' '
            
            # Construct the command
            get_command = 'wsman -o -m 512 '
            get_command += self.remote_options(remote)
            get_command += '-N %s references %s/wbem/wscim/1/* ' % (uri_host, reference.get("__cimnamespace",[cim_namespace])[0])
            get_command += '--filter %s?%s --dialect http://schemas.dmtf.org/wbem/wsman/1/cimbinding/associationFilter' % (reference.resource_uri, query)
            
            log.debug ("Executing command %s" % get_command)
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
        return Fault('WSManCLI',\
                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
        
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
            query = ','.join(pairs)
            classname = reference.classname
            
            # Construct the command
            get_command  = 'winrm put \"%s?%s\" ' % (reference.resource_uri, query)
            get_command += self.remote_options(remote)
            
            for k,v in properties.items():
                get_command += '-k \"%s=%s\" ' % (k,v)
            
            
            # Use the transport and execute the command
            output = self.get_transport().execute(get_command)
            if raw:
                return output
            else:
                return self.parse(output)
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        # Generate a Fault
        return Fault('WSManCLI',\
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
                pairs.append('%s=\"%s\"' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = ','.join(pairs)
            classname = reference.classname
            
            # Construct the command
            get_command  = 'wsman invoke \"%s?%s\" -a \"%s\" ' % (reference.resource_uri, query, command)
            get_command += self.remote_options(remote)
            
            # construct the options
            if isinstance(arguments, basestring):
                get_command += "--input=\"%s\"" % arguments
            elif isinstance(arguments, dict):
                for k,v in arguments.items():
                    get_command += '-k \"%s=%s\" ' % (k,v)
             
            output = self.get_transport().execute(get_command)
            
            if raw:
                return output
            else:
                instance_or_fault = self.parse(output)
                if not isinstance(instance_or_fault, Fault) and isinstance(instance_or_fault, list):                
                    if len(instance_or_fault) > 0:
                        return instance_or_fault[0]
                    
                return instance_or_fault
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
            
        # Generate a Fault
        return Fault('WSManCLI',\
                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
        
    
    
    def get(self, reference, cim_namespace, remote=None, raw=False):
        """
        Do a get operation for an instance. The instance object should already have
        a key reference established before doing a get operation.
        
        @param reference: CIM instance response object
        @type reference: L{Reference}
        @param cim_namespace: Namespace of the CIM class
        @type cim_namespace: String
        @param remote: Remote configuration object
        @type remote: L{Remote}
        
        @return: Response object after enumerating the keys
        @rtype: L{Instance}         
        """
        
        # Note: There are no gets on an association instance
    
        # Get the keys reference for this instance (This needs to be set prior to the get)
        if reference and\
		      isinstance(reference,Reference):
                
            # Important: 
            # Form the query from the reference and not from the enumerated instance
            pairs = []
            for (key, value) in reference.items:
                if key != '__cimnamespace': # Ignore this key
                                        
                    # Assemble the intermediate value since it is stored as a list
                    # TODO: What if the value is an array? How do we assemble an array for a get query?
                    value_ = value[0] if value else ''
                    value_ = value_ if value_ else ''
                    
                    # If there are any spaces in the value then we need to single quote the string
                    safe_value = '\"%s\"' % value_ if value_.find(' ') > 0 else value_
                    pairs.append('%s=%s' % (key, safe_value))
            
            # Get the query parameter for command construction
            query = ','.join(pairs) + ' '
            
            # Construct the command
            get_command = 'wsman -o -m 512 '
            get_command += self.remote_options(remote)
            get_command += '-N %s get %s?%s' % (reference.get("__cimnamespace",[cim_namespace])[0], reference.resource_uri, query)
            
            log.debug ("Executing command %s" % get_command)
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
                    
                return instance_or_fault
        
        else:
            raise TypeError("reference argument must be of type Reference.  Use values from enumerate_keys instead?")
        
        # Generate a Fault
        return Fault('WSManCLI',\
                     'Get is not supported on this instance or the reference is not set or it returned an error.',\
                     'WinRM provider for WSMAN returned an error.')
        
