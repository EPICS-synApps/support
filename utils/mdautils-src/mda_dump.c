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


/*****************  mda_dump.c  *****************/

#include <stdio.h>
#include <stdlib.h>

#include "mda-load.h"


#define VERSION "0.1.1"


void mda_dump_header( struct header_struct *header)
{
  int i;

  printf("Version = %g\n", header->version);
  printf("Scan number = %li\n", header->scan_number);
  printf("Data rank = %i\n", header->data_rank);
  
  printf("Largest scan bounds = ");
  for( i = 0; i < header->data_rank; i++)
    {
      if( i)
	printf(" x ");
      printf("%li", header->dimensions[i]);
    }
  printf("\n");

  printf("Regularity = %s\n",  header->regular ? 
	 "TRUE (No dimensions changed during scan)" :
	 "FALSE (Dimensions changed during scan)" );

  printf("File offset to extra PV's = %li bytes.\n", header->extra_pvs_offset);
   
  printf("\n\n");
}


void mda_dump_scan( struct scan_struct *scan)
{
  int i, j;


  printf("This scan's rank = %i.\n", scan->scan_rank);
  printf("Number of requested points = %li.\n", scan->requested_points);
  printf("Last completed point = %li.\n", scan->last_point);

  if( scan->scan_rank > 1)
    {
      printf("Offsets to lower scans = ");
      for( i = 0; i < scan->requested_points; i++)
	{
	  if( i)
	    printf(", ");
	  printf("%li", scan->offsets[i]);
	}
      printf("\n");
    }

  printf("Scan name = \"%s\".\n", scan->name);
  printf("Scan time = \"%s\".\n", scan->time);

  printf("Number of positioners = %i.\n", scan->number_positioners);
  printf("Number of detectors = %i.\n", scan->number_detectors);
  printf("Number of triggers = %i.\n", scan->number_triggers);

  for( i = 0; i < scan->number_positioners; i++)
    {
      printf( "\nPositioner Data Set #%i\n", i+1);

      printf("    %20s: %i\n", "Positioner", 
	     scan->positioners[i]->number + 1);
      printf("    %20s: %s\n", "Name", 
	     scan->positioners[i]->name);
      printf("    %20s: %s\n", "Description", 
	     scan->positioners[i]->description);
      printf("    %20s: %s\n", "Step Mode", 
	     scan->positioners[i]->step_mode);
      printf("    %20s: %s\n", "Unit", 
	     scan->positioners[i]->unit);
      printf("    %20s: %s\n", "Readback Name", 
	     scan->positioners[i]->readback_name);
      printf("    %20s: %s\n", "Readback Description", 
	     scan->positioners[i]->readback_description );
      printf("    %20s: %s\n", "Readback Unit", 
	     scan->positioners[i]->readback_unit);
    }

  for( i = 0; i < scan->number_detectors; i++)
    {
      printf( "\nDetector Data Set #%i\n", i+1);

      printf("    %12s: %2i\n", "Detector", 
	     scan->detectors[i]->number + 1);
      printf("    %12s: %s\n", "Name", 
	      scan->detectors[i]->name);
      printf("    %12s: %s\n", "Description", 
	      scan->detectors[i]->description);
      printf("    %12s: %s\n", "Unit", 
	      scan->detectors[i]->unit);
    }

  for( i = 0; i < scan->number_triggers; i++)
    {
      printf("\nTrigger #%i\n", i+1);

      printf( "    %s: %i\n", "Trigger", scan->triggers[i]->number + 1);
      printf( "    %s: %s\n", "Name", scan->triggers[i]->name);
      printf( "    %s: %g\n", "Command", scan->triggers[i]->command);
    }

  for( i = 0; i < scan->number_positioners; i++)
    {
      printf("\nPositioner #%i data:\n", i+1);
      for( j = 0; j < scan->requested_points; j++)
	printf("%.9lg ", (scan->positioners_data[i])[j]);
      printf("\n");
    }

  for( i = 0; i < scan->number_detectors; i++)
    {
      printf("\nDetector #%i data:\n", i+1);
      for( j = 0; j < scan->requested_points; j++)
	printf("%.9g ", (scan->detectors_data[i])[j]);
      printf("\n");
    }

  if( scan->scan_rank > 1)
    for( i = 0; (i < scan->requested_points) && 
	   (scan->sub_scans[i] != NULL); i++)
      {
	printf("\n\n%i-D Subscan #%i\n\n", scan->scan_rank - 1, i+1);
	mda_dump_scan( scan->sub_scans[i]);
      }

}


