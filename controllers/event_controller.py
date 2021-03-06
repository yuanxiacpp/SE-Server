from flask import Blueprint
from flask import request
from flask import render_template
from bson import json_util


from main import app,db,security
from models.models import EventModel,EventMatchModel,ProfileModel
import operator

event_api = Blueprint('event_api', __name__)

# API for viewing all new events
@event_api.route("/events", methods=['GET'])
def api_event_demo():
    doc = EventModel.objects(status='new').order_by('-createTime')
    print doc
    for d in doc:
        num = EventMatchModel.objects(eventId=str(d.id)).count()
        setattr(d, 'numOfRequests', num)
        photo = ProfileModel.objects.get(userID=d.userID).image
        setattr(d, 'image', photo)
    # docs =  json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    # app.logger.info(docs)
    return render_template('event_list.html',events=doc,paras={"title":"All Open Events",'action':'all'})


# API for viewing events in map view
@event_api.route("/map_view", methods=['GET'])
def api_event_map():
    doc = EventModel.objects(status='new')
    return render_template('map_view.html',events=doc,paras={"title":"All Open Events",'action':'all'})


# view all my events, need to pass user id
@event_api.route("/event/mine/<_uid>", methods=['GET'])
def api_event_mine(_uid = None):
    doc = EventModel.objects(userID=_uid)

    eventDict = dict((key, value) for (key, value) in [(d.id,d.status) for d in doc])
    
    for d in doc:
        num = EventMatchModel.objects(eventId=str(d.id)).count()
        setattr(d, 'numOfRequests', num)
        photo = ProfileModel.objects.get(userID=d.userID).image
        setattr(d, 'image', photo)
    return render_template('event_list.html',events=doc, eventDict=eventDict, paras={"title":"My Events",'action':'mine'})
    #return  json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    # app.logger.info(docs)
    #return render_template('events.html',events=doc)


# API for creating events
@event_api.route("/event/create", methods=['GET'])
def api_event_create():
    from flask.ext.security import current_user
    print current_user.id
    cnt = ProfileModel.objects(userID=str(current_user.id)).count()
    print cnt
    
    #return render_template('landing.html')
    if cnt == 0:
        return render_template('profile.html', action = 'create')
    else:
        return render_template('event.html', ev=None ,paras={"action":"create"})



# API to view my personal events
@event_api.route("/event/myrequest/<_uid>", methods=['GET'])
def api_event_myrequest(_uid = None):
    match = EventMatchModel.objects().filter(reqUserId = _uid)
    eids = [d.eventId for d in match]

    matchDict = dict((key, value) for (key, value) in [(d.eventId,d.status) for d in match])
    print matchDict
    print eids
    event = EventModel.objects(id__in=eids)
    for d in event:
        num = EventMatchModel.objects(eventId=str(d.id)).count()
        setattr(d, 'numOfRequests', num)
        photo = ProfileModel.objects.get(userID=d.userID).image
        setattr(d, 'image', photo)
    #return json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    return render_template('event_list.html',events=event,matchDict=matchDict,paras={"title":"My Requests",'action':'myrequest'})


# view event details. This API will also return requester's profile info
@event_api.route("/event/view/<_eid>", methods=['GET'])
def api_event_view(_eid = None):
    doc = EventModel.objects.get(id=_eid)

    doc2 = EventMatchModel.objects(eventId=_eid)

    # get profile info for all requesters
    for d in doc2:
        doc3 = ProfileModel.objects.get(userID=d.reqUserId)
        setattr(d, "reqProfile", doc3)

    setattr(doc, "Requests", doc2)

    #for d in doc.Requests:
    #    print d.reqProfile.name

    return render_template('event.html', ev=doc,paras={"action":"view"})

# API for event detail editing
@event_api.route("/event/edit/<_eid>", methods=['GET'])
def api_event_edit(_eid = None):
    doc = EventModel.objects.get(id=_eid)
    return render_template('event.html', ev=doc,paras={"action":"edit"})


