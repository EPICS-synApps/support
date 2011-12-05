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
  1.0.0 -- November 2009
           Basically gutted the old code, getting rid of mda-load library
           in order to access data directly
  1.0.1 -- August 2010
           Show actual offset of the scan and PV Extras as encountered
  1.1   -- November 2010

 */


/*****************  mda_dump.c  *****************/

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include <rpc/types.h>
#include <rpc/xdr.h>

#include <unistd.h>

#define VERSION       "1.1.0 (November 2010)"
#define VERSIONNUMBER "1.1.0"





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

  //  printf("length = %ld\n", length);

  /* If reading, obtain room for the string */
  if (mode)
    {
      *p = (char *) malloc( (length + 1) * sizeof(char) );
      (*p)[length] = '\0'; /* Null termination */
    }

  /* If the string length is nonzero, transfer it */
  return(length ? xdr_string(xdrs, p, length) : 1);
}



void print( char *fmt, ...)
{
  va_list args;

  va_start(args, fmt);
  vprintf( fmt, args);
  va_end(args);

  //  fflush( stdout);
}


long int li_print( XDR *xdrs, char *fmt )
{
  long int ll;

  if( !xdr_long(xdrs, &ll) )
    {
      fflush( stdout);
      exit(1);
    }

  printf( fmt, ll);

  return ll;
}


short int si_print( XDR *xdrs, char *fmt )
{
  short int ss;

  if( !xdr_short(xdrs, &ss) )
    {
      fflush( stdout);
      exit(1);
    }

  printf( fmt, ss);

  return ss;
}


float f_print( XDR *xdrs, char *fmt )
{
  float ff;

  if( !xdr_float(xdrs, &ff) )
    {
      fflush( stdout);
      exit(1);
    }

  printf( fmt, ff);

  return ff;
}

double d_print( XDR *xdrs, char *fmt )
{
  double dd;

  if( !xdr_double(xdrs, &dd) )
    {
      fflush( stdout);
      exit(1);
    }

  printf( fmt, dd);

  return dd;
}

char *cs_print( XDR *xdrs, char *fmt )
{
  char *cs;

  if( !xdr_counted_string( xdrs, &cs ) )
    {
      fflush( stdout);
      exit(1);
    }

  printf( fmt, cs);

  return cs;
}


int mda_dump_header( XDR *xdrs)
{
  short int rank;
  
  long int extrapvs;

  int i;

  f_print( xdrs, "Version = %g\n" );
  li_print( xdrs, "Scan number = %li\n");
  rank = si_print( xdrs, "Data rank = %i\n");

  if( rank <= 0)
    {
      fflush(stdout);
      exit(1);
    }
  
  print("Largest scan bounds = ");
  for( i = 0; i < rank; i++)
    {
      if( i)
	print(" x ");
      li_print( xdrs, "%li");
    }
  print("\n");

  li_print( xdrs, "Regularity = %li\n");

  extrapvs = li_print( xdrs, "File offset to extra PV's = %li bytes\n");

  if( extrapvs < 0)
    {
      fflush(stdout);
      exit(1);
    }
  
  print("\n\n");
  
  if( extrapvs)
    return 1;
  else
    return 0;
}


