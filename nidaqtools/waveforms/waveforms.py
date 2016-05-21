import numpy as np

def square_wave(x):
    return 2*(np.sin(x) >= 0) - 1
    
def squareroot_wave(x):
    return np.sqrt(np.abs(np.sin(0.5*x)))
    
    
class SampleLoop(object):
    def __init__(self,samples):
        self._samples = samples
        self._vectorized_evaluateSampleAtTime = np.vectorize(self._evaluateSampleAtTime)
        
        
    def _evaluateSampleAtTime(self,x):
        m,i = np.modf(x/(2*np.pi))
        return self._samples[int(m*len(self._samples))]
    
    def __call__(self,x):
        return self._vectorized_evaluateSampleAtTime(x)

