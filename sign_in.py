# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 20:12:44 2017

@author: Sarai
"""

from flask import Flask, request
import flask
import tweepy
import tokens
#import twitter_followers as tf

app = Flask(__name__)
app.config.from_pyfile('config.cfg', silent=True)

#consumer_key = app.config["CONSUMER_ID"]
#consumer_secret = app.config["CONSUMER_SECRET"]
#access_token_key = app.config["ACCESS_KEY"]
#access_token_secret = app.config["ACCESS_SECRET"]

callback_url = 'oob'
session = dict()
db = dict()



@app.route('/')
def send_token():
    redirect_url = ""
    auth = tweepy.OAuthHandler(tokens.consumer_key, tokens.consumer_secret, callback_url)

    try: 
        #get the request tokens
        redirect_url= auth.get_authorization_url()
        session['request_token']= (auth.request_token['oauth_token'],
            auth.request_token['oauth_token_secret'])
    except tweepy.TweepError:
        print('Error! Failed to get request token')

    #this is twitter's url for authentication
    return flask.redirect(redirect_url)


@app.route("/verify")
def get_verification():

    #get the verifier key from the request url
    verifier= request.args['oauth_verifier']

    auth = tweepy.OAuthHandler(tokens.consumer_key, tokens.consumer_secret)
    token = session['request_token']
    del session['request_token']

    auth.set_request_token(token[0], token[1])

    try:
            auth.get_access_token(verifier)
    except tweepy.TweepError:
            print('Error! Failed to get access token.')

    #now you have access!
    api = tweepy.API(auth)

    #store in a db
    db['api']=api
    db['access_token_key']=auth.access_token.key
    db['access_token_secret']=auth.access_token.secret
    return flask.redirect(flask.url_for('start'))


@app.route("/start")
def start():
    #auth done, app logic can begin
    api = db['api']
    userdata = api.me()
#    tf.main(userdata, api)

    #example, print your latest status posts
    return flask.render_template('followers.html', 
                                 name = userdata.name, 
                                 screen_name = userdata.screen_name, 
                                 bg_color = userdata.profile_background_color, 
                                 followers_count = userdata.followers_count, 
                                 created_at = userdata.created_at)


if __name__ == '__main__':
    app.run()