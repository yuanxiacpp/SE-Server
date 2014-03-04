from flask import Blueprint
from flask import request
from flask import render_template
from bson import json_util


from main import app,db,security
from models.models import EventModel

event_api = Blueprint('event_api', __name__)

@event_api.route("/events", methods=['GET'])
def api_event_demo():
    doc = EventModel.objects.all()
    # docs =  json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    # app.logger.info(docs)
    return render_template('events.html',events=doc)

@event_api.route("/event/mine/<_uid>", methods=['GET'])
def api_event_mine(_uid = None):
    doc = EventModel.objects(userID=_uid)
    return  json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    # app.logger.info(docs)
    #return render_template('events.html',events=doc)

@event_api.route("/event/create", methods=['GET'])
def api_event_create():
    return render_template('create_events.html', events=[])

######################## APIs BELOW ########################

@event_api.route("/api/event/near/<_eid>/<_dist>", methods=['GET'])
def api_event_near(_eid = None, _dist = 10):
    """ http://mongoengine-odm.readthedocs.org/guide/querying.html#geo-queries """
    if _eid is not None:
        ev = EventModel.objects.get(id=_eid)
        LatLng = ev['LatLng']['coordinates']
        dist = int(_dist)
        doc = EventModel.objects(LatLng__geo_within_center=[[LatLng[0], LatLng[1]],dist])
        return json_util.dumps([d.to_mongo() for d in doc],default=json_util.default)
    else:
        return '[]'

@event_api.route("/api/event/create", methods=['POST'])
def api_event_post():
    print request
    if request.method == 'POST':
        title = request.json['title']
        description = request.json['description']
        location = request.json['location']
        startTime = request.json['startTime']
        endTime = request.json['endTime']
        startTime = request.json['startTime']
        userID = request.json['userID']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        ZIP = request.json['ZIP']

        #model = EventModel(title=title,description=description,location=location,startTime=startTime,endTime=endTime,userID=userID,latitude=latitude,longitude=longitude,ZIP=ZIP)
        model = EventModel(title=title,description=description,location=location,startTime=startTime,endTime=endTime,userID=userID,LatLng={"type":"Point","coordinates":[latitude,longitude]},ZIP=ZIP)
        doc = model.save()
        print json_util.dumps(doc.to_mongo())
        app.logger.info(doc)
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