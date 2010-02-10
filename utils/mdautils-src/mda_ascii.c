/*************************************************************************\
* Copyright (c) 2005 The University of Chicago, 
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory, MHATT/XOR
  Send comments to dohnarms@anl.gov
  
  0.3   -- July 2005
  0.3.1 -- December 2005
           Removed scan divider when single file and trim options
           used together
  0.3.2 -- December 2006
           Added support for files that have more than 32k points

 */


/********************  mda_ascii.c  ***************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "mda-load.h"

#define VERSION "0.3.2"

enum { MERGE, TRIM, SINGLE, STDOUT };
enum { COMMENT, SEPARATOR, BASE, EXTENSION, DIRECTORY};



void print_head( struct mda_struct *mda, FILE *output, char *comment)
{
  int i, j;

  fprintf( output,"%s MDA File Version = %g\n", comment, mda->header->version);
  fprintf( output,"%s Scan number = %li\n", comment, mda->header->scan_number);
  fprintf( output,"%s Overall scan dimension = %i-D\n", comment, 
	   mda->header->data_rank);
  
  fprintf( output,"%s Total requested scan size = ", comment);
  for( i = 0; i < mda->header->data_rank; i++)
    {
      if( i)
	fprintf( output," x ");
      fprintf( output,"%li", mda->header->dimensions[i]);
    }
  fprintf( output,"\n");

  if( !mda->header->regular)
    fprintf( output,"%s Dimensions changed during the scan.\n", comment);
  
  fprintf( output,"\n\n");

  fprintf( output,"%s  Extra PV: name, descr, values (, unit)\n", comment );

  fprintf( output,"\n");

  if( mda->extra)
    {
      for( i = 0 ; i < mda->extra->number_pvs; i++)
	{ 
	  fprintf( output,"%s Extra PV %i: %s, %s, ", comment, i+1, 
		   mda->extra->pvs[i]->name,
		   mda->extra->pvs[i]->description);
	  
	  fprintf( output,"\"");
	  switch(mda->extra->pvs[i]->type)
	    {
	    case DBR_STRING:
	      fprintf( output,"%s", 
		       (char *) mda->extra->pvs[i]->values);
	      break;
	    case DBR_CTRL_CHAR:
	      for( j = 0; j < mda->extra->pvs[i]->count; j++)
		{
		  if( j)
		    fprintf( output,",");
		  fprintf( output,"%i", 
			   ((char *) mda->extra->pvs[i]->values)[j]);
		}
	      break;
	    case DBR_CTRL_SHORT:
	      for( j = 0; j < mda->extra->pvs[i]->count; j++)
		{
		  if( j)
		    fprintf( output,",");
		  fprintf( output,"%i", 
			   ((short *) mda->extra->pvs[i]->values)[j]);
		}
	      break;
	    case DBR_CTRL_LONG:
	      for( j = 0; j < mda->extra->pvs[i]->count; j++)
		{
		  if( j)
		    fprintf( output,",");
		  fprintf( output,"%li", 
			   ((long *) mda->extra->pvs[i]->values)[j]);
		}
	      break;
	    case DBR_CTRL_FLOAT:
	      for( j = 0; j < mda->extra->pvs[i]->count; j++)
		{
		  if( j)
		    fprintf( output,",");
		  fprintf( output,"%.9g", 
			   ((float *) mda->extra->pvs[i]->values)[j]);
		}
	      break;
	    case DBR_CTRL_DOUBLE:
	      for( j = 0; j < mda->extra->pvs[i]->count; j++)
		{
		  if( j)
		    fprintf( output,",");
		  fprintf( output,"%.9lg", 
			   ((double *) mda->extra->pvs[i]->values)[j]);
		}
	      break;
	    }
	  fprintf( output,"\"");
	  if( mda->extra->pvs[i]->type != DBR_STRING)
	    fprintf( output,", %s", mda->extra->pvs[i]->unit);
	  fprintf( output,"\n");
	} 

      fprintf( output,"\n\n");
    }
}



int print_pos_det_info(struct scan_struct *scan, FILE *output, char *comment,
		       int dimension, int index_offset)
{
  int col;

  int i;


  col = 0;
      
  for( i = 0; i < scan->number_positioners; i++)
    {
      col++;
      fprintf( output, "%s  %3d  ", comment, col + index_offset);
      fprintf( output,"[%i-D Positioner %i]  ", dimension,
	       scan->positioners[i]->number + 1);
      fprintf( output,"%s, %s, %s, %s, %s, %s, %s\n", 
	       scan->positioners[i]->name,
	       scan->positioners[i]->description, 
	       scan->positioners[i]->step_mode,
	       scan->positioners[i]->unit,
	       scan->positioners[i]->readback_name, 
	       scan->positioners[i]->readback_description,
	       scan->positioners[i]->readback_unit );
    }

  for( i = 0; i < scan->number_detectors; i++)
    {
      col++;
      fprintf( output, "%s  %3i  ", comment, col + index_offset);
      fprintf( output,"[%i-D Detector %3i]  ", dimension,
	       scan->detectors[i]->number + 1);
      fprintf( output,"%s, %s, %s\n", 
	       scan->detectors[i]->name,
	       scan->detectors[i]->description,
	       scan->detectors[i]->unit );
    }

  return col;
}


/* 
   Lets you know how many characters it takes to write a number:
   for 1945 it's 4, for 28 it's 2, ....
 */
