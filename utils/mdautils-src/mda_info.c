/*************************************************************************\
* Copyright (c) 2005 The University of Chicago, 
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory, MHATT/XOR
  Send comments to dohnarms@anl.gov
  
  0.1   -- August 2005
  0.1.1 -- December 2006
           Added support for files that have more than 32k points

  This program does not use the mda-load library, as there is no need
  to load the entire file.

 */



/****************  mda_info.c  **********************/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <rpc/types.h>
#include <rpc/xdr.h>


#define VERSION "0.1.1"


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




/////////////////////////////////////////////////////////////////////////////


int information( XDR *xdrs)
{
  float version;
  long  num;
  short d_rank, reg;
  long *dims;

  short rank, num_pos;
  long  pts, req;
  char *name, *time;

  char *pos_name, *pos_dscr, *pos_mode;

  short shorter;
  long   longer;
  long  *longer_array;
  char  *stringer;

  int i;


  if( !xdr_float(xdrs, &version  ))
    return 1;
  printf("          MDA file version = %g\n", version);

  if( !xdr_long(xdrs, &num ))
    return 1;
  printf("               Scan number = %li\n", num);

  if( !xdr_short(xdrs, &d_rank ))
    return 1;
  printf("       Scan dimensionality = %i\n", d_rank);

  dims = (long *) malloc( d_rank * sizeof(long));
  if( !xdr_vector( xdrs, (char *) dims, d_rank, 
		   sizeof( long), (xdrproc_t) xdr_long))
    return 1;
  printf("         Nominal scan size = ");
  for( i = 0; i < d_rank; i++)
    {
      if( i)
	printf("x");
      printf( "%li", dims[i]);
    }
  printf("\n");

  if( !xdr_short(xdrs, &reg ))
    return 1;
  printf("                Regularity = %s\n", reg ? "TRUE" : "FALSE" );

  /* not needed */
  if( !xdr_long(xdrs, &longer ))
    return 1;



  printf("\n");

  if( !xdr_short(xdrs, &rank ))
    return 1;
  if( !xdr_long(xdrs, &req ))
    return 1;
  if( !xdr_long(xdrs, &pts ))
    return 1;
  printf(" Completed %i-D scan points = %li of %li\n", 
	 rank, pts, req);

  /* not needed */
  if( rank > 1)
    {
      longer_array = (long *) malloc( req * sizeof(long));
      if( !xdr_vector( xdrs, (char *) longer_array, req, sizeof( long), 
		       (xdrproc_t) xdr_long))
	return 1;
    }

  if( !xdr_counted_string( xdrs, &name ))
    return 1;
  printf("              Scanner name = %s\n", name);

  if( !xdr_counted_string( xdrs, &time ))
    return 1;
  printf("           Scan start time = %s\n", time);

  if( !xdr_short(xdrs, &num_pos ))
    return 1;

  /* not needed */
  if( !xdr_short(xdrs, &shorter ))
    return 1;
  if( !xdr_short(xdrs, &shorter ))
    return 1;


  printf("\n");

  for( i = 0; i < num_pos; i++)
    {
      /* not needed */
      if( !xdr_short(xdrs, &shorter ))
	return 1;

      if( !xdr_counted_string( xdrs, &pos_name ) )
	return 1;
      if( !xdr_counted_string( xdrs, &pos_dscr ) )
	return 1;
      if( !xdr_counted_string( xdrs, &pos_mode ) )
	return 1;
      printf("         %i-D positioner #%i = %s (%s), %s mode\n", 
	     rank, i + 1, pos_name, pos_dscr, pos_mode);

      /* not needed */
      if( !xdr_counted_string( xdrs, &stringer ) )
	return 1;
      if( !xdr_counted_string( xdrs, &stringer ) )
	return 1;
      if( !xdr_counted_string( xdrs, &stringer ) )
	return 1;
      if( !xdr_counted_string( xdrs, &stringer ) )
	return 1;
    }

  return 0;
}





int main( int argc, char *argv[])
{
  FILE *input;
  XDR xdrstream;

  if( argc != 2)
    {
      printf("mda-info  %s  --  Prints the basic scan information about "
	     "the file.\n", VERSION);
      printf("  usage:  mda-info <MDA file>\n");
      return 0;
    }

  if( (input = fopen( argv[1], "r")) == NULL)
    {
      fprintf(stderr, "Can't open file!\n");
      return 1;
    }

  xdrstdio_create(&xdrstream, input, XDR_DECODE);

  if( information( &xdrstream) )
    {
      fprintf(stderr, "Can't read file!\n");
      return 1;
    }

  xdr_destroy( &xdrstream);

  fclose(input);
  
  return 0;
}


