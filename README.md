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
Davdav is properly tested for the environment.
You can also use Davdav on other servers, but you have no guarantees.

## 1. Install packages and dependencies

    $ sudo apt-get update
    $ sudo apt-get upgrade
    
    # Install Git
    $ sudo apt-get install -y git
    
    # Install MySQL
    $ sudo apt-get install -y mysql-server mysql-client libmysqlclient-dev
    
    # Install Apache2 
    $ sudo apt-get install -y apache2 libapache2-mod-wsgi
    
    # Install Python libraries
    $ sudo apt-get install -y python-setuptools
    $ sudo easy_install pip
    $ sudo pip install Flask SQLAlchemy MySQL-python PIL configobj

## 2. Prepare

Create user and directory for thumbnail images.

    $ sudo adduser davdav
    $ sudo -H -u davdav mkdir /home/davdav/thumbnail

## 3. Download Davdav

Clone davdav repository.

    $ sudo -H -u davdav git clone https://github.com/xcoo/davdav.git /home/davdav/davdav

## 4. Setup MySQL

Create MySQL database.

    $ cd /home/davdav/davdav
    $ mysql -u root -p < db/davdav.sql

## 5. Setup configuration

Copy a configuration example.

    $ sudo -u davdav cp config/davdav.ini.example config/davdav.ini
    
Then, edit davdav.ini.
Change __DB_URI__, __WEBDAV_ROOT__, __THUMB_ROOT_URL__, __WEBDAV_DIR__, and __THUMB_DIR__ according to your environment.

    DEBUG=False
    TESTING=False

    DB_URI='mysql://user:password@localhost/davdav?charset=utf8'

    WEBDAV_ROOT_URL='http://webdav.example.com/'
    THUMB_ROOT_URL='http://davdav.example.com/thumbnail'

    WEBDAV_DIR='/var/www/webdav'
    THUMB_DIR='/home/davdav/thumbnail'

    NUM_BY_PAGE=10

If you want to use virtualenv, you have to edit __config/virtualenv.ini__.
Specify activate python file for your virtualenv.
Notice that you must not add quotation characters (', ") to the file path.

    $ sudo -u davdav cp config/virtualenv.ini.example config/virtualenv.ini
    
    [virtualenv]
    VIRTUALENV_ACTIVATE=/path/to/env/bin/activate_this.py       

If you do not use virtualenv, delete this file (virtualenv.ini).

## 6. Setup crontab

Setup crontab for generating thumbnail images.

    $ sudo -H -u davdav crontab -e
    */5 * * * * python /home/davdav/davdav/tool/cron.py

## 7. Setup Apache2

Setup WSGI in apache2 configuration like the following:

    <VirtualHost *:80>
        ServerName davdav.example.com

        WSGIScriptAlias / /home/davdav/davdav/app/davdav.wsgi
        WSGIDaemonProcess davdav user=www-data group=www-data processes=5 threads=10 home=/home/davdav/davdav/app python-path=/home/davdav/davdav/app
        WSGIProcessGroup davdav

        Alias /thumbnail /home/davdav/thumbnail
    </VirtualHost>

Restart apache.

    $ sudo service apache2 restart

Access to __http://davdav.example.com__ from Web browser.

# License

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.