int num_width( int number)
{
  int width;

  width = 1;
  while( number >= 10)
    {
      number /= 10;
      width++;
    }

  return width;
}



int printer( struct mda_struct *mda, int option[], char *argument[])
{
  FILE *output;

  struct scan_struct *scan, *l_scan;

  int  depth;     // data_rank - 1 
  int *scan_pos;  // what scan we are on, a multidimensional index

  // Variables dependent on writing to file
  int  *log_dim;   // the width of the maximum scan number (for files)
  char *filename;
  char  format[16];

  int first;  // flag used to indicate if this is the first scan

  int i, j, k;

  char *comment; // to make life easier

  /* 
     This function is oddly coded, as it can handle arbitrary
     dimensional data.

     The trivial 1-D case goes through here, which results in giving
     zero to malloc, which is no big deal.  One could 'if' around the
     higher dimensional code, but it would just get really ugly.  
     It looks like bad things will happen, but they won't (remember
     that depth == 0 for the 1-D case).
  */

  comment = argument[COMMENT];

  depth = mda->header->data_rank - 1;

  scan_pos = (int *) malloc( depth * sizeof(int));

  for( i = 0; i < depth; i++)
    scan_pos[i] = 0;

  output = stdout;

  log_dim = NULL;
  filename = NULL;
  if( !option[SINGLE] )
    {
      log_dim = (int *) malloc( depth * sizeof(int));
      
      for( j = 0; j < depth; j++)
	log_dim[j] = num_width( mda->header->dimensions[j] );

      /*   +3 = '/' + '.' + '\0'  */
      i = strlen(argument[DIRECTORY]) + strlen(argument[BASE]) + 
	strlen(argument[EXTENSION]) + depth + 3;
      for( j = 0; j < depth; j++)
	i += log_dim[j];
      filename = (char *) malloc( i * sizeof(char));
    }
  else
    {   
      if( option[STDOUT])
	{
	  output = stdout;
	}
      else
	{
	  i = strlen(argument[DIRECTORY]) + strlen(argument[BASE]) + 
	    strlen(argument[EXTENSION]) + depth + 3;
	  filename = (char *) malloc( i * sizeof(char));

	  sprintf( filename, "%s/%s.%s", argument[DIRECTORY], 
		   argument[BASE], argument[EXTENSION]);

	  if( (output = fopen( filename, "w")) == NULL)
	    {
	      fprintf(stderr, "Can't open file \"%s\" for writing!\n",
		      filename);
	      return 1;
	    }
	}
    }

  first = 1;
  for(;;) // infinite loop
    {
      /* 
	 Here we check to make sure scan is not NULL.
	 Once we find a NULL scan, it's all over (we 'goto' out), 
	 due to way the MDA file is set up, and we are going through
	 the scans in "file order". 

	 Yes, using 'goto' is "bad style" in C programming, but this
	 is the classic situation when its use is justified, as I'd 
	 have to add extra code to get out of the infinite loop.
      */
      l_scan = mda->scan;
      for( i = 0; i < depth; i++)
	{
	  l_scan = l_scan->sub_scans[scan_pos[i]];
	  if( l_scan == NULL)
	    goto GetOut; 
	}
      scan = l_scan;  // scan is now the 1-D scan

      /* assemble filename */
      if( !option[SINGLE])
	{   
	  i = sprintf( filename, "%s/%s", argument[DIRECTORY], 
		       argument[BASE]);
	  for( j = 0 ; j < depth; j++)
	    {
	      sprintf( format, "_%%0%ii", log_dim[j]);
	      i += sprintf( filename + i, format, scan_pos[j] + 1);
	    }
	  sprintf( filename + i, ".%s" , argument[EXTENSION]);

	  if( (output = fopen( filename, "w")) == NULL)
	    {
	      fprintf(stderr, "Can't open file \"%s\" for writing!\n",
		      filename);
	      return 1;
	    }
	}

      if( !option[TRIM] )
	{
	  if( !option[SINGLE] || first)
	    {
	      fprintf( output,"%s%s mda2ascii %s generated output\n\n\n", 
		       comment, comment, VERSION);
	      print_head( mda, output, comment);
	      first = 0;
	    }

	  if( option[SINGLE])
	    fprintf(output, "%s "
		    "******************************  Scan Divider  "
		    "******************************\n\n\n", comment);

	  /*
	    Here we walk through the upper dimensions and pick out the
	    corresponding values for this particular 1-D scan.
	  */
	  l_scan = mda->scan;
	  for( i = 0; i < depth; i++)
	    {
	      fprintf( output, "%s %i-D Scan Point\n", comment, 
		       l_scan->scan_rank);
	      fprintf( output, "%s Current point = %i of %li\n", comment, 
		       scan_pos[i] + 1, l_scan->requested_points);
	      fprintf( output,"%s Scanner = %s\n", comment, l_scan->name);
	      fprintf( output,"%s Scan time = %s\n\n", comment, l_scan->time);
	      if( !option[MERGE])
		{
		  fprintf( output, "%s Column Descriptions:\n", comment);
		  print_pos_det_info( l_scan, output, comment, 
				      depth - i + 1, 0);
		  fprintf( output,"\n");
		  
		  fprintf( output,"%s %i-D Scan Values: ", 
			   comment, l_scan->scan_rank);
		  for( j = 0; j < l_scan->number_positioners; j++)
		    fprintf( output,"%.9lg ", 
			     (l_scan->positioners_data[j])[scan_pos[i]]);
		  for( j = 0; j < l_scan->number_detectors; j++)
		    fprintf( output,"%.9g ", 
			     (l_scan->detectors_data[j])[scan_pos[i]]);
		  fprintf( output,"\n\n\n");
		}

	      l_scan = l_scan->sub_scans[scan_pos[i]];
	    }

	  fprintf( output,"%s 1-D Scan\n", comment);
	  fprintf( output,"%s Points completed = %li of %li\n", 
		   comment, scan->last_point, scan->requested_points);
	  fprintf( output,"%s Scanner = %s\n", comment, scan->name);
	  fprintf( output,"%s Scan time = %s\n", comment, scan->time);

	  fprintf( output,"\n");


	  fprintf( output,"%s  Positioner: name, descr, step mode, unit, "
		   "rdbk name, rdbk descr, rdbk unit\n", comment );
	  fprintf( output,"%s  Detector: name, descr, unit\n", comment );
      
	  fprintf( output,"\n");

	  fprintf( output, "%s Column Descriptions:\n", comment);
	  fprintf( output, "%s    1  [     Index      ]\n", comment);
	  i = 1;
	  if( option[MERGE])
	    {
	      l_scan = mda->scan;
	      for( j = 0; j < depth; j++)
		{
		  i += print_pos_det_info( l_scan, output, comment, 
					   depth - j + 1, i);
		  l_scan = l_scan->sub_scans[scan_pos[j]];
		}
	    }
	  print_pos_det_info( scan, output, comment, 1, i);

	  fprintf( output,"\n%s 1-D Scan Values\n", comment);
	}  

      for( i = 0; i < scan->last_point; i++)
	{
	  fprintf( output, "%i", i+1);
	  if( option[MERGE])
	    {
	      l_scan = mda->scan;
	      for( k = 0; k < depth; k++)
		{
		  for( j = 0; j < l_scan->number_positioners; j++)
		    fprintf( output,"%s%.9lg", argument[SEPARATOR],
			     (l_scan->positioners_data[j])[scan_pos[k]]);
		  for( j = 0; j < l_scan->number_detectors; j++)
		    fprintf( output,"%s%.9g", argument[SEPARATOR], 
			     (l_scan->detectors_data[j])[scan_pos[k]]);
		  l_scan = l_scan->sub_scans[scan_pos[j]];
		}
	    }
	  for( j = 0; j < scan->number_positioners; j++)
	    fprintf( output,"%s%.9lg", argument[SEPARATOR],
		     (scan->positioners_data[j])[i]);
	  for( j = 0; j < scan->number_detectors; j++)
	    fprintf( output,"%s%.9g", argument[SEPARATOR],
		     (scan->detectors_data[j])[i]);
	  fprintf( output,"\n");
	}

      if( option[SINGLE] && !option[TRIM])
	fprintf( output,"\n");

      if( !option[SINGLE] && !option[STDOUT])
	fclose( output);

      for( j = depth - 1; j >= 0; j--)
	{
	  scan_pos[j]++;
	  if(scan_pos[j] < mda->header->dimensions[j])
	    break;
	  scan_pos[j] = 0;
	}
      if( j < 0)
	break; // done
    }

 GetOut:

  if( option[SINGLE] && (output != stdout) )
    fclose( output);

  free( scan_pos);
  free( log_dim);   // if NULL, it will be ignored 
  free( filename);  // ditto

  return 0;
}


