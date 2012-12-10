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

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

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

class ThumbnailDao():

    def __init__(self, engine):
        self._engine = engine

    def select_by_filepath(self, filepath):
        session = scoped_session(sessionmaker(bind=self._engine))
        query = session.query(Thumbnail).filter(Thumbnail.original==filepath)
        try:
            thumbnail = query.one()
            return thumbnail
        except NoResultFound:
            return None
        finally:
            session.close()
            
    def disable_thumbnail(self, thumb_id):
        session = scoped_session(sessionmaker(bind=self._engine))
        query = session.query(Thumbnail).filter(Thumbnail.id==thumb_id)
        try:
            thumbnail = query.one()
            thumbnail.enable = 0
            session.commit()
        except NoResultFound:
            raise
        finally:
            session.close()
