/*************************************************************************\
* Copyright (c) 2010 UChicago Argonne, LLC,
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*
 
  Written by Dohn A. Arms, Argonne National Laboratory
  Send comments to dohnarms@anl.gov
  
  0.3   -- July 2005
  0.3.1 -- December 2005
           Removed scan divider when single file and trim options 
               used together
  0.3.2 -- December 2006
           Added support for files that have more than 32k points
  1.0.0 -- October 2009
           All scans of any dimensionalty can be converted, or a specific
               dimensionalty can be chosen.
           Added -f, which displays the data in browsing-friendly format
           Added -i, which chooses the dimensionalty of the scans shown
           Added -e, which writes Extra PV information to a separate file
           Added to -m extra columns that show higher dimensional indices
           Made porting to Windows friendlier (but not trivial)
  1.0.1 -- August 2010
           Print out all exisiting scans (even if they SHOULDN'T be there).
  1.0.2 -- November 2010
           Add -a switch  to make printing out incomplete scans an option, 
               not the default.
  1.1   -- November 2010
  1.1.1 -- December 2010
           Forgot to comment out warning generated with incomplete scans 
               and -a.

*/


/********************  mda_ascii.c  ***************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>

//#include <mcheck.h>

// uncommenting the following converts \'s in argument paths to /'s
//#define WINDOWS

#include "mda-load.h"

#define VERSION       "1.1.1 (December 2010)"
#define VERSIONNUMBER "1.1.1"


enum { MERGE, TRIM, FRIENDLY, EXTRA, SINGLE, STDOUT, ALL, DIMENSION };
enum { COMMENT, SEPARATOR, BASE, EXTENSION, DIRECTORY };



void print_extra( struct mda_file *mda, FILE *output, char *comment)
{
  int i, j;

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


void print_head( struct mda_file *mda, FILE *output, char *comment)
{
  int i;

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
}


int print_pos_det_info(struct mda_scan *scan, FILE *output, 
                       char *comment, int index_offset)
{
  int col;

  int i;


  col = 0;
      
  for( i = 0; i < scan->number_positioners; i++)
    {
      col++;
      fprintf( output, "%s  %3d  ", comment, col + index_offset);
      fprintf( output,"[%i-D Positioner %i]  ", scan->scan_rank,
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
      fprintf( output,"[%i-D Detector %3i]  ", scan->scan_rank,
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


void max_check( int *fore_max, int *aft_max, int *exp_max, char *string)
{
  char *p, *q;
  int i, j, k;

  i = j = k = 0;

  p = strchr( string, '.');
  if( p != NULL)
    {
      *p = '\0';
      p++;
      q = strchr( p, 'e');
    }
  else
    {
      q = strchr( string, 'e');
    }

  if( q != NULL)
    {
      *q = '\0';
      q++;
      k = strlen( q);
    }

  if( p != NULL)
    j = strlen( p);
  
  i = strlen( string);

  if( i > *fore_max)
    *fore_max = i;
  if( j > *aft_max)
    *aft_max = j;
  if( k > *exp_max)
    *exp_max = k;
}

int formatter( int fore, int aft, int exp, char *string, int len, int lflag)
{
  int num;
  //  printf("%d %d %d - ", fore, aft, exp);

  if( !aft && !exp)
    {
      num = fore;
      snprintf( string, len, "%%s%%%d%s.9g", num, lflag ? "l" : ""  );
    }
  else if( !exp)
    {
      num = fore + aft + 1;
      snprintf( string, len, "%%s%%%d.%d%sf", num, aft, lflag ? "l" : ""  );
    }
  else
    {
      num = fore + exp + 1 + aft + ( aft ? 1 : 0);
      snprintf( string, len, "%%s%%%d.%d%se", num, aft, lflag ? "l" : ""  );
    }

  //  printf("%s\n", string);

  return num;
}


int printer( struct mda_file *mda, int option[], char *argument[])
{
  FILE *output;

  struct mda_scan *scan, **scan_array;

  int  depth;     // data_rank - 1 
  int *scan_pos;  // what scan we are on, a multidimensional index
  int  depth_init, depth_limit;

  // Variables dependent on writing to file
  // NULLing variables allows themto be free()'d safely if unused
  int  *log_dim = NULL;   // the width of the maximum scan number (for files)
  char *filename = NULL;
  char  name_format[16];

  // used to tell if we are in unfinished scans, to be marked as such
  int unfinished;

  int first;  // flag used to indicate if this is the first scan
  int dim_first;

  int i, j, k;
  int y;

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

  // This is needed at beginning, for option[STDOUT].
  // That option invokes option[SINGLE], which nullifies option[EXTRA].
  output = stdout;

  // This opens a file and leaves it open!
  if( option[SINGLE] && !option[STDOUT] )
    {   
      i = strlen(argument[DIRECTORY]) + strlen(argument[BASE]) + 
        strlen(argument[EXTENSION]) + 3;
      filename = (char *) malloc( i * sizeof(char));
      
      sprintf( filename, "%s/%s.%s", argument[DIRECTORY],
               argument[BASE], argument[EXTENSION]);
              
      if( (output = fopen( filename, "wt")) == NULL)
        {
          fprintf(stderr, "Can't open file \"%s\" for writing!\n", filename);
          return 1;
        }
      
      free(filename);
      filename = NULL;  // for later, make free() happy
    }

  first = 1;
  if( option[DIMENSION] > 0)
    {
      depth_init = mda->header->data_rank - option[DIMENSION];
      depth_limit = depth_init + 1;
    }
  else
    {
      depth_init = 0;
      depth_limit = mda->header->data_rank;
    }
  for( depth = depth_init; depth < depth_limit; depth++)
    {
      scan_pos = (int *) malloc( depth * sizeof(int));
      for( i = 0; i < depth; i++)
        scan_pos[i] = 0;

      scan_array = (struct mda_scan **) 
        malloc( mda->header->data_rank * sizeof(struct mda_scan *) );

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

      unfinished = 0;

      dim_first = 1;
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

          scan_array[0] = mda->scan;
          for( i = 0; i < depth; i++)
            {
              scan_array[i+1] = scan_array[i]->sub_scans[scan_pos[i]];
              if( scan_array[i+1] == NULL)
                goto Iterate; 
            }
          scan = scan_array[depth];  // scan is now the 1-D scan

          if( option[DIMENSION] == -1)
            if( !scan->number_detectors )  // nothing to display!
              goto Iterate;

          /* assemble filename */
          if( !option[SINGLE])
            {   
              i = sprintf( filename, "%s/%s", argument[DIRECTORY], 
                           argument[BASE]);
              for( j = 0 ; j < depth; j++)
                {
                  sprintf( name_format, "_%%0%ii", log_dim[j]);
                  i += sprintf( filename + i, name_format, scan_pos[j] + 1);
                }
              sprintf( filename + i, ".%s" , argument[EXTENSION]);
              
              if( (output = fopen( filename, "wt")) == NULL)
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
                           comment, comment, VERSIONNUMBER);
                  print_head( mda, output, comment);
                  if( !option[EXTRA] )
                    print_extra( mda, output, comment);
                  else
                    {
                      FILE *extra_output;
                      char *extra_filename;
                      
                      i = strlen(argument[DIRECTORY]) + 
                        strlen(argument[BASE]) +  
                        strlen(argument[EXTENSION]) + 13;
                      extra_filename = (char *) malloc( i * sizeof(char));
      
                      // write in main file that data is external
                      // write extra PV filename without directory
                      sprintf( extra_filename, "%s_extra_pvs.%s", 
                               argument[BASE], argument[EXTENSION]);
                      fprintf( output,
                               "%s  Extra PV: external file = %s\n\n\n", 
                               comment, extra_filename);

                      sprintf( extra_filename, "%s/%s_extra_pvs.%s", 
                               argument[DIRECTORY],
                               argument[BASE], argument[EXTENSION]);
      
                      if( (extra_output = fopen( extra_filename, "wt")) == NULL)
                        {
                          fprintf( stderr, 
                                  "Can't open file \"%s\" for writing!\n",
                                  extra_filename);
                          return 1;
                        }

                      fprintf( extra_output,
                               "%s%s mda2ascii %s generated output\n\n\n", 
                               comment, comment, VERSIONNUMBER);
                      print_extra( mda, extra_output, comment);
      
                      free( extra_filename);
                      fclose( extra_output);
                    }
                  
                  
                  first = 0;
                }
              
              if( option[SINGLE])
                {
                  if( dim_first)
                    {
                      fprintf(output, "%s "
                              "##############################   %2d-D Scans   "
                              "##############################\n", 
                              comment, scan->scan_rank);
                      dim_first = 0;
                    }
                  fprintf(output, "%s "
                          "******************************  Scan Divider  "
                          "******************************\n\n\n", comment);
                }

              /*
                Here we walk through the upper dimensions and pick out the
                corresponding values for this particular 1-D scan.
              */

              if( unfinished)
                fprintf( output, "%s !!!!!!!!!! "
                         "Subscan of Incomplete %d-D Scan Point "
                         "!!!!!!!!!!\n\n", comment, mda->header->data_rank);
              for( i = 0; i < depth; i++)
                {
                  fprintf( output, "%s %i-D Scan Point\n", comment, 
                           scan_array[i]->scan_rank);
                  fprintf( output, "%s Current point = %i of %li\n", comment, 
                           scan_pos[i] + 1, scan_array[i]->requested_points);
                  fprintf( output,"%s Scanner = %s\n", comment, 
                           scan_array[i]->name);
                  fprintf( output,"%s Scan time = %s\n\n", comment, 
                           scan_array[i]->time);
                  if( !option[MERGE])
                    {
                      fprintf( output, "%s Column Descriptions:\n", comment);
                      print_pos_det_info( scan_array[i], output, comment, 0);
                      fprintf( output,"\n");
                      
                      fprintf( output,"%s %i-D Scan Values: ", 
                               comment, scan_array[i]->scan_rank);
                      for( j = 0; j < scan_array[i]->number_positioners; j++)
                        fprintf( output,"%.9lg ", 
                                 (scan_array[i]->positioners_data[j])
                                 [scan_pos[i]]);
                      for( j = 0; j < scan_array[i]->number_detectors; j++)
                        fprintf( output,"%.9g ", 
                                 (scan_array[i]->detectors_data[j])
                                 [scan_pos[i]]);
                      fprintf( output,"\n\n\n");
                    }
                }

              fprintf( output,"%s %d-D Scan\n", comment, scan->scan_rank);
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
              i = 0;
              if( option[MERGE])
                {
                  for( j = 0; j <= depth; j++, i++)
                    fprintf( output, "%s  %3d  [   %d-D Index    ]\n", 
                             comment, i+1, scan_array[i]->scan_rank);
                }
              else
                {
                  fprintf( output, "%s    1  [     Index      ]\n", comment);
                  i++;
                }
              if( option[MERGE])
                {
                  for( j = 0; j < depth; j++)
                    i += print_pos_det_info( scan_array[j], output, comment, i);
                }
              print_pos_det_info( scan, output, comment, i);

              fprintf( output,"\n%s %d-D Scan Values\n", 
                       comment, scan->scan_rank);
            }  

          // this option causes a lot of weird code
          if( option[FRIENDLY])
            {
              // variables used for making uniform column widths
              char **format;
              int format_count;
              int *fmt_fore, *fmt_aft, *fmt_exp, *fmt_tot;
              char string[64];
              
              int indices;
              int m;


              // this lets me get away accounting for 
              // extra columns from MERGE a lot easier
              indices = 1;
              if( option[MERGE])
                indices += depth;

              format_count = indices;
              format_count += scan->number_positioners;
              format_count += scan->number_detectors;
              if( option[MERGE])
                for( i = 0; i < depth; i++)
                  {
                    format_count += scan_array[i]->number_positioners;
                    format_count += scan_array[i]->number_detectors;
                  }
              
             
              fmt_fore = (int *) malloc( sizeof(int) * format_count);
              fmt_aft = (int *) malloc( sizeof(int) * format_count);
              fmt_exp = (int *) malloc( sizeof(int) * format_count);
              fmt_tot = (int *) malloc( sizeof(int) * format_count);
              format = (char **) malloc( sizeof(char *) * format_count);
              for( i = 0; i < format_count; i++)
                format[i] = (char *) malloc( sizeof(char) * 16);
              
              
              for( i = 0; i < format_count; i++)
                fmt_fore[i] = fmt_aft[i] = fmt_exp[i] = fmt_tot[i] = 0;
              
              // include offset of comment and space
              for( i = 0; i < (indices - 1); i++)
                fmt_fore[i] = num_width( scan_array[i]->last_point);
              fmt_fore[indices-1] = num_width( scan->last_point);
              for( i = 0; i < scan->last_point; i++)
                {
                  m = indices;
                  if( option[MERGE])
                    {
                      for( k = 0; k < depth; k++)
                        {
                          for( j = 0; j < scan_array[k]->number_positioners; 
                               j++, m++)
                            {
                              snprintf( string, 64, "%.9lg", 
                                        (scan_array[k]->positioners_data[j])
                                        [scan_pos[k]]);
                              max_check( &fmt_fore[m], &fmt_aft[m], 
                                         &fmt_exp[m], string);
                            }
                          for( j = 0; j < scan_array[k]->number_detectors; 
                               j++, m++)
                            {
                              snprintf( string, 64, "%.9g",
                                        (scan_array[k]->detectors_data[j])
                                        [scan_pos[k]]);
                              max_check( &fmt_fore[m], &fmt_aft[m], 
                                         &fmt_exp[m], string);
                            }
                        }
                    }
                  for( j = 0; j < scan->number_positioners; j++, m++)
                    {
                      snprintf( string, 64, "%.9lg",
                                (scan->positioners_data[j])[i]);
                      max_check( &fmt_fore[m], &fmt_aft[m], 
                                 &fmt_exp[m], string);
                    }
                  for( j = 0; j < scan->number_detectors; j++, m++)
                    {
                      snprintf( string, 64, "%.9g",
                                (scan->detectors_data[j])[i]);
                      max_check( &fmt_fore[m], &fmt_aft[m], 
                                 &fmt_exp[m], string);
                    }
                }
              
              for( i = 0; i < (indices - 1); i++)
                snprintf( format[i], 16, "%%%di%%s", fmt_fore[i] );
              snprintf( format[indices - 1], 16, "%%%di", 
                        fmt_fore[indices - 1] );
              for( i = 0; i < indices; i++)
                fmt_tot[i] = fmt_fore[i];
              m = indices;
              if( option[MERGE])
                {
                  for( k = 0; k < depth; k++)
                    {
                      for( j = 0; j < scan_array[k]->number_positioners; 
                           j++, m++)
                        {
                          fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                         fmt_exp[m], format[m], 16, 1);
                          y = num_width( m + 1);
                          if( y > fmt_tot[m])
                            {
                              fmt_fore[m] += (y - fmt_tot[m]);
                              fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                                      fmt_exp[m], format[m], 
                                                      16, 1);
                            }
                        }
                      for( j = 0; j < scan_array[k]->number_detectors; 
                           j++, m++)
                        {
                          fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                         fmt_exp[m], format[m], 16, 0);
                          y = num_width( m + 1);
                          if( y > fmt_tot[m])
                            {
                              fmt_fore[m] += (y - fmt_tot[m]);
                              fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                                      fmt_exp[m], format[m], 
                                                      16, 0);
                            }
                        }
                    }
                }
              for( j = 0; j < scan->number_positioners; j++, m++)
                {
                  fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                          fmt_exp[m], format[m], 16, 1);
                  y = num_width( m + 1);
                  if( y > fmt_tot[m])
                    {
                      fmt_fore[m] += (y - fmt_tot[m]);
                      fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                              fmt_exp[m], format[m], 16, 1);
                    }
                }
              for( j = 0; j < scan->number_detectors; j++, m++)
                {
                  fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                          fmt_exp[m], format[m], 16, 0);
                  y = num_width( m + 1);
                  if( y > fmt_tot[m])
                    {
                      fmt_fore[m] += (y - fmt_tot[m]);
                      fmt_tot[m] = formatter( fmt_fore[m], fmt_aft[m], 
                                              fmt_exp[m], format[m], 16, 0);
                    }
                }

              fprintf( output, "%s ", argument[COMMENT] );
              for( i = 0; i < m; i++)
                {
                  if( i)
                    fprintf( output, "%s", argument[SEPARATOR] );
                  snprintf( string, 64, "%%%dd", fmt_tot[i]);
                  fprintf( output, string, i + 1);
                }
              fprintf( output, "\n" );
              for( i = 0; i < scan->last_point; i++)
                {
                  // a little cheesy, but whatever
                  for( j = 0; j < (strlen( argument[COMMENT] ) + 1); j++)
                    fprintf( output, " ");

                  for( j = 0; j < (indices - 1); j++)
                    fprintf( output, format[j], scan_pos[j] + 1, 
                             argument[SEPARATOR]);
                  fprintf( output, format[indices - 1], i+1);
                  m = indices;
                  if( option[MERGE])
                    {
                      for( k = 0; k < depth; k++)
                        {
                          for( j = 0; j < scan_array[k]->number_positioners; 
                               j++, m++)
                            fprintf( output, format[m], argument[SEPARATOR],
                                     (scan_array[k]->positioners_data[j])
                                     [scan_pos[k]]);
                          for( j = 0; j < scan_array[k]->number_detectors; 
                               j++, m++)
                            fprintf( output, format[m], argument[SEPARATOR], 
                                     (scan_array[k]->detectors_data[j])
                                     [scan_pos[k]]);
                        }
                    }
                  for( j = 0; j < scan->number_positioners; j++, m++)
                    fprintf( output,format[m], argument[SEPARATOR],
                             (scan->positioners_data[j])[i]);
                  for( j = 0; j < scan->number_detectors; j++, m++)
                    fprintf( output,format[m], argument[SEPARATOR],
                             (scan->detectors_data[j])[i]);
                  fprintf( output,"\n");
                }

              free( fmt_fore);
              free( fmt_aft);
              free( fmt_exp);
              free( fmt_tot);
              for( i = 0; i < format_count; i++)
                free( format[i]);
              free( format);
            }
          else
            {
              for( i = 0; i < scan->last_point; i++)
                {
                  if( option[MERGE])
                    {
                      for( k = 0; k < depth; k++)
                        fprintf( output, "%i%s", scan_pos[k] + 1, 
                                 argument[SEPARATOR] );
                    }
                  fprintf( output, "%i", i+1);
                  if( option[MERGE])
                    {
                      for( k = 0; k < depth; k++)
                        {
                          for( j = 0; j < scan_array[k]->number_positioners; 
                               j++)
                            fprintf( output,"%s%.9lg", argument[SEPARATOR],
                                     (scan_array[k]->positioners_data[j])
                                     [scan_pos[k]]);
                          for( j = 0; j < scan_array[k]->number_detectors; j++)
                            fprintf( output,"%s%.9g", argument[SEPARATOR], 
                                     (scan_array[k]->detectors_data[j])
                                     [scan_pos[k]]);
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
            }

          if( option[SINGLE] && !option[TRIM])
            fprintf( output,"\n");

          if( !option[SINGLE] && !option[STDOUT])
            fclose( output);

        Iterate:
          
          for( j = depth - 1; j >= 0; j--)
            {
              scan_pos[j]++;
              if(scan_pos[j] < mda->header->dimensions[j])
                break;
              scan_pos[j] = 0;
            }
          if( j < 0)
            break; // done

          // show unfinished scans is option asks for it only
          if( scan_pos[0] == mda->scan->last_point)
            {
              if( !option[ALL] )
                break; // get out
              else
                unfinished = 1;
            }
          // there can't be any scans at this point
          if( scan_pos[0] > mda->scan->last_point)
            break;
        }

      free( log_dim);
      free( filename);
 
      free( scan_pos);
      free( scan_array);
    }

  if( option[SINGLE] && (output != stdout) )
    fclose( output);

  return 0;
}


