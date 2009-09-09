#!/usr/bin/env python

# wish list:
# survey mda files should update if new files are added to directory
# would like to be able to display a file while it is being written

import os
import sys
import time
import locale

# the executable produced by pyinstaller doeasn't know what to make
# of matplotlib.numerix.ma.getmask, and it can't find the matplotlib data files
if hasattr(sys, 'frozen') and sys.frozen:
	import numpy.core.ma
	sys.modules['numpy.ma'] = sys.modules['numpy.core.ma']
	# This evidently is for py2exe, not pyinstaller
	#mpldir = os.path.join(theModuleManager.get_appdir(), 'matplotlibdata')
	#print 'mpldir=', mpldir
	#os.environ['MATPLOTLIBDATA'] = mpldir 

import matplotlib
#matplotlib.use('WXAgg')
import wx
import wxmpl
import wx.lib.scrolledpanel as scrolled
import wx.lib.mixins.listctrl as listmix
from pylab import *
import numpy

# try this to help pyinstaller find stuff
import matplotlib.numerix.fft
import matplotlib.numerix.linear_algebra
import matplotlib.numerix.ma
import matplotlib.numerix.mlab
import matplotlib.numerix.npyma
import matplotlib.numerix.random_array

import mda_f as mda

import string
import mdaTree

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.axes3d as axes3d
from matplotlib.ticker import NullLocator
import matplotlib.cbook as cbook

from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor

TIME_FORMAT = "%c" # Use Locale's time format
DEBUG = False
DIRLIST_TIME_MS = 10000

# We're going to have positioner and detector checkbox lists, and we have to
# keep their id's separate, but we also want the id's to correspond with 
# indices in the data structure we get from readMDA.  When we need the id's
# to be different, we'll add pIdOffset to positioner id's.
pIdOffset = 100
AXIS_IS_INDEX = 5

LINUX_PRINTING_COMMAND = 'lpr'

 
# From Python Cookbook
import re
re_digits = re.compile(r'(\d+)')
def embedded_numbers(s):
	pieces = re_digits.split(s)             # split into digits/nondigits
	pieces[1::2] = map(int, pieces[1::2])   # turn digits into numbers
	return pieces
def sort_strings_with_embedded_numbers(alist):
	aux = [ (embedded_numbers(s), s) for s in alist ]
	aux.sort()
	return [ s for __, s in aux ]           # convention: __ means "ignore"

def cmpStringsWithEmbeddedNumbers(s1, s2):
	if s1 == s2: return 0
	ss = sort_strings_with_embedded_numbers([s1,s2])
	if ss[0] == s1: return 1
	return -1

def dimensions(data):
	if isinstance(data, numpy.ndarray):
		return len(data.shape)
	else:
		dim = 0
		if (not isinstance(data, list)) and (not isinstance(data, tuple)):
			return dim
		dim += 1
		if (not isinstance(data[0], list)) and (not isinstance(data[0], tuple)):
			return dim
		dim += 1
		if (not isinstance(data[0][0], list)) and (not isinstance(data[0][0], tuple)):
			return dim
		dim += 1
		if (not isinstance(data[0][0][0], list)) and (not isinstance(data[0][0][0], tuple)):
			return dim
		return dim + 1

def rowColumn(rows, columns, plotNum):
	thisRow = plotNum // columns
	if plotNum % columns: thisRow += 1
	thisColumn = plotNum - (thisRow-1)*columns
	return (thisRow, thisColumn)

def isBottomPlot(rows, columns, plotNum, numPlots):
	r,c = rowColumn(rows, columns, plotNum)
	if r == rows: return True
	if plotNum+columns > numPlots: return True
	return False

def isLeftmostPlot(rows, columns, plotNum, numPlots):
	r,c = rowColumn(rows, columns, plotNum)
	return c==1

def calcRowsColumns(numPlots):
	if (numPlots == 0):
		return (0,0)
	columns = int(sqrt(numPlots)+0.5)
	rows = numPlots/columns
	if numPlots%columns:
		rows = rows+1
	return (rows, columns)

def makeXLabel(dim, posAxis):
	if posAxis < dim.np:
		p = dim.p[posAxis]
		label = p.name
		if (p.desc != ""):
			label = label + " '%s'" % p.desc
		if (p.unit != ""):
			label = label + " (%s)" % p.unit
	elif posAxis == AXIS_IS_INDEX:
		label = "index"
	else:
		print "unrecognized posAxis"
		return "None"
	return label

def makeDetLabel(y):
	if (y.desc and y.unit):
		label = "%s\n%s (%s)" % (y.name, y.desc, y.unit)
	elif (y.desc):
		label = "%s\n%s" % (y.name, y.desc)
	elif (y.unit):
		label = "%s (%s)" % (y.name, y.unit)
	else:
		label = y.name
	return label

def sliceStartEnd(ix, width, imax):
	iStart = max(0,ix-width/2)
	iEnd = min(imax, iStart+width)
	iStart = max(0,iEnd-width)
	return (iStart, iEnd)

def select2DSlice(data, indexList=None, widthList=None):
	#print "select2DSlice: indexList=", indexList
	dimension = dimensions(data)
	if dimension == 2:
		#if not isinstance(data, numpy.ndarray):
		#	data = numpy.array(data)
		return data
	elif dimension == 3:
		if not isinstance(data, numpy.ndarray):
			data = numpy.array(data)
		(ix, iy, iz) = (indexList[0:3])
		if ix != None:
			try:
				width = widthList[0] 
				assert(width > 1)
			except:
				return data[ix,:,:]
			else:
				(iStart, iEnd) = sliceStartEnd(ix, width, data.shape[0])
				b = apply_over_axes(sum, data[iStart:iEnd,:,:], 0)
				return b[0,:,:]
		elif iy != None:
			try:
				width = widthList[1]
				assert(width > 1)
			except:
				return data[:,iy,:]
			else:
				(iStart, iEnd) = sliceStartEnd(iy, width, data.shape[1])
				b = apply_over_axes(sum, data[:,iStart:iEnd,:], 1)
				return b[:,0,:]
		else:
			try:
				width = widthList[2]
				assert(width > 1)
			except:
				return data[:,:,iz]
			else:
				(iStart, iEnd) = sliceStartEnd(iz, width, data.shape[2])
				b = apply_over_axes(sum, data[:,:,iStart:iEnd], 2)
				return b[:,:,0]
	else:
		print "select2DSlice: Not ready for %d-dimensional data" % dimension
		return None


def select2DAxisData(frame, dimension, indexList):
	posAxisList = frame.posAxisList
	data = frame.data
	axisData = []
	axisLabel = []
	if indexList == None:
		indexList = [None, None, None]

	#print "select2DAxisData: dimension=", dimension, " indexList=", indexList
	nIx = min(dimension, len(indexList)) # indexList may have unneeded element
	for i in range(1, nIx+1):
		if indexList[i-1] == None:
			posAxis = posAxisList[i]
			if posAxis < data[i].np:
				if i == 1:
					array = data[i].p[posAxis].data
				elif i == 2:
					if isinstance(data[i].p[posAxis].data, list) or isinstance(data[i].p[posAxis].data, tuple):
						array = data[i].p[posAxis].data[0]
					else:
						array = data[i].p[posAxis].data[0,:]
				else:
					if isinstance(data[i].p[posAxis].data, list) or isinstance(data[i].p[posAxis].data, tuple):
						array = data[i].p[posAxis].data[0][0]
					else:
						array = data[i].p[posAxis].data[0,0,:]
				axisData.append(array)
				axisLabel.append(makeXLabel(data[i], posAxis))
			else:
				# if posAxis == AXIS_IS_INDEX, which is greater than any expected data[i].np
				axisData.append(range(data[i].curr_pt))
				axisLabel.append("index")
	return (axisData, axisLabel)

def select1DSlice(data, indexList=None, widthList=None):
	dimension = dimensions(data)
	#print "select1DSlice: indexList, data.shape=", indexList, data.shape
	if dimension == 1:
		return data
	if dimension > 3:
		print "    select1DSlice: Not ready for %d-dimensional data" % dimension
		return None

	if isinstance(data, list) or isinstance(data, tuple):
		data = numpy.array(data)
	if dimension == 2:
		for i,ix in enumerate(indexList[0:2]):
			if ix != None:
				#print "    select1DSlice: ix=", ix
				try:
					width = widthList[i]
					assert(width > 1)
				except:
					if i==0:
						return data[ix,:]
					else:
						return data[:,ix]
				else:
					(iStart, iEnd) = sliceStartEnd(ix, width, data.shape[i])
					if i==0:
						b = apply_over_axes(sum, data[iStart:iEnd,:], 0)
						return b[0,:]
					else:
						b = apply_over_axes(sum, data[:,iStart:iEnd], 1)
						return b[:,0]

	if dimension == 3:
		b = select2DSlice(data, indexList, widthList)
		if indexList == None:
			pass
		elif indexList[0] != None:
			indexList = indexList[1:3]
			if widthList != None:
				widthList = widthList[1:3]
		else:
			indexList = [indexList[0],indexList[2]]
			if widthList != None:
				widthList = [widthList[0],widthList[2]]
		return select1DSlice(b, indexList, widthList)


def select1DAxisData(frame, dim, indexList):
	posAxisList = frame.posAxisList
	data = frame.data
	axisData = None
	axisLabel = None

	if dim == 1:
		posAxis = posAxisList[1]
		if (posAxis < data[1].np):
			axisData = data[1].p[posAxis].data
			axisLabel = makeXLabel(data[1], posAxis)
		return (axisData, axisLabel)

	if (dim == 2):
		(ix, iy) = (indexList[0:2])
		if (ix==None):
			posAxis = posAxisList[1]
			if (posAxis < data[1].np):
				axisData = data[1].p[posAxis].data
				axisLabel = makeXLabel(data[1], posAxis)
		else:
			posAxis = posAxisList[2]
			if (posAxis < data[2].np):
				if isinstance(data[2].p[posAxis].data, list) or isinstance(data[2].p[posAxis].data, tuple):
					axisData = data[2].p[posAxis].data[0]
				else:
					axisData = data[2].p[posAxis].data[0,:]
				axisLabel = makeXLabel(data[2], posAxis)
		return (axisData, axisLabel)

	if (dim == 3):
		(ix, iy, iz) = (indexList[0:3])
		if (ix==None):
			posAxis = posAxisList[1]
			if (posAxis < data[1].np):
				axisData = data[1].p[posAxis].data
				axisLabel = makeXLabel(data[1], posAxis)
		elif (iy == None):
			posAxis = posAxisList[2]
			if (posAxis < data[2].np):
				if isinstance(data[2].p[posAxis].data, list) or isinstance(data[2].p[posAxis].data, tuple):
					axisData = data[2].p[posAxis].data[0]
				else:
					axisData = data[2].p[posAxis].data[0,:]
				axisLabel = makeXLabel(data[2], posAxis)
		else:
			posAxis = posAxisList[3]
			if (posAxis < data[3].np):
				if ininstance(data[3].p[posAxis].data, list):
					axisData = data[3].p[posAxis].data[0][0]
				else:
					axisData = data[3].p[posAxis].data[0,0,:]
				axisLabel = makeXLabel(data[3], posAxis)
		return (axisData, axisLabel)
	return (None, None)