# API to filter out events with certain distance
@event_api.route("/events/near", methods=['POST'])
def api_event_near():
    """ http://mongoengine-odm.readthedocs.org/guide/querying.html#geo-queries """
    print request
    if request.method == "POST":
        dist = float(request.json['dist'])
        _lat = float(request.json['lat'])
        _lng = float(request.json['lng'])

        doc = EventModel.objects(status = 'new')

        # for d in doc:
        #     print request
        #     lat = d.LatLng.get('coordinates')[0];
        #     lng = d.LatLng.get('coordinates')[1];
        #     if isWithin(_lat, _lng, lat, lng, dist) is not 1:
        #     else:
        #         pass

        
        nums = {}
        photos = {}
        return_doc = [d.to_mongo() for d in doc if isWithin(d.LatLng.get('coordinates')[0], d.LatLng.get('coordinates')[1],_lat,_lng,dist) == 1]
        
        for d in doc:
            if isWithin(d.LatLng.get('coordinates')[0], d.LatLng.get('coordinates')[1],_lat,_lng,dist) == 1:
                num = EventMatchModel.objects(eventId=str(d.id)).count()
                # setattr(d, 'numOfRequests', num)
                nums[str(d.id)] = num
                
                #print d.numOfRequests
                photo = ProfileModel.objects.get(userID=d.userID)
                photos[str(d.id)] = photo.image
                #setattr(d, 'image', photo.image)

        print json_util.dumps(return_doc)
        return json_util.dumps({'doc':return_doc, "nums":nums, "photos":photos},default=json_util.default)
        
        #print len(doc)
        #print json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
        #return json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
        #return render_template('event_list.html', ev=doc, paras={"action": "radius_refresh"})
import math
from math import radians, sqrt, sin, cos, atan2

def isWithin(lat1, lon1, lon2, lat2, radius):
    print lat1
    print lon1
    print lat2
    print lon2
    print radius
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    dlon = lon1 - lon2

    EARTH_R = 6372.8

    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)
    print EARTH_R * c
    if EARTH_R * c < radius:
        return 1
    else:
        return 0




# API for creating events
@event_api.route("/api/event/create", methods=['POST'])
def api_event_post():
    
    _method = request.json['_method']

    if _method == 'POST':
        print "entering here POST"

        title = request.json['title']
        description = request.json['description']
        location = request.json['location']
        #eventDate = request.json['eventDate']
        startTime = request.json['startTime']
        endTime = request.json['endTime']
        userID = request.json['userID']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        ZIP = request.json['ZIP']

        #might be swapped
        latitude, longitude = longitude, latitude

        #model = EventModel(title=title,description=description,location=location,startTime=startTime,endTime=endTime,userID=userID,latitude=latitude,longitude=longitude,ZIP=ZIP)
        model = EventModel(title=title,description=description,location=location,startTime=startTime,endTime=endTime,userID=userID,LatLng={"type":"Point","coordinates":[latitude,longitude]},ZIP=ZIP)
        doc = model.save()
        print json_util.dumps(doc.to_mongo())
        app.logger.info(doc)
        return json_util.dumps(doc.to_mongo())
    elif _method == 'PUT':
        
        eventId = request.json['eventId']
        doc = EventModel.objects.get(id=eventId)
        print "entering here PUT"
        title = request.json['title']
        description = request.json['description']
        location = request.json['location']
        #eventDate = request.json['eventDate']
        startTime = request.json['startTime']
        endTime = request.json['endTime']
        userID = request.json['userID']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        ZIP = request.json['ZIP']

        if not title is None or title == '':
           doc.title = title
        if not description is None or description == '':
           doc.description = description
        if not location is None or location == '':
           doc.location = location
        if not startTime is None or startTime == '':
           doc.startTime = startTime
        if not endTime is None or endTime == '':
           doc.endTime = endTime
        if not userID is None or userID == '':
           doc.userID = userID
        if not latitude is None or latitude == '':
           doc.latitude = latitude
        if not longitude is None or longitude == '':
           doc.longitude = longitude 
        if not ZIP is None or ZIP == '':
           doc.ZIP = ZIP 


        doc.save()
        return json_util.dumps(doc.to_mongo())





@event_api.route("/api/event", methods=['GET'])
@event_api.route("/api/event/<_id>", methods=['GET','POST'])
def api_event_getputdelete(_id = None):
    """ <_id> is for update/delete/get operation"""
    if(request.method == 'GET'):
        if _id == None:
            doc = EventModel.objects.all()
            app.logger.info(doc)
            return json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
        else:
            doc = EventModel.objects.get(id=_id)
            return json_util.dumps(doc.to_mongo())
    if(request.method == 'POST'):
        if(request.json['_method'] == 'DELETE'):
            print _id;  
            doc = EventModel.objects.get(id=_id)
            doc.delete()
            print json_util.dumps(doc.to_mongo())
            return json_util.dumps(doc.to_mongo())
        elif(request.json['_method'] == 'PUT'):
            print _id;  
            doc = EventModel.objects.get(id=_id)
            #doc.k1 = request.json['k1']
            doc.save()
            print json_util.dumps(doc.to_mongo())
            return json_util.dumps(doc.to_mongo())