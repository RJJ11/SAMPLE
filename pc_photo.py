# Copyright 2015 Google Inc. All rights reserved.
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

# [START all]
import webapp2
import endpoints

from google.appengine.api.images import get_serving_url
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from settings import ANROID_CLIENT_ID,WEB_CLIENT_ID,ANDROID_ID2,ANDROID_ID3
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

ALLOWED_APP_IDS = (ANROID_CLIENT_ID,WEB_CLIENT_ID,API_EXPLORER_CLIENT_ID,ANDROID_ID2,ANDROID_ID3)

class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        # [START upload_url]
        upload_url = blobstore.create_upload_url('/upload_photo')
        print upload_url
        # [END upload_url]
        # [START upload_form]
        # The method must be "POST" and enctype must be set to "multipart/form-data".
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
          name="submit" value="Submit"> </form></body></html>''')
        #self.response.write(upload_url)
        #print 'a'
        # [END upload_form]


app = webapp2.WSGIApplication([('/pc_upload_photo', PhotoUploadFormHandler),
                              ], debug=True)
# [END all]