void mda_dump_extra( struct extra_struct *extra)
{
  int i, j;

  printf("\n\nNumber of Extra PV's = %i.\n", extra->number_pvs);

  for( i = 0 ; i < extra->number_pvs; i++)
    { 
      printf("\nExtra PV #%i:\n", i+1);

      printf("    Name = %s\n", extra->pvs[i]->name);
      printf("    Description = %s\n", extra->pvs[i]->description);

      if( extra->pvs[i]->type != DBR_STRING)
	{
	  printf("    Count = %i\n", extra->pvs[i]->count);
	  printf("    Unit = %s\n", extra->pvs[i]->unit);
	}

      switch(extra->pvs[i]->type)
	{
	case DBR_STRING:
	  printf("    Type = %i (DBR_STRING)\n", extra->pvs[i]->type);
	  printf("    Value = \"%s\"\n", 
		 (char *) extra->pvs[i]->values);
	  break;
	case DBR_CTRL_CHAR:
	  printf("    Type = %i (DBR_CTRL_CHAR)\n", extra->pvs[i]->type);
	  printf("    Value%s = ", (extra->pvs[i]->count == 1) ? "" : "s");
	  for( j = 0; j < extra->pvs[i]->count; j++)
	    {
	      if( j)
		printf(", ");
	      printf("%i", ((char *) extra->pvs[i]->values)[j]);
	    }
	  printf("\n");
	  break;
	case DBR_CTRL_SHORT:
	  printf("    Type = %i (DBR_CTRL_SHORT\n", extra->pvs[i]->type);
	  printf("    Value%s = ", (extra->pvs[i]->count == 1) ? "" : "s");
	  for( j = 0; j < extra->pvs[i]->count; j++)
	    {
	      if( j)
		printf(", ");
	      printf("%i", ((short *) extra->pvs[i]->values)[j]);
	    }
	  printf("\n");
	  break;
	case DBR_CTRL_LONG:
	  printf("    Type = %i (DBR_CTRL_LONG)\n", extra->pvs[i]->type);
	  printf("    Value%s = ", (extra->pvs[i]->count == 1) ? "" : "s");
	  for( j = 0; j < extra->pvs[i]->count; j++)
	    {
	      if( j)
		printf(", ");
	      printf("%li", ((long *) extra->pvs[i]->values)[j]);
	    }
	  printf("\n");
	  break;
	case DBR_CTRL_FLOAT:
	  printf("    Type = %i (DBR_CTRL_FLOAT)\n", extra->pvs[i]->type);
	  printf("    Value%s = ", (extra->pvs[i]->count == 1) ? "" : "s");
	  for( j = 0; j < extra->pvs[i]->count; j++)
	    {
	      if( j)
		printf(", ");
	      printf("%.9g", ((float *) extra->pvs[i]->values)[j]);
	    }
	  printf("\n");
	  break;
	case DBR_CTRL_DOUBLE:
	  printf("    Type = %i (DBR_CTRL_DOUBLE)\n", extra->pvs[i]->type);
	  printf("    Value%s = ", (extra->pvs[i]->count == 1) ? "" : "s");
	  for( j = 0; j < extra->pvs[i]->count; j++)
	    {
	      if( j)
		printf(", ");
	      printf("%.9lg", ((double *) extra->pvs[i]->values)[j]);
	    }
	  printf("\n");
	  break;
	}
    } 
}



int mda_dump( char *file)
{
  FILE *input;
  struct mda_struct *mda;

  if( (input = fopen( file, "r")) == NULL)
    {
      fprintf(stderr, "Can't open file!\n");
      return 1;
    }
  
  if( (mda = mda_load( input)) == NULL )
    {
      fprintf(stderr, "Loading file failed!\n");
      return 1;
    }

  fclose(input);

  mda_dump_header( mda->header);
  mda_dump_scan( mda->scan);
  if( mda->extra != NULL)
    mda_dump_extra( mda->extra);

  mda_unload(mda);

  return 0;
}


int main( int argc, char *argv[])
{
  if( argc != 2)
    {
      printf("mda-dump  %s  --  Does a dump of everything in an "
	     "EPICS MDA file.\n", VERSION);
      printf("  usage:  mda-dump <MDA file>\n");
      return 0;
    }

  printf("********** mda-dump %s generated output **********\n\n\n", VERSION);

  if( mda_dump( argv[1]) )
    {
      fprintf(stderr, "Error!\n");
      return 1;
    }
  
  return 0;
}

