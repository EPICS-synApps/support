/* drvUSB1608G.cpp
 *
 * Driver for Measurement Computing USB-1608G multi-function DAQ board using asynPortDriver base class
 *
 * This driver supports simple analog in/out, digital in/out bit and word, timer (digital pulse generator), counter,
 *   waveform out (aribtrary waveform generator), and waveform in (digital oscilloscope)
 *
 * Mark Rivers
 * November 5, 2011
*/

#include <math.h>

#include <iocsh.h>
#include <epicsExport.h>
#include <epicsThread.h>

#include <asynPortDriver.h>

#include "cbw.h"

static const char *driverName = "USB1608G";

typedef enum {
  waveTypeUser,
  waveTypeSin,
  waveTypeSquare,
  waveTypeSawTooth,
  waveTypePulse,
  waveTypeRandom
} waveType_t;

// Pulse output parameters
#define pulseStartString          "PULSE_START"
#define pulsePeriodString         "PULSE_PERIOD"
#define pulseWidthString          "PULSE_WIDTH"
#define pulseDelayString          "PULSE_DELAY"
#define pulseCountString          "PULSE_COUNT"
#define pulseIdleStateString      "PULSE_IDLE_STATE"

// Counter parameters
#define counterCountsString       "COUNTER_VALUE"
#define counterResetString        "COUNTER_RESET"

// Analog input parameters
#define analogInValueString       "ANALOG_IN_VALUE"
#define analogInRangeString       "ANALOG_IN_RANGE"

// Waveform digitizer parameters
#define waveDigWaveformString     "WAVEDIG_WAVEFORM"
#define waveDigDwellString        "WAVEDIG_DWELL"
#define waveDigFirstChanString    "WAVEDIG_FIRST_CHAN"
#define waveDigLastChanString     "WAVEDIG_LAST_CHAN"
#define waveDigRunString          "WAVEDIG_RUN"

// Analog output parameters
#define analogOutValueString      "ANALOG_OUT_VALUE"

// Waveform generator parameters
#define waveGenWaveTypeString     "WAVEGEN_WAVE_TYPE"
#define waveGenUserWFString       "WAVEGEN_USER_WF"
#define waveGenInternalWFString   "WAVEGEN_INTERNAL_WF"
#define waveGenTimeWFString       "WAVEGEN_TIME_WF"
#define waveGenNumPointsString    "WAVEGEN_NUM_POINTS"
#define waveGenCurrentPointString "WAVEGEN_CURRENT_POINT"
#define waveGenDwellString        "WAVEGEN_DWELL"
#define waveGenActualDwellString  "WAVEGEN_ACTUAL_DWELL"
#define waveGenFreqString         "WAVEGEN_FREQ"
#define waveGenPulseWidthString   "WAVEGEN_PULSE_WIDTH"
#define waveGenAmplitudeString    "WAVEGEN_AMPLITUDE"
#define waveGenOffsetString       "WAVEGEN_OFFSET"
#define waveGenEnableString       "WAVEGEN_ENABLE"
#define waveGenExtTriggerString   "WAVEGEN_EXT_TRIGGER"
#define waveGenExtClockString     "WAVEGEN_EXT_CLOCK"
#define waveGenContinuousString   "WAVEGEN_CONTINUOUS"
#define waveGenRunString          "WAVEGEN_RUN"

// Digital I/O parameters
#define digitalDirectionString    "DIGITAL_DIRECTION"
#define digitalInputString        "DIGITAL_INPUT"
#define digitalOutputString       "DIGITAL_OUTPUT"

#define MIN_FREQUENCY   0.0149
#define MAX_FREQUENCY   32e6
#define MIN_DELAY       0.
#define MAX_DELAY       67.11
#define NUM_ANALOG_IN   16  // Number analog inputs on 1608G
#define NUM_ANALOG_OUT  2   // Number of analog outputs on 1608G
#define NUM_COUNTERS    2   // Number of counters on 1608G
#define NUM_TIMERS      1   // Number of timers on 1608G
#define NUM_IO_BITS     8   // Number of digital I/O bits on 1608G
#define MAX_SIGNALS     NUM_ANALOG_IN

#define DEFAULT_POLL_TIME 0.01

#define PI 3.14159265

/** This is the class definition for the USB1608G class
  */
class USB1608G : public asynPortDriver {
public:
  USB1608G(const char *portName, int boardNum, int maxInputPoints, int maxOutputPoints);

