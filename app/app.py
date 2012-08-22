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

import datetime
import os
import re
import sys

from flask import Flask
from flask import render_template, redirect, request, abort
from werkzeug import SharedDataMiddleware
from sqlalchemy import create_engine

from thumbnail import ThumbnailDao

app = Flask(__name__)

try:
    app.config.from_envvar('DAVDAV_CONFIG')
except RuntimeError:
    app.debug   = True
    app.testing = True
    app.config['DB_URI']          = 'mysql://root:root@localhost/davdav?charset=utf8'
    app.config['WEBDAV_ROOT_URL'] = 'http://localhost:5000/test/main'
    app.config['THUMB_ROOT_URL']  = 'http://localhost:5000/test/thumbnail'
    app.config['WEBDAV_DIR']      = os.path.join(os.path.dirname(__file__), 'static/test/main')
    app.config['THUMB_DIR']       = os.path.join(os.path.dirname(__file__),'static/test/thumbnail')
    app.config['NUM_BY_PAGE']     = 2

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
        })

engine = create_engine(app.config['DB_URI'],
                       encoding='utf-8',
                       convert_unicode=True,
                       pool_recycle=3600)

thumbnail_dao = ThumbnailDao(engine)

@app.route('/')
def root():

    try:
        arg = request.args.get('page', '')
        if arg is not '':
            page = int(arg)
        else:
            page = 0
    except KeyError:
        page = 0

    pages = _count_pages()
    if page < 0 or pages < page:
        abort(404)

    dav_dates = _get_dav_dates(page)

    prev_page = None
    if page > 0:
        prev_page = page - 1

    next_page = None
    if page < _count_pages() - 1:
        next_page = page + 1

    return render_template('main.html', dav_dates=dav_dates,
                                        prev_page=prev_page,
                                        next_page=next_page)

@app.route('/top')
@app.route('/home')
@app.route('/main')
def redirect_root():
    return redirect('/')

@app.route('/detail/<path:img_path>')
def detail(img_path):
    img_src = '%s/%s' % (app.config['WEBDAV_ROOT_URL'], img_path)
    return render_template('detail.html', title=img_path, src=img_src, href=img_src)

def _get_dav_dates(page=0):
    webdav_dir  = app.config['WEBDAV_DIR']
    num_by_page = app.config['NUM_BY_PAGE']

    dav_dates = []

    dirs = os.listdir(webdav_dir)
    dirs.sort() 
    dirs.reverse()
    
    num = 0 
    for d in dirs:

        if not os.path.isdir(os.path.join(webdav_dir, d)):
            continue

        num += 1
        if num <= page * num_by_page:
            continue

        if len(dav_dates) >= num_by_page:
            break

        dav_imgs = []

        try:
            group_title = _format_date(d, '%Y%m%d', '%Y/%m/%d (%a)')
        except:
            continue

        for dt_root, dt_dirs, dt_files in os.walk(os.path.join(webdav_dir, d)):

            for f in dt_files:

                base, ext = os.path.splitext(f)
                if not re.match('^\.(jpe?g|png|gif|bmp)', ext, re.IGNORECASE):
                    continue
                    
                orig_path = os.path.join(d, f)
                thumb_path = thumbnail_dao.select_thumbnail(orig_path)

                try:
                    title = _format_date(base, '%Y%m%d_%H%M%S', '%H:%M')
                except:
                    continue

                if not thumb_path == None:
                    src = '%s/%s' % (app.config['THUMB_ROOT_URL'], thumb_path)
                else:
                    src = '/img/nothumbnail.jpg'

                href = '/detail/' + d + '/' + f

                dav_img = { 'title': title, 'src': src, 'href': href }
                dav_imgs.append(dav_img)

        dav_date = { 'title': group_title, 'dav_imgs': dav_imgs }
        dav_dates.append(dav_date)

    return dav_dates

def _count_pages():
    webdav_dir  = app.config['WEBDAV_DIR']
    num_by_page = app.config['NUM_BY_PAGE']

    pages = 0
    for d in os.listdir(webdav_dir)[::-1]:
        if not os.path.isdir(webdav_dir + '/' + d):
            continue
        pages += 1

    return round(pages / num_by_page)

def _format_date(dt_str, src_format, dst_format):
    dt = datetime.datetime.strptime(dt_str, src_format)
    return dt.strftime(dst_format)

if __name__ == '__main__':
    app.run()
