import numpy as np

from scipy.signal import gaussian, convolve

from .boxcar import Boxcar

std2fwhm = lambda std : std  * 2*np.sqrt(2*np.log(2)) / .72
fwhm2std = lambda fwhm: fwhm / 2*np.sqrt(2*np.log(2)) * .72

class Gaussian (Boxcar) :

  NAME = __name__.split('.',2)[2]
  PARAMETERS = 'fwhm', 'flagged'
  DEPENDENCIES = ()

  def window(self, fwhm):

    window = gaussian(self.spectrum.N, fwhm2std(fwhm))
    return window / np.sum(window)

  def auto(self):

    fwhm = len(self.spectrum.wave) / 100.
    return dict(fwhm=fwhm)

  def __call__(self, fwhm, flagged=None):

    self.fwhm = fwhm
    self.flagged = flagged if not flagged is None else self.flagged

    i = self.get_mask()
    flux = np.interp(self.spectrum.wave, self.spectrum.wave[i], self.spectrum.flux[i])

    window = self.window(fwhm)
    smooth = convolve(flux, window, 'same')

    return smooth