  /* These are the methods that we override from asynPortDriver */
  virtual asynStatus writeInt32(asynUser *pasynUser, epicsInt32 value);
  virtual asynStatus readInt32(asynUser *pasynUser, epicsInt32 *value);
  virtual asynStatus getBounds(asynUser *pasynUser, epicsInt32 *low, epicsInt32 *high);
  virtual asynStatus writeFloat64(asynUser *pasynUser, epicsFloat64 value);
  virtual asynStatus writeUInt32Digital(asynUser *pasynUser, epicsUInt32 value, epicsUInt32 mask);
  virtual asynStatus readFloat32Array(asynUser *pasynUser, epicsFloat32 *value, size_t nElements, size_t *nIn);
  virtual asynStatus writeFloat32Array(asynUser *pasynUser, epicsFloat32 *value, size_t nElements);
  virtual void report(FILE *fp, int details);
  // These should be private but are called from C
  virtual void pollerThread(void);

protected:
  // Pulse generator parameters
  int pulseStart_;
  #define FIRST_USB1608G_PARAM pulseStart_
  int pulsePeriod_;
  int pulseWidth_;
  int pulseDelay_;
  int pulseCount_;
  int pulseIdleState_;
  
  // Counter parameters
  int counterCounts_;
  int counterReset_;
  
  // Analog input parameters
  int analogInValue_;
  int analogInRange_;
  
  // Waveform digitizer parameters
  int waveDigWaveform_;
  int waveDigDwell_;
  int waveDigFirstChan_;
  int waveDigLastChan_;
  int waveDigRun_;
  
  // Analog output parameters
  int analogOutValue_;
  
  // Waveform generator parameters
  int waveGenWaveType_;
  int waveGenUserWF_;
  int waveGenInternalWF_;
  int waveGenTimeWF_;
  int waveGenNumPoints_;
  int waveGenCurrentPoint_;
  int waveGenDwell_;
  int waveGenActualDwell_;
  int waveGenFreq_;
  int waveGenPulseWidth_;
  int waveGenAmplitude_;
  int waveGenOffset_;
  int waveGenEnable_;
  int waveGenExtTrigger_;
  int waveGenExtClock_;
  int waveGenContinuous_;
  int waveGenRun_;

  // Digital I/O parameters
  int digitalDirection_;
  int digitalInput_;
  int digitalOutput_;
  #define LAST_USB1608G_PARAM digitalOutput_

private:
  int boardNum_;
  double pollTime_;
  int forceCallback_;
  size_t maxInputPoints_;
  size_t maxOutputPoints_;
  epicsFloat32 *waveDigBuffer_[NUM_ANALOG_IN];
  epicsFloat32 *waveGenInternalBuffer_[NUM_ANALOG_OUT];
  epicsFloat32 *waveGenUserBuffer_[NUM_ANALOG_OUT];
  epicsFloat32 *waveGenTimeBuffer_;
  HGLOBAL inputMemHandle_;
  HGLOBAL outputMemHandle_;
  int startPulseGenerator();
  int startWaveformGenerator();
  int startWaveformDigitizer();
  int defineWaveform(int channel);
};

#define NUM_PARAMS (&LAST_USB1608G_PARAM - &FIRST_USB1608G_PARAM + 1)

static void pollerThreadC(void * pPvt)
{
    USB1608G *pUSB1608G = (USB1608G *)pPvt;
    pUSB1608G->pollerThread();
}

