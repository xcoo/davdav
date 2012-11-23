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
import math
import os
import re
import sys
from functools import wraps

from flask import Flask, Response
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
    app.config['FOOTER_ENABLE']   = True
    app.config['AUTH_ENABLE']     = True
    app.config['AUTH_USERNAME']   = 'username'
    app.config['AUTH_PASSWORD']   = 'password'
    
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/': os.path.join(os.path.dirname(__file__), 'static')
        })

engine = create_engine(app.config['DB_URI'],
                       encoding='utf-8',
                       convert_unicode=True,
                       pool_recycle=3600)

thumbnail_dao = ThumbnailDao(engine)


# Authorization -----

def _check_auth(username, password):
    return username == app.config['AUTH_USER'] and password == app.config['AUTH_PASSWORD']

def _authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if app.config['AUTH_ENABLE'] and (not auth or not _check_auth(auth.username, auth.password)):
            return _authenticate()
        return f(*args, **kwargs)
    return decorated


# Requests -----

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
    if page < pages - 1:
        next_page = page + 1

    return render_template('main.html', dav_dates=dav_dates,
                                        prev_page=prev_page,
                                        next_page=next_page,
                                        footer_enable=app.config['FOOTER_ENABLE'])

@app.route('/top')
@app.route('/home')
@app.route('/main')
def redirect_root():
    return redirect('/')

@app.route('/detail/<path:img_path>')
def detail(img_path):
    title = _format_date(img_path.split('/')[1].split('.jpg')[0],
                         '%Y%m%d_%H%M%S', '%m/%d %H:%M')
    img_src = '%s/%s' % (app.config['WEBDAV_ROOT_URL'], img_path)
    
    prev_next_img = _get_prev_next_img(img_path)
    prev_img_ref = prev_next_img['prev_img']
    next_img_ref = prev_next_img['next_img']

    return render_template('detail.html', title=title,
                                          src=img_src,
                                          href=img_src,
                                          prev_ref=prev_img_ref,
                                          next_ref=next_img_ref,
                                          footer_enable=app.config['FOOTER_ENABLE'])
    
@app.route('/disable',methods=['POST'])
@requires_auth
def disable():
    file_path=request.form['file_path']
#    thumbnail_dao.disable_thumbnail(file_path)
    return redirect('/')


# Other functions

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

                thumbnail = thumbnail_dao.select_by_filepath(orig_path)
                
                if thumbnail is None or thumbnail.enable == 0:
                    continue
                
                thumb_path = thumbnail.thumbnail

                try:
                    title = _format_date(base, '%Y%m%d_%H%M%S', '%H:%M')
                except:
                    continue

                if not thumb_path == None:
                    src = '%s/%s' % (app.config['THUMB_ROOT_URL'], thumb_path)
                else:
                    src = '/img/nothumbnail.jpg'

                href = '/detail/' + d + '/' + f
                
                dav_img = { 'title': title, 'src': src, 'href': href, 'thumb_path':thumb_path }
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

    return math.ceil(float(pages) / num_by_page)

def _format_date(dt_str, src_format, dst_format):
    dt = datetime.datetime.strptime(dt_str, src_format)
    return dt.strftime(dst_format)
        
# Added by maasaamiichii
def _get_prev_next_img(img_path):
    webdav_dir  = app.config['WEBDAV_DIR']
    num_by_page = app.config['NUM_BY_PAGE']

    dirs = os.listdir(webdav_dir)
    dirs.sort() 
    dirs.reverse()
    
    next_find_flag=0
    prev_find_flag=0
    tmp_ref=''
    tmp_path=''
    prev_img=''
    next_img=''
    for d in dirs:

        if not os.path.isdir(os.path.join(webdav_dir, d)):
            continue
        
        if prev_find_flag==1:
            break

        for dt_root, dt_dirs, dt_files in os.walk(os.path.join(webdav_dir, d)):
        
            if prev_find_flag==1:
                break

            for f in dt_files:

                base, ext = os.path.splitext(f)
                if not re.match('^\.(jpe?g|png|gif|bmp)', ext, re.IGNORECASE):
                    continue
                    
                orig_path = os.path.join(d, f)
                thumbnail = thumbnail_dao.select_by_filepath(orig_path)
                if thumbnail is None or thumbnail.enable == 0:
                    continue
                
                if next_find_flag==1:
                    next_img = '/detail/' + d + '/' + f
                    prev_find_flag=1
                    break 
                
                if img_path==orig_path:
                    prev_img = tmp_ref
                    next_find_flag=1
              
                if next_find_flag==0:
                    tmp_ref = '/detail/' + d + '/' + f
                    tmp_path = orig_path
    
    prev_next_imgs={'prev_img':prev_img, 'next_img':next_img}

    return prev_next_imgs

if __name__ == '__main__':
    app.run()
