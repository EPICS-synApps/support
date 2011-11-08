; This program defines a complex waveform for the 1608G

npts = 100000L
prefix = '1608G:'
time = findgen(npts)/(npts-1)
volts = 2.*sin(time*4*!pi) + 2*sin(time*200*!pi) * 1*cos(time*3.1*!pi)
t = caput(prefix + 'WaveGenDwell', 1./npts)
t = caput(prefix + 'WaveGen1UserWF', volts)
t = caput(prefix + 'WaveGenNumPoints', npts)
t = caput(prefix + 'WaveGen1Type', 'User-defined')
end