USB1608G::USB1608G(const char *portName, int boardNum, int maxInputPoints, int maxOutputPoints)
  : asynPortDriver(portName, MAX_SIGNALS, NUM_PARAMS, 
      asynInt32Mask | asynUInt32DigitalMask | asynInt32ArrayMask | asynFloat32ArrayMask | asynFloat64Mask | asynDrvUserMask,
      asynInt32Mask | asynUInt32DigitalMask | asynInt32ArrayMask | asynFloat32ArrayMask | asynFloat64Mask, 
      ASYN_MULTIDEVICE, 1, /* ASYN_CANBLOCK=0, ASYN_MULTIDEVICE=1, autoConnect=1 */
      0, 0),  /* Default priority and stack size */
    boardNum_(boardNum),
    pollTime_(DEFAULT_POLL_TIME),
    forceCallback_(1),
    maxInputPoints_(maxInputPoints),
    maxOutputPoints_(maxOutputPoints)
{
  int i;
  static const char *functionName = "USB1608G";
  
  // Pulse generator parameters
  createParam(pulseStartString,                asynParamInt32, &pulseStart_);
  createParam(pulsePeriodString,             asynParamFloat64, &pulsePeriod_);
  createParam(pulseWidthString,              asynParamFloat64, &pulseWidth_);
  createParam(pulseDelayString,              asynParamFloat64, &pulseDelay_);
  createParam(pulseCountString,                asynParamInt32, &pulseCount_);
  createParam(pulseIdleStateString,            asynParamInt32, &pulseIdleState_);

  // Counter parameters
  createParam(counterCountsString,             asynParamInt32, &counterCounts_);
  createParam(counterResetString,              asynParamInt32, &counterReset_);

  // Analog input parameters
  createParam(analogInValueString,             asynParamInt32, &analogInValue_);
  createParam(analogInRangeString,             asynParamInt32, &analogInRange_);
  
  // Waveform digitizer parameters
  createParam(waveDigWaveformString,    asynParamFloat32Array, &waveDigWaveform_);
  createParam(waveDigDwellString,            asynParamFloat64, &waveDigDwell_);
  createParam(waveDigFirstChanString,          asynParamInt32, &waveDigFirstChan_);
  createParam(waveDigLastChanString,           asynParamInt32, &waveDigLastChan_);
  createParam(waveDigRunString,                asynParamInt32, &waveDigRun_);
  
  // Analog output parameters
  createParam(analogOutValueString,            asynParamInt32, &analogOutValue_);
  
  // Waveform generator parameters
  createParam(waveGenWaveTypeString,           asynParamInt32, &waveGenWaveType_);
  createParam(waveGenUserWFString,      asynParamFloat32Array, &waveGenUserWF_);
  createParam(waveGenInternalWFString,  asynParamFloat32Array, &waveGenInternalWF_);
  createParam(waveGenTimeWFString,      asynParamFloat32Array, &waveGenTimeWF_);
  createParam(waveGenNumPointsString,          asynParamInt32, &waveGenNumPoints_);
  createParam(waveGenCurrentPointString,       asynParamInt32, &waveGenCurrentPoint_);
  createParam(waveGenDwellString,            asynParamFloat64, &waveGenDwell_);
  createParam(waveGenActualDwellString,      asynParamFloat64, &waveGenActualDwell_);
  createParam(waveGenFreqString,             asynParamFloat64, &waveGenFreq_);
  createParam(waveGenPulseWidthString,       asynParamFloat64, &waveGenPulseWidth_);
  createParam(waveGenAmplitudeString,        asynParamFloat64, &waveGenAmplitude_);
  createParam(waveGenOffsetString,           asynParamFloat64, &waveGenOffset_);
  createParam(waveGenEnableString,             asynParamInt32, &waveGenEnable_);
  createParam(waveGenExtTriggerString,         asynParamInt32, &waveGenExtTrigger_);
  createParam(waveGenExtClockString,           asynParamInt32, &waveGenExtClock_);
  createParam(waveGenContinuousString,         asynParamInt32, &waveGenContinuous_);
  createParam(waveGenRunString,                asynParamInt32, &waveGenRun_);

  // Digital I/O parameters
  createParam(digitalDirectionString,  asynParamUInt32Digital, &digitalDirection_);
  createParam(digitalInputString,      asynParamUInt32Digital, &digitalInput_);
  createParam(digitalOutputString,     asynParamUInt32Digital, &digitalOutput_);

  // Allocate memory for the input and output buffers
  for (i=0; i<NUM_ANALOG_IN; i++) {
    waveDigBuffer_[i]  = (epicsFloat32 *) calloc(maxInputPoints_,  sizeof(epicsFloat32));
  }
  for (i=0; i<NUM_ANALOG_OUT; i++) {
    waveGenInternalBuffer_[i] = (epicsFloat32 *) calloc(maxOutputPoints_, sizeof(epicsFloat32));
    waveGenUserBuffer_[i]     = (epicsFloat32 *) calloc(maxOutputPoints_, sizeof(epicsFloat32));
  }
  waveGenTimeBuffer_ = (epicsFloat32 *) calloc(maxOutputPoints_, sizeof(epicsFloat32));
  inputMemHandle_  = cbWinBufAlloc(maxInputPoints  * NUM_ANALOG_IN);
  outputMemHandle_ = cbWinBufAlloc(maxOutputPoints * NUM_ANALOG_OUT);

  /* Start the thread to poll counters and digital inputs and do callbacks to 
   * device support */
  epicsThreadCreate("USB1608GPoller",
                    epicsThreadPriorityLow,
                    epicsThreadGetStackSize(epicsThreadStackMedium),
                    (EPICSTHREADFUNC)pollerThreadC,
                    this);
}

