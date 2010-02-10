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



/****************  mda_loader.c  **********************/


#include <stdlib.h>
#include <string.h>

#include <rpc/types.h>
#include <rpc/xdr.h>
#include "mda-load.h"



static bool_t xdr_counted_string( XDR *xdrs, char **p)
{
  int mode;
  short length;
 
  mode = (xdrs->x_op == XDR_DECODE);

  /* If writing, obtain the length */
  if( !mode) 
    length = strlen(*p);
 
  /* Transfer the string length */
  if( !xdr_short(xdrs, &length)) 
    return 0;

  /* If reading, obtain room for the string */
  if (mode)
    {
      *p = (char *) malloc( (length + 1) * sizeof(char) );
      (*p)[length] = '\0'; /* Null termination */
    }

  /* If the string length is nonzero, transfer it */
  return(length ? xdr_string(xdrs, p, length) : 1);
}


static struct header_struct *header_read( XDR *xdrs)
{
  struct header_struct *header;

  header = (struct header_struct *) malloc( sizeof(struct header_struct));

  if( !xdr_float(xdrs, &(header->version) ))
    return NULL;

  if( !xdr_long(xdrs, &(header->scan_number) ))
    return NULL;

  if( !xdr_short(xdrs, &(header->data_rank) ))
    return NULL;

  header->dimensions = (long *) malloc( header->data_rank * sizeof(long));
  if( !xdr_vector( xdrs, (char *) header->dimensions, header->data_rank, 
		   sizeof( long), (xdrproc_t) xdr_long))
    return NULL;

  if( !xdr_short(xdrs, &(header->regular) ))
    return NULL;

  if( !xdr_long(xdrs, &(header->extra_pvs_offset) )) 
    return NULL;

  return header;
}


static struct positioner_struct *positioner_read(XDR *xdrs)
{
  struct positioner_struct *positioner;


  positioner = (struct positioner_struct *) 
    malloc( sizeof(struct positioner_struct));

  if( !xdr_short(xdrs, &(positioner->number) ))
    return NULL;

  if( !xdr_counted_string( xdrs, &(positioner->name) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->description) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->step_mode) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->unit) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->readback_name) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->readback_description) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(positioner->readback_unit) ) )
    return NULL;

  return positioner;
}



static struct detector_struct *detector_read(XDR *xdrs)
{
  struct detector_struct *detector;


  detector = (struct detector_struct *) 
    malloc( sizeof(struct detector_struct));

  if( !xdr_short(xdrs, &(detector->number) ))
    return NULL;

  if( !xdr_counted_string( xdrs, &(detector->name) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(detector->description) ) )
    return NULL;
  if( !xdr_counted_string( xdrs, &(detector->unit) ) )
    return NULL;

  return detector;
}




static struct trigger_struct *trigger_read(XDR *xdrs)
{
  struct trigger_struct *trigger;


  trigger = (struct trigger_struct *) malloc( sizeof(struct trigger_struct));

  if( !xdr_short(xdrs, &(trigger->number) ))
    return NULL;
  if( !xdr_counted_string( xdrs, &(trigger->name ) ))
    return NULL;
  if( !xdr_float(xdrs, &(trigger->command) ))
    return NULL;

  return trigger;
}



/* this function is recursive, due to the nature of the file format */
static struct scan_struct *scan_read(XDR *xdrs)
{
  struct scan_struct *scan;
 
  int i;

  scan = (struct scan_struct *) malloc( sizeof(struct scan_struct));


  if( !xdr_short(xdrs, &(scan->scan_rank) ))
    return NULL;
  if( !xdr_long(xdrs, &(scan->requested_points) ))
    return NULL;
    if( !xdr_long(xdrs, &(scan->last_point) ))
    return NULL;

  if( scan->scan_rank > 1)
    {
      scan->offsets = (long *) malloc( scan->requested_points * sizeof(long));
      if( !xdr_vector( xdrs, (char *) scan->offsets, scan->requested_points, 
		       sizeof( long), (xdrproc_t) xdr_long))
	return NULL;
    }
  else
    scan->offsets = NULL;

  if( !xdr_counted_string( xdrs, &(scan->name) ))
    return NULL;
  if( !xdr_counted_string( xdrs, &(scan->time) ))
    return NULL;

