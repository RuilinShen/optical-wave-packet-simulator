# BPM module - Angular Spectrum Method
import numpy as np
from scipy.fft import fft2, ifft2, fftfreq

def angular_spectrum_propagate(E0, X, Y, wavelength, z):
    dx = X[0, 1] - X[0, 0]
    dy = Y[1, 0] - Y[0, 0]
    Nx, Ny = E0.shape
    kx = 2 * np.pi * fftfreq(Nx, dx)
    ky = 2 * np.pi * fftfreq(Ny, dy)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    k = 2 * np.pi / wavelength
    kz_sq = k**2 - KX**2 - KY**2
    kz_safe = np.maximum(kz_sq, 0)
    kz_neg = np.maximum(-kz_sq, 0)
    phase = np.where(kz_sq >= 0, np.exp(1j * np.sqrt(kz_safe) * z), np.exp(-np.sqrt(kz_neg) * z))
    return ifft2(fft2(E0) * phase)

def beam_propagate(E0, X, Y, wavelength, z, steps=50):
    dz = z / steps
    zs, Es = [], []
    E = E0.copy()
    for i in range(steps):
        E = angular_spectrum_propagate(E, X, Y, wavelength, dz)
        if i % max(1, steps // 20) == 0 or i == steps - 1:
            zs.append((i + 1) * dz)
            Es.append(E.copy())
    return {"z": np.array(zs), "fields": np.array(Es)}
