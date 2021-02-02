from inspect import stack, getmro

from copy import deepcopy

from .iterator import BaseIterator

class BaseTool (object) :

    def __init__(self, spectrum):

        self.set_spectrum(spectrum)

    def auto(self, limits=None):

        return {}

    def set_spectrum(self, spectrum):

        self.spectrum = spectrum

    def set_parameters(self, **params):

        params = deepcopy(params)
        for p in self.PARAMETERS:
            if not p in params:
                raise KeyError(p)
            setattr(self, p, params[p])

        return params

    def get_parameters(self):

        params = dict()
        for p in self.PARAMETERS:
            if not hasattr(self, p):
                return None
            params[p] = getattr(self, p)

        return deepcopy(params)

    def del_parameters(self):

        for p in self.PARAMETERS:
            if hasattr(self, p):
                delattr(self, p)

    @classmethod
    def iterator_modifier(cls, m):

        def _(f):
            def __(self, *a, **kw):

                if not 'self' in stack()[1][0].f_locals:
                    return f(self, *a, **kw)
                caller = stack()[1][0].f_locals['self'].__class__
                if not BaseIterator in getmro(caller):
                    return f(self, *a, **kw)

                modifier = m(self, *a, **kw)
                result = f(*next(modifier))

                try:
                    next(modifier)
                except StopIteration:
                    pass

                return result

            return __
        return _

    def _map_nested_lists(self, f, l):

        l = deepcopy(l)

        def _(l):

            for i in range(len(l)):

                if isinstance(l[i], list):
                    _(l[i])
                elif l[i] is None:
                    continue
                else:
                    l[i] = f(l[i])

        _(l)

        return l

    def _zip_nested_lists(self, *l):

        zl = []

        def _(zl, l):

            for i in range(len(l)):

                if isinstance(l[i][0], list):
                    zl.append([])
                    _(zl[-1], list(zip(*l[i])))
                else:
                    zl.append(l[i])

        _(zl, list(zip(*l)))

        return zl
