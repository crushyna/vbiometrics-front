
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/AppName")

from AppName import app as application
application.secret_key = 'yuapfosiu23efj2kj32fkjvxjdj'