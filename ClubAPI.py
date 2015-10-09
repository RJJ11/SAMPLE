__author__ = 'Siddharth'

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Club_Creation,CollegeDb,Profile,Club,ClubMiniForm

def createClub(request=None):

        #When createClubRequest is called

        print("Request Entity for Create Club ", request)
        clubRequest = Club_Creation()


        collegeId = ndb.Key('CollegeDb',int(request.college_id))
        college = CollegeDb.query(CollegeDb.key == collegeId).fetch(1)

        college_key = college[0].key



        if request and college :

            for field in ('abbreviation','club_name','from_pid','to_pid','isAlumni','collegeId','description'):


                if field == "abbreviation":
                    clubRequest.abbreviation = request.abbreviation
                elif field == "club_name":
                    clubRequest.club_name = request.club_name
                elif field == "description":
                    clubRequest.description = request.description

                elif field == "from_pid":
                     print("Entered from_pid")
                     profile =  Profile(
                            name = 'SiddharthSend',
                            email = 'sid.tiger184@gmail.com',
                            phone = '7760531993',
                            password = '1803mutd1',
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

                               isAlumni='N',
                               collegeId=college_key
                               )
                     profile_key = profile.put()

                     setattr(clubRequest, field, profile_key)
                elif field == "isAlumni":
                     setattr(clubRequest, field, "N")
                elif field == "collegeId":
                     setattr(clubRequest, field, college_key)
            clubRequest.put()

        return clubRequest


def createClubAfterApproval(requestentity=None):

        if requestentity:
            newClub = Club()
            newClub.abbreviation = requestentity.abbreviation
            newClub.admin = requestentity.from_pid
            newClub.collegeId = requestentity.collegeId
            newClub.name = requestentity.club_name
            newClub.isAlumni = requestentity.isAlumni
            newClub.description = requestentity.description
            newClub.members.append(requestentity.from_pid)
            clubkey = newClub.put()

            profile = requestentity.from_pid.get()

            print("To check if profile retrieval is correct ", profile)
            profile.clubsJoined.append(clubkey)

            print("Checking if the  guy has joined the club",profile.clubsJoined)

            profile.follows.append(clubkey)
            print("Check if the profile has folowed the club",profile.follows)

            profile.put()

            college = newClub.collegeId.get()


            if(college):
              college.group_list.append(newClub.key)


              college.put()

        print("finished appending college list")

        return newClub


def getClub(request=None):

        retClub = ClubMiniForm()
        clubKey = ndb.Key('Club',int(request.club_id))
        club = clubKey.get()

        print("The retrieved club is",club)

        collegeidret = club.collegeId
        adminret = club.admin
        print("Admin ret",adminret)

        if club:
             college = CollegeDb.query(CollegeDb.collegeId == collegeidret.get().collegeId).fetch(1)

             print("Club id is",club.key.id())
             retClub.club_id = str(club.key.id())
             retClub.admin = adminret.get().name
             retClub.abbreviation = club.abbreviation
             retClub.name = club.name
             retClub.collegeName = college[0].name
             retClub.description = club.description
        return retClub

