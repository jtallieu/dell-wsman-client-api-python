"""functools.py - Tools for working with functions and callable objects
"""
# Python module wrapper for _functools C module
# to allow utilities written in Python to be added
# to the functools module.
# Written by Nick Coghlan <ncoghlan at gmail.com>
# and Raymond Hettinger <python at rcn.com>
#   Copyright (C) 2006-2010 Python Software Foundation.
# See C source code for _functools credits/copyright

"""
Modified to support cache bypass argument for decorated methods

@copyright: 2011
@author: Joseph Tallieu <joseph_tallieu@dell.com>
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

__all__ = ['update_wrapper', 'wraps', 'WRAPPER_ASSIGNMENTS', 'WRAPPER_UPDATES',
           'total_ordering', 'cmp_to_key', 'lru_cache', 'reduce', 'partial']

from _functools import partial, reduce
from collections import namedtuple
from ordereddict import OrderedDict

try:
    from thread import allocate_lock as Lock
except:
    print "ERROR importing _threa", sys.exc_info()
    from _dummy_thread import allocate_lock as Lock

# update_wrapper() and wraps() are tools to help write
# wrapper functions that can handle naive introspection

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__doc__', '__annotations__')
WRAPPER_UPDATES = ('__dict__',)
def update_wrapper(wrapper,
                   wrapped,
                   assigned = WRAPPER_ASSIGNMENTS,
                   updated = WRAPPER_UPDATES):
    """Update a wrapper function to look like the wrapped function

       wrapper is the function to be updated
       wrapped is the original function
       assigned is a tuple naming the attributes assigned directly
       from the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated is a tuple naming the attributes of the wrapper that
       are updated with the corresponding attribute from the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    wrapper.__wrapped__ = wrapped
    for attr in assigned:
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wrapper, attr, value)
    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    # Return the wrapper so this can be used as a decorator via partial()
    return wrapper

def wraps(wrapped,
          assigned = WRAPPER_ASSIGNMENTS,
          updated = WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().
    """
    return partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated)

def total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    convert = {
        '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                   ('__le__', lambda self, other: self < other or self == other),
                   ('__ge__', lambda self, other: not self < other)],
        '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                   ('__lt__', lambda self, other: self <= other and not self == other),
                   ('__gt__', lambda self, other: not self <= other)],
        '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                   ('__ge__', lambda self, other: self > other or self == other),
                   ('__le__', lambda self, other: not self > other)],
        '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                   ('__gt__', lambda self, other: self >= other and not self == other),
                   ('__lt__', lambda self, other: not self >= other)]
    }
    # Find user-defined comparisons (not those inherited from object).
    roots = [op for op in convert if getattr(cls, op, None) is not getattr(object, op, None)]
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
    return cls

def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    class K(object):
        __slots__ = ['obj']
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
        def __hash__(self):
            raise TypeError('hash not implemented')
    return K

_CacheInfo = namedtuple("CacheInfo", "hits misses maxsize currsize")

def lru_cache(maxsize=100):
    """Least-recently-used cache decorator.

    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize) with
    f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    """
    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function,
                tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):
        cache_stats = {'hits':0, 'misses': 0}
        kwd_mark = (object(),)          # separates positional and keyword args
        lock = Lock()                   # needed because ordereddicts aren't threadsafe

        
        cache = OrderedDict()       # ordered least recent to most recent
        cache_popitem = cache.popitem
        cache_renew = cache.move_to_end


        @wraps(user_function)
        def wrapper(*args, **kwds):
            # check for bypass
            use_cache = "True"
            as_tuple = "False"
            from_cache = False
            
            if kwds.has_key("cache"):
                try:
                    use_cache = kwds.pop("cache").lower()
                except:
                    pass
            
            if kwds.has_key("as_tuple"):
                try:
                    as_tuple = kwds.pop("as_tuple").lower()
                except:
                    pass
            
            
            #generate key
            key = args
            if kwds:
                key += kwd_mark + tuple(sorted(kwds.items()))
            
            # bypass cache?
            if use_cache.lower() == "false" or use_cache.lower() == "no" or use_cache.lower() == "off":
                result = user_function(*args, **kwds)
                with lock:
                    cache[key] = result     # record recent use of this key
                    cache_stats['misses'] += 1
                    if len(cache) > maxsize:
                        cache_popitem(0)    # purge least recently used cache entry
                if as_tuple.lower() == "true":
                    return (from_cache, "command", result)
                else:
                    return result
            
            try:
                with lock:
                    result = cache[key]
                    cache_renew(key)        # record recent use of this key
                    cache_stats['hits'] += 1
                    from_cache = True
            except KeyError:
                result = user_function(*args, **kwds)
                with lock:
                    cache[key] = result     # record recent use of this key
                    cache_stats['misses'] += 1
                    if len(cache) > maxsize:
                        cache_popitem(0)    # purge least recently used cache entry
            
            if as_tuple.lower() == "true":
                return (from_cache, "command", result)
            else:
                return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return _CacheInfo(cache_stats['hits'], cache_stats['misses'], maxsize, len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            #nonlocal hits, misses
            with lock:
                cache.clear()
                cache_stats['hits'] = 0
                cache_stats['misses'] = 0

        
        
        
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    # Added to help epydoc use the proper parameters for lru_cache decorated methods.
    try:
        decorating_function.__doc__ = user_function.__doc__
        decorating_function.__repr__ = user_function.__repr__
    except:
        pass
    return decorating_function
