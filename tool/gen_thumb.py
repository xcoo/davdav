#!/usr/bin/env python
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
import re

from configobj import ConfigObj

from PIL import Image

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# OR mapping
Base = declarative_base()

class Thumbnail(Base):

    __tablename__ = 'thumbnail'

    id         = Column(Integer, primary_key=True, autoincrement=True)
    original   = Column(String(255), nullable=False)
    thumbnail  = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False, default=sqlalchemy.func.now())
    updated_at = Column(Date, nullable=False, default=sqlalchemy.func.now())
    enable     = Column(Boolean, nullable=False, default=True)

    def __init__(self, original, thumbnail):
        self.original  = original
        self.thumbnail = thumbnail

    def __repr__(self):
        if self.id == None:
            return "<thumb('%s', '%s', '%s')>" % (self.original,
                                                  self.created_at,
                                                  self.updated_at)
        else:
            return "<thumb('%d', '%s', '%s', '%s')>" % (self.id,
                                                        self.original,
                                                        self.created_at,
                                                        self.updated_at)

# Load configuration
try:
    ini_file = os.environ['DAVDAV_CONFIG']
    conf = ConfigObj(ini_file)
    db_uri     = conf.get('DB_URI')
    webdav_dir = conf.get('WEBDAV_DIR')
    thumb_dir  = conf.get('THUMB_DIR')
except KeyError:
    print "Not found environment 'DAVDAV_CONFIG'"
    db_uri     = 'mysql://root:root@localhost/davdav?charset=utf8'
    webdav_dir = os.path.join(os.path.dirname(__file__), '../app/static/test/main')
    thumb_dir  = os.path.join(os.path.dirname(__file__), '../app/static/test/thumbnail')

engine = create_engine(db_uri,
                       encoding='utf-8',
                       convert_unicode=True,
                       pool_recycle=3600)

def exist_thumb_in_db(orig_file):
    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))

    query = session.query(Thumbnail).filter(Thumbnail.original==orig_file)
    try:
        thumbnail = query.one()
        return True
    except NoResultFound, e:
        return False
    finally:
        session.close()

def gen_thumb(src_file, dst_file):
    im = Image.open(src_file)
    im.thumbnail((256, 256))
    im.save(dst_file)

def add_thumb_to_db(orig_file, thumb_file):
    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    
    thumb = Thumbnail(orig_file, thumb_file)

    session.add(thumb)
    session.commit()
    session.close()

def main():
    for d in os.listdir(webdav_dir):

        if not os.path.isdir(os.path.join(webdav_dir, d)):
            continue

        for dt_root, dt_dirs, dt_files in os.walk(os.path.join(webdav_dir,d)):

            for f in dt_files:

                base, ext = os.path.splitext(f)
                if not re.match('^\.(jpe?g|png|gif|bmp)', ext, re.IGNORECASE):
                    continue
                    
                rel_src = os.path.join(d, f)
                rel_dst = os.path.join(d, f)
                abs_src = os.path.join(webdav_dir, rel_src)
                abs_dst = os.path.join(thumb_dir, rel_dst)

                if exist_thumb_in_db(rel_src):
                    print '%s: The thumbnail image was already generated' % rel_src
                    continue

                intermediate_dir = os.path.join(thumb_dir, d)
                if not os.path.isdir(intermediate_dir):
                    os.makedirs(intermediate_dir)

                gen_thumb(abs_src, abs_dst)
                add_thumb_to_db(rel_src, rel_dst)
                
                print rel_src + ': Generate a new thumbnail image'

if __name__ == '__main__':
    main()