void helper(void)
{
  printf("mda2ascii %s  --  Converts EPICS MDA files to ASCII files.\n\n", 
	 VERSION);
  printf("It's default behavior is to automatically generate the name(s) "
	 "of the output\n"
	 "file(s), and split multidimensional MDA files into multiple "
	 "ASCII files.\n\n");

  printf("usage: mda2ascii [-hmt1] [-x <extension>] [-d <directory>] "
	 "[-o <output>]\n"
         "           [-c <commenter>] [-s <separator>]  <MDA file>  "
	 "[<more MDA files>]\n\n");

  printf("-h  This help message.\n"
	 "-m  Merge higher dimensional values into data as redundant columns.\n"
	 "-t  Trim off all the commented header lines.\n"
	 "-1  Write multidimensional MDA files to a single ASCII file. "
	 "An overall\n"
	 "    header is at start of file, and scans are separated by "
	 "dividers.\n"
	 "-x  Set output file's extension (default: \"asc\").\n"
	 "-d  Set output file's directory (default: current directory).\n"
	 "-o  Specify output file, limiting number of input MDA files "
	 "to one. Specify\n"
	 "    either entire filename or just base, "
	 "where an extension and directory is\n"
	 "    added to base. Alternatively, specifying \"-\" redirects "
	 "output to screen.\n"
	 "-c  Set string for signifying comment (default: \"#\").\n"
	 "-s  Set string for data value separator (default: \" \").\n"
	 );

  printf("\nWritten by Dohn Arms, Argonne National Laboratory, "
	 "dohnarms@anl.gov\n");
}


