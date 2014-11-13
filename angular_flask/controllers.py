import os

from flask import Flask, request, Response
from flask import render_template, url_for, redirect, send_from_directory
from flask import send_file, make_response, abort
import mpylayer
from os import listdir,getcwd
from os.path import isfile,join, islink
import json
import subprocess, time
import pdb
import threading

from angular_flask import app

# routing for API endpoints (generated from the models designated as API_MODELS)
from angular_flask.core import api_manager
from angular_flask.models import *

threads = []
class File(object):

	def __init__(self):
		self.name =""
		self.path = ""
		self.isdir = False
		self.parent_file = 0
		self.children_files = []
		self.children_dirs = []

	def __str__(self):
		json_str  = '{'
		json_str += '"name":"%s", '%(self.name)
		json_str += '"path":"%s", '%(self.path)
		json_str += '"isdir":%s, '%(str(self.isdir).lower())
		json_str += '"parent_file":"%s", '%(self.parent_file)
		json_str += '"children_dirs":%s,'%(self.children_dirs)
		json_str += '"children_files":%s'%(self.children_files)
		json_str += '}'
		return json_str



for model_name in app.config['API_MODELS']:
	model_class = app.config['API_MODELS'][model_name]
	api_manager.create_api(model_class, methods=['GET', 'POST'])

session = api_manager.session
mp = mpylayer.MPlayerControl()

# routing for basic pages (pass routing onto the Angular app)
@app.route('/')
@app.route('/about')
@app.route('/blog')
def basic_pages(**kwargs):
	return make_response(open('angular_flask/templates/index.html').read())

# routing for CRUD-style endpoints
# passes routing onto the angular frontend if the requested resource exists
from sqlalchemy.sql import exists

crud_url_models = app.config['CRUD_URL_MODELS']

def perform_command(p, cmd, expect):
	import select
	if not p:
		return
	p.stdin.write(cmd + '\n') # there's no need for a \n at the beginning
	while select.select([p.stdout], [], [], 0.05)[0]: # give mplayer time to answer...
		output = p.stdout.readline()
		if output.rstrip():
			print("output: {}".format(output.rstrip()))
		split_output = output.split(expect + '=', 1)
		if len(split_output) == 2 and split_output[0] == '': # we have found it
			value = split_output[1]
			return value.rstrip()

p = None 

def playfile(path):
	global p
	cmd = ['mplayer', '-slave', '-quiet', path.replace('+','/')]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

@app.route('/player/play/<path>')
def play(path):
	print "path to play "+path
	#mp.loadfile(path.replace('+','/'))
	t = threading.Thread(target=playfile , args=(path,))
	threads.append(t)
	t.start()
	return "played"


@app.route('/player/pause')
def pause():
	if p:
		print 'about to pasye'
		#p.stdin.write('pause' + '\n') # there's no need for a \n at the beginning
		perform_command(p,'pause','PAUSE')
		
	return "suce"


@app.route('/player/stop')
def stop():
	if p:
		perform_command(p,'quit','QUIT')
		p.terminate()
	return "suce"


@app.route('/player/fullscreen')
def fullscreen():
	if p:
		perform_command(p,'vo_fullscreen','VO_FULLSCREEN')
	return "suce"


@app.route('/player/volume/up')
def volume_up():
	if mp.volume < 100:
		mp.volume = mp.volume+10
	return "suce"


@app.route('/player/volume/down')
def volume_down():
	if mp.volume >0:
		mp.volume = mp.volume-10
	return "suce"


@app.route('/files/root')
def parent_files():
	rootpath = "/home/vamshi/nfs"
	return filelist(rootpath)

@app.route('/files/<path>')
def folderfiles(path):
	#rootpath = "/home/vamshi/nfs"
	return filelist(path.replace('+','/'))


def filelist(path):
	files = listdir(path)
	file_list = []
	for file in files:
		fileobj={}
		fileobj['name'] = file
		fileobj['dir'] = not isfile(path+"/"+file)
		file_list.append(fileobj)
	return json.dumps(file_list)

@app.route('/<model_name>/')
@app.route('/<model_name>/<item_id>')
def rest_pages(model_name, item_id=None):
	if model_name in crud_url_models:
		model_class = crud_url_models[model_name]
		if item_id is None or session.query(exists().where(
			model_class.id == item_id)).scalar():
			return make_response(open(
				'angular_flask/templates/index.html').read())
	abort(404)

# special file handlers and error handlers
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
							   'img/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404



