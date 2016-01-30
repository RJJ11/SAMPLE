import re,unicodedata
import endpoints
from datetime import datetime,date,time
import datetime as dt
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models_v1 import Post_Request,CollegeDb,Post,Profile,Club, CommentsResponseForm
from Models_v1 import PostForm,LikePost,CommentsForm,Comments,GetPostRequestsForm,BDComments
#from Hashtags import processTags
#commentBody = "The gults will win #AP #TS"

stateList = ['#GJ','#RJ','#BR','#UP','#MP','#UB','#KA','#KR','#AP','#TS','#MH','#NE','#TN','#WB']


def processTags(comment):
    commentBody = comment.commentBody.strip()
    commentBody = comment.commentBody.upper()
    #BDComment = BDComments()
    for x in stateList:
        if x in commentBody:
            print "Matched for " , x

            query = BDComments.query(BDComments.pid == comment.pid,BDComments.commentHashTag==x)

            if query:
                count = 0
                for q in query:
                    #print q
                    count +=1
                print count

                if count ==0: #Indicates nothing present
                    print "Entered here with ", x
                    BDComment = BDComments()
                    BDComment.pid = comment.pid
                    BDComment.commentBody = [comment.commentBody]
                    BDComment.commentHashTag = x
                    BDComment.name = comment.pid.get().name
                    k1 = BDComment.put()
                    print "INSERTED"
                    print k1

                else:
                    for q in query:
                        q.commentBody.append(comment.commentBody)
                        q.put()

            else:
                print "False"

    return
