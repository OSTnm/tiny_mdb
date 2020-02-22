# def __readonly__(self, *args, **kwargs):
#     raise TypeError("Cannot modify a FrozenDict")

# # It is hashable if keys and values are hashable. It is not truly read-only:
# # its internal dict is a public attribute.
# class ImmutableDict:
#     def __init__(self, dict):
#         if isinstance(dict, ImmutableDict):
#             self.data = dict.data
#         else:
#             self.data = {}
#             self.data.update(dict)

#     def __repr__(self):
#         return repr(self.data)

#     def __cmp__(self, dict):
#         if isinstance(dict, ImmutableDict):
#             return cmp(self.data, dict.data)
#         else:
#             return cmp(self.data, dict)
#     def __len__(self):
#         return len(self.data)

#     def __getitem__(self, key):
#         return self.data[key]

#     def copy(self):
#         assert self.__class__ is ImmutableDict, "Must be re-implemented"
#         return ImmutableDict(self.data)

#     def keys(self):
#         return self.data.keys()

#     def items(self):
#         return self.data.items()

#     def iteritems(self):
#         return self.data.iteritems()

#     def iterkeys(self):
#         return self.data.iterkeys()

#     def itervalues(self):
#         return self.data.itervalues()

#     def values(self):
#         return self.data.values()

#     def has_key(self, key):
#         return self.data.has_key(key)

#     def get(self, key, failobj=None):
#         return self.get(key, failobj)

#     def __contains__(self, key):
#         return key in self.data

#     def __iter__(self):
#         return iter(self.data)

#  # A frozendict is a dictionary that cannot be modified after being created
#  # - but it is hashable and may serve as a member of a set or a key in a
#  # dictionary

# class frozendict(dict):
#     def _blocked_attribute(obj):
#         raise AttributeError, "A frozendict cannot be modified."

#     _blocked_attribute = property(_blocked_attribute)
#     __delitem__ = __setitem__ = clear = _blocked_attribute
#     pop = popitem = setdefault = update = _blocked_attribute

#     def __new__(cls, *args, **kw):
#         new = dict.__new__(cls)
#         dict.__init__(new, *args, **kw)
#         return new

#     def __init__(self, *args, **kw):
#         pass


#     def __hash__(self):
#         try:
#             h = self._cached_hash
#         except AttributeError:
#             h = self._cached_hash = hash(frozenset(self.items()))

#         return h

#     def __repr__(self):
#         return "frozendict(%s)" % dict.__repr__(self)


# class FrozenDict(dict):
#     """
#     A FrozenDict is an immutable dictionary.
#     """

#     def __init__(self, *args, **kwargs):
#         dict.__init__(self, *args, **kwargs)
#         self.__hash = None
#         self.__init__ = None

#     __delitem__ = None
#     __setitem__ = None
#     clear = None

#     def copy(self):
#         return type(self)(dict.copy(self))
#     pop = None
#     popitem = None
#     setdefault = None
#     update = None

#     def __hash__(self):
#         if self.__hash is None:
#             self.__hash = pass

#         return self.__hash

#     def __repr__(self):
#         return '%s(%s)' % (type(self).__name__, dict.__repr__(self))

#     @classmethod
#     def fromkeys(S, v=None):
#         """
#         FrozenDict.fromkeys(S[,v]) -> New FrozenDict with keys from S and
#           values equal to v.
#         v defaults to None.
#         """
#         return FrozenDict(dict.fromkeys(S, v))

# class frozendict(dict):
#     def _blocked_attribute(obj):
#         raise AttributeError, "A frozendict cannot be modified."
#     _blocked_attribute = property(_blocked_attribute)

#     __delitem__ = __setitem__ = clear = _blocked_attribute
#     pop = popitem = setdefault = update = _blocked_attribute

#     def __new__(cls, *args):
#         new = dict.__new__(cls)
#         dict.__init__(new, *args)
#         return new

#     def __init__(self, *args):
#         pass

#     def __hash__(self):
#         try:
#             return self._cached_hash
#         except AttributeError:
#             h = self._cached_hash = hash(tuple(sorted(self.items())))
#             return h

#     def __repr__(self):
#         return "frozendict(%s)" % dict.__repr__(self)

# import collections

# class DictWrapper(collections.Mapping):

#     def __init__(self, data):
#         self._data = data

#     def __getitem__(self, key):
#         return self._data[key]

#     def __len__(self):
#         return len(self._data)

#     def __iter__(self):
#         return iter(self._data)


# import collections
# import operator
# import functools


# class frozendict(collections.Mapping):

#     def __init__(self, *args, **kwargs):
#         self.__dict = dict(*args, **kwargs)
#         self.__hash = None

#     def __getitem__(self, key):
#         return self.__dict[key]

#     def copy(self, **add_or_replace):
#         return frozendict(self, **add_or_replace)

#     def __iter__(self):
#         return iter(self.__dict)

#     def __len__(self):
#         return len(self.__dict)

#     def __repr__(self):
#         return '<frozendict %s>' % repr(self.__dict)

#     def __hash__(self):
#         if self.__hash is None:
#             hashes = map(hash, self.items())
#             self.__hash = functools.reduce(operator.xor, hashes, 0)

#         return self.__hash

# class ImmutableContainer(object):
#     def _immutable(self, *arg, **kw):
#         raise TypeError("%s object is immutable" % self.__class__.__name__)

#     __delitem__ = __setitem__ = __setattr__ = _immutable


# class immutabledict(ImmutableContainer, dict):

#     clear = pop = popitem = setdefault = \
#         update = ImmutableContainer._immutable

#     def __new__(cls, *args):
#         new = dict.__new__(cls)
#         dict.__init__(new, *args)
#         return new

#     def __init__(self, *args):
#         pass

#     def __reduce__(self):
#         return immutabledict, (dict(self), )

#     def union(self, d):
#         if not d:
#             return self
#         elif not self:
#             if isinstance(d, immutabledict):
#                 return d
#             else:
#                 return immutabledict(d)
#         else:
#             d2 = immutabledict(self)
#             dict.update(d2, d)
#             return d2

#     def __repr__(self):
#         return "immutabledict(%s)" % dict.__repr__(self)

# def immutabledict(data):
#     return types.MappingProxyType(data)
