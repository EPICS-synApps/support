/*************************************************************************\
* Copyright (c) 2005 The University of Chicago, 
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory, MHATT/XOR
  Send comments to dohnarms@anl.gov
  
  0.1   -- July 2005
  0.1.1 -- December 2006
           Added support for files that have more than 32k points

 */


/******************  mda_load.h  **************/


#include <stdio.h>


struct header_struct
{
  float  version;
  long   scan_number;
  short  data_rank;
  long  *dimensions;
  short  regular;
  long   extra_pvs_offset;
};


struct positioner_struct
{
  short number;
  char *name;
  char *description;
  char *step_mode;
  char *unit;
  char *readback_name;
  char *readback_description;
  char *readback_unit;
};


struct detector_struct
{
  short number;
  char *name;
  char *description;
  char *unit;
};


struct trigger_struct
{
  short number;
  char *name;
  float command;
};


struct scan_struct
{
  short scan_rank;
  long  requested_points;
  long  last_point;
  long *offsets;
  char *name;
  char *time;
  short number_positioners;
  short number_detectors;
  short number_triggers;

  struct positioner_struct **positioners;  
  struct detector_struct **detectors;
  struct trigger_struct **triggers;
  double **positioners_data;
  float  **detectors_data;

  struct scan_struct **sub_scans;
};

enum PV_TYPES { DBR_STRING=0,     DBR_CTRL_CHAR=32,  DBR_CTRL_SHORT=29, 
		DBR_CTRL_LONG=33, DBR_CTRL_FLOAT=30, DBR_CTRL_DOUBLE=34 };

struct pv_struct
{
  char *name;
  char *description;
  short type;
  short count;
  char *unit;
  void *values;
};


struct extra_struct
{
  short number_pvs;
  struct pv_struct **pvs;
};


struct mda_struct
{
  struct header_struct *header;
  struct scan_struct *scan;
  struct extra_struct *extra;
};




struct mda_struct *mda_load( FILE *fptr);
void mda_unload( struct mda_struct *mda);