void mda_dump_scan( XDR *xdrs)
{
  int i, j;
  
  short int rank, num_pos, num_det, num_trg;
  
  long int req_pts, cmp_pts;
  long int *offsets;
  
  offsets = NULL;
  
  
  rank = si_print( xdrs, "This scan's rank = %i\n");
  req_pts = li_print( xdrs, "Number of requested points = %li\n");
  cmp_pts = li_print( xdrs, "Last completed point = %li\n");
  
  if( (rank <= 0) || (req_pts <= 0) || (cmp_pts < 0) )
    {
      fflush(stdout);
      exit(1);
    }
  
  if( rank > 1)
    {
      offsets = (long int *) malloc( sizeof( long int) * req_pts);
      
      print("Offsets to lower scans = ");
      for( i = 0; i < req_pts; i++)
	{
	  if( i)
	    print(", ");
	  offsets[i] = li_print( xdrs, "%li");
	}
      print("\n");
    }
  
  cs_print( xdrs, "Scan name = \"%s\"\n");
  cs_print( xdrs, "Scan time = \"%s\"\n");
  
  num_pos = si_print( xdrs, "Number of positioners = %i\n");
  num_det = si_print( xdrs, "Number of detectors = %i\n");
  num_trg = si_print( xdrs, "Number of triggers = %i\n");

  if( num_pos < 0)
    {
      fflush(stdout);
      exit(1);
    }

  for( i = 0; i < num_pos; i++)
    {
      print( "\nPositioner Data Set #%i\n", i+1);

      si_print( xdrs, "              Positioner: %i\n");
      cs_print( xdrs, "                    Name: %s\n");
      cs_print( xdrs, "             Description: %s\n");
      cs_print( xdrs, "               Step Mode: %s\n");
      cs_print( xdrs, "                    Unit: %s\n");
      cs_print( xdrs, "           Readback Name: %s\n");
      cs_print( xdrs, "    Readback Description: %s\n");
      cs_print( xdrs, "           Readback Unit: %s\n");
    }

  if( num_det < 0)
    {
      fflush(stdout);
      exit(1);
    }

  for( i = 0; i < num_det; i++)
    {
      print( "\nDetector Data Set #%i\n", i+1);
      
      si_print( xdrs, "        Detector: %2i\n");
      cs_print( xdrs, "            Name: %s\n");
      cs_print( xdrs, "     Description: %s\n");
      cs_print( xdrs, "            Unit: %s\n");
    }

  if( num_trg < 0)
    {
      fflush(stdout);
      exit(1);
    }

  for( i = 0; i < num_trg; i++)
    {
      print( "\nTrigger #%i\n", i+1);

      si_print( xdrs, "    Trigger: %i\n");
      cs_print( xdrs, "       Name: %s\n");
      f_print(  xdrs, "    Command: %g\n");
    }

  for( i = 0; i < num_pos; i++)
    {
      print( "\nPositioner #%i data:\n", i+1);
      for( j = 0; j < req_pts; j++)
	d_print( xdrs, "%.9lg ");
      print( "\n");
    }

  for( i = 0; i < num_det; i++)
    {
      print( "\nDetector #%i data:\n", i+1);
      for( j = 0; j < req_pts; j++)
	f_print( xdrs, "%.9g ");
      print( "\n");
    }

  if( rank > 1)
    for( i = 0; i < req_pts; i++)
      {
      if( offsets[i] == 0)
          break;
        print( "\n\n%i-D Subscan #%i\n", rank - 1, i+1);
        print( "Offset = %li\n\n", xdr_getpos( xdrs) );
        mda_dump_scan( xdrs);
      }

}