int USB1608G::startPulseGenerator()
{
  int status=0;
  double period, width, delay;
  int timerNum=0;
  double frequency, dutyCycle;
  int count, pulseStart, idleState;
  static const char *functionName = "startPulseGenerator";
  
  getDoubleParam (timerNum, pulsePeriod_,    &period);
  getDoubleParam (timerNum, pulseWidth_,     &width);
  getDoubleParam (timerNum, pulseDelay_,     &delay);
  getIntegerParam(timerNum, pulseCount_,     &count);
  getIntegerParam(timerNum, pulseIdleState_, &idleState);
  getIntegerParam(timerNum, pulseStart_,     &pulseStart);
  
  frequency = 1. / period;
  if (frequency < MIN_FREQUENCY) frequency = MIN_FREQUENCY;
  if (frequency > MAX_FREQUENCY) frequency = MAX_FREQUENCY;
  dutyCycle = width / period;
  if (dutyCycle <= 0.) dutyCycle = .0001;
  if (dutyCycle >= 1.) dutyCycle = .9999;
  if (delay < MIN_DELAY) delay = MIN_DELAY;
  if (delay > MAX_DELAY) delay = MAX_DELAY;

  status = cbPulseOutStart(boardNum_, timerNum, &frequency, &dutyCycle, count, &delay, idleState, 0);
  asynPrint(pasynUserSelf, ASYN_TRACE_FLOW,
    "%s:%s: started pulse generator %d period=%f, width=%f, count=%d, delay=%f, idleState=%d, status=%d\n",
    driverName, functionName, timerNum, period, width, count, delay, idleState, status);
  // We may not have gotten the frequency, dutyCycle, and delay we asked for, set the actual values
  // in the parameter library
  period = 1. / frequency;
  width = period * dutyCycle;
  asynPrint(pasynUserSelf, ASYN_TRACE_FLOW,
    "%s:%s: started pulse generator %d actual period=%f, actual width=%f, actual delay=%f\n",
    driverName, functionName, timerNum, period, width, delay);
  setDoubleParam(timerNum, pulsePeriod_, period);
  setDoubleParam(timerNum, pulseWidth_, width);
  setDoubleParam(timerNum, pulseDelay_, delay);
  return status;
}

int USB1608G::defineWaveform(int channel)
{
  int waveType;
  int numPoints;
  int nPulse;
  int i;
  epicsFloat32 *outPtr = waveGenInternalBuffer_[channel];
  double dwell, freq, offset, base, amplitude, pulseWidth, scale;
  static const char *functionName = "defineWaveform";

  getIntegerParam(waveGenNumPoints_,  &numPoints);
  if ((size_t)numPoints > maxOutputPoints_) {
    asynPrint(pasynUserSelf, ASYN_TRACE_ERROR,
      "%s:%s: ERROR numPoints=%d must be less than maxOutputPoints=%d\n",
      driverName, functionName, numPoints, maxOutputPoints_);
    return -1;
  }

  getIntegerParam(channel, waveGenWaveType_,  &waveType);
  if (waveType == waveTypeUser) {
    getDoubleParam(waveGenDwell_,             &dwell);
    setDoubleParam(waveGenActualDwell_, dwell);
    return 0;
  }

  getDoubleParam(waveGenFreq_,                 &freq);
  getDoubleParam(channel, waveGenOffset_,      &offset);
  getDoubleParam(channel, waveGenAmplitude_,   &amplitude);
  getDoubleParam(channel, waveGenPulseWidth_,  &pulseWidth);
  dwell = 1. / freq / numPoints;
  setDoubleParam(waveGenActualDwell_, dwell);
  base = offset - amplitude/2.;
  switch (waveType) {
    case waveTypeSin:
      scale = 2.*PI/(numPoints-1);
      for (i=0; i<numPoints; i++)           *outPtr++ = (epicsFloat32) (offset + amplitude/2. * sin(i*scale));
      break;
    case waveTypeSquare:
      for (i=0; i<numPoints/2; i++)         *outPtr++ = (epicsFloat32) (base + amplitude);
      for (i=numPoints/2; i<numPoints; i++) *outPtr++ = (epicsFloat32) (base);
      break;
    case waveTypeSawTooth:
      scale = 1./(numPoints-1);
      for (i=0; i<numPoints; i++)           *outPtr++ = (epicsFloat32) (base + amplitude*i*scale);
      break;
    case waveTypePulse:
      nPulse = (int) ((pulseWidth / dwell) + 0.5);
      if (nPulse < 1) nPulse = 1;
      if (nPulse >= numPoints-1) nPulse = numPoints-1;
      for (i=0; i<nPulse; i++)              *outPtr++ = (epicsFloat32) (base + amplitude);
      for (i=nPulse; i<numPoints; i++)      *outPtr++ = (epicsFloat32) (base);
      break;
    case waveTypeRandom:
      scale = amplitude / RAND_MAX;
      srand(1);
      for (i=0; i<numPoints; i++)           *outPtr++ = (epicsFloat32) (base + rand() * scale);
      break;
  }
  doCallbacksFloat32Array(waveGenInternalBuffer_[channel], numPoints, waveGenInternalWF_, channel);
  return 0;
}
 
