#!/bin/csh

foreach i ( areaDetector autosave busy calc camac configure dac128V delaygen documentation dxp ebrick ip ip330 ipUnidig love mca modbus motor optics quadEM sscan softGlue std stream utils vac vme vxStats xxx )
	svn up $i
end