###########################################################################################
class xyMultiCursor:
	def __init__(self, canvas, axes, **lineprops):
		self.canvas = canvas
		#self.axes = axes
		xmin, xmax = axes[-1].get_xlim()
		xmid = 0.5*(xmin+xmax)
		ymin, ymax = axes[-1].get_ylim()
		ymid = 0.5*(ymin+ymax)
		self.linesv = [ax.axvline(xmid, visible=False, **lineprops) for ax in axes]
		self.linesh = [ax.axhline(ymid, visible=False, **lineprops) for ax in axes]

		self.visible = True
		self.background = None
		self.needclear = False

		self.canvas.mpl_connect('motion_notify_event', self.onmove)
		self.canvas.mpl_connect('draw_event', self.clear)

	def clear(self, event):
		'clear the cursor'
		for line in self.linesv: line.set_visible(False)
		for line in self.linesh: line.set_visible(False)

	def onmove(self, event):
		if event.inaxes is None: return
		#if not self.canvas.widgetlock.available(self): return
		self.needclear = True
		if not self.visible: return

		for line in self.linesv:
			line.set_xdata((event.xdata, event.xdata))
			line.set_visible(self.visible)
		for line in self.linesh:
			line.set_ydata((event.ydata, event.ydata))
			line.set_visible(self.visible)
		self.canvas.draw()

	def _update(self):
			self.canvas.draw_idle()

