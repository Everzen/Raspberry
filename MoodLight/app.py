# -*- coding: utf-8 -*-

from __future__ import with_statement
from socket import gethostname
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import time
import json


from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, jsonify

from pigredients.ics import ws2801 as ws2801

SECRET_KEY = 'nkjfsnkgbkfnge347r28fherg8fskgsd2r3fjkenwkg33f3s'
LOGGING_PATH = "moodLight.log"

led_chain = None

# create our little application
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True

# Stolen from http://stackoverflow.com/questions/4296249/how-do-i-convert-a-hex-triplet-to-an-rgb-tuple-and-back
HEX = '0123456789abcdef'
HEX2 = dict((a+b, HEX.index(a)*16 + HEX.index(b)) for a in HEX for b in HEX)

def rgb(triplet):
    triplet = triplet.lower()
    return { 'R' : HEX2[triplet[0:2]], 'G' : HEX2[triplet[2:4]], 'B' : HEX2[triplet[4:6]]}

def triplet(rgb):
    return format((rgb[0]<<16)|(rgb[1]<<8)|rgb[2], '06x')

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.before_request
def before_request():
    pass
        
@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/set/<hex_val>', methods=['GET', 'POST'])
def send_command(hex_val):
    return_object = {'output' : None , 'error' : None, 'success' : False}
    rgb_val = rgb(hex_val)
    print "Given colour_val : %s, converted it to %s" % (hex_val, rgb_val)
    led_chain.set_rgb(rgb_value=[rgb_val['R'],rgb_val['G'],rgb_val['B']], lumi=100)
    led_chain.write()
    return_object['success'] = True
    return jsonify(return_object)   
    
# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime


if __name__ == '__main__':
    # create console handler and set level to debug, with auto log rotate max size 10mb keeping 10 logs.
    file_handler = RotatingFileHandler( LOGGING_PATH , maxBytes=10240000, backupCount=10)

    # create formatter
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    # add formatter to our console handler
    file_handler.setFormatter(log_formatter)

    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    led_chain = ws2801.WS2801_Chain()

    app.run(host='0.0.0.0', port=8080)