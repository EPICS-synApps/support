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
           Added support for files that have more than 32k points.
  0.2.0 -- October 2007
           Added several new functions for accessing scans or the extra PV's
                 without loading the entire file (never publically released).
  0.2.1 -- March 2009
           Removed several memory leaks. Made trace structure consistent.
  1.0.0 -- October 2009
           Release with vastly changed mda-utils.
           Renamed structures to give them "mda_" prefix.
  1.0.1 -- June 2010
           Added checking in header code to make sure there were no screwy
           dimensions, by looking for 0xFFFFFFFF in one of them.
  1.0.2 -- August 2010
           Use offsets to load scans, as bad files sometimes have them out 
           of order.
  1.1   -- November 2010

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
  long int length;
 
  mode = (xdrs->x_op == XDR_DECODE);

  /* If writing, obtain the length */
  if( !mode) 
    length = strlen(*p);
 
  /* Transfer the string length */
  if( !xdr_long(xdrs, &length)) 
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


static struct mda_header *header_read( XDR *xdrs)
{
  struct mda_header *header;

  header = (struct mda_header *) 
    malloc( sizeof(struct mda_header));

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

  {  // need to do error checking on dimensions!
    int i;

    for( i = 0; i < header->data_rank; i++)
      if(  header->dimensions[i] == 0xFFFFFFFF) // -1 is it was short, not long
        {
          free( header);
          free( header->dimensions);
          return NULL;
        }
  }

  return header;
}


static struct mda_positioner *positioner_read(XDR *xdrs)
{
  struct mda_positioner *positioner;


  positioner = (struct mda_positioner *) 
    malloc( sizeof(struct mda_positioner));

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



static struct mda_detector *detector_read(XDR *xdrs)
{
  struct mda_detector *detector;


  detector = (struct mda_detector *) 
    malloc( sizeof(struct mda_detector));

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




static struct mda_trigger *trigger_read(XDR *xdrs)
{
  struct mda_trigger *trigger;


  trigger = (struct mda_trigger *) 
    malloc( sizeof(struct mda_trigger));

  if( !xdr_short(xdrs, &(trigger->number) ))
    return NULL;
  if( !xdr_counted_string( xdrs, &(trigger->name ) ))
    return NULL;
  if( !xdr_float(xdrs, &(trigger->command) ))
    return NULL;

  return trigger;
}



/* this function is recursive, due to the nature of the file format */
/* it can be turned off by making recursive 0 */
static struct mda_scan *scan_read(XDR *xdrs, int recursive)
{
  struct mda_scan *scan;
 
  int i;

  scan = (struct mda_scan *) malloc( sizeof(struct mda_scan));


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



  scan->positioners = (struct mda_positioner **) 
    malloc( scan->number_positioners * sizeof(struct mda_positioner *));
  for( i = 0; i < scan->number_positioners; i++)
    {
      if( (scan->positioners[i] = positioner_read( xdrs)) == NULL )
	return NULL;
    }

  scan->detectors = (struct mda_detector **) 
    malloc( scan->number_detectors * sizeof(struct mda_detector *));
  for( i = 0; i < scan->number_detectors; i++)
    {
      if( (scan->detectors[i] = detector_read( xdrs)) == NULL )
	return NULL;
    }

  scan->triggers = (struct mda_trigger **) 
    malloc( scan->number_triggers * sizeof(struct mda_trigger *));
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

  if( (scan->scan_rank > 1) && recursive)
    {
      scan->sub_scans = (struct mda_scan **)
	malloc( scan->requested_points * sizeof( struct mda_scan *) );
      for( i = 0; i < scan->requested_points; i++)
	scan->sub_scans[i] = NULL;
      for( i = 0 ; (i < scan->requested_points) && 
	     (scan->offsets[i] != 0); i++)
	/* it recurses here */
        {
          if( xdr_getpos( xdrs) != scan->offsets[i])
            {
              if( !xdr_setpos( xdrs,scan->offsets[i] ) )
                return NULL;
            }
          scan->sub_scans[i] = scan_read(xdrs, recursive);
        }
    }
  else
    scan->sub_scans = NULL;


  return scan;
}




static struct mda_pv *pv_read(XDR *xdrs)
{
  struct mda_pv *pv;

  unsigned int   byte_count;