int USB1608G::startWaveformGenerator()
{
  int status=0;
  int numPoints;
  int enable;
  int firstChan=-1, lastChan;
  long pointsPerSecond;
  int waveType;
  int extTrigger, extClock, continuous;
  int options;
  int i, j;
  double scale=65535./20.;
  double dwell;
  epicsFloat32* inPtr;
  epicsUInt16 *outPtr = (epicsUInt16 *)outputMemHandle_;
  static const char *functionName = "startWaveformGenerator";
  
  getIntegerParam(waveGenNumPoints_,  &numPoints);
  getIntegerParam(waveGenExtTrigger_, &extTrigger);
  getIntegerParam(waveGenExtClock_,   &extClock);
  getIntegerParam(waveGenContinuous_, &continuous);
 
  for (i=0; i<NUM_ANALOG_OUT; i++) {
    getIntegerParam(i, waveGenEnable_, &enable);
    if (enable) {
      if (firstChan < 0) firstChan = i;
      lastChan = i;
      status = defineWaveform(i);
      if (status) return -1;
    }
  }
  
  if (firstChan < 0) {
    asynPrint(pasynUserSelf, ASYN_TRACE_ERROR,
      "%s:%s: ERROR no enabled channels\n",
      driverName, functionName);
     return -1;
  }
  
  // ActualDwell was computed by defineWaveform above
  getDoubleParam(waveGenActualDwell_, &dwell);
  pointsPerSecond = (int)((1. / dwell) + 0.5);
  
  // Copy data from float32 array to outputMemHandel, converting from volts to D/A units
  for (i=firstChan; i<=lastChan; i++) {
    getIntegerParam(i, waveGenWaveType_,  &waveType);
    if (waveType == waveTypeUser) 
      inPtr = waveGenUserBuffer_[i];
    else
      inPtr = waveGenInternalBuffer_[i];
    for (j=0; j<numPoints; j++) {
      *outPtr++ = (epicsUInt16)((*inPtr++ + 10.)*scale + 0.5);
    }
  }
  options                  = BACKGROUND;
  if (extTrigger) options |= EXTTRIGGER;
  if (extClock)   options |= EXTCLOCK;
  if (continuous) options |= CONTINUOUS;
  status = cbAOutScan(boardNum_, firstChan, lastChan, numPoints, &pointsPerSecond, BIP10VOLTS,
                      outputMemHandle_, options);
  if (status) {
    asynPrint(pasynUserSelf, ASYN_TRACE_ERROR,
      "%s:%s: ERROR calling cbAOutScan, firstChan=%d, lastChan=%d, numPoints=%d, pointsPerSecond=%d, options=0x%x, status=%d\n",
      driverName, functionName, firstChan, lastChan, numPoints, pointsPerSecond, options, status);
    return status;
  }

  // Convert back from pointsPerSecond to dwell, since value might have changed
  dwell = (1. / pointsPerSecond);
  setDoubleParam(waveGenActualDwell_, dwell);
  // Construct the timebase array which is used by clients for display
  for (i=0; i<numPoints; i++) {
    waveGenTimeBuffer_[i] = (epicsFloat32) (i * dwell);
  }
  doCallbacksFloat32Array(waveGenTimeBuffer_, numPoints, waveGenTimeWF_, 0);
  return status;
}
  
int USB1608G::startWaveformDigitizer()
{
  return 0;
}
 

asynStatus USB1608G::getBounds(asynUser *pasynUser, epicsInt32 *low, epicsInt32 *high)
{
  int function = pasynUser->reason;

  // Both the analog outputs and analog inputs are 16-bit devices
  if ((function == analogOutValue_) ||
      (function == analogInValue_)) {
    *low = 0;
    *high = 65535;
    return(asynSuccess);
  } else {
    return(asynError);
  }
}

