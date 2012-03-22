"""
Utilities for the WSMan extension
"""

# Standard
import copy

# Internal
from wsman.response.fault import Fault 
from wsman.response.instance import Instance
from wsman.response.reference import Reference
from wsman.response.association import Association


def is_match(instance, reference):
    """
    Check if the reference is a match for the specified instance.
    
    @param instance: Instance of the class
    @type instance: L{Instance}
    @param reference: Key end point reference for the class
    @type reference: L{Reference} 
    """    
    
    for (key, value) in reference.items:
        if key.lower() != '__cimnamespace':
            if not (instance.get(key) == value):
                return False            
    return True
                 

def associate(instances, references):
    """
    Associate the instances with their respective reference keys
    
    @param instances: List of L{Instance} responses
    @type instances: List
    @param references: List of L{Reference} responses
    @type references: List
    
    @return: The status of the association
    @rtype: Tuple of (Status, Reason)
    """    
    
    # Length should be the same
    if not (len(instances) == len(references)):
        return (False, 'EPR(%d) and Enumerate(%d) did not returned same number of instances' % (len(references),len(instances)))
    
    available = copy.copy(references)
    for instance in instances:
        
        # if this is an association instance then ignore it.
        if isinstance(instance, Association):
            break
        
        # For non association instances do the pairing and setting                
        for reference in available:
            if is_match(instance, reference):
                instance.reference = reference
                available.remove(reference)
                break
        
        if not instance.reference:
            return (False, 'No reference(Keys) matched an instance')
        
    return (True, 'Success')
    
    
    