  pv = (struct mda_pv *) malloc( sizeof(struct mda_pv));


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
      if( !xdr_counted_string( xdrs, &(pv->values) ))
	return NULL;
      break;
    case DBR_CTRL_CHAR:
      if( !xdr_bytes( xdrs, &(pv->values), &byte_count, pv->count ) )
	return NULL;
      pv->count = byte_count;
      break;
    case DBR_CTRL_SHORT:
      pv->values = (char *) malloc( pv->count * sizeof(short));
      if( !xdr_vector( xdrs, pv->values, pv->count, 
		       sizeof( short), (xdrproc_t) xdr_short))
	return NULL;
      break;
    case DBR_CTRL_LONG:
      pv->values = (char *) malloc( pv->count * sizeof(long));
      if( !xdr_vector( xdrs, pv->values, pv->count, 
		       sizeof( long), (xdrproc_t) xdr_long))
	return NULL;
      break;
    case DBR_CTRL_FLOAT:
      pv->values = (char *) malloc( pv->count * sizeof(float));
      if( !xdr_vector( xdrs, pv->values, pv->count, 
		       sizeof( float), (xdrproc_t) xdr_float))
	return NULL;
      break;
    case DBR_CTRL_DOUBLE:
      pv->values = (char *) malloc( pv->count * sizeof(double));
      if( !xdr_vector( xdrs, pv->values, pv->count, 
		       sizeof( double), (xdrproc_t) xdr_double))
	return NULL;
      break;
    }

  return pv;
}




static struct mda_extra *extra_read(XDR *xdrs)
{
  struct mda_extra *extra;

  int i;

  extra = (struct mda_extra *) malloc( sizeof(struct mda_extra));


  if( !xdr_short(xdrs, &(extra->number_pvs) ))
    return NULL;

  extra->pvs = (struct mda_pv **) 
    malloc( extra->number_pvs * sizeof( struct mda_pv *) );

   for( i = 0 ; i < extra->number_pvs; i++)
     { 
       if( (extra->pvs[i] = pv_read(xdrs)) == NULL )
	 return NULL;
     } 

  return extra;
}


/////////////////////////////////////////////////////////////




struct mda_file *mda_load( FILE *fptr)
{
  XDR xdrstream;
  struct mda_file *mda;

  rewind( fptr);

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);

  mda = (struct mda_file *) malloc( sizeof(struct mda_file));

  if( (mda->header = header_read( &xdrstream)) == NULL)
    return NULL;
  if( (mda->scan = scan_read( &xdrstream, 1)) == NULL)
    return NULL;
  if( mda->header->extra_pvs_offset)
    {
      if( !xdr_setpos( &xdrstream, mda->header->extra_pvs_offset ))
        return NULL;
      if( (mda->extra = extra_read( &xdrstream)) == NULL)
	return NULL;
    }
  else
    mda->extra = NULL;
  
  xdr_destroy( &xdrstream);

  return mda;
}


struct mda_header *mda_header_load( FILE *fptr)
{
  XDR xdrstream;
  struct mda_header *header;

  rewind( fptr);

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);

  if( (header = header_read( &xdrstream)) == NULL)
    return NULL;


  xdr_destroy( &xdrstream);
  
  return header;
}





struct mda_scan *mda_scan_load( FILE *fptr)
{
  return mda_subscan_load( fptr, 0, NULL, 1);
}


struct mda_scan *mda_subscan_load( FILE *fptr, int depth, int *indices, 
                                          int recursive)
{
  struct mda_scan *scan;

  XDR xdrstream;
  struct mda_header *header;

  rewind( fptr);

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);

  if( (header = header_read( &xdrstream)) == NULL)
    return NULL;

  if( (depth < 0) || (depth >= header->data_rank ) )
    return NULL;

  if( depth)
    {
      int i;

      short scan_rank;
      long  requested_points;
      long  last_point;
      long *offsets;

      for( i = 0; i < depth; i++)
	{
	  if( indices[i] >= header->dimensions[i])
	    return NULL;
	}

      for( i = 0; i < depth; i++)
	{
	  if( !xdr_short(&xdrstream, &scan_rank ))
	    return NULL;
	  if( scan_rank == 1)  // this case should not happen
	    return NULL;

	  if( !xdr_long(&xdrstream, &requested_points ))
	    return NULL;

	  if( !xdr_long(&xdrstream, &last_point ))
	    return NULL;
	  if( indices[i] >= last_point)
	    return NULL;


	  offsets = (long *) malloc( requested_points * sizeof(long));
	  if( !xdr_vector( &xdrstream, (char *) offsets, requested_points, 
			   sizeof( long), (xdrproc_t) xdr_long))
	    return NULL;

	  if( offsets[indices[i]])
	    fseek( fptr, offsets[indices[i]], SEEK_SET);
	  else
	    return NULL;

	  free( offsets);
	}
    }

  if( (scan = scan_read( &xdrstream, recursive)) == NULL)
    return NULL;

  
  xdr_destroy( &xdrstream);

  mda_header_unload(header);

  return scan;
}