void mda_dump_extra( XDR *xdrs)
{
  enum PV_TYPES { DBR_STRING=0,     DBR_CTRL_CHAR=32,  DBR_CTRL_SHORT=29,
		  DBR_CTRL_LONG=33, DBR_CTRL_FLOAT=30, DBR_CTRL_DOUBLE=34 };

  int i, j;
  
  short int pvs, type, count;

  count = 0;

  print( "\n\nExtra PV Offset = %li", xdr_getpos( xdrs) );

  pvs = si_print( xdrs, "\n\nNumber of Extra PV's = %i.\n");
  if( pvs < 0)
    {
      fflush(stdout);
      exit(1);
    }


  for( i = 0 ; i < pvs; i++)
    {
      print( "\nExtra PV #%i:\n", i+1);
      
      cs_print( xdrs, "    Name = %s\n");
      cs_print( xdrs, "    Description = %s\n");

      if( !xdr_short(xdrs, &type) )
	return;

      if( (type != DBR_STRING) && (type != DBR_CTRL_CHAR) && 
	  (type != DBR_CTRL_SHORT) &&  (type != DBR_CTRL_LONG) && 
	  (type != DBR_CTRL_FLOAT) && (type != DBR_CTRL_DOUBLE))
	{
	  print( "    Type = %i (UNKNOWN)\n", type);
	  print( "\nExiting......\n");
	  exit(2);
	}

      if( type != DBR_STRING)
	{
	  count = si_print( xdrs, "    Count = %i\n");
	  cs_print( xdrs, "    Unit = %s\n");
	}

      switch(type)
	{
	case DBR_STRING:
	  print( "    Type = %i (DBR_STRING)\n", type);
	  cs_print( xdrs, "    Value = \"%s\"\n");
	  break;
	case DBR_CTRL_CHAR:
	  {
	    unsigned int size, maxsize;
	    char *bytes;

	    print( "    Type = %i (DBR_CTRL_CHAR)\n", type);
	    print( "    Value%s = ", (count == 1) ? "" : "s");

	    maxsize = count;

	    if( !xdr_bytes( xdrs, &(bytes), &size, maxsize ) )
	      return;
	    count = size;

	    for( j = 0; j < count; j++)
	      {
		if( j)
		  print( ", ");
		print( "%i", bytes[j]);
	      }
	    print( "\n");
	  }
	  break;
	case DBR_CTRL_SHORT:
	  {
	    short int *shorts;

	    print( "    Type = %i (DBR_CTRL_SHORT\n", type);
	    print( "    Value%s = ", (count == 1) ? "" : "s");

	    shorts = (short int *) malloc( count * sizeof(short));
	    if( !xdr_vector( xdrs, (char *) shorts, count, 
			     sizeof( short), (xdrproc_t) xdr_short))
	      return;

	    for( j = 0; j < count; j++)
	      {
		if( j)
		  print( ", ");
		print( "%i", shorts[j]);
	      }
	    print( "\n");

	    free (shorts);
	  }
	  break;
	case DBR_CTRL_LONG:
	  {
	    long int *longs;
	    
	    print( "    Type = %i (DBR_CTRL_LONG)\n", type);
	    print( "    Value%s = ", (count == 1) ? "" : "s");

	    longs = (long int *) malloc( count * sizeof(long));
	    if( !xdr_vector( xdrs, (char *) longs, count, 
			     sizeof( long), (xdrproc_t) xdr_long))
	      return ;

	    for( j = 0; j < count; j++)
	      {
		if( j)
		  print( ", ");
		print( "%li", longs[j]);
	      }
	    print( "\n");

	    free( longs);
	  }
	  break;
	case DBR_CTRL_FLOAT:
	  {
	    float *floats;

	    print( "    Type = %i (DBR_CTRL_FLOAT)\n", type);
	    print( "    Value%s = ", (count == 1) ? "" : "s");

	    floats = (float *) malloc( count * sizeof(float));
	    if( !xdr_vector( xdrs, (char *) floats, count, 
			     sizeof( float), (xdrproc_t) xdr_float))
	      return ;

	    for( j = 0; j < count; j++)
	      {
		if( j)
		  print( ", ");
		print( "%.9g", floats[j]);
	      }
	    print( "\n");

	    free( floats);
	  }
	  break;
	case DBR_CTRL_DOUBLE:
	  {
	    double *doubles;

	    print( "    Type = %i (DBR_CTRL_DOUBLE)\n", type);
	    print( "    Value%s = ", (count == 1) ? "" : "s");

	    doubles = (double *) malloc( count * sizeof(double));
	    if( !xdr_vector( xdrs, (char *) doubles, count, 
			     sizeof( double), (xdrproc_t) xdr_double))
	      return;

	    for( j = 0; j < count; j++)
	      {
		if( j)
		  print( ", ");
		print( "%.9lg", doubles[j]);
	      }
	    print( "\n");

	    free( doubles);
	  }
	  break;
	}
    }
}



int mda_dump( char *file)
{
  XDR xdrstream;

  FILE *input;

  int extraflag;


  if( (input = fopen( file, "rb")) == NULL)
    {
      fprintf(stderr, "Can't open file!\n");
      return 1;
    }


  xdrstdio_create(&xdrstream, input, XDR_DECODE);
  

  extraflag = mda_dump_header( &xdrstream);
  mda_dump_scan( &xdrstream);
  if( extraflag)
    mda_dump_extra( &xdrstream);


  xdr_destroy( &xdrstream);

  fclose(input);

  return 0;
}


void help(void)
{
  printf("Usage:  mda-dump [-hv] FILE\n"
         "Does a dump of everything in the EPICS MDA file, FILE.\n"
         "\n"
         "-h  This help text.\n"
         "-v  Show version information.\n"
         "\n"
         "The output format of the information exactly follows the binary "
         "format\n"
         "in the MDA file.\n"
);

}

void version(void)
{
  printf("mda-dump %s\n"
         "\n"
         "Copyright (c) 2010 UChicago Argonne, LLC,\n"
         "as Operator of Argonne National Laboratory.\n"
         "\n"
         "Written by Dohn Arms, dohnarms@anl.gov.\n",
         VERSION);
}


int main( int argc, char *argv[])
{
  int opt;

  while((opt = getopt( argc, argv, "hv")) != -1)
    {
      switch(opt)
        {
        case 'h':
          help();
          return 0;
          break;
        case 'v':
          version();
          return 0;
          break;
        case ':':
          // option normally resides in 'optarg'
          printf("Error: option missing its value!\n");
          return -1;
          break;
        }
    }

  if( ((argc - optind) == 0) || ((argc - optind) > 1) )
    {
      printf("For help, type: mda-dump -h\n");
      return 0;
    }


  printf("********** mda-dump %s generated output **********\n\n\n", 
         VERSIONNUMBER);

  if( mda_dump( argv[optind]) )
    {
      fprintf(stderr, "Error!\n");
      return 1;
    }
  
  return 0;
}