##############################################################################################
class CanvasFrame(wx.Frame):
	def __init__(self, parent, id, frame, dataDim,
			plotFunc=None, sliders=[], size=(600,600), dpi=96):
		wx.Frame.__init__(self, parent, id, frame.fileName, size=(600,600))

		self.sliders = sliders # list of needed sliders ['x', 'y', 'z']
		self.frame = frame
		self.dataDim = dataDim
		self.plotFunc = plotFunc
		self.parent = parent
		self.indexList = [None, None, None]
		self.widthList = [0,0,0]
		self.ixSlider = None
		self.plot3D_dX = None

		self.iySlider = None
		self.plot3D_dY = None

		self.izSlider = None
		self.plot3D_dZ = None

		pData = wx.PrintData()
		pData.SetPaperId(wx.PAPER_LETTER)
		if callable(getattr(pData, 'SetPrinterCommand', None)):
			pData.SetPrinterCommand(LINUX_PRINTING_COMMAND)
		self.printer = wxmpl.FigurePrinter(self, pData)

		menuBar = wx.MenuBar()
		menu = wx.Menu()
		MENU_PSETUP = wx.NewId()
		MENU_PREVIEW = wx.NewId()
		MENU_PRINT = wx.NewId()
		MENU_SAVE = wx.NewId()
		menu.Append(MENU_PSETUP, "Page Setup...",    "Printer Setup")
		menu.Append(MENU_PREVIEW,"Print Preview...", "Print Preview")
		menu.Append(MENU_PRINT,  "&Print",           "Print Plot")
		menu.Append(MENU_SAVE,   "&Export",   "Save Image of Plot")
		menuBar.Append(menu,     "&File");
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.onPrintSetup, id=MENU_PSETUP)
		self.Bind(wx.EVT_MENU, self.onPrintPreview, id=MENU_PREVIEW)
		self.Bind(wx.EVT_MENU, self.onPrint, id=MENU_PRINT)
		self.Bind(wx.EVT_MENU, self.onExport, id=MENU_SAVE)

		self.statusBar = wx.StatusBar(self, -1)
		self.statusBar.SetFieldsCount(2)
		self.SetStatusBar(self.statusBar)

		self.framePanel = wx.Panel(self)

		self.plotPanel = wx.Panel(self.framePanel)
		self.plotPanel.figure = Figure()
		self.plotPanel.canvas = FigureCanvas(self.plotPanel, -1, self.plotPanel.figure)
		self.plotPanel.figure.set_facecolor("azure")

		if plotFunc != 'plotDetsSurface':
			if hasattr(self, "cid1"):
				self.plotPanel.canvas.mpl_disconnect(self.cid1)
				self.plotPanel.canvas.mpl_disconnect(self.cid2)
			# Note that event is a MplEvent.  Can disconnect by calling, e.g.,
			# self.plotPanel.canvas.mpl_disconnect(self.cid1)
			self.cid1 = self.plotPanel.canvas.mpl_connect('motion_notify_event', self.UpdateStatusBar)
			if sys.platform != "sunos5":
				self.cid2 = self.plotPanel.canvas.mpl_connect('button_press_event', self.on_ButtonPress)

		self.plotPanel.canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)
		self.plotPanel.toolbar = NavigationToolbar2Wx(self.plotPanel.canvas)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.plotPanel.canvas, 1, wx.GROW)

		if sliders:
			self.userPanel = wx.Panel(self.plotPanel)
			self.makeSliders(self.userPanel, sliders)
			sizer.Add(self.userPanel, 0, wx.EXPAND)
			self.timer = wx.CallLater(100, self.onTimer)

		sizer.Add(self.plotPanel.toolbar, 0, wx.EXPAND)
		self.plotPanel.SetSizer(sizer)
		self.plotPanel.toolbar.Show()

		framePanelSizer = wx.BoxSizer(wx.VERTICAL)
		framePanelSizer.Add(self.plotPanel, 1, wx.EXPAND)
		self.framePanel.SetSizer(framePanelSizer)

		if plotFunc:
			# call the appropriate plot function
			pass

	def doPlot(self):
		if self.plotFunc == None:
			return
		elif self.plotFunc == 'plotDets2D':
			self.plotDets2D()
		elif self.plotFunc == 'plotDets2DwZ':
			self.plotDets2DwZ()
		elif self.plotFunc == 'plotDets1D':
			self.plotDets1D()
		return
	
	
	def onPrintSetup(self,event=None):
		#self.plotPanel.canvas.Printer_Setup(event=event)
		self.printer.pageSetup()

	def onPrintPreview(self,event=None):
		#self.plotPanel.canvas.Printer_Preview(event=event)
		self.printer.previewFigure(self.get_figure())

	def onPrint(self,event=None):
		#self.plotPanel.canvas.Printer_Print(event=event)
		self.printer.printFigure(self.get_figure())

	def onExport(self,event=None):
		""" save figure image to file"""
		file_choices =	"PNG (*.png)|*.png|" \
						"PS (*.ps)|*.ps|" \
						"EPS (*.eps)|*.eps|" \
						"BMP (*.bmp)|*.bmp"

		thisdir  = os.getcwd()
		dlg = wx.FileDialog(self, message='Save Plot Figure as...',
			defaultDir=thisdir, defaultFile='plot.png', wildcard=file_choices, style=wx.SAVE)

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.plotPanel.canvas.print_figure(path,dpi=300)
			if (path.find(thisdir) ==  0):
				path = path[len(thisdir)+1:]
			print 'Saved plot to %s' % path

	def ChangeCursor(self, event):
		self.plotPanel.canvas.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

	def on_ButtonPress(self, event):
		#print "on_ButtonPress: button, event.inaxes:", event.button, event.inaxes
		if event.inaxes:
			self.axNum = -1
			for (i,a) in enumerate(self.axes):
				if a == event.inaxes:
					self.axNum = i
					break

			if event.button == 3:
				# only do this part the first time so the events are only bound once
				if hasattr(self, "popupOneID"):
					#print "   on_ButtonPress: menu events are bound"
					pass
				else:
					#print "   on_ButtonPress: binding menu events"
					self.popupOneID = wx.NewId()
					self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupOneID)
					self.popupTwoID = wx.NewId()
					self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupTwoID)

				# Get the list and list-entry number of the plot uer clicked on 
				(lst, num) = self.axisNum_to_ShowListNum(self.axNum)
				if (lst == None) or (num == None):
					return
				# make a menu
				menu = wx.Menu()
				if lst == 'pos':
					name = self.frame.data[self.dataDim].p[num].fieldName
				else:
					name = self.frame.data[self.dataDim].d[num].fieldName
				menu.Append(self.popupOneID, "Select %s for plotting" % name)
				menu.Append(self.popupTwoID, "Unselect %s for plotting" % name)

				# Popup the menu.  If an item is selected then its handler
				# will be called before PopupMenu returns.
				self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnCaptureLost)
				self.PopupMenu(menu)
				menu.Destroy()

	def OnCaptureLost(self, evt):
		self.Unbind(wx.EVT_MOUSE_CAPTURE_LOST)
		menu.Destroy()
		#print "capture lost"

	def OnPopupOne(self, event):
		plotDimPanel = self.frame.dimPanelList[self.dataDim-1]
		(lst, num) = self.axisNum_to_ShowListNum(self.axNum)
		plotDimPanel.posDetListPanel.list.selectByShowListNum(lst, num, 1)
		# If we don't replot, then axis numbers won't match simply against pos/det showList
		# numbers.  If plotEverything, showlist isn't used, so no need to replot
		if not self.frame.plotEverything:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			self.doPlot()
			self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

	def OnPopupTwo(self, event):
		plotDimPanel = self.frame.dimPanelList[self.dataDim-1]
		(lst, num) = self.axisNum_to_ShowListNum(self.axNum)
		plotDimPanel.posDetListPanel.list.selectByShowListNum(lst, num, 0)
		if not self.frame.plotEverything:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			self.doPlot()
			self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

	def axisNum_to_ShowListNum(self, num):
		if self.frame.plotEverything:
			if num < self.frame.data[self.dataDim].nd:
				return ('det', num)
			else:
				return ('pos', num-self.frame.data[self.dataDim].nd)
		else:
			axNum = 0
			for i in range(len(self.frame.detShowListList[self.dataDim])):
				if (self.frame.detShowListList[self.dataDim][i]):
					if num == axNum: return ('det', i)
					axNum += 1
			for i in range(len(self.frame.posShowListList[self.dataDim])):
				if (self.frame.posShowListList[self.dataDim][i]):
					if num == axNum: return ('pos', i)
					axNum += 1
		return (None, None)

	def UpdateStatusBar(self, event):
		if event.inaxes:
			x, y = event.xdata, event.ydata
			self.statusBar.SetStatusText("x=%.3g, y=%.3g" % (x,y), 0)
		else:
			self.statusBar.SetStatusText("", 0)

	# functions to make this behave like wxmpl.PlotFrame
	def get_figure(self):
		return self.plotPanel.figure

	def draw(self):
		self.plotPanel.canvas.draw()

	def makeSliders(self, panel, sliders):
		mSizer = wx.BoxSizer(wx.VERTICAL)
		panel.SetSizer(mSizer)

		if 'x' in sliders:
			self.indexList[0] = 0
			p = wx.Panel(panel)
			pSizer = wx.BoxSizer(wx.HORIZONTAL)
			self.plot3D_decX = wx.ToggleButton(p, -1, size=(20,-1), label = "x-")
			pSizer.Add(self.plot3D_decX, 0, wx.ALL, 10)
			self.ixSlider = wx.Slider(p, -1, 0, minValue=0, maxValue=self.frame.data[1].curr_pt-1,
				size=(-1,-1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
			self.Bind(wx.EVT_SLIDER, self.ixSliderHandler, self.ixSlider)
			pSizer.Add(self.ixSlider, 1, wx.EXPAND, 10)
			self.plot3D_incX = wx.ToggleButton(p, -1, size=(20,-1), label = "x+")
			pSizer.Add(self.plot3D_incX, 0, wx.ALL, 10)

			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(wx.StaticText(p, -1, "slice width"))
			self.plot3D_dX = wx.SpinCtrl(p, -1, "", size=(60,-1))
			sizer.Add(self.plot3D_dX)
			self.plot3D_dX.SetRange(1, max(1,self.frame.data[1].curr_pt))
			pSizer.Add(sizer, 0, wx.ALL, 10)
			self.Bind(wx.EVT_SPINCTRL, self.plot3D_dXHandler, self.plot3D_dX)

			p.SetSizer(pSizer)
			mSizer.Add(p, 0, wx.EXPAND, 10)

		if 'y' in sliders:
			self.indexList[1] = 0
			p = wx.Panel(panel)
			pSizer = wx.BoxSizer(wx.HORIZONTAL)
			self.plot3D_decY = wx.ToggleButton(p, -1, size=(20,-1), label = "y-")
			pSizer.Add(self.plot3D_decY, 0, wx.ALL, 10)
			self.iySlider = wx.Slider(p, -1, 0, minValue=0, maxValue=self.frame.data[2].curr_pt-1,
				size=(-1,-1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
			self.Bind(wx.EVT_SLIDER, self.iySliderHandler, self.iySlider)
			pSizer.Add(self.iySlider, 1, wx.EXPAND, 10)
			self.plot3D_incY = wx.ToggleButton(p, -1, size=(20,-1), label = "y+")
			pSizer.Add(self.plot3D_incY, 0, wx.ALL, 10)

			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(wx.StaticText(p, -1, "slice width"))
			self.plot3D_dY = wx.SpinCtrl(p, -1, "dY", size=(60,-1))
			sizer.Add(self.plot3D_dY)
			self.plot3D_dY.SetRange(1, max(1,self.frame.data[2].curr_pt))
			pSizer.Add(sizer, 0, wx.ALL, 10)
			self.Bind(wx.EVT_SPINCTRL, self.plot3D_dYHandler, self.plot3D_dY)

			p.SetSizer(pSizer)
			mSizer.Add(p, 0, wx.EXPAND, 10)

		if 'z' in sliders:
			self.indexList[2] = 0
			p = wx.Panel(panel)
			pSizer = wx.BoxSizer(wx.HORIZONTAL)
			self.plot3D_decZ = wx.ToggleButton(p, -1, size=(20,-1), label = "z-")
			pSizer.Add(self.plot3D_decZ, 0, wx.ALL, 10)
			self.izSlider = wx.Slider(p, -1, 0, minValue=0, maxValue=self.frame.data[3].curr_pt-1,
				size=(-1,-1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
			self.Bind(wx.EVT_SLIDER, self.izSliderHandler, self.izSlider)
			pSizer.Add(self.izSlider, 1, wx.EXPAND, 10)
			self.plot3D_incZ = wx.ToggleButton(p, -1, size=(20,-1), label = "z+")
			pSizer.Add(self.plot3D_incZ, 0, wx.ALL, 10)

			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(wx.StaticText(p, -1, "slice width"))
			self.plot3D_dZ = wx.SpinCtrl(p, -1, "dZ", size=(60,-1))
			sizer.Add(self.plot3D_dZ)
			self.plot3D_dZ.SetRange(1, max(1,self.frame.data[3].curr_pt))
			pSizer.Add(sizer, 0, wx.ALL, 10)
			self.Bind(wx.EVT_SPINCTRL, self.plot3D_dZHandler, self.plot3D_dZ)

			p.SetSizer(pSizer)
			mSizer.Add(p, 0, wx.EXPAND, 10)

	def doSliderToggle(self, slider, incToggle, decToggle, sliderVar):
		if incToggle.GetValue():
			if slider.GetValue() < slider.GetMax():
				sliderVar += 1
				slider.SetValue(sliderVar)
				self.replot3D()
			else:
				incToggle.SetValue(0)
		if decToggle.GetValue():
			if slider.GetValue() > slider.GetMin():
				sliderVar -= 1
				slider.SetValue(sliderVar)
				self.replot3D()
			else:
				decToggle.SetValue(0)
		return sliderVar

	def onTimer(self):
		if 'x' in self.sliders:
			self.indexList[0] = self.doSliderToggle(self.ixSlider, self.plot3D_incX, self.plot3D_decX, self.indexList[0])
		if 'y' in self.sliders:
			self.indexList[1] = self.doSliderToggle(self.iySlider, self.plot3D_incY, self.plot3D_decY, self.indexList[1])
		if 'z' in self.sliders:
			self.indexList[2] = self.doSliderToggle(self.izSlider, self.plot3D_incZ, self.plot3D_decZ, self.indexList[2])
		self.timer.Restart(1)

	def izSliderHandler(self, event):
		self.indexList[2] = self.izSlider.GetValue()
		self.replot3D()

	def ixSliderHandler(self, event):
		self.indexList[0] = self.ixSlider.GetValue()
		self.replot3D()

	def iySliderHandler(self, event):
		self.indexList[1] = self.iySlider.GetValue()
		self.replot3D()

	def plot3D_dXHandler(self, event):
		self.widthList[0] = self.plot3D_dX.GetValue()
		self.replot3D()

	def plot3D_dYHandler(self, event):
		self.widthList[1] = self.plot3D_dY.GetValue()
		self.replot3D()

	def plot3D_dZHandler(self, event):
		self.widthList[2] = self.plot3D_dZ.GetValue()
		self.replot3D()

	def replot3D(self):
		frame = self.frame
		fig = self.get_figure()
		fig.clf()
		if self.dataDim == 2:
			self.plotDets1D()
		elif self.dataDim == 3:
			if len(self.sliders) == 1:
				if self.plotFunc == 'plotDets2DwZ':
					self.plotDets2DwZ()
				else:
					self.plotDets2D()
			else:
				self.plotDets1D()
		self.draw()
		self.Show()

	def gatherData(self):
		# Note that we don't want to cache this in the class, because we hope to
		# stay alive while user selects a new data file (during which the class will
		# be deleted and reconstructed).
		dimData = self.frame.data[self.dataDim]
		y = []
		for i in range(len(self.frame.detShowListList[self.dataDim])):
			if (self.frame.detShowListList[self.dataDim][i]) or self.frame.plotEverything:
				y.append(dimData.d[i])
		for i in range(len(self.frame.posShowListList[self.dataDim])):
			if (self.frame.posShowListList[self.dataDim][i]) or self.frame.plotEverything:
				y.append(dimData.p[i])
		return y


	def plotDetsSurface(self):
		self.SetTitle(self.frame.fileName)
		fig = self.get_figure()
		fig.clf()
		dimData = self.frame.data[self.dataDim]
		z = None
		for i in range(len(self.frame.detShowListList[self.dataDim])):
			if (self.frame.detShowListList[self.dataDim][i]) or self.frame.plotEverything:
				z = array(dimData.d[i].data)
				break
		if z == None:
			return

		rows, cols = z.shape
		x, y = meshgrid(arange(0, cols, 1), arange(0, rows, 1))
		ax = axes3d.Axes3D(self.get_figure())
		#ax.plot_wireframe(x,y,z)
		ax.plot_surface(x,y,z, rstride=5, cstride=5)
		self.draw()
		self.Show()


	def calcFontSize(self, rows, columns):
		"""
		(w,h) = self.plotPanel.canvas.GetClientSize()
		(ch) = self.plotPanel.canvas.GetCharHeight()
		f = self.plotPanel.canvas.GetFont()
		(fw, fh) = f.GetPixelSize()
		fhp = f.GetPointSize()
		pixelsPerPoint = float(fh)/fhp
		print "w,h,ch,f=", w,h,ch,f
		"""

		(w,h) = self.plotPanel.canvas.GetClientSize()
		#print "canvas w,h=", w, h
		fact = h/float(500)
		fontSize = 12
		titleFontSize = 12
		if (columns > 2) or (rows > 2):
			fontSize = 10
			titleFontSize = 12
		if (columns > 3) or (rows > 3):
			fontSize = 8
			titleFontSize = 12
		if (columns > 4) or (rows > 4):
			fontSize = 7
			titleFontSize = 10
		if (columns > 5) or (rows > 5):
			fontSize = 6
			titleFontSize = 10
		return (fontSize, titleFontSize)

	def calcPlotSpace(self, rows, columns):
		wSpace = 0.5
		if columns > 2:
			wSpace = .75
		if columns > 3:
			wSpace = 1.

		hSpace = 0.5
		if rows > 3:
			hSpace = .75
		if rows > 5:
			hSpace = 1.
		return (hSpace, wSpace)

	def plotDets2D(self):
		t1 = time.time()
		frame = self.frame
		self.SetTitle(frame.fileName)
		fig = self.get_figure()
		fig.clf()

		if self.frame.plotEverything:
			numPlots = len(frame.detShowListList[self.dataDim]) + len(frame.posShowListList[self.dataDim])
		else:
			numPlots = int(sum(frame.detShowListList[self.dataDim]) + sum(frame.posShowListList[self.dataDim]))
		(rows, columns) = calcRowsColumns(numPlots)

		y = self.gatherData()

		(fontSize, titleFontSize) = self.calcFontSize(rows, columns)

		matplotlib.rcParams['xtick.labelsize'] = fontSize
		matplotlib.rcParams['ytick.labelsize'] = fontSize

		self.axes = []
		for i in range(numPlots):
			if (len(self.axes)==0):
				ax = fig.add_subplot(rows, columns, i+1)
			else:
				if frame.plot2D_withSharedAxes:
					ax = fig.add_subplot(rows, columns, i+1, sharex=self.axes[0], sharey=self.axes[0])
				else:
					ax = fig.add_subplot(rows, columns, i+1)
			self.axes.append(ax)
			dataMinMax = None
			if frame.plot2D_withAxes == False:
				null_locator = NullLocator()
				ax.xaxis.set_major_locator(null_locator)
				ax.yaxis.set_major_locator(null_locator)
			else:
				xLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.xaxis.set_major_locator(xLocator)
				yLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.yaxis.set_major_locator(yLocator)

				(axisData, axisLabel) = select2DAxisData(frame, self.dataDim, self.indexList)
				if (axisLabel[0] != "index" and axisLabel[1] != "index"):
					xMin = axisData[0][0]
					xMax = axisData[0][-1]
					yMin = axisData[1][0]
					yMax = axisData[1][-1]
					dataMinMax=(xMin, xMax, yMin, yMax)
				else :
					# If either axis is index, we make both index, by leaving dataMinMax == None
					# But select2DAxisData() doesn't know this, so we fix
					axisLabel[0] = "index"
					axisLabel[1] = "index"

				if frame.plot2D_withLabels:
					if isBottomPlot(rows, columns, i+1, numPlots):
						ax.set_xlabel(axisLabel[0], fontsize=fontSize)
					if isLeftmostPlot(rows, columns, i+1, numPlots):
						ax.set_ylabel(axisLabel[1], fontsize=fontSize)

			if columns < 4:
				ax.set_title(makeDetLabel(y[i]), fontsize=fontSize)
			else:
				ax.set_title(y[i].fieldName, fontsize=titleFontSize)

			if dimensions(y[i].data) > 2:
				if isinstance(y[i].data, list) or isinstance(y[i].data, tuple):
					y[i].data = numpy.array(y[i].data, copy = 0)
				data = select2DSlice(y[i].data, self.indexList, self.widthList)
				if frame.plot2D_autoAspect:
					im = ax.imshow(data, aspect='auto', extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
				else:
					im = ax.imshow(data, extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
			else:
				if frame.plot2D_autoAspect:
					im = ax.imshow(y[i].data, aspect='auto', extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
				else:
					im = ax.imshow(y[i].data, extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
			if frame.plot2D_withColorBar:
				fig.colorbar(im)

		if frame.showCrossHair:
			multi = xyMultiCursor(fig.canvas, self.axes, color='r', lw=1)

		self.SendSizeEvent()
		"""
		(w,h) = self.plotPanel.canvas.GetClientSize()
		(ch) = self.plotPanel.canvas.GetCharHeight()
		f = self.plotPanel.canvas.GetFont()
		(fw, fh) = f.GetPixelSize()
		fhp = f.GetPointSize()
		pixelsPerPoint = float(fh)/fhp
		print "w,h,ch,f=", w,h,ch,f
		"""
		#fig.subplots_adjust(left=.2, right=.9, bottom=.1, top=.9, wspace=.5, hspace=.5)

		hSpace = 0.5
		wSpace = 0.5
		if (frame.plot2D_withLabels or frame.plot2D_withAxes or frame.plot2D_withSharedAxes) :
			(hSpace, wSpace) = self.calcPlotSpace(rows, columns)
		# The following puts color bars on top of plots
		if not frame.plot2D_withColorBar:
			fig.subplots_adjust(left=.15, right=.9, bottom=.1, top=.9, wspace=wSpace, hspace=hSpace)

		self.draw()
		self.Show()
		plotTime = time.time()-t1
		self.SetStatusText("plot time=%.1f s" % plotTime, 1)

	def plotDets2DwZ(self):
		t1 = time.time()
		frame = self.frame
		self.SetTitle(frame.fileName)
		fig = self.get_figure()
		fig.clf()

		if self.frame.plotEverything:
			numPlots = len(frame.detShowListList[self.dataDim]) + len(frame.posShowListList[self.dataDim])
		else:
			numPlots = int(sum(frame.detShowListList[self.dataDim]) + sum(frame.posShowListList[self.dataDim]))
		(rows, columns) = (2, numPlots)

		y = self.gatherData()

		(fontSize, titleFontSize) = self.calcFontSize(rows, columns)

		matplotlib.rcParams['xtick.labelsize'] = fontSize
		matplotlib.rcParams['ytick.labelsize'] = fontSize

		self.axes = []
		for i in range(numPlots):
			if (len(self.axes)==0):
				ax = fig.add_subplot(rows, columns, i+1)
			else:
				if frame.plot2D_withSharedAxes:
					ax = fig.add_subplot(rows, columns, i+1, sharex=self.axes[0], sharey=self.axes[0])
				else:
					ax = fig.add_subplot(rows, columns, i+1)
			self.axes.append(ax)
			dataMinMax = None
			if frame.plot2D_withAxes == False:
				null_locator = NullLocator()
				ax.xaxis.set_major_locator(null_locator)
				ax.yaxis.set_major_locator(null_locator)
			else:
				xLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.xaxis.set_major_locator(xLocator)
				yLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.yaxis.set_major_locator(yLocator)

				(axisData, axisLabel) = select2DAxisData(frame, self.dataDim, self.indexList)
				if (axisLabel[0] != "index" and axisLabel[1] != "index"):
					xMin = axisData[0][0]
					xMax = axisData[0][-1]
					yMin = axisData[1][0]
					yMax = axisData[1][-1]
					dataMinMax=(xMin, xMax, yMin, yMax)
				else :
					# If either axis is index, we make both index, by leaving dataMinMax == None
					# But select2DAxisData() doesn't know this, so we fix
					axisLabel[0] = "index"
					axisLabel[1] = "index"

				if frame.plot2D_withLabels:
					if isBottomPlot(rows, columns, i+1, numPlots):
						ax.set_xlabel(axisLabel[0], fontsize=titleFontSize)
					if isLeftmostPlot(rows, columns, i+1, numPlots):
						ax.set_ylabel(axisLabel[1], fontsize=titleFontSize)


			if columns < 4:
				ax.set_title(makeDetLabel(y[i]), fontsize=fontSize)
			else:
				ax.set_title(y[i].fieldName, fontsize=titleFontSize)

			if isinstance(y[i].data, list) or isinstance(y[i].data, tuple):
				y[i].data = numpy.array(y[i].data, copy = 0)
			data = select2DSlice(y[i].data, self.indexList, self.widthList)
			if frame.plot2D_autoAspect:
				im = ax.imshow(data, aspect='auto', extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
			else:
				im = ax.imshow(data, extent=dataMinMax, origin = 'lower', interpolation = 'nearest')
			if frame.plot2D_withColorBar:
				fig.colorbar(im)

		################################
		pStyle = ""
		if frame.plot1D_lines: pStyle += "-"
		if frame.plot1D_points: pStyle += "s"

		indexList = [0,0,None]
		widthList = [frame.data[1].curr_pt, frame.data[2].curr_pt, 0]

		self.axes = []
		for i in range(numPlots):
			if (len(self.axes)==0):
				ax = fig.add_subplot(rows, columns, numPlots+i+1)
			else:
				ax = fig.add_subplot(rows, columns, numPlots+i+1, sharex=self.axes[0])
			self.axes.append(ax)

			if frame.plot1D_withAxes == False:
				null_locator = NullLocator()
				ax.xaxis.set_major_locator(null_locator)
				ax.yaxis.set_major_locator(null_locator)
			else:
				xLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.xaxis.set_major_locator(xLocator)
				yLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.yaxis.set_major_locator(yLocator)

			if frame.plot1D_withLabels:
				if rows < 4:
					ax.set_ylabel(makeDetLabel(y[i]), fontsize=fontSize)
				else:
					ax.set_ylabel(y[i].fieldName, fontsize=fontSize)

			if columns < 4:
				ax.set_title(y[i].name, fontsize=fontSize)
			else:
				ax.set_title(y[i].fieldName, fontsize=titleFontSize)

			if isinstance(y[i].data, list) or isinstance(y[i].data, tuple):
				y[i].data = numpy.array(y[i].data, copy = 0)
			data = select1DSlice(y[i].data, indexList, widthList)
			(x, xLabel) = select1DAxisData(frame, self.dataDim, indexList)
			if (x == None):
				x = arange(len(data))
				xLabel = "index"

			# Get the data that contributes to the 2D image in xSelected, ySelected
			(iStart, iEnd) = sliceStartEnd(self.indexList[2], self.widthList[2], data.shape[0])
			xSelected = x[iStart:iEnd+1]
			ySelected = data[iStart:iEnd+1]
			oStyle = pStyle + 'r' # red
			posY = [yy for yy in data if yy > 0]
			ymin = min(posY)

			if frame.plot1D_logY:
				p = ax.semilogy(x, data, pStyle)
				ax.semilogy(xSelected, ySelected, oStyle)
				if ((ymin > 0) and (min(ySelected) > 0)):
					xs, ys = poly_between(xSelected, ymin, ySelected)
					ax.fill(xs, ys, facecolor='red')
			else:
				p = ax.plot(x, data, pStyle)
				ax.plot(xSelected, ySelected, oStyle)
				xs, ys = poly_between(xSelected, 0, ySelected)
				ax.fill(xs, ys, facecolor='red')
			if frame.plot1D_withLabels:
				yticklabels = getp(fig.gca(), 'yticklabels')
				setp(yticklabels, fontsize=fontSize)
				if isBottomPlot(rows, columns, i+1, numPlots):
					ax.set_xlabel(xLabel, fontsize=fontSize)
					xticklabels = getp(fig.gca(), 'xticklabels')
					setp(xticklabels, fontsize=fontSize)


		hSpace = 0.5
		wSpace = 0.5
		if (frame.plot2D_withLabels or frame.plot2D_withAxes or frame.plot2D_withSharedAxes) :
			(hSpace, wSpace) = self.calcPlotSpace(rows, columns)
		fig.subplots_adjust(left=.15, right=.9, bottom=.1, top=.9, wspace=wSpace, hspace=hSpace)

		self.draw()
		self.Show()
		plotTime = time.time()-t1
		self.SetStatusText("plot time=%.1f s" % plotTime, 1)


	def plotDets1D(self):
		t1 = time.time()
		frame = self.frame
		self.SetTitle(frame.fileName)
		fig = self.get_figure()
		fig.clf()

		if self.frame.plotEverything:
			numPlots = len(frame.detShowListList[self.dataDim]) + len(frame.posShowListList[self.dataDim])
		else:
			numPlots = int(sum(frame.detShowListList[self.dataDim]) + sum(frame.posShowListList[self.dataDim]))
		(rows, columns) = calcRowsColumns(numPlots)

		y = self.gatherData()

		# (See matplotlib.lines.Line2D)
		pStyle = ""
		if frame.plot1D_lines: pStyle += "-"
		if frame.plot1D_points: pStyle += "s"

		(fontSize, titleFontSize) = self.calcFontSize(rows, columns)

		self.axes = []
		for i in range(numPlots):
			if (len(self.axes)==0):
				ax = fig.add_subplot(rows, columns, i+1)
			else:
				if frame.plot1D_withSharedAxes:
					ax = fig.add_subplot(rows, columns, i+1, sharex=self.axes[0], sharey=self.axes[0])
				else:
					ax = fig.add_subplot(rows, columns, i+1, sharex=self.axes[0])
			self.axes.append(ax)

			if frame.plot1D_withAxes == False:
				null_locator = NullLocator()
				ax.xaxis.set_major_locator(null_locator)
				ax.yaxis.set_major_locator(null_locator)
			else:
				xLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.xaxis.set_major_locator(xLocator)
				yLocator = MaxNLocator(nbins=5, steps=[1, 2, 5, 10])
				ax.yaxis.set_major_locator(yLocator)

			if frame.plot1D_withLabels:
				if rows < 4:
					ax.set_ylabel(makeDetLabel(y[i]), fontsize=fontSize)
				else:
					ax.set_ylabel(y[i].fieldName, fontsize=fontSize)

			if columns < 4:
				ax.set_title(y[i].name, fontsize=fontSize)
			else:
				ax.set_title(y[i].fieldName, fontsize=titleFontSize)

			if dimensions(y[i].data) > 1:
				if isinstance(y[i].data, list) or isinstance(y[i].data, tuple):
					y[i].data = numpy.array(y[i].data, copy = 0)
				data = select1DSlice(y[i].data, self.indexList, self.widthList)
			else:
				data = y[i].data

			(x, xLabel) = select1DAxisData(frame, self.dataDim, self.indexList)
			if (x == None):
				x = arange(len(data))
				xLabel = "index"

			if frame.plot1D_logY:
				p = ax.semilogy(x, data, pStyle)
			else:
				p = ax.plot(x, data, pStyle)

			if frame.plot1D_withLabels:
				yticklabels = getp(fig.gca(), 'yticklabels')
				setp(yticklabels, fontsize=fontSize)
				xticklabels = getp(fig.gca(), 'xticklabels')
				setp(xticklabels, fontsize=fontSize)
				if isBottomPlot(rows, columns, i+1, numPlots):
					ax.set_xlabel(xLabel, fontsize=fontSize)

		(hSpace, wSpace) = self.calcPlotSpace(rows, columns)
		fig.subplots_adjust(left=.15, right=.9, bottom=.1, top=.9, wspace=wSpace, hspace=hSpace)

		if frame.showCrossHair:
			multi = MultiCursor(fig.canvas, self.axes, color='r', lw=1)
		self.draw()
		self.Show()
		plotTime = time.time()-t1
		self.SetStatusText("plot time=%.1f s" % plotTime, 1)

#####################################################################################
class PlotDimPanel(wx.Panel):
	def __init__(self, parent, frame, id, **kwds):
		wx.Panel.__init__(self, parent, id, **kwds)
		self.frame = frame
		self.data = frame.data
		self.dataDim = id
		self.dim = self.data[self.dataDim]
		self.detShowList = frame.detShowListList[self.dataDim]
		self.posShowList = frame.posShowListList[self.dataDim]
		self.posAxisList = frame.posAxisList

		text1 = wx.StaticText(self, -1, "%dD data"%self.dataDim)
		text1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
		dimText = "%d" % self.data[1].curr_pt
		for i in range(2, self.dataDim+1):
			dimText = dimText + ("x%d" % self.data[i].curr_pt)
		text2 = wx.StaticText(self, -1, "%s data points, %d detectors" % (dimText, self.dim.nd))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(text1, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
		sizer.Add(text2, 0, wx.LEFT|wx.BOTTOM|wx.RIGHT, 10)

		self.posDetListPanel = PosDetListPanel(self)
		sizer.Add(self.posDetListPanel, 1, wx.EXPAND|wx.ALL, 5)

		if (self.dataDim == 1):
			plotButton = wx.Button(self, -1, "Plot")
			self.Bind(wx.EVT_BUTTON, self.plot1D, plotButton)
			sizer.Add(plotButton, 0, wx.ALL, 10)

		elif (self.dataDim == 2):
			p = wx.Panel(self)

			# 2D plot buttons
			p2D = wx.Panel(p)
			plotButton = wx.Button(p2D, -1, "Plot")
			plotSurfaceButton = wx.Button(p2D, -1, "PlotSurface")

			p2DSizer = wx.BoxSizer(wx.VERTICAL)
			p2DSizer.Add(plotButton)
			p2DSizer.Add(plotSurfaceButton)
			p2D.SetSizer(p2DSizer)

			self.Bind(wx.EVT_BUTTON, self.plot2D, plotButton)
			self.Bind(wx.EVT_BUTTON, self.plotSurface, plotSurfaceButton)

			# 1D plot buttons (show slice of 2D data)
			p1D = wx.Panel(p)
			plotXButton = wx.Button(p1D, -1, "Plot Column")
			plotYButton = wx.Button(p1D, -1, "Plot Row")

			p1DSizer = wx.BoxSizer(wx.VERTICAL)
			p1DSizer.Add(plotXButton)
			p1DSizer.Add(plotYButton)
			p1D.SetSizer(p1DSizer)

			self.Bind(wx.EVT_BUTTON, self.plot2D_X, plotXButton)
			self.Bind(wx.EVT_BUTTON, self.plot2D_Y, plotYButton)

			pSizer = wx.BoxSizer(wx.HORIZONTAL)
			pSizer.Add(p2D, 0, wx.ALL, 10)
			pSizer.Add(p1D, 0, wx.ALL, 10)
			p.SetSizer(pSizer)
			sizer.Add(p)

		elif (self.dataDim == 3):
			p = wx.Panel(self)

			# 2D plot buttons (slice of 3D data)
			p2D = wx.Panel(p)
			plotXYButton = wx.Button(p2D, -1, "Plot XY plane")
			plotXZButton = wx.Button(p2D, -1, "Plot XZ plane")
			plotYZButton = wx.Button(p2D, -1, "Plot YZ plane")
			plotXYwZButton = wx.Button(p2D, -1, "Plot XY plane/Z")

			p2DSizer = wx.BoxSizer(wx.VERTICAL)
			p2DSizer.Add(plotXYButton)
			p2DSizer.Add(plotXZButton)
			p2DSizer.Add(plotYZButton)
			p2DSizer.Add(plotXYwZButton)
			p2D.SetSizer(p2DSizer)

			self.Bind(wx.EVT_BUTTON, self.plot3D_XY, plotXYButton)
			self.Bind(wx.EVT_BUTTON, self.plot3D_XZ, plotXZButton)
			self.Bind(wx.EVT_BUTTON, self.plot3D_YZ, plotYZButton)
			self.Bind(wx.EVT_BUTTON, self.plot3D_XYwZ, plotXYwZButton)

			# 1D plot buttons (slice of slice of 3D data)
			p1D = wx.Panel(p)
			plotXButton = wx.Button(p1D, -1, "Plot X vector")
			plotYButton = wx.Button(p1D, -1, "Plot Y vector")
			plotZButton = wx.Button(p1D, -1, "Plot Z vector")

			p1DSizer = wx.BoxSizer(wx.VERTICAL)
			p1DSizer.Add(plotXButton)
			p1DSizer.Add(plotYButton)
			p1DSizer.Add(plotZButton)
			p1D.SetSizer(p1DSizer)

			self.Bind(wx.EVT_BUTTON, self.plot3D_X, plotXButton)
			self.Bind(wx.EVT_BUTTON, self.plot3D_Y, plotYButton)
			self.Bind(wx.EVT_BUTTON, self.plot3D_Z, plotZButton)

			pSizer = wx.BoxSizer(wx.HORIZONTAL)
			pSizer.Add(p2D, 0, wx.ALL, 10)
			pSizer.Add(p1D, 0, wx.ALL, 10)
			p.SetSizer(pSizer)
			sizer.Add(p)

		self.SetSizer(sizer)
		self.maybePlot()

	# If autoUpdatePlots is True, then do plots in all existing plotFrames
	def maybePlot(self):
		frame = self.frame
		if not frame.autoUpdatePlots:
			return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if (self.dataDim == 1) and frame.plotFrame1D:
			self.plot1D()
		elif (self.dataDim == 2):
			if frame.plotFrame2D: self.plot2D()
			if frame.plotFrame2D_X: self.plot2D_X()
			if frame.plotFrame2D_Y: self.plot2D_Y()

		elif (self.dataDim == 3):
			if frame.plotFrame3D_XY: self.plot3D_XY()
			if frame.plotFrame3D_XYwZ: self.plot3D_XYwZ()
			if frame.plotFrame3D_XZ: self.plot3D_XZ()
			if frame.plotFrame3D_YZ: self.plot3D_YZ()
			if frame.plotFrame3D_X: self.plot3D_X()
			if frame.plotFrame3D_Y: self.plot3D_Y()
			if frame.plotFrame3D_Z: self.plot3D_Z()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def noData(self):
		nodat = False
		if (self.dim == None) or (len(self.detShowList)+len(self.posShowList) == 0):
			nodat = True
		elif self.frame.plotEverything:
			nodat = False
		elif (sum(self.detShowList)+sum(self.posShowList))==0:
			nodat = True
		if nodat:
			self.frame.SetStatusText("Please select something to plot, or choose Options/Plot Everything")
			return True
		return False

	def plot1D(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame1D:
			frame.plotFrame1D = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D')
		frame.plotFrame1D.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot2D(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame2D:
			frame.plotFrame2D = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets2D')
		frame.plotFrame2D.plotDets2D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot2D_X(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame2D_X:
			frame.plotFrame2D_X = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D', sliders=['y'])
		frame.plotFrame2D_X.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot2D_Y(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame2D_Y:
			frame.plotFrame2D_Y = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D', sliders=['x'])
		frame.plotFrame2D_Y.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_XY(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_XY:
			frame.plotFrame3D_XY = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets2D', sliders=['z'])
		frame.plotFrame3D_XY.plotDets2D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_XYwZ(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_XYwZ:
			frame.plotFrame3D_XYwZ = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets2DwZ', sliders=['z'])
		frame.plotFrame3D_XYwZ.plotDets2DwZ()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_XZ(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_XZ:
			frame.plotFrame3D_XZ = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets2D', sliders=['y'])
		frame.plotFrame3D_XZ.plotDets2D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_YZ(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_YZ:
			frame.plotFrame3D_YZ = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets2D', sliders=['x'])
		frame.plotFrame3D_YZ.plotDets2D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_X(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_X:
			frame.plotFrame3D_X = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D', sliders=['y', 'z'])
		frame.plotFrame3D_X.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_Y(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_Y:
			frame.plotFrame3D_Y = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D', sliders=['x', 'z'])
		frame.plotFrame3D_Y.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plot3D_Z(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrame3D_Z:
			frame.plotFrame3D_Z = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDets1D', sliders=['x', 'y'])
		frame.plotFrame3D_Z.plotDets1D()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def plotSurface(self, event=None):
		frame = self.frame
		if self.noData(): return
		frame.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		if not frame.plotFrameSurface:
			frame.plotFrameSurface = CanvasFrame(frame, -1, frame, self.dataDim, plotFunc='plotDetsSurface')
		frame.plotFrameSurface.plotDetsSurface()
		frame.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

###########################################################################
# PosDetList
class PosDetList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, grandparent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

		self.frame = grandparent.frame
		self.dim = grandparent.dim
		self.dataDim = grandparent.dataDim
		self.grandparent = grandparent

		self.saved_posShowList = self.frame.fullPosShowListList[self.dataDim]
		self.saved_detShowList = self.frame.fullDetShowListList[self.dataDim]
		self.saved_posAxisList = self.frame.fullPosAxisList
		self.posShowList = self.frame.posShowListList[self.dataDim]
		self.detShowList = self.frame.detShowListList[self.dataDim]
		self.itemDataMap = {}

		self.InsertColumn(0, "axis")
		self.InsertColumn(1, "plot")
		self.InsertColumn(2, "field")
		self.InsertColumn(3, "PV name")
		self.InsertColumn(4, "Description {from env}")

		# fill list
		i = 0
		axisValue = self.saved_posAxisList[self.dataDim]
		for pos in self.dim.p:
			axisText = ""
			if axisValue == pos.number:
				axisText = "  *"
				self.frame.posAxisList[self.dataDim] = i
			plotValue = self.saved_posShowList[pos.number]
			self.posShowList.append(plotValue)
			plotText = ""
			if plotValue: plotText = "  *"
			self.itemDataMap[i] = (axisText, plotText, pos.fieldName, pos.name, pos.desc, i+pIdOffset, pos.number)
			i += 1			

		axisText = ""
		if axisValue == AXIS_IS_INDEX:
			axisText = "  *"
			self.frame.posAxisList[self.dataDim] = AXIS_IS_INDEX
		self.itemDataMap[i] = (axisText, "", "index", "", "", i+pIdOffset, 0)
		i += 1

		self.itemDataMap[i] = ("", "", "", "", "", 0, 0)
		i += 1
		self.firstDet = i
		for (j,det) in enumerate(self.dim.d):
			value = self.saved_detShowList[det.number]
			self.detShowList.append(value)
			plotText = ""
			if value: plotText = "  *"
			self.itemDataMap[i] = ("", plotText, det.fieldName, det.name, det.desc, j, det.number)
			i += 1
		self.numItems = i	# save this

		items = self.itemDataMap.items()
		for (i, data) in items:
			self.InsertStringItem(i, data[0])
			for j in range(1,5):
				self.SetStringItem(i, j, data[j])
			# low 16 bits: index into data array;  high 16 bits: positioner or detector number (index into full list)
			self.SetItemData(i, data[5] + (data[6]<<16)) 

		self.SetColumnWidth(0, 35)
		self.SetColumnWidth(1, 35)
		for i in range(2,5):
			self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		self.columnRightBound = []
		b = 0
		for i in range(5):
			b += self.GetColumnWidth(i)
			self.columnRightBound.append(b)

		self.Bind(wx.EVT_LEFT_DOWN, self.On_EVT_LEFT_DOWN)
		self.Bind(wx.EVT_LIST_KEY_DOWN, self.On_KEY_DOWN, self)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)
		self.selectedItems = set()
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self)
		self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self)

		# for wxMSW
		self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

		# for wxGTK
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

		(junk,height) = self.GetItemPosition(self.numItems-1)
		(x,y) = self.GetItemPosition(self.numItems-2)
		height += height-y

		width = 0
		for i in range(5):
			width += self.GetColumnWidth(i)
		#print "PosDetList: summed width, height=", width, height

		# Without this, list panel starts out in very small space, but with it,
		# scroll panels don't have scroll bars at all (even after a user resize
		# that makes them necessary) on Solaris.
		if sys.platform == "win32":
			self.SetInitialSize((width+5, height+5))

	def whichColumn(self, x):
		for i, b in enumerate(self.columnRightBound):
			if x <= b: return i
			
	def getColumnText(self, index, col):
		item = self.GetItem(index, col)
		return item.GetText()

	def On_KEY_DOWN(self, event):
		#print "On_KEY_DOWN\n"
		#print "dir(event)=", dir(event)
		event.Skip() # so other handlers will see the event

	def OnItemSelected(self, event):
		self.selectedItems.add(event.m_itemIndex)
		event.Skip()

	def OnItemDeselected(self, event):
		if event.m_itemIndex in self.selectedItems:
			self.selectedItems.remove(event.m_itemIndex)
		event.Skip()

	def OnItemActivated(self, event):
		item = event.m_itemIndex
		#print "OnItemActivated:"
		# Show all positioner or detector info?

	def OnItemDelete(self, event):
		#print "OnItemDelete\n"
		pass

	def OnColBeginDrag(self, event):
		#print "OnColBeginDrag\n"
		## Show how to not allow a column to be resized
		col = event.GetColumn()
		if col < 2:
			event.Veto()

	def selectByShowListNum(self, lst, num, plotFlag=1):
		if lst == 'pos':
			if num < self.dim.np:
				item = num
		else:
			item = num + self.dim.np + 2
		self.setSelectedForPlot(item, plot=plotFlag)

	def setSelectedForPlot(self, item, plot=None):
		itemData = self.GetItemData(item)
		itemNumber = itemData & 0xff
		posDetNumber = itemData >> 16
		#print "setSelectedForPlot: item %d, itemData=0x%x" % (item, itemData)
		if itemNumber >= pIdOffset:
			# positioner or index
			thisId = itemNumber - pIdOffset
			thisList = self.posShowList
			saveList = self.saved_posShowList
			thisSaveListElement = posDetNumber
		elif itemNumber < self.dim.nd:
			# detector
			thisId = itemNumber
			thisList = self.detShowList
			saveList = self.saved_detShowList
			thisSaveListElement = posDetNumber
		else:
			return

		if plot == None:
			# toggle plottable flag
			thisList[thisId] = not thisList[thisId]
		else:
			thisList[thisId] = plot
		saveList[thisSaveListElement] = thisList[thisId]
		if thisList[thisId]:
			self.SetStringItem(item, 1, "  *")
		else:
			self.SetStringItem(item, 1, "")


	def On_EVT_LEFT_DOWN(self, event):
		#print "On_EVT_LEFT_DOWN"
		x = event.GetX()
		y = event.GetY()
		item, flags = self.HitTest((x, y))
		if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
			#print "item, flags=", item, flags
			col = self.whichColumn(x)
			if col == 0 and item <= self.dim.np:
				for i in range(self.dim.np+1):
					self.SetStringItem(i, 0, "")
				text = self.getColumnText(item, 0)
				self.SetStringItem(item, 0, "  *")
				self.frame.posAxisList[self.dataDim] = item
				itemData = self.GetItemData(item)
				posDetNumber = itemData >> 16
				self.saved_posAxisList[self.dataDim] = posDetNumber
				self.grandparent.maybePlot()
			elif item in [self.dim.np, self.dim.np+1]:
				pass
			elif col == 1:
				self.setSelectedForPlot(item)
				self.grandparent.maybePlot()
		event.Skip()


	def OnRightClick(self, event):
		#print "OnRightClick %s\n" % self.GetItemText(self.currentItem)

		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.popupID5 = wx.NewId()
			self.popupID6 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

		# make a menu
		menu = wx.Menu()
		# add some items
		menu.Append(self.popupID1, "Select for plotting")
		menu.Append(self.popupID2, "Unselect for plotting")
		menu.Append(self.popupID3, "Hide")
		menu.Append(self.popupID4, "Show all")
		menu.Append(self.popupID5, "extra1")
		menu.Append(self.popupID6, "extra2")

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()


	def OnPopupOne(self, event):
		#print "OnPopupOne"
		#print "selected items:", self.selectedItems
		for item in self.selectedItems:
			self.setSelectedForPlot(item, True)
		self.grandparent.maybePlot()

	def OnPopupTwo(self, event):
		#print "OnPopupTwo"
		#print "selected items:", self.selectedItems
		for item in self.selectedItems:
			self.setSelectedForPlot(item, False)
		self.grandparent.maybePlot()

	def OnPopupThree(self, event):
		print "OnPopupThree: not implemented"
		#self.ClearAll()
		#wx.CallAfter(self.PopulateList)

	def OnPopupFour(self, event):
		print "OnPopupFour: not implemented"

	def OnPopupFive(self, event):
		print "OnPopupFive: not implemented"

	def OnPopupSix(self, event):
		print "OnPopupSix: not implemented"



class PosDetListPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.list = PosDetList(self, parent)
		self.sizer.Add(self.list, 1, wx.EXPAND)
		self.SetSizer(self.sizer)
		
###########################################################################
# Environment PV list
class EnvList(wx.ListCtrl, listmix.ColumnSorterMixin, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, dict):
		wx.ListCtrl.__init__(
			self, parent, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		self.itemDataMap = {}

		self.InsertColumn(0, "PV name")
		self.InsertColumn(1, "description")
		self.InsertColumn(2, "value")
		self.InsertColumn(3, "units")
		self.InsertColumn(4, "EPICS type")

		# fill list
		ourKeys = dict['ourKeys']  # Keys made by readMDA, not originally in file
		i = 0
		for key in dict.keys():
			if (key not in ourKeys):
				value = dict[key][2]
				if (type(value) == type([]) and (len(value)==1)):
					value = value[0]
				self.itemDataMap[i] = (
					str(key).rstrip(),
					str(dict[key][0]).rstrip(),
					str(value).rstrip(),
					str(dict[key][1]).rstrip(),
					mda.EPICS_types(dict[key][3])
				)
				i += 1

		self.itemDataMap[i] = (
			"PV name",
			"description",
			"value",
			"units",
			"EPICS type"
		)
		self.lastKey = i

		items = self.itemDataMap.items()
		for (i, data) in items:
			self.InsertStringItem(i, data[0])
			self.SetStringItem(i, 1, data[1])
			self.SetStringItem(i, 2, data[2])
			self.SetStringItem(i, 3, data[3])
			self.SetStringItem(i, 4, data[4])
			self.SetItemData(i, i)
		self.SetItemTextColour(self.lastKey, "red")

		listmix.ColumnSorterMixin.__init__(self, 5)

		for i in range(5):
			self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

	def GetListCtrl(self):
		return self

	def GetColumnSorter(self):
		"""Returns a callable object to be used for comparing column values when sorting."""
		return self.__ColumnSorter

	def __ColumnSorter(self, key1, key2):
		col = self._col
		ascending = self._colSortFlag[col]
		if key1 == self.lastKey:
			return 1
		if key2 == self.lastKey:
			return -1

		item1 = self.itemDataMap[key1][col]
		item2 = self.itemDataMap[key2][col]

		cmpVal = cmpStringsWithEmbeddedNumbers(item1, item2)
		if cmpVal == 0:
			item1 = self.itemDataMap[key1][0]
			item2 = self.itemDataMap[key2][0]
			#cmpVal = locale.strcoll(str(item1), str(item2))
			cmpVal = cmpStringsWithEmbeddedNumbers(item1, item2)

			if cmpVal == 0:
				cmpVal = key1 < key2

		if ascending:
			return cmpVal
		else:
			return -cmpVal

class EnvListPanel(wx.Panel):
   def __init__(self, parent, dict):
		wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SUNKEN)
		#wx.Panel.__init__(self, parent, -1)
		sizer = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, -1, "Scan-environment PV's: -- Lift sash to view -- Click column head to sort")
		sizer.Add(title, 0, wx.ALL, 5)
		self.list = EnvList(self, dict)
		sizer.Add(self.list, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
		self.SetSizer(sizer)

###########################################################################
# Directory list, for "Survey MDA Files"

def num(s):
	if s.endswith('k'):
		return float(s[:-1])*1024
	elif s.endswith('M'):
		return float(s[:-1])*1024*1024
	else:
		return float(s)

def makeFileDescription(f,d):
	fileDate = time.strftime(TIME_FORMAT, time.localtime(os.stat(f).st_mtime))
	size = os.stat(f).st_size
	if size > 1024*1024:
		sizeStr = "%.1fM" % (float(size)/(1024*1024))
	elif size > 1024:
		sizeStr = "%.1fk" % (float(size)/1024)
	else:
		sizeStr = str(size)

	acq_dimensions = d[0]['acquired_dimensions']
	dimensions = d[0]['dimensions']
	dimensionStr = ""
	detectorStr = ""
	for j in range(len(dimensions)):
		if dimensionStr != "":
			dimensionStr += ", "
		dimensionStr += "%d" % (acq_dimensions[j])
		if detectorStr != "":
			detectorStr += ", "
		detectorStr += "%d" % (d[j+1].nd)
	
	fileType = str(d[0]['rank'])+"D"
	return (sizeStr, fileType, dimensionStr, detectorStr, fileDate)

class DirList(wx.ListCtrl, listmix.ColumnSorterMixin, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, user, directory):
		wx.ListCtrl.__init__(
			self, parent, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
		listmix.ListCtrlAutoWidthMixin.__init__(self)
		self.frame = user
		self.itemDataMap = {}
		self.listedFiles = []
		self.mostRecentFileTime = 0.0

		self.user = user
		self.directory = directory
		self.InsertColumn(0, "File name")
		self.InsertColumn(1, "size")
		self.InsertColumn(2, "type")
		self.InsertColumn(3, "dimensions")
		self.InsertColumn(4, "detectors")
		self.InsertColumn(5, "date last modified")

		# fill list
		i = 0
		files = os.listdir(directory)
		for f in files:
			if f.find(".mda") != -1:
				d = mda.skimMDA(f, verbose=True)
				if d != None:
					(sizeStr, fileType, dimensionStr, detectorStr, fileDate) = makeFileDescription(f, d)
					self.itemDataMap[i] = (f, sizeStr, fileType, dimensionStr, detectorStr, fileDate)
					self.listedFiles.append(f)
					self.mostRecentFileTime = max(self.mostRecentFileTime, os.stat(f).st_mtime)
					i += 1
		# Add one last item duplicating column-head text, because that doesn't get
		# autosized
		self.columnHeadItem = i
		self.itemDataMap[i] = (
			"File name",
			"size",
			"type",
			"dimensions",
			"detectors",
			"date last modified"
		)
		self.lastKey = i

		# fill list
		items = self.itemDataMap.items()
		for (i, data) in items:
			self.InsertStringItem(i, data[0])
			self.SetStringItem(i, 1, data[1])
			self.SetStringItem(i, 2, data[2])
			self.SetStringItem(i, 3, data[3])
			self.SetStringItem(i, 4, data[4])
			self.SetStringItem(i, 5, data[5])
			self.SetItemData(i, i)
		self.SetItemTextColour(self.columnHeadItem, "red")

		listmix.ColumnSorterMixin.__init__(self, 6)

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemSelected, self)

		for i in range(5):
			self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		self.timer = wx.CallLater(DIRLIST_TIME_MS, self.onTimer)

	def onTimer(self):
		""" Check current directory for files more recent than self.mostRecentFileTime.  If any, add them to list,
		and update self.mostRecentFileTime with most recent of the new files.  If an updated file is currently being
		displayed (i.e., if name == self.frame.fileName), then update display.
		"""
		files = os.listdir(self.directory)
		mostRecentNewFileTime = self.mostRecentFileTime
		for f in files:
			fileTimeSecs = os.stat(f).st_mtime
			if fileTimeSecs > self.mostRecentFileTime:
				mostRecentNewFileTime = max(mostRecentNewFileTime, fileTimeSecs)
				if f.find(".mda") != -1:
					d = mda.skimMDA(f)
					if d != None:
						if f in self.listedFiles:
							if self.frame.autoUpdatePlots:
								fullPathName = os.path.join(self.directory, f)
								if fullPathName == self.frame.fileName:
									#self.user.readData(fullPathName)
									self.frame.data = mda.readMDA(self.frame.fileName, maxdim=self.frame.maxDataDim, verbose=0, showHelp=0, outFile=None, useNumpy=False, readQuick=True)
									for dimPanel in self.frame.dimPanelList:
										dimPanel.maybePlot()
						else:
							self.lastKey += 1
							i = self.lastKey
							(sizeStr, fileType, dimensionStr, detectorStr, fileDate) = makeFileDescription(f, d)
							self.itemDataMap[i] = (f, sizeStr, fileType, dimensionStr, detectorStr, fileDate)
							self.listedFiles.append(f)
							self.mostRecentFileTime = max(self.mostRecentFileTime, fileTimeSecs)
							# update list
							self.InsertStringItem(i, f)
							self.SetStringItem(i, 1, sizeStr)
							self.SetStringItem(i, 2, fileType)
							self.SetStringItem(i, 3, dimensionStr)
							self.SetStringItem(i, 4, detectorStr)
							self.SetStringItem(i, 5, fileDate)
							self.SetItemData(i, i)
		self.mostRecentFileTime = mostRecentNewFileTime

		self.timer.Restart(DIRLIST_TIME_MS)

	def OnItemSelected(self, event):
		item = event.m_itemIndex
		#print "OnItemSelected: item=%d %s" % (self.currentItem, self.GetItemText(self.currentItem))
		if item != self.columnHeadItem:
			path = os.path.join(self.directory, self.GetItemText(item))
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			self.user.readData(path)
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def GetListCtrl(self):
		return self

	def GetColumnSorter(self):
		"""Returns a callable object to be used for comparing column values when sorting."""
		return self.__ColumnSorter

	def __ColumnSorter(self, key1, key2):
		col = self._col
		ascending = self._colSortFlag[col]
		if key1 == self.columnHeadItem:
			return 1
		if key2 == self.columnHeadItem:
			return -1

		item1 = self.itemDataMap[key1][col]
		item2 = self.itemDataMap[key2][col]

		if col == 0 or col == 2:
			#cmpVal = locale.strcoll(str(item1), str(item2))
			cmpVal = cmpStringsWithEmbeddedNumbers(str(item1), str(item2))
		elif col == 1:
			# mind k and M
			f1 = num(item1)
			f2 = num(item2)
			if f1 > f2:
				cmpVal = 1
			elif f1 < f2:
				cmpVal = -1
			else:
				cmpVal = 0
			
		elif col == 3 or col == 4:
			# mind number of elements
			cmpVal = 0
			list1 = item1.split(',')
			list2 = item2.split(',')
			if len(list1) > len(list2):
				cmpVal = 1
			elif len(list1) < len(list2):
				cmpVal = -1
			else:
				for i in range(len(list1)):
					int1 = int(list1[i])
					int2 = int(list2[i])
					if int1 > int2:
						cmpVal =  1
						break
					elif int1 < int2:
						cmpVal = -1
						break
		elif col == 5:
			seconds1 = time.mktime(time.strptime(item1,TIME_FORMAT))
			seconds2 = time.mktime(time.strptime(item2,TIME_FORMAT))
			cmpVal = 0
			if (seconds1 > seconds2): cmpVal = 1
			if (seconds1 < seconds2): cmpVal = -1

		if cmpVal == 0:
			item1 = self.itemDataMap[key1][0]
			item2 = self.itemDataMap[key2][0]
			#cmpVal = locale.strcoll(str(item1), str(item2))
			cmpVal = cmpStringsWithEmbeddedNumbers(str(item1), str(item2))

			if cmpVal == 0:
				cmpVal = key1 < key2

		if ascending:
			return cmpVal
		else:
			return -cmpVal

class DirListFrame(wx.Frame):
	def __init__(self, parent, directory):
		wx.Frame.__init__(self, parent, -1, "MDA Survey", size=(500,-1))
		self.frame = parent
		panel = wx.Panel(self, -1, style=wx.WANTS_CHARS)
		sizer = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(panel, -1, "MDA files in: %s" % directory)
		title.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
		sizer.Add(title, 0, wx.ALL, 5)
		helpTxt1 = wx.StaticText(panel, -1, "Click column head to sort.")
		sizer.Add(helpTxt1, 0, wx.LEFT, 5)
		helpTxt2 = wx.StaticText(panel, -1, "Double-click on a file to read it into MDA Explorer")
		sizer.Add(helpTxt2, 0, wx.LEFT|wx.BOTTOM, 5)
		panel.list = DirList(panel, parent, directory)
		sizer.Add(panel.list, 1, wx.EXPAND)
		panel.SetSizer(sizer)

###########################################################################

def setImages(tree, branch, il):
	(child, cookie) = tree.GetFirstChild(branch)
	if child.IsOk():
		tree.SetItemImage(branch, il[0], wx.TreeItemIcon_Normal)
		tree.SetItemImage(branch, il[1], wx.TreeItemIcon_Expanded)
	else:
		tree.SetItemImage(branch, il[2], wx.TreeItemIcon_Normal)
	while child.IsOk():
		setImages(tree, child, il)
		(child, cookie) = tree.GetNextChild(branch, cookie)

class MDA_TreeCtrlPanel(wx.Panel):
	def __init__(self, parent, filename):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		self.Bind(wx.EVT_SIZE, self.OnSize)

		tID = wx.NewId()

		tree = wx.TreeCtrl(self, tID, wx.DefaultPosition, wx.DefaultSize,
			wx.TR_DEFAULT_STYLE)
		self.tree = tree
		#font = wx.Font(pointSize, family, style, weight, underline, face)
		font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Courier New")
		tree.SetFont(font)

		isz = (16,16)
		il = wx.ImageList(isz[0], isz[1])
		fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
		fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
		fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
		tree.SetImageList(il)
		self.il = il

		root = mdaTree.readMDA_FillTree(filename, maxdim=4, tree=tree)
		if root:
			myIL = [fldridx, fldropenidx, fileidx]
			setImages(tree, root, myIL)
			tree.Expand(root)

		#self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, tree)
		#self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, tree)
		#self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, tree)
		#self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, tree)
		#self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, tree)
		#self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, tree)

		#tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		#tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)


	def OnRightDown(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		if item:
			#print "OnRightClick: %s, %s, %s" % (self.tree.GetItemText(item), type(item), item.__class__)
			self.tree.SelectItem(item)


	def OnRightUp(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		if item:
			#print "OnRightUp: %s (manually starting label edit)" % self.tree.GetItemText(item)
			self.tree.EditLabel(item)

	def OnBeginEdit(self, event):
		#print "OnBeginEdit"
		# show how to prevent edit...
		item = event.GetItem()
		if item and self.tree.GetItemText(item) == "The Root Item":
			wx.Bell()
			#print "You can't edit this one..."

			# Lets just see what's visible of its children
			cookie = 0
			root = event.GetItem()
			(child, cookie) = self.tree.GetFirstChild(root)

			while child.IsOk():
				#print "Child [%s] visible = %d" % (self.tree.GetItemText(child), self.tree.IsVisible(child))
				(child, cookie) = self.tree.GetNextChild(root, cookie)

			event.Veto()


	def OnEndEdit(self, event):
		#print "OnEndEdit: %s %s" % (event.IsEditCancelled(), event.GetLabel())
		# show how to reject edit, we'll not allow any digits
		for x in event.GetLabel():
			if x in string.digits:
				#print "You can't enter digits..."
				event.Veto()
				return


	def OnSize(self, event):
		w,h = self.GetClientSizeTuple()
		self.tree.SetDimensions(0, 0, w, h)


	def OnItemExpanded(self, event):
		item = event.GetItem()
		if item:
			#print "OnItemExpanded: %s" % self.tree.GetItemText(item)
			pass

	def OnItemCollapsed(self, event):
		item = event.GetItem()
		if item:
			#print "OnItemCollapsed: %s" % self.tree.GetItemText(item)
			pass

	def OnSelChanged(self, event):
		self.item = event.GetItem()
		if self.item:
			#print "OnSelChanged: %s" % self.tree.GetItemText(self.item)
			if wx.Platform == '__WXMSW__':
				#print "BoundingRect: %s" % self.tree.GetBoundingRect(self.item, True)
				pass
			#items = self.tree.GetSelections()
			#print map(self.tree.GetItemText, items)
		event.Skip()


	def OnActivate(self, event):
		if self.item:
			#print "OnActivate: %s" % self.tree.GetItemText(self.item)
			pass

class TreeFrame(wx.Frame):
	def __init__(self, parent, filename):
		wx.Frame.__init__(self, parent, -1, "MDA Tree")
		panel = wx.Panel(self, -1, style=wx.WANTS_CHARS)
		sizer = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(panel, -1, "MDA file: %s" % filename)
		title.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
		sizer.Add(title, 0, wx.ALL, 5)
		treePanel = MDA_TreeCtrlPanel(panel, filename)
		sizer.Add(treePanel, 1, wx.EXPAND)
		panel.SetSizer(sizer)

###########################################################################
MDA_wildcard = "MDA (*.mda)|*.mda|All files (*.*)|*.*"

class MainPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.parent = parent

		self.bottomWin = wx.SashLayoutWindow(self, -1, (-1,-1), (200, 30), wx.SW_3D)
		self.bottomWin.SetDefaultSize((-1, 25))
		self.bottomWin.SetOrientation(wx.LAYOUT_HORIZONTAL)
		self.bottomWin.SetAlignment(wx.LAYOUT_BOTTOM)
		# Doesn't work; have to do it by hand in self.OnSashDrag()
		#self.bottomWin.SetMinimumSizeY(30)

		self.topWin = wx.SashLayoutWindow(self, -1, (-1,-1), (-1, -1), wx.SW_3D)
		(x,y) = self.parent.GetClientSize()
		self.topWin.SetDefaultSize((-1, y-30))
		self.topWin.SetOrientation(wx.LAYOUT_HORIZONTAL)
		self.topWin.SetAlignment(wx.LAYOUT_TOP)
		self.topWin.SetSashVisible(wx.SASH_BOTTOM, True)
		self.topWin.SetMinimumSizeY(30)

		self.Bind(wx.EVT_SASH_DRAGGED, self.OnSashDrag, id=self.topWin.GetId())
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def OnSashDrag(self, event):
		#print "OnSashDrag: height=", event.GetDragRect().height
		(pW, pH) =  self.parent.GetClientSize()
		#print "OnSashDrag: clientHeight=", pH

		eobj = event.GetEventObject()
		height = event.GetDragRect().height
		topWinHeight = max(30, min(pH-30, height))
		# Because bottomWin was created first, LayoutWindow doesn't care
		# about topWin's default size
		#self.topWin.SetDefaultSize((-1, topWinHeight))
		self.bottomWin.SetDefaultSize((-1, pH-topWinHeight))
		wx.LayoutAlgorithm().LayoutWindow(self, None)

	def OnSize(self, event):
		#print "OnSize: height=", self.parent.GetClientSize()[1]
		wx.LayoutAlgorithm().LayoutWindow(self, None)

def posShowNumtoFullShowNum(frame, dimension, num):
	if num >= frame.data[dimension].np:
		return None
	return frame.data[dimension].p[num].number

def detShowNumtoFullShowNum(frame, dimension, num):
	if num >= frame.data[dimension].nd:
		return None
	return frame.data[dimension].d[num].number

###########################################################################

NUMDET = 70
NUMPOS = 4
NUMDIMENSION=3+1
class TopFrame(wx.Frame):
	def __init__(self, parent, id, title, **kwds):
		wx.Frame.__init__(self, parent, id, title, **kwds)

		self.width = None
		self.height = None

		# init data structures
		self.data = None
		self.fileName = ""
		# lists with entries only for data that exist in the current file,
		# same ordering as full lists, but no missing elements
		self.detShowListList=[]
		self.posShowListList=[]
		self.posAxisList=[]
		# lists with entries for all detectors and positioners, numbered
		# by pos.number, det.number as read from file
		self.fullDetShowListList=[]
		self.fullPosShowListList=[]
		self.fullPosAxisList=[]
		self.dimPanelList = None

		self.plotFrame1D = None
		self.plotFrame2D = None
		self.plotFrame2D_X = None
		self.plotFrame2D_Y = None
		self.plotFrame3D_XY = None
		self.plotFrame3D_XYwZ = None
		self.plotFrame3D_XZ = None
		self.plotFrame3D_YZ = None
		self.plotFrame3D_X = None
		self.plotFrame3D_Y = None
		self.plotFrame3D_Z = None
		self.plotFrameSurface = None

		for i in range(NUMDIMENSION):
			self.fullDetShowListList.append([0]*NUMDET)
			self.fullPosShowListList.append([0]*NUMPOS)
			self.fullPosAxisList.append(AXIS_IS_INDEX)
			self.detShowListList.append([])
			self.posShowListList.append([])
			self.posAxisList.append(AXIS_IS_INDEX)

		# init vars controlled by menu selections
		self.maxDataDim = 2
		self.autoUpdatePlots = False
		self.plot1D_lines = True
		self.plot1D_points =  False
		self.plot1D_withAxes = True
		self.plot1D_withLabels = True
		self.plot1D_logY = False
		self.plot1D_withSharedAxes = False
		self.plot2D_withAxes = False
		self.plot2D_withLabels = False
		self.plot2D_withColorBar = False
		self.plot2D_withSharedAxes = False
		self.plot2D_autoAspect = False
		self.showCrossHair = False
		self.plotEverything = False

		# make menuBar
		menu1 = wx.Menu()
		menu1.Append(101, "Survey MDA files", "Gather info about MDA files in a directory")
		menu1.Append(102, "Open MDA file", "Open an MDA file")
		menu1.Append(103, "Save as ASCII file", "Save current MDA file as an ASCII file")
		menu1.Append(104, "Show file as tree", "Display a tree view of the current MDA file")
		menu1.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this application")
		self.Bind(wx.EVT_MENU, self.on_surveyMDA_MenuSelection, id=101)
		self.Bind(wx.EVT_MENU, self.on_openFile_MenuSelection, id=102)
		self.Bind(wx.EVT_MENU, self.on_saveAscii_MenuSelection, id=103)
		self.Bind(wx.EVT_MENU, self.on_showTree_MenuSelection, id=104)
		self.Bind(wx.EVT_MENU, self.on_Exit_Event, id=wx.ID_EXIT)

		menu2 = wx.Menu()
		menu2.Append(201, "Read 3D Data", "Read 3D data (else only 1D and 2D)", wx.ITEM_CHECK)
		item = menu2.Append(203, "AutoUpdatePlots", "Selecting a detector updates displayed plots", wx.ITEM_CHECK)
		item.Check(self.autoUpdatePlots)


		subMenu = wx.Menu()
		item = subMenu.Append(2041, "lines", "plot lines", wx.ITEM_CHECK)
		item.Check(self.plot1D_lines)
		item = subMenu.Append(2042, "points", "plot points", wx.ITEM_CHECK)
		item.Check(self.plot1D_points)
		item = subMenu.Append(2043, "with axes", "Show ticks", wx.ITEM_CHECK)
		item.Check(self.plot1D_withAxes)
		item = subMenu.Append(2044, "with labels", "Show x and y labels", wx.ITEM_CHECK)
		item.Check(self.plot1D_withLabels)
		subMenu.Append(2045, "log Y axis", "Y axis is logarithmic", wx.ITEM_CHECK)
		item = subMenu.Append(2046, "with shared axes", "Zoom/pan affect all images", wx.ITEM_CHECK)
		item.Check(self.plot1D_withSharedAxes)
		menu2.AppendMenu(204, "1D plots", subMenu)

		subMenu = wx.Menu()
		item = subMenu.Append(2051, "with axes", "Show axes, ticks, and axis labels", wx.ITEM_CHECK)
		item.Check(self.plot2D_withAxes)
		item = subMenu.Append(2052, "with labels", "Show  x and y labels", wx.ITEM_CHECK)
		item.Check(self.plot2D_withLabels)
		item = subMenu.Append(2053, "with color bar", "Show color bar beside image", wx.ITEM_CHECK)
		item.Check(self.plot2D_withColorBar)
		item = subMenu.Append(2054, "with shared axes", "Zoom/pan affect all images", wx.ITEM_CHECK)
		item.Check(self.plot2D_withSharedAxes)
		item = subMenu.Append(2055, "auto aspect", "Make square image plots", wx.ITEM_CHECK)
		item.Check(self.plot2D_autoAspect)
		menu2.AppendMenu(205, "2D plots", subMenu)

		item = menu2.Append(206, "Show crosshair", "Show crosshair cursor on plots", wx.ITEM_CHECK)
		item.Check(self.showCrossHair)

		item = menu2.Append(207, "Plot Everything", "Ignore selections", wx.ITEM_CHECK)
		item.Check(self.plotEverything)

		self.Bind(wx.EVT_MENU, self.on_read3D_Data_MenuSelection, id=201)
		self.Bind(wx.EVT_MENU, self.on_autoUpdatePlots_MenuSelection, id=203)
		self.Bind(wx.EVT_MENU_RANGE, self.on_Plot1D_MenuSelection, id=2041, id2=2046)
		self.Bind(wx.EVT_MENU_RANGE, self.on_plot2D_MenuSelection, id=2051, id2=2055)
		self.Bind(wx.EVT_MENU, self.on_showCrossHair_MenuSelection, id=206)
		self.Bind(wx.EVT_MENU, self.on_plotEverything_MenuSelection, id=207)


		menu3 = wx.Menu()
		item = menu3.Append(301, "Debug", "Execute debug statements", wx.ITEM_CHECK)
		item.Check(DEBUG)
		self.Bind(wx.EVT_MENU, self.on_Debug_MenuSelection, id=301)

		menuBar = wx.MenuBar()
		menuBar.Append(menu1, "&File")
		menuBar.Append(menu2, "&Options")
		menuBar.Append(menu3, "&Debug")
		self.SetMenuBar(menuBar)

		# make statusBar
		statusBar = self.CreateStatusBar()
		statusBar.SetFieldsCount(2)

		self.mainPanel = MainPanel(self)
		self.fillMainPanel()

	def on_Exit_Event(self, event):
		self.Close()

	def fillMainPanel(self):
		topPanel = wx.Panel(self.mainPanel.topWin, style=wx.BORDER_SUNKEN)
		topPanelSizer = wx.BoxSizer(wx.VERTICAL)
		text1 = wx.StaticText(topPanel, -1, "Data File: %s" % self.fileName)
		topPanelSizer.Add(text1, 0, wx.ALL, 5)

		dimPanel = wx.Panel(topPanel)
		topPanelSizer.Add(dimPanel, 3, wx.EXPAND)
		dimPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.mainPanel.Fit()

		if self.data:
			self.dimPanelList = []
			for i in range(1,len(self.data)):
				dp = PlotDimPanel(dimPanel, self, i, style=wx.BORDER_RAISED)
				self.dimPanelList.append(dp)
				dimPanelSizer.Add(dp, 1, wx.EXPAND|wx.ALL, 5)
		dimPanel.SetSizer(dimPanelSizer)
		topPanel.SetSizer(topPanelSizer)

		if self.data:
			self.envPanel = EnvListPanel(self.mainPanel.bottomWin, self.data[0])
			#envPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
			#envPanelSizer.Add(self.envPanel, 1, wx.EXPAND)
			#self.mainPanel.bottomWin.SetSizer(envPanelSizer)
			#self.mainPanel.bottomWin.Layout()

	def on_Debug_MenuSelection(self, event):
		global DEBUG
		id = event.GetId()
		if id == 301: DEBUG = event.Checked()

	def on_Plot1D_MenuSelection(self, event):
		id = event.GetId()
		if id == 2041: self.plot1D_lines = event.Checked()
		elif id == 2042: self.plot1D_points = event.Checked()
		elif id == 2043: self.plot1D_withAxes = event.Checked()
		elif id == 2044: self.plot1D_withLabels = event.Checked()
		elif id == 2045: self.plot1D_logY = event.Checked()
		elif id == 2046: self.plot1D_withSharedAxes = event.Checked()
		if self.autoUpdatePlots:
			for dimPanel in self.dimPanelList:
				dimPanel.maybePlot()

	def on_plot2D_MenuSelection(self, event):
		id = event.GetId()
		if id == 2051: self.plot2D_withAxes = event.Checked()
		elif id == 2052: self.plot2D_withLabels = event.Checked()
		elif id == 2053: self.plot2D_withColorBar = event.Checked()
		elif id == 2054: self.plot2D_withSharedAxes = event.Checked()
		elif id == 2055: self.plot2D_autoAspect = event.Checked()
		if self.autoUpdatePlots:
			for dimPanel in self.dimPanelList:
				dimPanel.maybePlot()

	def on_read3D_Data_MenuSelection(self, event):
		if event.Checked():
			self.maxDataDim = 3
		else:
			self.maxDataDim = 2

	def on_autoUpdatePlots_MenuSelection(self, event):
		if event.Checked():
			self.autoUpdatePlots = True
		else:
			self.autoUpdatePlots = False

	def on_showCrossHair_MenuSelection(self, event):
		if event.Checked():
			self.showCrossHair = True
		else:
			self.showCrossHair = False

	def on_plotEverything_MenuSelection(self, event):
		if event.Checked():
			self.plotEverything = True
		else:
			self.plotEverything = False

	def openFile(self):
		return wx.FileSelector("Choose a file", default_path=os.getcwd(),
			default_filename="", default_extension=".mda", wildcard=MDA_wildcard,
			flags=wx.OPEN|wx.CHANGE_DIR)

	def on_showTree_MenuSelection(self, event):
		self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		path = self.fileName
		if path == "":
			path = self.openFile()
		if path:
			treeFrame = TreeFrame(self, path)
			treeFrame.Show(True)
		self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def on_openFile_MenuSelection(self, event):
		path = self.openFile()
		if path:
			self.readData(path)

	def readData(self, path):
		self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
		self.fileName = path
		self.SetStatusText("Reading...", 0)
		t1 = time.time()
		self.data = mda.readMDA(self.fileName, maxdim=self.maxDataDim, verbose=0, showHelp=0, outFile=None, useNumpy=False, readQuick=True)
		readTime = time.time()-t1
		self.SetStatusText("read time=%.1f s" % readTime, 0)
		mda.getDescFromEnv(self.data)
		if self.data:
			t1 = time.time()
			self.mainPanel.Destroy()
			# clear out showLists
			self.detShowListList = []
			self.posShowListList = []
			self.posAxisList = []
			for i in range(NUMDIMENSION):
				self.detShowListList.append([])
				self.posShowListList.append([])
				self.posAxisList.append(AXIS_IS_INDEX)

			self.mainPanel = MainPanel(self)
			self.fillMainPanel()
			self.SendSizeEvent()
			#self.Fit()
			displayTime = time.time()-t1
			self.SetStatusText("display time=%.1f s" % displayTime, 1)
		self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def on_saveAscii_MenuSelection(self, event):
		if self.fileName == "":
			self.SetStatusText("You have to open an MDA file first", 0)
			return
		fname = os.path.basename(self.fileName)
		(asciiName, junk) = os.path.splitext(fname)
		asciiName = asciiName  + ".txt"
		wildcard = "MDA (*.mda)|*.mda|All files (*.*)|*.*"
		dlg = wx.FileDialog(self, message="Save as ...",
			defaultDir=os.getcwd(), defaultFile=asciiName, wildcard=wildcard,
			style=wx.SAVE | wx.CHANGE_DIR)
		path = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if path:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			mda.writeAscii(self.data, path)
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def on_surveyMDA_MenuSelection(self, event):
		directory = wx.DirSelector(message="Choose a directory:", defaultPath=os.getcwd(),
			style=wx.DD_DEFAULT_STYLE|wx.DD_CHANGE_DIR)
		if directory:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			dirFrame = DirListFrame(self, directory)
			dirFrame.Show(True)
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

def main():
	app = wx.PySimpleApp()
	frame = TopFrame(None, -1, 'MDA Explorer', size=(800,500))
	frame.Center()
	(hS, vS) = frame.GetSize()
	(hP, vP) = frame.GetPosition()
	frame.width = (hP + hS/2)*2
	frame.height = (vP + vS/2)*2
	frame.SetMaxSize((frame.width, frame.height))
	frame.Show(True)
	app.MainLoop()


if __name__ == '__main__':
	main()
