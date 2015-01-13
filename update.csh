#!/bin/csh

foreach i ( autosave busy calc camac caputRecorder configure dac128V delaygen documentation dxp ebrick ip ip330 ipUnidig love mca measComp modbus motor optics quadEM sscan softGlue std stream utils vac vme xxx )
	svn up $i
end
