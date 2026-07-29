import numpy as np

def kolmogorov_phase_screen(N, dx, r0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    kx = 2*np.pi*np.fft.fftfreq(N, dx)
    ky = 2*np.pi*np.fft.fftfreq(N, dx)
    KX, KY = np.meshgrid(kx, ky)
    k = np.sqrt(KX**2 + KY**2)
    k[0,0] = 1e-12
    Phi = 0.023 * r0**(-5/3) * k**(-11/3)
    Phi[0,0] = 0  # Zero DC to avoid float64 precision loss
    cn = (np.random.normal(size=(N,N)) + 1j*np.random.normal(size=(N,N))) * np.sqrt(Phi)
    phase = np.real(np.fft.ifft2(cn)) * N
    s = np.std(phase)
    return phase / s * 0.5 if s > 0 else phase

def apply_phase(E, phase):
    return E * np.exp(1j * phase)
