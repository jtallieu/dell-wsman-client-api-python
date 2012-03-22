"""
Remote configuration

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

class Remote(object):
    """
    Remote configuration class
    """
    
    def __init__(self, ip, username, password):
        """
        Constructor for the remote configuration
        
        @param ip: IP address of the SUT
        @type ip: String
        @param username: Username for the SUT
        @type username: String
        @param password: Password for the SUT
        @type password: String  
        """
        
        #Store the IP, Username and Password
        self.__ip = ip
        self.__username = username
        self.__password = password
    
    
    def __cmp__(self, other):
        if self.__ip == other.ip and self.__password == other.password and self.__username == other.username:
            return 0
        else:
            return 1
        
    def __hash__(self):
        """
        The hash function
        """
        return hash("%s %s %s" % (self.__ip, self.__username, self.__password))
        
            
    # Properties of the Remote class
    ip       = property(fget=lambda x: x.__ip)
    username = property(fget=lambda x: x.__username)
    password = property(fget=lambda x: x.__password)
    
    
if __name__ == "__main__":
    
    remote = Remote('127.0.0.1', 'root', 'calvin')
    print remote.ip, remote.username, remote.password
    try:
        remote.ip = '192.168.0.1'
    except AttributeError:        
        print "Check: This attribute cannot be set"