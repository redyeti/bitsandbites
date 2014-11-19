from mongoengine import *
from mongoengine import base

DBNAME = 'bitsandbites'
conn = connect(DBNAME, username="bitsandbites", password="RyfexgCDwdTUk45")

# define some types
import types