  if( !xdr_short(xdrs, &(scan->number_positioners) ))
    return NULL;
  if( !xdr_short(xdrs, &(scan->number_detectors) ))
    return NULL;
  if( !xdr_short(xdrs, &(scan->number_triggers) ))
    return NULL;



  scan->positioners = (struct positioner_struct **) 
    malloc( scan->number_positioners * sizeof(struct positioner_struct *));
  for( i = 0; i < scan->number_positioners; i++)
    {
      if( (scan->positioners[i] = positioner_read( xdrs)) == NULL )
	return NULL;
    }

  scan->detectors = (struct detector_struct **) 
    malloc( scan->number_detectors * sizeof(struct detector_struct *));
  for( i = 0; i < scan->number_detectors; i++)
    {
      if( (scan->detectors[i] = detector_read( xdrs)) == NULL )
	return NULL;
    }

  scan->triggers = (struct trigger_struct **) 
    malloc( scan->number_triggers * sizeof(struct trigger_struct *));
  for( i = 0; i < scan->number_triggers; i++)
    {
      if( (scan->triggers[i] = trigger_read( xdrs)) == NULL )
	return NULL;
    }

  scan->positioners_data = (double **) 
    malloc( scan->number_positioners * sizeof(double *));
  for( i = 0 ; i < scan->number_positioners; i++)
    {
      scan->positioners_data[i] = (double *) 
	malloc( scan->requested_points * sizeof(double));
      if( !xdr_vector( xdrs, (char *) scan->positioners_data[i], 
		       scan->requested_points, 
		       sizeof( double), (xdrproc_t) xdr_double))
	return NULL;
    }

  scan->detectors_data = (float **) 
    malloc( scan->number_detectors * sizeof(float *));
  for( i = 0 ; i < scan->number_detectors; i++)
    {
      scan->detectors_data[i] = (float *) 
	malloc( scan->requested_points * sizeof(float));
      if( !xdr_vector( xdrs, (char *) scan->detectors_data[i], 
		       scan->requested_points, 
		       sizeof( float), (xdrproc_t) xdr_float))
	return NULL;
    }

  if( scan->scan_rank > 1)
    {
      scan->sub_scans = (struct scan_struct **)
	malloc( scan->requested_points * sizeof( struct scan_struct *) );
      for( i = 0; i < scan->requested_points; i++)
	scan->sub_scans[i] = NULL;
      for( i = 0 ; (i < scan->requested_points) && 
	     (scan->offsets[i] != 0); i++)
	/* it recurses here */
	scan->sub_scans[i] = scan_read(xdrs);
    }
  else
    scan->sub_scans = NULL;


  return scan;
}




static struct pv_struct *pv_read(XDR *xdrs)
{
  struct pv_struct *pv;

  int   byte_count;

  pv = (struct pv_struct *) malloc( sizeof(struct pv_struct));


  if( !xdr_counted_string( xdrs, &(pv->name) ))
    return NULL;
  if( !xdr_counted_string( xdrs, &(pv->description) ))
    return NULL;
  if( !xdr_short(xdrs, &(pv->type) ))
    return NULL;

  if( pv->type != DBR_STRING)
    {
      if( !xdr_short(xdrs, &(pv->count) ))
	return NULL;
      if( !xdr_counted_string( xdrs, &(pv->unit) ))
	return NULL;
    }
  else
    {
      pv->count = 0;
      pv->unit = NULL;
    }

  switch( pv->type)
    {
    case DBR_STRING:
      if( !xdr_counted_string( xdrs, (char **) &(pv->values) ))
	return NULL;
      break;
    case DBR_CTRL_CHAR:
      if( !xdr_bytes( xdrs, (char **) &(pv->values), &byte_count, pv->count ) )
	return NULL;
      pv->count = byte_count;
      break;
    case DBR_CTRL_SHORT:
      pv->values = malloc( pv->count * sizeof(short));
      if( !xdr_vector( xdrs, (char *) pv->values, pv->count, 
		       sizeof( short), (xdrproc_t) xdr_short))
	return NULL;
      break;
    case DBR_CTRL_LONG:
      pv->values = malloc( pv->count * sizeof(long));
      if( !xdr_vector( xdrs, (char *) pv->values, pv->count, 
		       sizeof( long), (xdrproc_t) xdr_long))
	return NULL;
      break;
    case DBR_CTRL_FLOAT:
      pv->values = malloc( pv->count * sizeof(float));
      if( !xdr_vector( xdrs, (char *) pv->values, pv->count, 
		       sizeof( float), (xdrproc_t) xdr_float))
	return NULL;
      break;
    case DBR_CTRL_DOUBLE:
      pv->values = malloc( pv->count * sizeof(double));
      if( !xdr_vector( xdrs, (char *) pv->values, pv->count, 
		       sizeof( double), (xdrproc_t) xdr_double))
	return NULL;
      break;
    }

