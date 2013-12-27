import os
import sqlite3

class Grassdb(object):
    '''
    Object representing a grass database, but connecting directly through sqlite
    '''
    def __init__(self, mapset='PERMANENT', location='gbl_ll', gdata=os.path.join(os.environ['HOME'], 'grassdata'), db='sqlite.db'):
        self.sqlitedb = os.path.join(gdata,location,mapset,db)
        self.conn = sqlite3.connect(self.sqlitedb)
    
    def get_data(self, col, table, key='cat'):
        return dict(self.conn.execute('SELECT {0},{1} '
                                      'FROM {2} '
                                      'ORDER BY {0}'.format(key, col, table)).fetchall())
                          
    def get_columns(self, table):
        return self.conn.execute('PRAGMA table_info({0});'.format(table)).fetchall()
                          
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        self.conn.close()