asynStatus USB1608G::writeInt32(asynUser *pasynUser, epicsInt32 value)
{
  int addr;
  int function = pasynUser->reason;
  int status=0;
  int waveGenRunning;
  static const char *functionName = "writeInt32";

  getIntegerParam(waveGenRun_, &waveGenRunning);

  this->getAddress(pasynUser, &addr);
  setIntegerParam(addr, function, value);

  // Pulse generator functions
  if (function == pulseStart_) {
    if (value) {
      status = startPulseGenerator();
    } else {
      status = cbPulseOutStop(boardNum_, 0);
    }
  }

  // Counter functions
  else if (function == counterReset_) {
     // LOADREG0=0, LOADREG1=1, so we use addr
     status = cbCLoad32(boardNum_, addr, 0);
  }

  // Analog input functions
  else if (function == waveDigRun_) {
    startWaveformDigitizer();
  }
  
  // Analog output functions
  else if (function == analogOutValue_) {
    if (waveGenRunning) {
      asynPrint(pasynUser, ASYN_TRACE_ERROR,
        "%s:%s: ERROR cannot write analog outputs while waveform generator is running.\n",
        driverName, functionName);
      return asynError;
    }
    status = cbAOut(boardNum_, addr, BIP10VOLTS, value);
  }

  else if (function == waveGenRun_) {
    if ((value) && !waveGenRunning)
      status = startWaveformGenerator();
    else if (!value && waveGenRunning) 
      status = cbStopBackground(boardNum_, AOFUNCTION);
  }

  else if ((function == waveGenWaveType_)   ||
           (function == waveGenNumPoints_)  ||
           (function == waveGenRun_)        ||
           (function == waveGenEnable_)     ||
           (function == waveGenExtTrigger_) ||
           (function == waveGenExtClock_)   ||
           (function == waveGenContinuous_)) {
    if (waveGenRunning) {
      status = cbStopBackground(boardNum_, AOFUNCTION);
      status |= startWaveformGenerator();
    }
   }

  callParamCallbacks(addr);
  if (status == 0) {
    asynPrint(pasynUser, ASYN_TRACEIO_DRIVER, 
             "%s:%s, port %s, wrote %d to address %d\n",
             driverName, functionName, this->portName, value, addr);
  } else {
    asynPrint(pasynUser, ASYN_TRACE_ERROR, 
             "%s:%s, port %s, ERROR writing %d to address %d, status=%d\n",
             driverName, functionName, this->portName, value, addr, status);
  }
  return (status==0) ? asynSuccess : asynError;
}


asynStatus USB1608G::readInt32(asynUser *pasynUser, epicsInt32 *value)
{
  int addr;
  int function = pasynUser->reason;
  int status=0;
  unsigned short shortVal;
  int range;
  static const char *functionName = "readInt32";

  this->getAddress(pasynUser, &addr);

  // Analog input function
  if (function == analogInValue_) {
    getIntegerParam(addr, analogInRange_, &range);
    status = cbAIn(boardNum_, addr, range, &shortVal);
    *value = shortVal;
    setIntegerParam(addr, analogInValue_, *value);
  }

  // Other functions we call the base class method
  else {
     status = asynPortDriver::readInt32(pasynUser, value);
  }

  callParamCallbacks(addr);
  if (status != 0) {
    asynPrint(pasynUser, ASYN_TRACE_ERROR, 
             "%s:%s, port %s, ERROR reading from address %d, status=%d\n",
             driverName, functionName, this->portName, addr, status);
  }
  return (status==0) ? asynSuccess : asynError;
}

asynStatus USB1608G::writeFloat64(asynUser *pasynUser, epicsFloat64 value)
{
  int addr;
  int function = pasynUser->reason;
  int waveGenRunning;
  int status=0;
  static const char *functionName = "writeFloat64";

  getIntegerParam(waveGenRun_, &waveGenRunning);

  this->getAddress(pasynUser, &addr);
  setDoubleParam(addr, function, value);

  if ((function == waveGenDwell_)      ||
      (function == waveGenFreq_)       ||
      (function == waveGenPulseWidth_) ||
      (function == waveGenAmplitude_)  ||
      (function == waveGenOffset_)) {
    if (waveGenRunning) {
      status = cbStopBackground(boardNum_, AOFUNCTION);
      status |= startWaveformGenerator();
    }
  }
  
  callParamCallbacks(addr);
  if (status == 0) {
    asynPrint(pasynUser, ASYN_TRACEIO_DRIVER, 
             "%s:%s, port %s, wrote %d to address %d\n",
             driverName, functionName, this->portName, value, addr);
  } else {
    asynPrint(pasynUser, ASYN_TRACE_ERROR, 
             "%s:%s, port %s, ERROR writing %f to address %d, status=%d\n",
             driverName, functionName, this->portName, value, addr, status);
  }
  return (status==0) ? asynSuccess : asynError;
}

