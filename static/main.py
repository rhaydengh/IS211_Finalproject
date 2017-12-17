#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assignment 12"""

from flask import Flask, render_template, request, redirect, session, url_for, g, abort, flash, escape
from contextlib import closing
import sqlite3 as sql
import sys

DATABASE = 'blogsdb.db'
DEBUG = True
SECRET_KEY = "key"
USERNAME = "admin"
PASSWORD = "password"



app = Flask(__name__)
app.config.from_object(__name__)

conn = sql.connect("blogsdb.db", timeout=5)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS blogs;")
cursor.execute("CREATE TABLE IF NOT EXISTS blogs(blognum INTEGER PRIMARY KEY AUTOINCREMENT,"
               "title text not null,author text not null, date text not null, content text not null);")
cursor.execute("INSERT INTO blogs(title,author,date,content) VALUES('Blog Site', 'snowflake1', 'Feb 1, 2017', 'this is a really cool site!');")

conn.commit()

def connect_db():
    return sql.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    if 'username' in session:
        return render_template('blogsdb.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        session = request.form['username']
        return redirect('/blogpage')
    else:
        flash('Invalid login')
        print 'Invalid login'
        return render_template('index.html')

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    return render_template('index.html')


@app.route('/blogpage', methods = ['GET'])
def blogpage():
    curs = g.db.execute('select blognum, title, date, author, content from blogs ORDER BY blognum DESC')
    blogs = [dict(blognum = row[0], title = row[1], date = row[2], author = row[3], content = row[4])
                    for row in curs.fetchall()]
    return render_template("blogsite.html", blogs=blogs)


@app.route('/blog/add', methods = ['POST', 'GET'])
def addblog():
    title = request.form['title']
    date = request.form['date']
    author = request.form['author']
    content = request.form['content']
    g.db.execute('insert into blogs (title, date, author, content) values (?, ?, ?, ?)',
                     [request.form['title'], request.form['date'], request.form['author'], request.form['content']])
    g.db.commit()
    return redirect(url_for('blogpage'))

@app.route('/edit/post', methods=['GET', 'POST'])
def editpost():
    if request.method == 'POST':
        g.db.execute('update blogs SET title=?, author=?, date=?, content=? WHERE blognum=?',
                     [request.form['title'], request.form['author'],request.form['date'],request.form['content'],request.form['blognum']])
        g.db.commit()
        return redirect(url_for('blogpage'))
    return render_template('editpost.html')

@app.route('/delete/post', methods=['GET', 'POST'])
def deletepost():
    if request.method == 'POST':
        g.db.execute('DELETE FROM blogs WHERE blognum=?',
                     [request.form['blognum']])
        g.db.commit()
        return redirect(url_for('blogpage'))
    return render_template('deletepost.html')


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()