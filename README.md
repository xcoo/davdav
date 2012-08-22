# davdav

WebDAV viewer for uploaded pictures by Upupu.

# Requirements

* Python 2.7 and higher version
* Python libraries
    * Flask
    * SQLAlchemy
    * MySQL-python
    * PIL
    * configobj
* MySQL 5.0 and higher version

# Usage

## Clone Git repository

    $ git clone https://github.com/xcoo/davdav.git

## Setup configuration

    $ cp config/davdav.ini.example config/davdav.ini

## Apache2 configuration

    <VirtualHost *:80>
        ServerName davdav.example.com

        WSGIScriptAlias /davdav /home/davdav/davdav/app/production.wsgi
        WSGIDaemonProcess davdav user=www-data group=www-data processes=5 threads=10 home=/home/davdav/davdav/app python-path=/home/davdav/davdav/app
        WSGIProcessGroup davdav

        <Directory "/home/davdav/davdav">
            Order deny,allow
            allow from all
        </Directory>
    </VirtualHost>

#License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.