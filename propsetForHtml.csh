#!/bin/csh
svn propset svn:mime-type text/html $1
svn commit -m "mime-type=text/html" $1