void helper(void)
{
  printf("Usage: mda2ascii [-hvmtfe1a] [-x EXTENSION] [-d DIRECTORY] "
	 "[-o OUTPUT | -]\n"
         "         [-c COMMENTER] [-s SEPARATOR] "
         "[-i DIMENSION | -] FILE [FILE ...]\n"
         "Converts EPICS MDA files to ASCII files.\n"
         "\n"
         "-h  This help text.\n"
         "-v  Show version information.\n"
	 "-m  Merge higher dimensional values into data as redundant "
         "columns.\n"
	 "-t  Trim off all the commented header lines.\n"
         "-f  Friendlier data presentation with aligned columns.\n"
         "-e  Write \"Extra PV\" information into separate file. "
         "Overridden by -1, -t.\n"
	 "-1  Write multidimensional MDA files to a single ASCII file. "
	 "An overall\n"
	 "    header is at start of file, and scans are separated by "
	 "dividers.\n"
	 "-a  Write out all scans, even those that are not considered "
         "truly finished,\n"
	 "    normally due to an aborted scan.  These scans can be faulty.\n"
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
         "-i  Selects dimension(s) to be processed.  Possible parameters "
         "are dimension\n"
         "    number or \"-\" for all dimensions (default: dimensions "
         "containing detectors)\n"
         "\n"
         "The default behavior is to automatically generate the name(s) "
	 "of the output\n"
	 "file(s), split multidimensional MDA files into multiple "
	 "ASCII files,\n"
         "and generate files for all dimensions that contain detectors.\n"

	 );
}


