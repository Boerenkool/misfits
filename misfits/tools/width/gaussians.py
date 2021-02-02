from copy import deepcopy

from ..velocity import Gaussians as VelocityGaussians

from ..base import BaseToolGaussians

class Gaussians (VelocityGaussians) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'continuum', 'amplitudes', 'x0s', 'stddevs', 'limits'

    def locations(self):

        zl = self._zip_nested_lists(self.x0s, self.amplitudes)

        f = lambda p: (p[0], self.spectrum[p[0]][1] - p[1]/2)
        return self._map_nested_lists(f, zl)

    def continuum_error(self, *args, **kwargs):

        _, limits, continuum, amplitudes, x0s, stddevs, _ = \
                next(super(Gaussians, self).continuum_error(*args, **kwargs, references=None))

        yield self, limits, continuum, amplitudes, x0s, stddevs

    @BaseToolGaussians.iterator_modifier(continuum_error)
    def __call__(self, *args, **kwargs):

        _, _, chi2s = super(Gaussians, self).__call__(*args, **kwargs, references=None)

        delattr(self, 'references')

        return deepcopy(self.stddevs), deepcopy(self._std_stddevs), chi2s
