import numpy as np
from scipy.fft import fft, ifft, fftfreq

def xpm_propagate(A1, A2, t, beta2_1, beta2_2, gamma, length, dz):
    Nz = int(length/dz)
    w = 2*np.pi*fftfreq(len(t), t[1]-t[0])
    op1 = np.exp(1j*beta2_1/2*w**2*dz/2)
    op2 = np.exp(1j*beta2_2/2*w**2*dz/2)
    zs=[]; f1=[]; f2=[]
    for n in range(Nz):
        A1=ifft(fft(A1)*op1); A2=ifft(fft(A2)*op2)
        A2=A2*np.exp(1j*2*gamma*np.abs(A1)**2*dz/2)
        A1=A1*np.exp(1j*gamma*np.abs(A1)**2*dz/2)
        A2=ifft(fft(A2)*op2); A1=ifft(fft(A1)*op1)
        if n%max(1,Nz//20)==0 or n==Nz-1:
            zs.append(n*dz); f1.append(A1.copy()); f2.append(A2.copy())
    return {"z":np.array(zs),"field1":np.array(f1),"field2":np.array(f2)}
