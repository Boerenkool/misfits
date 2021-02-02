from copy import deepcopy

import numpy as np

from scipy.interpolate import UnivariateSpline

from ..base import BaseToolGaussians, BaseIterator

class Gaussians (BaseToolGaussians) :

    NAME = __name__.split('.',2)[2]
    PARAMETERS = 'continuum', 'amplitudes', 'x0s', 'stddevs', 'limits', 'references'
    DEPENDENCIES = 'spectrum.error',

    def __init__(self, *args, **kwargs):

        super(Gaussians, self).__init__(*args, **kwargs)

        self.fix_continuum = False

    def set_fix_continuum(self, state):

        self.fix_continuum = state

    def locations(self):

        f = lambda w: (w, self.spectrum[w][1])
        return self._map_nested_lists(f, self.x0s)

    def transform(self, x0, reference):

        if reference is not None:

            velocity = list((np.array(x0) / reference - 1) * 299792.458)
            units = 'km/s'

        else:

            velocity = x0
            units = ''

        return velocity, units

    def continuum_error(self, limits, continuum, amplitudes, x0s, stddevs, references):

        continuum, amplitudes = deepcopy(continuum), deepcopy(amplitudes)

        for i in range(len(limits)):

            loc = np.poly1d(continuum[i])(limits[i])
            scale = np.abs(loc) * self.spectrum.continuum_error

            cx0s  = np.poly1d(continuum[i])(x0s[i])

            continuum[i] = list(np.polyfit(limits[i], np.random.normal(loc, scale), 1))
            amplitudes[i] = list(amplitudes[i] - cx0s + np.poly1d(continuum[i])(x0s[i]))

        spectrum_error = self.spectrum.error
        self.spectrum.set_error(np.ones_like(spectrum_error))

        yield self, limits, continuum, amplitudes, x0s, stddevs, references

        self.spectrum.set_error(spectrum_error)

    @BaseToolGaussians.iterator_modifier(continuum_error)
    def __call__(self, limits, continuum, amplitudes, x0s, stddevs, references):

        self.continuum = []
        self.amplitudes = []
        self.x0s = []
        self.stddevs = []

        self._std_x0s = []
        self._std_stddevs = []

        chi2s = []

        for i in range(len(limits)):

            s = self.spectrum(*limits[i])
            x, y, e = s.wave, s.flux, s.error

            a0 = dict(continuum=continuum[i], amplitudes=amplitudes[i], x0s=x0s[i], stddevs=stddevs[i])
            a, std, chi2 = self.fit(self.gaussians, x, y, e, fixed=('continuum',) if self.fix_continuum else (), **a0)

            for k, v in a.items():
                getattr(self, k).append(v)
            self._std_x0s.append(std['x0s'])
            self._std_stddevs.append(std['stddevs'])

            chi2s.append(chi2)

        self.continuum = list(map(tuple, self.continuum))
        self.limits = limits
        self.references = references

        return deepcopy(self.x0s), deepcopy(self._std_x0s), chi2s
