__author__ = 'rohit'
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Profile,ProfileMiniForm,CollegeDb

def _copyProfileToForm(prof):
        pf = ProfileMiniForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                if field.name=='collegeId':
                    collegeId=getattr(prof,field.name).get().collegeId
                    setattr(pf,field.name,collegeId)
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

def _getProfileFromUser():
        """Return user Profile from datastore"""
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required fuck you')

        user_id=Profile.query(Profile.email==user.email()).fetch(1)
        if len(user_id)>0:
            return user_id[0]
            #p_key = ndb.Key(Profile, user_id[0])
            #profile = p_key.get()

        else:
            return Profile(name = '',
                           email = '',
                           phone = '',
                           password = '',
                           pid = '',
                           isAlumni='N',
                           )
        #else:
         #   return user_id[0]


def _doProfile(save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        prof = _getProfileFromUser()
        pf = ProfileMiniForm()

        if save_request:
            for field in pf.all_fields():
                collegeLocation=getattr(save_request,'collegeLocation')
                print collegeLocation,"is location"
                if hasattr(save_request, field.name):
                    val = getattr(save_request, field.name)
                    if field.name is 'collegeLocation':
                        continue
                    if field.name is 'collegeName':
                        college=CollegeDb.query(CollegeDb.name==val,CollegeDb.location==collegeLocation).fetch()
                        setattr(prof,'collegeId',college[0].key)
                    else:
                        setattr(prof,field.name,val)
            prof.put()

        return _copyProfileToForm(prof)