  return pv;
}




static struct extra_struct *extra_read(XDR *xdrs)
{
  struct extra_struct *extra;

  int i;

  extra = (struct extra_struct *) malloc( sizeof(struct extra_struct));


  if( !xdr_short(xdrs, &(extra->number_pvs) ))
    return NULL;

  extra->pvs = (struct pv_struct **) 
    malloc( extra->number_pvs * sizeof( struct pv_struct *) );

   for( i = 0 ; i < extra->number_pvs; i++)
     { 
       if( (extra->pvs[i] = pv_read(xdrs)) == NULL )
	 return NULL;
     } 

  return extra;
}


/////////////////////////////////////////////////////////////

/* this function is recursive */
static void scan_unload( struct scan_struct *scan)
{
  int i;

  if( scan->scan_rank > 1)
    {
      for( i = 0; (i < scan->requested_points) && (scan->sub_scans[i]); i++)
	scan_unload( scan->sub_scans[i]);
    }
  
  free( scan->offsets);
  free( scan->name);
  free( scan->time);

  for( i = 0; i < scan->number_positioners; i++)
    {
      free(scan->positioners[i]->name);
      free(scan->positioners[i]->description);
      free(scan->positioners[i]->step_mode);
      free(scan->positioners[i]->unit);
      free(scan->positioners[i]->readback_name);
      free(scan->positioners[i]->readback_description);
      free(scan->positioners[i]->readback_unit);
    }
  free( scan->positioners);

  for( i = 0; i < scan->number_triggers; i++)
    free(scan->triggers[i]->name);
  free( scan->triggers);

  for( i = 0; i < scan->number_detectors; i++)
    {
      free(scan->detectors[i]->name);
      free(scan->detectors[i]->description);
      free(scan->detectors[i]->unit);
    }
  free( scan->detectors);

  for( i = 0 ; i < scan->number_positioners; i++)
    free( scan->positioners_data[i] );
  free( scan->positioners_data );

  for( i = 0 ; i < scan->number_detectors; i++)
    free( scan->detectors_data[i] );
  free( scan->detectors_data );

  free( scan);
}


//////////////////////////////////////////////////////////////
/*   Only public functions   */

struct mda_struct *mda_load( FILE *fptr)
{
  XDR xdrstream;
  struct mda_struct *mda;

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);

  mda = (struct mda_struct *) malloc( sizeof(struct mda_struct));

  if( (mda->header = header_read( &xdrstream)) == NULL)
    return NULL;
  if( (mda->scan = scan_read( &xdrstream)) == NULL)
    return NULL;
  if( mda->header->extra_pvs_offset)
    {
      if( (mda->extra = extra_read( &xdrstream)) == NULL)
	return NULL;
    }
  else
    mda->extra = NULL;
  
  xdr_destroy( &xdrstream);

  return mda;
}


/*  deallocates all the memory used for the mda file loading  */
void mda_unload( struct mda_struct *mda)
{
  int i;


  free( mda->header->dimensions);
  free( mda->header);

  /* this function recurses */
  scan_unload(mda->scan);

  if( mda->extra)
    {
      for( i = 0; i < mda->extra->number_pvs; i++)
	{
	  free( mda->extra->pvs[i]->name);
	  free( mda->extra->pvs[i]->description);
	  if( mda->extra->pvs[i]->unit)
	    free( mda->extra->pvs[i]->unit);
	  free( mda->extra->pvs[i]->values);
	}
      free( mda->extra->pvs);
      free( mda->extra);
    }


  free( mda);

}
