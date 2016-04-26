import PyDAQmx as daq
import numpy as np
import time
import thread

class DAQFunctionGenerator(object):
    """
    A high level asynchronous interface for controlling a National Instruments DAQmx device as a function generator.
    """

    
    __sampleFrequencyStep = 100e6/2**32 #the sample rate should be an integer multiple of this value
    __sampleFrequency = 2e6// __sampleFrequencyStep * __sampleFrequencyStep
    __updateSize = 50000
    
    
    def __init__(self,channel, voltageRange=(-10,10)):
        self._channel = channel
        self._voltageRange = voltageRange
        
        
        self._frequency = 1000.0
        self._offset = 0.0
        self._amplitude = 1.0
        self._external_amplification = 1.0
        self._number_of_periods = 0
        
        self._stop_requested = False
        
        
        self._thread = None
        
        self._initialize_task()
    
    def _initialize_task(self):
        self._ao = daq.Task()
        self._ao.CreateAOVoltageChan(self._channel,"",self._voltageRange[0],self._voltageRange[1],daq.DAQmx_Val_Volts,None)
        self._ao.SetWriteRegenMode(daq.DAQmx_Val_DoNotAllowRegen)
        
        self._ao.WriteAnalogScalarF64(True,0,self._offset / self.external_amplification,None)
        
    
    @property
    def frequency(self):
        return self._frequency
    
    @frequency.setter
    def frequency(self,value):
        assert value > 0.1
        self._frequency = value
        
    @property
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self,value):
        self._offset = value
        if not self.is_running:
            self._ao.WriteAnalogScalarF64(True,0,self.offset/self.external_amplification,None)
            
    @property
    def number_of_periods(self):
        return self._number_of_periods

    @number_of_periods.setter
    def number_of_periods(self,value):
        self._number_of_periods = value
        

    @property
    def amplitude(self):
        return self._amplitude
    
    @amplitude.setter
    def amplitude(self,value):
        self._amplitude = value
        
    @property
    def external_amplification(self):
        return self._external_amplification
    
    @external_amplification.setter
    def external_amplification(self,value):
        self._external_amplification = value
    
    @property
    def is_running(self):
        return self._thread is not None
    
    def _generate_waveform(self):
                
        updateInterval = self.__updateSize / self.__sampleFrequency
        
        taskStarted = False
        t_start = 0
        t_max = self._number_of_periods * self._frequency
        t_end = None
        while not self._stop_requested:

            t_end = t_start + updateInterval
            if t_max > 0 and t_end > t_max:
                t_end = t_max
                self.stop()
            
            t_values = np.linspace(t_start,t_end,updateSize,endpoint=t_end==t_max)
            waveform = self.amplitude * np.sin(2*np.pi*self.frequency * tValues)
            data = (self.offset + waveform) / self.external_amplification

            samplesWritten = daq.int32()
            self._ao.CfgSampClkTiming("",sampleFrequency,daq.DAQmx_Val_Rising,daq.DAQmx_Val_ContSamps,self.__updateSize)
            
            self._ao.WriteAnalogF64(self.__updateSize, True, 10.0, daq.DAQmx_Val_GroupByChannel, data, daq.byref(samplesWritten), None)
            if not taskStarted:
                taskStarted = True

            t_start = t_end

        try:
            self._ao.WaitUntilTaskDone(1)
        except:
            pass
        
        self._ao.ClearTask()
        self._initialize_task()
        self._thread = None
        self._stop_requested = False
        print "finished"
        
    def start(self):
        if not self.is_running:
            self._thread = thread.start_new_thread(self._generate_waveform,())
            
    def stop(self):
        self._stop_requested = True