asynStatus USB1608G::writeUInt32Digital(asynUser *pasynUser, epicsUInt32 value, epicsUInt32 mask)
{
  int function = pasynUser->reason;
  int status=0;
  int i;
  epicsUInt32 outValue=0, outMask, direction=0;
  static const char *functionName = "writeUInt32Digital";


  setUIntDigitalParam(function, value, mask);
  if (function == digitalDirection_) {
    outValue = (value == 0) ? DIGITALIN : DIGITALOUT; 
    for (i=0; i<NUM_IO_BITS; i++) {
      if ((mask & (1<<i)) != 0) {
        status = cbDConfigBit(boardNum_, AUXPORT, i, outValue);
      }
    }
  }

  else if (function == digitalOutput_) {
    getUIntDigitalParam(digitalDirection_, &direction, 0xFFFFFFFF);
    for (i=0, outMask=1; i<NUM_IO_BITS; i++, outMask = (outMask<<1)) {
      // Only write the value if the mask has this bit set and the direction for that bit is output (1)
      outValue = ((value &outMask) == 0) ? 0 : 1; 
      if ((mask & outMask & direction) != 0) {
        status = cbDBitOut(boardNum_, AUXPORT, i, outValue);
      }
    }
  }
  
  callParamCallbacks();
  if (status == 0) {
    asynPrint(pasynUser, ASYN_TRACEIO_DRIVER, 
             "%s:%s, port %s, wrote outValue=0x%x, value=0x%x, mask=0x%x, direction=0x%x\n",
             driverName, functionName, this->portName, outValue, value, mask, direction);
  } else {
    asynPrint(pasynUser, ASYN_TRACE_ERROR, 
             "%s:%s, port %s, ERROR writing outValue=0x%x, value=0x%x, mask=0x%x, direction=0x%x, status=%d\n",
             driverName, functionName, this->portName, outValue, value, mask, direction, status);
  }
  return (status==0) ? asynSuccess : asynError;
}

asynStatus USB1608G::readFloat32Array(asynUser *pasynUser, epicsFloat32 *value, size_t nElements, size_t *nIn)
{
  int function = pasynUser->reason;
  int addr;
  int numPoints;
  epicsFloat32 *inPtr;
  static const char *functionName = "readFloat32Array";
  
  this->getAddress(pasynUser, &addr);
  
  if (function == waveDigWaveform_) {
    if (addr >= NUM_ANALOG_IN) {
      asynPrint(pasynUser, ASYN_TRACE_ERROR,
        "%s:%s: ERROR: addr=%d max=%d\n",
        driverName, functionName, addr, NUM_ANALOG_IN-1);
      return asynError;
    } 
    *nIn = nElements;
    // This should really be the number of points actually available - CHANGE
    if (*nIn > maxInputPoints_) *nIn = maxInputPoints_;
    memcpy(value, waveDigBuffer_[addr], *nIn*sizeof(epicsFloat32));
    return asynSuccess; 
  }

  // All other functions read the waveGen arrays
  if (addr >= NUM_ANALOG_OUT) {
    asynPrint(pasynUser, ASYN_TRACE_ERROR,
      "%s:%s: ERROR: addr=%d max=%d\n",
      driverName, functionName, addr, NUM_ANALOG_OUT-1);
    return asynError;
  } 
  if (function == waveGenUserWF_)
    inPtr = waveGenUserBuffer_[addr];
  else if (function == waveGenInternalWF_)
    inPtr = waveGenInternalBuffer_[addr];
  else if (function == waveGenTimeWF_)
    inPtr = waveGenTimeBuffer_;
  else {
    asynPrint(pasynUser, ASYN_TRACE_ERROR,
      "%s:%s: ERROR: unknown function=%d\n",
      driverName, functionName, function);
    return asynError;
  }
  getIntegerParam(waveGenNumPoints_, &numPoints);
  *nIn = nElements;
  if (*nIn > (size_t) numPoints) *nIn = (size_t) numPoints;
  memcpy(value, inPtr, *nIn*sizeof(epicsFloat32)); 

  return asynSuccess;
}

