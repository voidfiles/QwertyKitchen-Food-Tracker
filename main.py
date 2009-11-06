#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import db
import logging
class Tweet(db.Expando):
    tweetid =  db.IntegerProperty()
    username = db.StringProperty()
    tweet = db.StringProperty()
    tags = db.StringListProperty()
    created = db.DateTimeProperty()
    image = db.StringProperty()

import wsgiref.handlers


from google.appengine.ext import webapp

class TaskHandler(webapp.RequestHandler):

    def get(self, task):

        from google.appengine.api import memcache
        import pprint
        
        url = "http://search.twitter.com/search.json?q=%23having"
        

        self.get_json(url)
        
        self.response.out.write('Hello world!')
        
    def get_json(self, url =None):
        from django.utils import simplejson as json
        from google.appengine.api.urlfetch import fetch
        import datetime, time
        import re
        result = fetch(url, deadline=10)
        if int(result.status_code) != 200: 
            logging.info('early exit, failed http, %s %s' % (result.status_code, request.content))
            return False
            
        obj = json.loads(result.content)
        for result in obj["results"]:
            # Try and store unless, we have seen that 
            query = Tweet.all()
            if query.filter("tweetid =", result["id"]).count() >= 1:
                logging.info('early exit, found some old tweets')
                return False
            the_time = time.strptime(result["created_at"], '%a, %d %b %Y %H:%M:%S +0000')
            the_time = datetime.datetime(*the_time[0:6])
            the_tweet = result["text"].replace("\n","")
            new_tweet = Tweet(
                tweetid=result["id"],
                username=result["from_user"],
                tweet = the_tweet,
                created = the_time,
                image = result["profile_image_url"],
            )
            if result["geo"]:
                new_tweet.geo = result["geo"]
                
            new_tweet.put()
        url = "http://search.twitter.com/search.json"+ obj["next_page"]
        
        self.get_json(url)

"""
{
    "profile_image_url":"http://a3.twimg.com/profile_images/382761821/twitterProfilePhoto_normal.jpg",
    "created_at":"Thu,
     05 Nov 2009 08:25:59 +0000",
    "from_user":"iGrace",
    "to_user_id":null,
    "text":"#having aalu ki sabji,
     dal n roti",
    "id":5445046479,
    "from_user_id":5446,
    "geo":null,
    "iso_language_code":"is",
    "source":"&lt;a href=&quot;http://twitter.com/&quot;&gt;web&lt;/a&gt;"
},
"""
class MainHandler(webapp.RequestHandler):

    def get(self):
        self.response.out.write('Hello world!')

def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        (r'/tasks/([^/]*)', TaskHandler),],
        debug=False
    )
    wsgiref.handlers.CGIHandler().run(application)
        



if __name__ == '__main__':
    main()