// logic here is screwy, as a NULL return could mean there are no extra PV's
struct mda_extra *mda_extra_load( FILE *fptr)
{
  struct mda_extra *extra;

  XDR xdrstream;
  struct mda_header *header;


  rewind( fptr);

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);

  if( (header = header_read( &xdrstream)) == NULL)
    return NULL;


  if( header->extra_pvs_offset)
    {
      fseek( fptr, header->extra_pvs_offset, SEEK_SET);
      if( (extra = extra_read( &xdrstream)) == NULL)
	return NULL;
    }
  else
    extra = NULL;


  xdr_destroy( &xdrstream);

  mda_header_unload(header);

  return extra;
}


///////////////////////////////////////////////////////////////////
// unloaders


void mda_header_unload(struct mda_header *header)
{
  free( header->dimensions);
  free( header);
}


/* this function is recursive */
void mda_scan_unload( struct mda_scan *scan)
{
  int i;

  if( (scan->scan_rank > 1) && (scan->sub_scans != NULL))
    {
      for( i = 0; (i < scan->requested_points) && (scan->sub_scans[i] != NULL); 
           i++)
	mda_scan_unload( scan->sub_scans[i]);
    }
  free( scan->sub_scans);
  
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
      free(scan->positioners[i]);
    }
  free( scan->positioners);

  for( i = 0; i < scan->number_triggers; i++)
    {
      free(scan->triggers[i]->name);
      free(scan->triggers[i]);
    }      
  free( scan->triggers);

  for( i = 0; i < scan->number_detectors; i++)
    {
      free(scan->detectors[i]->name);
      free(scan->detectors[i]->description);
      free(scan->detectors[i]->unit);
      free(scan->detectors[i]);
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


void mda_extra_unload(struct mda_extra *extra)
{
  int i;

  if( extra)
    {
      for( i = 0; i < extra->number_pvs; i++)
	{
	  free( extra->pvs[i]->name);
	  free( extra->pvs[i]->description);
	  if( extra->pvs[i]->unit)
	    free( extra->pvs[i]->unit);
	  free( extra->pvs[i]->values);
	  free( extra->pvs[i]);
	}
      free( extra->pvs);
      free( extra);
    }
}


/*  deallocates all the memory used for the mda file loading  */
void mda_unload( struct mda_file *mda)
{
  mda_header_unload(mda->header);
  mda_scan_unload(mda->scan);
  mda_extra_unload(mda->extra);

  free( mda);
}




//////////////////////////////////////////////////////////////////////////


struct mda_fileinfo *mda_info_load( FILE *fptr)
{
  struct mda_fileinfo *fileinfo;

  XDR xdrstream;

  long  last_point;
  long *offsets;
  char *time;

  int i, j;

  long t;
  
 
  rewind( fptr);

  xdrstdio_create(&xdrstream, fptr, XDR_DECODE);


  fileinfo = (struct mda_fileinfo *) 
    malloc( sizeof(struct mda_fileinfo));
  
  if( !xdr_float(&xdrstream, &(fileinfo->version) ))
    return NULL;

  if( !xdr_long(&xdrstream, &(fileinfo->scan_number) ))
    return NULL;

  if( !xdr_short(&xdrstream, &(fileinfo->data_rank) ))
    return NULL;

  fileinfo->dimensions = (long *) malloc( fileinfo->data_rank * sizeof(long));
  if( !xdr_vector( &xdrstream, (char *) fileinfo->dimensions, 
                   fileinfo->data_rank, sizeof( long), (xdrproc_t) xdr_long))
    return NULL;

  for( i = 0; i < fileinfo->data_rank; i++)
    if(  fileinfo->dimensions[i] == 0xFFFFFFFF) // -1 is it was short, not long
      {
        free(fileinfo->dimensions);
        free(fileinfo);
        return NULL;
      }

  if( !xdr_short(&xdrstream, &(fileinfo->regular) ))
    return NULL;

  // don't need this
  if( !xdr_long(&xdrstream, &t )) 
    return NULL;


  // This double pointer business is a bit of overkill, but to be consistent, 
  // I'll do it here as well
  fileinfo->scaninfos = (struct mda_scaninfo **) 
    malloc( fileinfo->data_rank * sizeof(struct mda_scaninfo *));


  for( i = 0; i < fileinfo->data_rank; i++)
    {
      fileinfo->scaninfos[i] = (struct mda_scaninfo *) 
        malloc( sizeof(struct mda_scaninfo ));

      if( !xdr_short(&xdrstream, &(fileinfo->scaninfos[i]->scan_rank) ))
        return NULL;

      if( !xdr_long(&xdrstream, &(fileinfo->scaninfos[i]->requested_points) ))
	return NULL;
      if( !xdr_long(&xdrstream, &last_point ))
	return NULL;

      if( fileinfo->scaninfos[i]->scan_rank > 1)
	{
	  offsets = (long *) malloc( fileinfo->scaninfos[i]->requested_points 
				     * sizeof(long));
	  if( !xdr_vector( &xdrstream, (char *) offsets, 
			   fileinfo->scaninfos[i]->requested_points, 
			   sizeof( long), (xdrproc_t) xdr_long))
	    return NULL;
	}
      else
	offsets = NULL;

      if( !xdr_counted_string( &xdrstream, &(fileinfo->scaninfos[i]->name) ))
	return NULL;

      if( !xdr_counted_string( &xdrstream, &time ))
	return NULL;
      
      // only want this stuff for outer loop
      if( !i)
	{
	  fileinfo->last_topdim_point = last_point;
	  fileinfo->time = time;
	}
      else
	free(time);

      if( !xdr_short(&xdrstream, &(fileinfo->scaninfos[i]->number_positioners)))
	return NULL;
      if( !xdr_short(&xdrstream, &(fileinfo->scaninfos[i]->number_detectors)))
	return NULL;
      if( !xdr_short(&xdrstream, &(fileinfo->scaninfos[i]->number_triggers)))
	return NULL;

     
      fileinfo->scaninfos[i]->positioners = (struct mda_positioner **) 
	malloc( fileinfo->scaninfos[i]->number_positioners * 
		sizeof(struct mda_positioner *));
      for( j = 0; j < fileinfo->scaninfos[i]->number_positioners; j++)
	{
	  if( (fileinfo->scaninfos[i]->positioners[j] = 
	       positioner_read(&xdrstream)) == NULL )
	    return NULL;
	}

      fileinfo->scaninfos[i]->detectors = (struct mda_detector **) 
	malloc( fileinfo->scaninfos[i]->number_detectors * 
		sizeof(struct mda_detector *));
      for( j = 0; j < fileinfo->scaninfos[i]->number_detectors; j++)
	{
	  if( (fileinfo->scaninfos[i]->detectors[j] = 
	       detector_read( &xdrstream)) == NULL )
	    return NULL;
	}

      fileinfo->scaninfos[i]->triggers = (struct mda_trigger **) 
	malloc( fileinfo->scaninfos[i]->number_triggers * 
		sizeof(struct mda_trigger *));
      for( j = 0; j < fileinfo->scaninfos[i]->number_triggers; j++)
	{
	  if( (fileinfo->scaninfos[i]->triggers[j] = 
	       trigger_read( &xdrstream)) == NULL )
	    return NULL;
	}

      if( offsets != NULL)
	{
	  fseek( fptr, offsets[0], SEEK_SET);
	  free( offsets);
	}
    }

  
  xdr_destroy( &xdrstream);

  return fileinfo;
}


void mda_info_unload( struct mda_fileinfo *fileinfo)
{
  int i, j;

  struct mda_scaninfo *scaninfo;

  free( fileinfo->time);

  for( j = 0; j < fileinfo->data_rank; j++)
  {
    scaninfo = fileinfo->scaninfos[j];

    free( scaninfo->name);

    for( i = 0; i < scaninfo->number_positioners; i++)
      {
	free(scaninfo->positioners[i]->name);
	free(scaninfo->positioners[i]->description);
	free(scaninfo->positioners[i]->step_mode);
	free(scaninfo->positioners[i]->unit);
	free(scaninfo->positioners[i]->readback_name);
	free(scaninfo->positioners[i]->readback_description);
	free(scaninfo->positioners[i]->readback_unit);
	free(scaninfo->positioners[i]);
      }
    free( scaninfo->positioners);
    
    for( i = 0; i < scaninfo->number_triggers; i++)
      {
        free(scaninfo->triggers[i]->name);
        free(scaninfo->triggers[i]);
      }
    free( scaninfo->triggers);
    
    for( i = 0; i < scaninfo->number_detectors; i++)
      {
	free(scaninfo->detectors[i]->name);
	free(scaninfo->detectors[i]->description);
	free(scaninfo->detectors[i]->unit);
        free(scaninfo->detectors[i]);
      }
    free( scaninfo->detectors);

    free( scaninfo);
 }

  free( fileinfo->scaninfos);
  free( fileinfo->dimensions);
  
  free( fileinfo);

}
