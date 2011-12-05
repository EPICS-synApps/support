/*************************************************************************\
* Copyright (c) 2010 UChicago Argonne, LLC,
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory
  Send comments to dohnarms@anl.gov
  
  0.1   -- August 2005
  0.1.1 -- December 2006
           Added support for files that have more than 32k points.
  0.2.0 -- November 2007
           Use new fileinfo routines to get information.
  1.0.0 -- October 2009
           Overhauled the output format, adding information about 
           detectors and triggers.
  1.0.1 -- May 2010
           Added showing numbering of detectors, positioners, 
           and triggers as done by saveData.
  1.1   -- November 2010

 */



/****************  mda_info.c  **********************/


#include <stdio.h>
#include <string.h>

#include <unistd.h>

#include "mda-load.h"

//#include <mcheck.h>

#define VERSION "1.1.0 (November 2010)"




/////////////////////////////////////////////////////////////////////////////

int test_print(char *format, char *string)
{
  if( string[0] != '\0')
    return printf( format, string);

  return 0;
}


int information( struct mda_fileinfo *fileinfo)
{
  int i, j;


  printf("MDA file version = %g\n", fileinfo->version);
  printf("     Scan number = %li\n", fileinfo->scan_number);
  printf("  Dimensionality = %i\n", fileinfo->data_rank);
  printf("       Scan size = ");
  if( fileinfo->last_topdim_point != fileinfo->dimensions[0] )
    printf("(%li)", fileinfo->last_topdim_point );
  for( i = 0; i < fileinfo->data_rank; i++)
    {
      if( i)
	printf("x");
      printf( "%li", fileinfo->dimensions[i]);
    }
  printf("\n");
  printf(" Scan start time = %s\n", fileinfo->time);

  if( !fileinfo->regular)
    {
      printf("\n      Regularity = FALSE\n"); 
      printf("Actual scan size = ");
      if( fileinfo->last_topdim_point != 
          fileinfo->scaninfos[0]->requested_points )
        printf( "(%li)", fileinfo->last_topdim_point);
      for( i = 0; i < fileinfo->data_rank; i++)
        {
          if( i)
            printf("x");
          printf( "%li", fileinfo->scaninfos[i]->requested_points);
        }
      printf("\n");
    }

  for( i = 0; i < fileinfo->data_rank; i++)
    {
      printf("\n%i-D scanner name = %s\n", fileinfo->scaninfos[i]->scan_rank,
             fileinfo->scaninfos[i]->name);
      printf("%i-D triggers:%s\n", fileinfo->scaninfos[i]->scan_rank,
             !fileinfo->scaninfos[i]->number_triggers ? "  None" : "" );
      for( j = 0; j < fileinfo->scaninfos[i]->number_triggers; j++)
	{
	  printf( "    %i (T%d) = %s\n", j + 1,
                  (fileinfo->scaninfos[i]->triggers[j])->number + 1,
                  (fileinfo->scaninfos[i]->triggers[j])->name);
        }
      printf("%i-D positioners:%s\n", fileinfo->scaninfos[i]->scan_rank,
             !fileinfo->scaninfos[i]->number_positioners ? "  None" : "");
      for( j = 0; j < fileinfo->scaninfos[i]->number_positioners; j++)
	{
	  printf("    %i (P%i) = %s", j + 1, 
                 (fileinfo->scaninfos[i]->positioners[j])->number + 1,
                 (fileinfo->scaninfos[i]->positioners[j])->name);
          test_print(" (%s)", 
                     (fileinfo->scaninfos[i]->positioners[j])->description);
          test_print(" [%s]", (fileinfo->scaninfos[i]->positioners[j])->unit);
          printf("\n");
          if( (fileinfo->scaninfos[i]->positioners[j])->readback_name[0] 
              != '\0')
            {
              printf("             %s",
                     (fileinfo->scaninfos[i]->positioners[j])->readback_name );
              test_print(" (%s)", 
                         (fileinfo->scaninfos[i]->positioners[j])->readback_description);
              test_print(" [%s]", 
                         (fileinfo->scaninfos[i]->positioners[j])->readback_unit);
              printf("\n");
            }
	}
      
      printf("%i-D detectors:%s\n", fileinfo->scaninfos[i]->scan_rank,
             !fileinfo->scaninfos[i]->number_detectors ? "  None" : "");
      for( j = 0; j < fileinfo->scaninfos[i]->number_detectors; j++)
	{
	  printf("  %02i (D%02i) = %s", j + 1,
                 (fileinfo->scaninfos[i]->detectors[j])->number + 1,
		 (fileinfo->scaninfos[i]->detectors[j])->name);
          test_print(" (%s)", (fileinfo->scaninfos[i]->detectors[j])->description);
          test_print(" [%s]", (fileinfo->scaninfos[i]->detectors[j])->unit);
          printf("\n");
	}
    }
  
  return 0;
}



void help(void)
{
  printf("Usage: mda-info [-hv] FILE\n"
         "Prints the basic scan information about the EPICS MDA file, FILE.\n"
         "\n"
         "-h  This help text.\n"
         "-v  Show version information.\n"
         "\n"
         "Information such as dimensionality and time of scan start are shown,\n"
         "as well as all the positioners, detectors, and triggers for each dimension.\n"
         "For each trigger, positioner, and detector there is both a number and\n"
         "(in parentheses) the PV field number used in saveData.\n"
         );
}

void version(void)
{
  printf("mda-info %s\n"
         "\n"
         "Copyright (c) 2010 UChicago Argonne, LLC,\n"
         "as Operator of Argonne National Laboratory.\n"
         "\n"
         "Written by Dohn Arms, dohnarms@anl.gov.\n",
         VERSION);
}

int main( int argc, char *argv[])
{
  FILE *input;
  struct mda_fileinfo *fileinfo;

  int opt;

  //  mtrace();  // for looking for memory leaks

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
      printf("For help, type: mda-info -h\n");
      return 0;
    }

  if( (input = fopen( argv[optind], "rb")) == NULL)
    {
      fprintf(stderr, "Can't open file \"%s\"!\n", argv[optind]);
      return 1;
    }

  if( (fileinfo = mda_info_load( input)) == NULL )
    {
      fprintf(stderr, "Loading file \"%s\" failed!\n", argv[optind]);
      return 1;
    }

  fclose(input);

  information(fileinfo);

  mda_info_unload(fileinfo);

  //  muntrace();  // for looking for memory leaks

  return 0;
}


