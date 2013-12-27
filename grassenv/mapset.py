import os
import sqlite3
import tempfile
import shutil
from grass.script import run_command

class MapsetError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Mapset(object):
    def __init__(self, mapset='PERMANENT', location='gbl_ll', gdata=os.path.join(os.environ['HOME'],'grassdata'), create=False):
        # setup GIS_LOCK, GISRC
        os.environ['GIS_LOCK'] = str(os.getpid())
        self.tmpdir = tempfile.mkdtemp(prefix='grass6_')
        os.environ['GISRC'] = os.path.join(self.tmpdir,'gisrc')
        shutil.copy(os.path.join(os.environ['HOME'],'.grassrc6'), os.environ['GISRC'])
        os.environ['GRASS_TRUECOLOR']='TRUE'
        self.mapset = mapset
        self.location = location
        self.gdata = gdata
        self.sqlitedb = os.path.join(gdata, location, mapset, 'sqlite.db')
        self.set_mapset(mapset, location, gdata, create)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        if hasattr(self, 'conn'):
            self.conn.close()
        try:
            os.remove(os.path.join(self.gdata, self.location, self.mapset,'.gislock'))
        except OSError:
            pass
        try:
            shutil.rmtree(self.tmpdir)
        except OSError:
            pass

    def set_mapset(self, mapset=None, location=None, gdata=None, create=False):
        if mapset is None:
            mapset = self.mapset
        if location is None:
            location = self.location
        if gdata is None:
            gdata = self.gdata
        try:
            self._confirm_mapset(mapset, location, gdata)
        except (AssertionError):
            prev_mapset = self.mapset
            self.mapset = mapset
            prev_location = self.location
            self.location = location
            prev_gdata = self.gdata
            self.gdata = gdata
            prev_sqlitedb = self.sqlitedb
            self.sqlitedb = os.path.join(self.gdata, self.location, self.mapset, 'sqlite.db')
            if create:
                err = run_command('g.mapset', 'c', gisdbase=self.gdata, location=self.location, mapset=self.mapset)
                if err:
                    #for some reason, sometimes doesn't work the first time
                    err = run_command('g.mapset', 'c', gisdbase=self.gdata, location=self.location, mapset=self.mapset)
            else:
                err = run_command('g.mapset', gisdbase=self.gdata, location=self.location, mapset=self.mapset)
            if err:
                self.mapset = prev_mapset
                self.location = prev_location
                self.gdata = prev_gdata
                self.sqlitedb = prev_sqlitedb
                raise MapsetError('Unable to change mapset to: {0}/{1}/{2}'.format(gdata,location,mapset))
            self._confirm_mapset(self.mapset, self.location, self.gdata)
            run_command('g.region','d')
        run_command('db.connect',driver='sqlite',database=self.sqlitedb)

    def get_db_connection(self):
        self.conn = sqlite3.connect(self.sqlitedb)
        return self.conn

    def get_columns(self, vect):
        if not hasattr(self, 'conn'):
            self.conn = self.get_db_connection()
        return self.conn.execute('PRAGMA table_info({0});'.format(vect)).fetchall()

    def get_other_db_connection(self,mapset=None,location=None,gdata=None):
        if mapset is None:
            mapset = self.mapset
        if location is None:
            location = self.location
        if gdata is None:
            gdata = self.gdata
        return sqlite3.connect(os.path.join(data,location,mapset,'sqlite.db'))

    def confirm_mapset(self):
        return self._confirm_mapset(self.mapset, self.location, self.gdata)

    def _confirm_mapset(self, mapset, location, gdata):
        with open(os.environ['GISRC']) as f:
            for line in f:
                toks=line.replace('\n','').replace(' ','').split(':')
                if toks[0] == 'GISDBASE':
                    assert toks[1] == gdata
                if toks[0] == 'LOCATION_NAME':
                    assert toks[1] == location
                if toks[0] == 'MAPSET':
                    assert toks[1] == mapset
        print 'GISDBASE = ', gdata
        print 'LOCATION = ', location
        print 'MAPSET = ', mapset
        return 