char *file_base( char *file_name)
{
  char *s, *t, *p;
	      
  s = strdup( file_name);
  
  t = strrchr( s, '/');
  if( t == NULL)
    t = s;
	  
  p = strrchr( t, '.');
  if( p != NULL)
    *p = '\0';
	      
  p = strdup( t);
  free( s);
  return p;
}


int main( int argc, char *argv[])
{
  int flag;

  int   option[4] = { 0, 0, 0, 0 };
  char *argument[5] = { NULL, NULL, NULL, NULL, NULL };
  char *outname = NULL;

  FILE *input;
  struct mda_struct *mda;

  int i;
  

  if( argc == 1)
    {
      printf("mda2ascii %s  --  Converts EPICS MDA files to ASCII output.\n"
	     "For help, type: mda2ascii -h\n", VERSION);
      return 0;
    }

  /* 
     We start by parsing the command line.
  */
  while((flag = getopt( argc, argv, "hmt1c:s:x:d:o:")) != -1)
    {
      switch(flag)
	{
	case 'h':
	  helper();
	  return 0;
	  break;
	case 'm':
	  option[MERGE] = 1;
	  break;
	case 't':
	  option[TRIM] = 1;
	  break;
	case '1':
	  option[SINGLE] = 1;
	  break;
	case 'c':
	  if( argument[COMMENT] != NULL)
	    free( argument[COMMENT] );
	  argument[COMMENT] = strdup( optarg);
	  break;
	case 's':
	  if( argument[SEPARATOR] != NULL)
	    free( argument[SEPARATOR] );
	  argument[SEPARATOR] = strdup( optarg);
	  break;
	case 'x':
	  if( argument[EXTENSION] != NULL)
	    free( argument[EXTENSION] );
	  argument[EXTENSION] = strdup( optarg);
	  break;
	case 'd':
	  if( argument[DIRECTORY] != NULL)
	    free( argument[DIRECTORY] );
	  argument[DIRECTORY] = strdup( optarg);
	  break;
	case 'o':
	  if( outname != NULL)
	    free( outname );
	  outname = strdup( optarg);
	  break;
 	case '?':
	  puts("Error: unrecognized option!");
	  return -1;
	  break;
	case ':':
	  // option normally resides in 'optarg'
	  puts("Error: option missing its value!");  
	  return -1;
	  break;
	}
    }

  if( (argc - optind) == 0)
    {
      printf("You need to specify a file to process.\n");
      return 0;
    }
  if( ((argc - optind) > 1) && outname )
    {
      printf("You can only specify only one file to process when using the "
	     "-o option.\n");
      return 0;
    }


  if( argument[COMMENT] == NULL)
    argument[COMMENT] = strdup( "#" );
  if( argument[SEPARATOR] == NULL)
    argument[SEPARATOR] = strdup( " " );

  if( outname)
    {
      /* standard output option */
      if( (outname[0] == '-') &&  (outname[1] == '\0'))
	{
	  option[STDOUT] = 1;
	  /* following are side-effects */
	  option[SINGLE] = 1;
	  free( argument[EXTENSION]);
	  free( argument[DIRECTORY]);
	  argument[EXTENSION] = argument[DIRECTORY] = NULL;
	}
      else
	{
	  char *s, *t, *p;
	      
	  s = outname;
	      
	  t = strrchr( s, '/');
	  if( t == NULL)
	    t = s;
	  else
	    {
	      *t = '\0';
	      t++;
	      free( argument[DIRECTORY]);
	      argument[DIRECTORY] = strdup( s);
	    }
	  
	  p = strrchr( t, '.');
	  if( p)
	    {
	      *p = '\0';
	      p++;
	      free( argument[EXTENSION]);
	      argument[EXTENSION] = strdup( p );
	    }
	      
	  argument[BASE] = strdup( t);
	}
    }

  if( argument[DIRECTORY] == NULL)
    argument[DIRECTORY] = strdup( "." );

  if( argument[EXTENSION] == NULL)
    argument[EXTENSION] = strdup( "asc" );

  /* The -o case will only make one loop */
  for( i = optind; i < argc; i++)
    {
      /* there's no reason the -o case needs to do this */
      if( outname == NULL)
	{
	  free( argument[BASE]);
	  argument[BASE] = file_base(argv[i]);
	}

      /* Now we load up the MDA file into the mda structure. */
      if( (input = fopen( argv[i], "r")) == NULL)
	{
	  fprintf(stderr, "Can't open file \"%s\"for reading!\n", argv[i]);
	  return 1;
	}
      if( (mda = mda_load( input)) == NULL )
	{
	  fprintf(stderr, "Loading file \"%s\" failed!\n", argv[i]);
	  return 1;
	}
      fclose(input);

      /* Send the mda structure, along with variables, to be processed. */
      if( printer( mda, option, argument) )
	break;

      /* Free up the memory allocated by the mda structure */
      mda_unload(mda);
    }

  return 0;
}


