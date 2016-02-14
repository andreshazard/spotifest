from library import create_app

from library.auth import *
from library.app import *
from library.search import *
from library.helpers import *
from library.db import *

if __name__ == '__main__':
    app.run(debug=True)