asynStatus USB1608G::writeFloat32Array(asynUser *pasynUser, epicsFloat32 *value, size_t nElements)
{
  int function = pasynUser->reason;
  int addr;
  static const char *functionName = "writeFloat32Array";
  
  this->getAddress(pasynUser, &addr);
  
  if (function == waveGenUserWF_) {
    if ((addr >= NUM_ANALOG_OUT) || ((int)nElements > maxOutputPoints_)) {
      asynPrint(pasynUser, ASYN_TRACE_ERROR,
        "%s:%s: ERROR: addr=%d max=%d, nElements=%d max=%d\n",
        driverName, functionName, addr, NUM_ANALOG_OUT-1, nElements, maxOutputPoints_);
      return asynError;
    } 
    memcpy(waveGenUserBuffer_[addr], value, nElements*sizeof(epicsFloat32)); 
  }
  else {
    asynPrint(pasynUser, ASYN_TRACE_ERROR,
      "%s:%s: ERROR: unknown function=%d\n",
      driverName, functionName, function);
    return asynError;
  }

  return asynSuccess;
}

void USB1608G::pollerThread()
{
  /* This function runs in a separate thread.  It waits for the poll
   * time */
  static const char *functionName = "pollerThread";
  epicsUInt32 newValue, changedBits, prevInput=0;
  unsigned short biVal;;
  int i;
  unsigned long countVal;
  long wgCount, wgIndex;
  short wgStatus;
  int status;

  while(1) { 
    lock();
    status = cbDIn(boardNum_, AUXPORT, &biVal);
    if (status) 
      asynPrint(pasynUserSelf, ASYN_TRACE_ERROR, 
                "%s:%s: ERROR calling cbDIn, status=%d\n", 
                driverName, functionName, status);
    newValue = biVal;
    changedBits = newValue ^ prevInput;
    if (forceCallback_ || (changedBits != 0)) {
      prevInput = newValue;
      forceCallback_ = 0;
      setUIntDigitalParam(digitalInput_, newValue, 0xFFFFFFFF);
    }
    for (i=0; i<NUM_COUNTERS; i++) {
      status = cbCIn32(boardNum_, i, &countVal);
      if (status)
        asynPrint(pasynUserSelf, ASYN_TRACE_ERROR, 
                  "%s:%s: ERROR calling cbCIn32, status=%d\n", 
                  driverName, functionName, status);
      setIntegerParam(i, counterCounts_, countVal);
    }
    // Poll the status of the waveform generator output
    status = cbGetStatus(boardNum_, &wgStatus, &wgCount, &wgIndex, AOFUNCTION);
    setIntegerParam(waveGenRun_, wgStatus);
    setIntegerParam(waveGenCurrentPoint_, wgIndex);
    for (i=0; i<MAX_SIGNALS; i++) {
      callParamCallbacks(i);
    }
    unlock();
    epicsThreadSleep(pollTime_);
  }
}

/* Report  parameters */
void USB1608G::report(FILE *fp, int details)
{
  int i;
  int counts;
  
  asynPortDriver::report(fp, details);
  fprintf(fp, "  Port: %s, board number=%d\n", 
          this->portName, boardNum_);
  if (details >= 1) {
    fprintf(fp, "  counterCounts = ");
    for (i=0; i<NUM_COUNTERS; i++)
      getIntegerParam(i, counterCounts_, &counts); 
      fprintf(fp, " %d", counts);
    fprintf(fp, "\n");
  }
}

/** Configuration command, called directly or from iocsh */
extern "C" int USB1608GConfig(const char *portName, int boardNum, 
                              int maxInputPoints, int maxOutputPoints)
{
  USB1608G *pUSB1608G = new USB1608G(portName, boardNum, maxInputPoints, maxOutputPoints);
  pUSB1608G = NULL;  /* This is just to avoid compiler warnings */
  return(asynSuccess);
}


static const iocshArg configArg0 = { "Port name",      iocshArgString};
static const iocshArg configArg1 = { "Board number",      iocshArgInt};
static const iocshArg configArg2 = { "Max. input points", iocshArgInt};
static const iocshArg configArg3 = { "Max. output points",iocshArgInt};
static const iocshArg * const configArgs[] = {&configArg0,
                                              &configArg1,
                                              &configArg2,
                                              &configArg3};
static const iocshFuncDef configFuncDef = {"USB1608GConfig",4,configArgs};
static void configCallFunc(const iocshArgBuf *args)
{
  USB1608GConfig(args[0].sval, args[1].ival, args[2].ival, args[3].ival);
}

void drvUSB1608GRegister(void)
{
  iocshRegister(&configFuncDef,configCallFunc);
}

extern "C" {
epicsExportRegistrar(drvUSB1608GRegister);
}
