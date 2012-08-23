# Davdav

"Davdav" is WebDAV viewer for uploaded pictures by Upupu.

# Requirements

* Python 2.7 and higher version
* Python libraries
    * Flask
    * SQLAlchemy
    * MySQL-python
    * PIL
    * configobj
* MySQL 5.0 and higher version
* Git

# Install

This installation guide is written for Ubuntu and Apache2 web server.
You can also use Davdav on other servers.

## Clone repository

    $ git clone https://github.com/xcoo/davdav.git

## Setup MySQL

    $ mysql -u root -p < db/davdav.sql

## Setup configuration

Copy a configuration example.

    $ cp config/davdav.ini.example config/davdav.ini
    
Then, edit davdav.ini.
Change __DB_URI__, __WEBDAV_ROOT__, __THUMB_ROOT_URL__, __WEBDAV_DIR__, and __THUMB_DIR__ according to your environment.

    DEBUG=False
    TESTING=False

    DB_URI='mysql://user:password@localhost/davdav?charset=utf8'

    WEBDAV_ROOT_URL='http://webdav.example.com/'
    THUMB_ROOT_URL='http://davdav.example.com/thumbnail'

    WEBDAV_DIR='/data/var/webdav'
    THUMB_DIR='/data/var/davdav/thumbnail'

    NUM_BY_PAGE=10

If you want to use virtualenv, you have to edit __config/virtualenv.ini__.
Specify activate python file for your virtualenv.
Notice that you must not add quotation characters (', ") to the file path.

    $ cp config/virtualenv.ini.example config/virtualenv.ini
    ----------
    VIRTUALENV_ACTIVATE=/home/davdav/davdav/.virtualenvs/davdav/bin/activate_this.py

If you do not use virtualenv, delete this file (virtualenv.ini).


## Setup crontab for generating thumbnail images

    $ crontab -e
    */5 * * * * python /home/davdav/davdav/tool/cron.py

## Setup webserver

### Apache2

    <VirtualHost *:80>
        ServerName davdav.example.com

        WSGIScriptAlias /davdav /home/davdav/davdav/app/davdav.wsgi
        WSGIDaemonProcess davdav user=www-data group=www-data processes=5 threads=10 home=/home/davdav/davdav/app python-path=/home/davdav/davdav/app
        WSGIProcessGroup davdav

        <Directory /home/davdav/davdav>
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

Restart apache.

    $ sudo service apache2 restart

Access to __http://davdav.example.com__ from Web browser.

# License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.