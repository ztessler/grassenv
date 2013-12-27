* Grassenv

Grassenv provides classes for managing a GRASS GIS environment from Python,
without first starting a GRASS session.

This requires the GRASS python binding to be installed, and assumes the use of
sqlite databases for vector map attribute tables.

There are two classes:

* Mapset
* Grassdb

** Mapset

The Mapset class is a context manager that setups and tears down the
environment variables that GRASS modules expect, such as LOCATION, MAPSET,
GDATA, GISRC, and others.  It manages the lock files that prevent a single
mapset from being written two by two users simultaneously.

*** Use
from grassenv import Mapset

m = Mapset(location='location_name', mapset='PERMANENT', gdata='grassdata')
m.run('g.region', 'p')

or

with Mapset(location='location_name', mapset='PERMANENT', gdata='grassdata') as
m:
    m.run('g.region', 'p')
    output = m.read('g.region', 'p')

The context manager form cleans up the environment variables and lockfiles when
the block ends.

** Grassdb

Access vector map attribute tables direcly through the sqlite3 module

*** Use

db = Grassdb(location='location_name', mapset='PERMANENT', gdata='grassdata')
db.get_columns('vector_map')
db.get_data('column_name', 'vector_map', 'cat')
db.close()

** Caveates

* Hacky! No guarentees to set all environment variables properly, but works for
  me
* Forces sqlite3 database for vector maps
* Leaves a mess behind in /tmp
* Default location, mapset, grassdata directory should probably be edited
