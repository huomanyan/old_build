import MySQLdb
import time
import os
import json
import cStringIO
import pycurl
import redis
import MySQLdb.cursors

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)