void version(void)
{
  printf( "mda2ascii %s\n"
          "\n"
          "Copyright (c) 2010 UChicago Argonne, LLC,\n"
          "as Operator of Argonne National Laboratory.\n"
          "\n"
          "Written by Dohn Arms, dohnarms@anl.gov.\n", VERSION);
}



int main( int argc, char *argv[])
{
  int flag;

  int   option[8] = { 0, 0, 0, 0, 0, 0, 0 , 0};
  char *argument[5] = { NULL, NULL, NULL, NULL, NULL };
  char *outname = NULL;

  FILE *input;
  struct mda_file *mda;

  int dim_flag;

  int i;
  
  //  mtrace();

  if( argc == 1)
    {
      printf( "For help, type: mda2ascii -h\n");
      return 0;
    }

  /* 
     We start by parsing the command line.
  */

  dim_flag = 1;
  option[DIMENSION] = -1;
  while((flag = getopt( argc, argv, "hvmtfe1ac:s:x:d:i:o:")) != -1)
    {
      switch(flag)
	{
	case 'h':
	  helper();
	  return 0;
	  break;
	case 'v':
	  version();
	  return 0;
	  break;
	case 'm':
	  option[MERGE] = 1;
	  break;
	case 't':
	  option[TRIM] = 1;
	  break;
        case 'f':
          option[FRIENDLY] = 1;
          break;
        case 'e': 
          if( option[SINGLE] ) // impossible if single file
            break;
          option[EXTRA] = 1;
          break;
	case '1':
	  option[SINGLE] = 1;  
          option[EXTRA] = 0;  // impossible if single file
	  break;
	case 'a':
	  option[ALL] = 1;
	  break;
        case 'i':
          // default is -1, just detectors
          if((optarg[0] == '-') &&  (optarg[1] == '\0'))
            {
              dim_flag = 1;
              option[DIMENSION] = -2; // all
            }
          else
            {
              dim_flag = 0;
              option[DIMENSION] = atoi( optarg);
            }
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
#ifdef WINDOWS
// have to turn blackslashes in directory paths to forward slashes
          {
            char *p;
            p = argument[DIRECTORY];
            while( *p != '\0')
              {
                if( *p == '\\')
                  *p = '/';
                p++;
              }
          }
#endif
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

  if( !dim_flag && (option[DIMENSION] <= 0) )
    {
      fprintf( stderr, 
               "Don't understand which dimensions you want shown!\n");
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
          option[EXTRA] = 0;
	  free( argument[EXTENSION]);
	  free( argument[DIRECTORY]);
	  argument[EXTENSION] = argument[DIRECTORY] = NULL;
	}
      else
	{
	  char *s, *t, *p;
	      
	  s = outname;

#ifdef WINDOWS
          p = s;
          while( *p != '\0')
            {
              if( *p == '\\')
                *p = '/';
              p++;
            }
#endif
	      
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

  if( argument[EXTENSION] == NULL)
    argument[EXTENSION] = strdup( "asc" );

  if( argument[DIRECTORY] == NULL)
    argument[DIRECTORY] = strdup( "." );

  /* The -o case will only make one loop */
  for( i = optind; i < argc; i++)
    {
      /* there's no reason the -o case needs to do this */
      if( outname == NULL)
	{
          char *s, *t, *p;

	  free( argument[BASE]);

          s = strdup( argv[i]);
  
#ifdef WINDOWS
          p = s;
          while( *p != '\0')
            {
              if( *p == '\\')
                *p = '/';
              p++;
            }
#endif

          t = strrchr( s, '/');
          if( t == NULL)
            t = s;
	  
          p = strrchr( t, '.');
          if( p != NULL)
            *p = '\0';
	      
          argument[BASE] = strdup( t);
          free( s);
	}

      /* Now we load up the MDA file into the mda structure. */
      if( (input = fopen( argv[i], "rb")) == NULL)
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
      
      if( !dim_flag && (option[DIMENSION] > mda->header->data_rank))
        {
          fprintf( stderr, 
                   "Skipping \"%s\": this file contains only %d dimension%s!\n",
                   argv[i], mda->header->data_rank, 
                   (mda->header->data_rank > 1) ? "s" : "");
          mda_unload(mda);
          continue;
        }

      /* Send the mda structure, along with variables, to be processed. */
      if( printer( mda, option, argument) )
	break;

      /* Free up the memory allocated by the mda structure */
      mda_unload(mda);
    }

  //  muntrace();

  return 0;
}


