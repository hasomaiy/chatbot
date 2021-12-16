# -*- coding: utf-8 -*-

import codecs
from contextlib import contextmanager
import datetime
import math
import os
import random
import re
import subprocess
import sys
import time
import warnings

try:
    from io import StringIO
except ImportError:
    from io import StringIO



sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    PATH = os.path.dirname(os.path.realpath(__file__))
except:
    PATH = ""
