from mongoengine import *

DBNAME = 'bitsandbites'
conn = connect(DBNAME, username="bitsandbites", password="RyfexgCDwdTUk45")

# define some types
import types
