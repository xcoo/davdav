# -*- coding: utf-8 -*-

#
#   davdav
#   https://github.com/xcoo/davdav
#   Copyright (C) 2012, Xcoo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import ConfigParser

# Set main configuration file's path.
davdav_conf_file = os.path.join(os.path.dirname(__file__), '../config/davdav.ini')

# Set virtualenv configuration file's path.
virtualenv_conf_file = os.path.join(os.path.dirname(__file__), '../config/virtualenv.ini')

sys.stdout = sys.stderr

os.environ['DAVDAV_CONFIG'] = davdav_conf_file

if os.path.isfile(virtualenv_conf_file):
    conf = ConfigParser.SafeConfigParser()
    conf.read(virtualenv_conf_file)
    activate_this = conf.get('virtualenv', 'VIRTUALENV_ACTIVATE')
    execfile(activate_this, dict(__file__=activate_this))

from app import app as application
