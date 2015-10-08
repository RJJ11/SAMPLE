__author__ = 'rohit'

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Club_Creation,CollegeDb,Profile,Club,ClubMiniForm

def createClub(requestentity=None):

        #When createClubRequest is called

        print("Request Entity for Create Club ", requestentity)
        clubRequest = Club_Creation()

        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()

        college = CollegeDb.query(CollegeDb.name == requestentity.college_name).fetch(1)
        print(college[0])
        college_key = college[0].key

        print("Retrieved College Key is ",college_key)

        if requestentity and college :
            for field in ('abbreviation','club_name','from_pid','to_pid','club_id','isAlumni','collegeId','club_creation_id'):
                if hasattr(requestentity, field):

                    val = getattr(requestentity, field)
                    if val:
                        print("entered second val")
                        setattr(clubRequest, field, str(val))
                elif field == "from_pid":
                     print("Entered from_pid")
                     profile =  Profile(
                            name = 'SiddharthSend',
                            email = 'sid.tiger184@gmail.com',
                            phone = '7760531993',
                            password = '1803mutd1',
                            pid = '1234',
                            isAlumni='N',
                            collegeId=college_key
                            )
                     profile_key = profile.put()
                     print("Finished frompid")
                     setattr(clubRequest, field, profile_key)
                elif field == "to_pid":
                     print("Entered To PID")
                     profile =  Profile(
                               name = 'SiddharthRec',
                               email = 'sid.tiger183@gmail.com',
                               phone = '7760531994',
                               password = '1803mutd',
                               pid = '5678',
                               isAlumni='N',
                               collegeId=college_key
                               )
                     profile_key = profile.put()

                     setattr(clubRequest, field, profile_key)
                elif field == "club_id":
                     setattr(clubRequest, field, "9999")
                elif field == "isAlumni":
                     setattr(clubRequest, field, "N")
                elif field == "collegeId":
                     setattr(clubRequest, field, college_key)
                elif field == "club_creation_id":
                     setattr(clubRequest, field, "1")
        clubRequest.put()
        return clubRequest


def createClubAfterApproval(requestentity=None):

        if requestentity:
            newClub = Club()
            newClub.abbreviation = requestentity.abbreviation
            newClub.clubId = requestentity.club_id
            newClub.admin = requestentity.from_pid
            newClub.collegeId = requestentity.collegeId
            newClub.name = requestentity.club_name
            newClub.isAlumni = requestentity.isAlumni

            newClub.put()

            #print("college Id of new ", newClub.collegeId.get())
            college = newClub.collegeId.get()
            #college = CollegeDb.query(CollegeDb.collegeId == newClub.collegeId.get().collegeId).fetch(1)
            print ("The retrieved college is ",college)

            if(college):
              college.group_list.append(newClub.key)
              print(college.group_list)

              college.put()

        return newClub

def getClub(requestentity=None):

        print("Request entity is",requestentity)

        if requestentity:
            clubQuery = Club.query(Club.name == requestentity.name).filter(Club.abbreviation == requestentity.abbreviation).fetch(1)
            print(clubQuery)

            if clubQuery:
             college = CollegeDb.query(CollegeDb.collegeId == requestentity.collegeId.get().collegeId).fetch(1)
             profile = Profile.query(Profile.pid == requestentity.admin.get().pid).fetch(1)
             retClub = ClubMiniForm()
             retClub.admin = profile[0].name
             retClub.abbreviation = requestentity.abbreviation
             retClub.name = requestentity.name
             retClub.collegeName = college[0].name



        return retClub