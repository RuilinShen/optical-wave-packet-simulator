import numpy as np

def jones_vector(theta, phi=0):
    ex = np.cos(theta)
    ey = np.sin(theta) * np.exp(1j * phi)
    return np.array([ex, ey])

def linear_polarization(angle):
    return jones_vector(angle, 0)

def circular_polarization(left=True):
    return np.array([1, -1j if left else 1j]) / np.sqrt(2)

def birefringent_propagate(J, delta_n, L, wavelength):
    phi = 2 * np.pi * delta_n * L / wavelength
    Jx = J[0] * np.exp(-1j * phi / 2)
    Jy = J[1] * np.exp(1j * phi / 2)
    return np.array([Jx, Jy])

def stokes_parameters(J):
    S0 = np.abs(J[0])**2 + np.abs(J[1])**2
    S1 = np.abs(J[0])**2 - np.abs(J[1])**2
    S2 = 2 * np.real(J[0] * np.conj(J[1]))
    S3 = 2 * np.imag(J[0] * np.conj(J[1]))
    return np.array([S0, S1, S2, S3])
