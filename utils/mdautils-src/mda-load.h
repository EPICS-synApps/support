/*************************************************************************\
* Copyright (c) 2010 UChicago Argonne, LLC,
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory
  Send comments to dohnarms@anl.gov
  
  0.1   -- July 2005
  0.1.1 -- December 2006
           Added support for files that have more than 32k points
  0.2.0 -- October 2007
           Added several new functions for accessing scans or the extra PV's
                 without loading the entire file.
  0.2.1 -- March 2009
           Removed several memory leaks.
  1.0   -- October 2009
           Renamed structures.
  1.1   -- November 2010

 */


/******************  mda_load.h  **************/


#include <stdio.h>


struct mda_header
{
  float  version;
  long   scan_number;
  short  data_rank;
  long  *dimensions;
  short  regular;
  long   extra_pvs_offset;
};


struct mda_positioner
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


struct mda_detector
{
  short number;
  char *name;
  char *description;
  char *unit;
};


struct mda_trigger
{
  short number;
  char *name;
  float command;
};


struct mda_scan
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

  struct mda_positioner **positioners;  
  struct mda_detector **detectors;
  struct mda_trigger **triggers;
  double **positioners_data;
  float  **detectors_data;

  struct mda_scan **sub_scans;
};

enum PV_TYPES { DBR_STRING=0,     DBR_CTRL_CHAR=32,  DBR_CTRL_SHORT=29, 
		DBR_CTRL_LONG=33, DBR_CTRL_FLOAT=30, DBR_CTRL_DOUBLE=34 };

struct mda_pv
{
  char *name;
  char *description;
  short type;
  short count;
  char *unit;
  char *values; // used to be void *, but gave a lot of headaches
};


struct mda_extra
{
  short number_pvs;
  struct mda_pv **pvs;
};


struct mda_file
{
  struct mda_header *header;
  struct mda_scan *scan;
  struct mda_extra *extra;
};


////////////////////////

struct mda_scaninfo
{
  short scan_rank;          // redundant
  long  requested_points;   // redundant
  char *name;
  short number_positioners;
  short number_detectors;
  short number_triggers;

  struct mda_positioner **positioners;  
  struct mda_detector **detectors;
  struct mda_trigger **triggers;
};

struct mda_fileinfo
{
  float  version;
  long   scan_number;
  short  data_rank;
  long  *dimensions;
  short  regular;
  long   last_topdim_point;
  char  *time;
  struct mda_scaninfo **scaninfos;
};

////////////////////////


struct mda_file *mda_load( FILE *fptr);
struct mda_header *mda_header_load( FILE *fptr);
struct mda_scan *mda_scan_load( FILE *fptr);
struct mda_scan *mda_subscan_load( FILE *fptr, int depth, int *indices, 
				      int recursive);
struct mda_extra *mda_extra_load( FILE *fptr);


void mda_unload( struct mda_file *mda);
void mda_header_unload( struct mda_header *header);
void mda_scan_unload( struct mda_scan *scan);
void mda_extra_unload( struct mda_extra *extra);


struct mda_fileinfo *mda_info_load( FILE *fptr);
void mda_info_unload( struct mda_fileinfo *fileinfo);
