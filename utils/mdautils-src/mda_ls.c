/*************************************************************************\
* Copyright (c) 2010 UChicago Argonne, LLC,
*               as Operator of Argonne National Laboratory.
* This file is distributed subject to a Software License Agreement
* found in file LICENSE that is included with this distribution. 
\*************************************************************************/


/*

  Written by Dohn A. Arms, Argonne National Laboratory
  Send comments to dohnarms@anl.gov
  
  0.1.0 -- May 2009
  1.0.0 -- October 2009
               Added Search capabilities
  1.0.1 -- November 2009
               Redid directory scanning code to not use scandir()
  1.1   -- November 2010

 */



#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <unistd.h>
#include <dirent.h>


#include "mda-load.h"


#define VERSION "1.1.0 (November 2010)"


// this function relies too much on the input format not changing
void time_reformat( char *original, char *new)
{
  int i;

  char *months[12] = { "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };


  for( i = 0; i < 4; i++)
    new[i] = original[8+i];

  new[4] = '-';

  for( i = 0; i < 12; i++)
    {
      if( !strncasecmp( months[i], original, 3) )
        {
          new[5] = '0' + (i+1)/10;
          new[6] = '0' + (i+1)%10;
          break;
        }
    }
  if( i == 12)
    {
      new[0] = '\0';
      return;
    }

  new[7] = '-';

  for( i = 0; i < 2; i++)
    new[8+i] = original[4+i];

  new[10] = ' ';

  strncpy( &new[11], &original[13], 8);
  
  new[19] = '\0';
}




void helper(void)
{
  printf( "Usage: mda-ls [-hvf] [-p POSITIONER] [-d DETECTOR] [-t TRIGGER] [DIRECTORY]\n"
          "Shows scan information for all MDA files in a directory.\n"
          "\n"
          "-h  This help text.\n"
          "-v  Show version information.\n"
	  "-f  Show a fuller listing, including the time of the scan start.\n"
          "-p  Include only listings with POSITIONER as a scan positioner.\n"
          "-d  Include only listings with DETECTOR as a scan detector.\n"
          "-t  Include only listings with TRIGGER as a scan trigger.\n"
          "\n"
          "The directory searched is specified with DIRECTORY else the current directory\n"
          "is used. The format of the listing is: filename, [date and time,] scan size,\n"
          "and positioners. The scansize shows the number of points for each dimension;\n"
          "an incomplete highest level scan has the intended number shown in parentheses.\n"
          "The positioner entries show: scan level, positioner PV, and description.\n"
          );

}


void version(void)
{
  printf( "mda-ls %s\n"
          "\n"
          "Copyright (c) 2010 UChicago Argonne, LLC,\n"
          "as Operator of Argonne National Laboratory.\n"
          "\n"
          "Written by Dohn Arms, dohnarms@anl.gov.\n", VERSION);
}


int filter(const struct dirent *a)
{
  int len;

  len = strlen( a->d_name);

  if( len < 5)
    return 0;
  if( strcmp( ".mda", &a->d_name[len-4]) )
    return 0;

  return 1;
}

int sort(const char **a, const char **b)
{
  return(strcmp(*a, *b));
}

int mda_dir(const char *dirname, char ***namelist )
{
  // shove entries on linked list stack, and pop them back onto array
  struct link
  {
    char *name;
    struct link *next;
  };

  struct link *head, *entry;
  int count;
  DIR *dir;
  struct dirent *direntry;
  int i;

  head = NULL;

  if ((dir = opendir(dirname)) == NULL)
     return -1;
  count = 0;
  while( (direntry = readdir(dir)) != NULL)
    {
      if( !filter(direntry)) 
        continue;
      entry = (struct link *) malloc( sizeof( struct link));
      if( entry == NULL)
        return -1;

      entry->name = strdup( direntry->d_name);
      if( entry->name == NULL)
        return -1;
      entry->next = head;
      head = entry;
      count++;
    }
  if( closedir(dir)) 
    return -1;
  if( !count) 
    return 0;

  *namelist = (char **) malloc( count * sizeof( char *) );
  if( *namelist == NULL)
    return -1;
  for( i = count - 1; i >= 0 ; i--)
    { 
      entry = head;
      (*namelist)[i] = entry->name;
      head = entry->next;
      free( entry);
    }

  qsort((void *) (*namelist), (size_t) count, sizeof( char *), 
        (const void *) &sort);
  
  return count;
}


int main( int argc, char *argv[])
{
  char **filelist;
  int dir_number;

  struct mda_fileinfo **fileinfos;
  FILE *fptr;

  char *dir;


#define STRING_SIZE (4096)
#define FORMAT_SIZE (256)

  char string[STRING_SIZE];
  char name_format[FORMAT_SIZE];
  char dim_format[FORMAT_SIZE];

  int max_namelen, max_dimlen, max_timelen, offset;

  int full_flag = 0;
  int search_flag = 0;
  int positioner_flag = 0;
  char *positioner_term = NULL;
  int detector_flag = 0;
  char *detector_term = NULL;
  int trigger_flag = 0;
  char *trigger_term = NULL;

  // values are to shut up gcc
  int   allow_count = 0;
  char *allow_list = NULL;

  int opt;


  int i, j, k, m, n;


  while((opt = getopt( argc, argv, "hvfp:d:t:")) != -1)
    {
      switch(opt)
        {
        case 'h':
          helper();
          return 0;
          break;
        case 'v':
          version();
          return 0;
          break;
        case 'f':
          full_flag = 1;
          break;
	case 'p':
	  positioner_flag = 1;
          search_flag = 1;
	  positioner_term = strdup( optarg);
	  break;
	case 'd':
	  detector_flag = 1;
          search_flag = 1;
	  detector_term = strdup( optarg);
	  break;
	case 't':
	  trigger_flag = 1;
          search_flag = 1;
	  trigger_term = strdup( optarg);
	  break;
        case ':':
          // option normally resides in 'optarg'
          printf("Error: option missing its value!\n");  
          return -1;
          break;
        }
    }

  if( (argc - optind) > 1)
    {
      helper();
      return 1;
    }

  if( (argc - optind) == 0)
    {
      dir = NULL;
      dir_number = mda_dir( ".", &filelist);
    }
  else
    {
      dir = strdup( argv[argc - 1]);
      dir_number = mda_dir( dir, &filelist);
    }

  if (dir_number <= 0)
    {
      printf("No MDA files in the directory.\n");
      return 1;
    }

  if( (dir != NULL) &&  chdir( dir) )
    {
      printf("Can't change to that directory.\n");
      return 1;
    }

  
  fileinfos = (struct mda_fileinfo **) 
    malloc( dir_number * sizeof(struct mda_fileinfo *) );
  for( i = 0; i < dir_number; i++)
    {
      if( (fptr = fopen( filelist[i], "rb")) == NULL)
        {
          printf("Can't open file: \"%s\".\n", filelist[i] );
          return 1;
        }
      fileinfos[i] = mda_info_load( fptr);
      fclose(fptr);
    }

  if( search_flag)
    {
      allow_count = 0;
      allow_list = (char *) malloc( dir_number * sizeof(char) );
      for( i = 0; i < dir_number; i++)
	allow_list[i] = 0;
      for( i = 0; i < dir_number; i++)
	{
          if( positioner_flag) 
            {
              for( k = 0; k < fileinfos[i]->data_rank; k++)
                if( fileinfos[i]->scaninfos[k]->number_positioners)
                  for( j = 0; j < fileinfos[i]->scaninfos[k]->number_positioners; j++)
                    if( !strcmp( positioner_term, 
                                 (fileinfos[i]->scaninfos[k]->positioners[j])->name ))
                      {
                        allow_list[i] = 1;
                        allow_count++;
                        goto Pos_Shortcut;
                      }
            }
	Pos_Shortcut:
	  ;
          if( detector_flag )
            {
              for( k = 0; k < fileinfos[i]->data_rank; k++)
                if( fileinfos[i]->scaninfos[k]->number_detectors)
                  for( j = 0; j < fileinfos[i]->scaninfos[k]->number_detectors; j++)
                    if( !strcmp( detector_term, 
                                 (fileinfos[i]->scaninfos[k]->detectors[j])->name ))
                      {
                        allow_list[i] = 1;
                        allow_count++;
                        goto Det_Shortcut;
                      }
            }
	Det_Shortcut:
	  ;
          if( trigger_flag )
            {
              for( k = 0; k < fileinfos[i]->data_rank; k++)
                if( fileinfos[i]->scaninfos[k]->number_triggers)
                  for( j = 0; j < fileinfos[i]->scaninfos[k]->number_triggers; j++)
                    if( !strcmp( trigger_term, 
                                 (fileinfos[i]->scaninfos[k]->triggers[j])->name ))
                      {
                        allow_list[i] = 1;
                        allow_count++;
                        goto Trig_Shortcut;
                      }
            }
	Trig_Shortcut:
	  ;
	}

      if( !allow_count)
	{
	  printf("No MDA files in the directory fit your search.\n");
	  return 1;
	}
    }

  max_namelen = 0;
  max_dimlen = 0;
  for( i = 0; i < dir_number; i++)
    {
      if( search_flag)
	if( !allow_list[i] )
	  continue;

      j = strlen( filelist[i]);
      if( j > max_namelen)
        max_namelen = j;

      if( fileinfos[i] == NULL)
        {
          //          printf("Invalid\n");
          if( 7 > max_dimlen)
            max_dimlen = 7;
        }
      else
        {
          if( fileinfos[i]->dimensions[0] != fileinfos[i]->last_topdim_point)
            j = snprintf( string, STRING_SIZE, "%li(%li)", 
                          fileinfos[i]->last_topdim_point, 
                          fileinfos[i]->dimensions[0]);
          else
            j = snprintf( string, STRING_SIZE, "%li", fileinfos[i]->dimensions[0]);

          for( k = 1; k < fileinfos[i]->data_rank; k++)
            j += snprintf( &string[j], STRING_SIZE - j, "x%li", 
                           fileinfos[i]->dimensions[k]);

          if( j > max_dimlen)
            max_dimlen = j;
        }

    }

  max_timelen = 19;

  snprintf( name_format, FORMAT_SIZE, "%%%ds  ", max_namelen);  // "%12s - "
  snprintf( dim_format, FORMAT_SIZE, "%%-%ds -", max_dimlen);  // "%-12s "

  offset = max_namelen + max_dimlen + 4;
  if( full_flag)
    offset += (2 + max_timelen);

  for( i = 0; i < dir_number; i++)
    {
      if( search_flag)
	if( !allow_list[i] )
	  continue;

      printf(name_format, filelist[i]);

      if( fileinfos[i] == NULL)
        {
          printf("Invalid\n");
          continue;
        }

      if( full_flag)
        {
          time_reformat( fileinfos[i]->time, string);
          printf( "%s  ", string );
        }

      if( fileinfos[i]->dimensions[0] != fileinfos[i]->last_topdim_point)
        j = snprintf( string, STRING_SIZE, "%li(%li)", 
                      fileinfos[i]->last_topdim_point, fileinfos[i]->dimensions[0]);
      else
        j = snprintf( string, STRING_SIZE, "%li", fileinfos[i]->dimensions[0]);
      for( k = 1; k < fileinfos[i]->data_rank; k++)
        j += snprintf( &string[j], STRING_SIZE - j, "x%li", 
                       fileinfos[i]->dimensions[k]);
      printf(dim_format, string);

      m = 0;
      for( k = 0; k < fileinfos[i]->data_rank; k++)
        if( fileinfos[i]->scaninfos[k]->number_positioners)
          for( j = 0; j < fileinfos[i]->scaninfos[k]->number_positioners; j++)
            {
              if( m)
                for( n = 0; n < offset; n++)
                  printf(" ");
              printf(" %dD %s",
                     fileinfos[i]->scaninfos[k]->scan_rank,
                     (fileinfos[i]->scaninfos[k]->positioners[j])->name );
              if( (fileinfos[i]->scaninfos[k]->positioners[j])->description[0] 
                  != '\0' )
                printf(" (%s)",
                       (fileinfos[i]->scaninfos[k]->positioners[j])->description );
              printf("\n");
              m = 1;
            }
      if( !m)
        printf("\n");
    }

  for( i = 0; i < dir_number; i++)
    {
      if( fileinfos[i] != NULL) 
        mda_info_unload(fileinfos[i]);
    }
  free( filelist);
  free( fileinfos);

  if( search_flag)
    free(allow_list );



  return 0;
}


