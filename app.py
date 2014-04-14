import jsonParser
import uuid
import time
import sys
import datetime
import pymongo
import os
import threading
import boto
import logging


from flask import Flask, Response, request,  jsonify, render_template, send_from_directory


from customer import Customer
from asset import Asset
from pymongo import Connection
from bson.objectid import ObjectId
from urlparse import urlparse
from boto.s3.key import Key
from logging.handlers import RotatingFileHandler


app = Flask(__name__)
app.debug = True
handler = RotatingFileHandler('loggingSander.log', maxBytes=1 * 1024 *1024, backupCount=10)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s: %(message)s [in %(filename)s:%(lineno)d]")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

def getapp():
    return app
#adding mongo
from customer import Customer

MONGODB_URI = 'mongodb://heroku_app23820427:2vvldvjb4gdgr8t183pictgg1l@ds043047.mongolab.com:43047/heroku_app23820427'


if MONGODB_URI:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[urlparse(MONGODB_URI).path[1:]]
else:
    client = pymongo.MongoClient('localhost', 27017)
    db=client[aws-database]

collection_assets = db['assets']
collection_customers = db['customers']


@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp



def startTranscodingjob(input_filename, output_filename):
    conn_transcode=boto.connect_elastictranscoder()
    #conn_transcode.create_pipeline("pipelinewymediatest","wymedia.transcoding.in","wymedia.transcoding.out","arn:aws:iam::745665279123:role/Elastic_Transcoder_Default_Role",{'Progressing': '', 'Completed': '', 'Warning': '', 'Error': ''})
    
    transcode_input = {'Container':
        'auto',
        'Key': input_filename,
        'Resolution': 'auto',
        'AspectRatio': 'auto',
        'FrameRate': 'auto',
        'Interlaced': 'auto'
    }

    transcode_output = {'Rotate': 'auto',
        'PresetId': '1351620000001-100080',
        'Key': output_filename
    }

    
    job = conn_transcode.create_job("1395751910303-92ulfo", transcode_input, transcode_output)
    

    if job:
        return 0
    else:
        return -1

#---------START OF REST FUNCTIONS-----------

@app.route("/")
def index():
    data = {"Status":"Index retrieved"}
    responseStatusCode = 200
    mime = 'application/json'
    return Response(data, status=responseStatusCode, mimetype=mime)

@app.route('/notification', methods=['POST'])
def notify():
    if request.method == 'POST':
        app.logger.error('POST /notification method called')
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            notification_obj = Notification.fromJson(request.data)
            app.logger.error('notification_obj guid: ' + str(notification_obj.guid))
            #collection_notifications.insert(notification_obj.toDict())
            #data = {'notification':notification_obj}
            #app.logger.error('Data sent as part of the POST /notifications: ' + str(data))
            response = []
            data = {'notifications':  response}
            (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
            responseStatusCode = 200


        except TypeError as e:
            data = {"error":"Notification could not be created because the data in the body of the request was bad." + str(e)}
            responseStatusCode = 400
        except Exception as e:
            data = {"error":"Something went wrong. Please try again later."+ str(e)}
            app.logger.error('Error in POST /customers: '+str(e)) 
            responseStatusCode = 500
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)


@app.route('/customers', methods=['GET','POST'])
def customers():
    if request.method == 'GET':
        app.logger.error('GET /customers method called')
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            customers = collection_customers.find()
            response = []
            for customer_dict in customers:
                app.logger.error("sander" + str(customer_dict))
                customer_obj = Customer.fromDict(customer_dict)
                response.append(customer_obj)
            data = response
            app.logger.error('Data sent as part of the GET /customers: ' + str(data))
            responseStatusCode = 200
        except Exception as e:
            data={"error":"Something went wrong. Please try again later. "+str(e)}  
            app.logger.error('Error in GET /customers: '+repr(e)) 
            responseStatusCode = 500
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)
    
    if request.method == 'POST':
        app.logger.error('POST /customers method called')
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:     
            customer_obj = Customer.fromJson(request.data)
            collection_customers.insert(customer_obj.toDict())
            data = customer_obj
            #app.logger.error('Data sent as part of the POST /customers: ' + str(data))
            (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
            responseStatusCode = 200

        except TypeError as e:
            data = {"error":"Customer could not be created because the data in the body of the request was bad." + str(e)}
            responseStatusCode = 400
        except Exception as e:
            data = {"error":"Something went wrong. Please try again later."+ str(e)}
            app.logger.error('Error in POST /customers: '+str(e)) 
            responseStatusCode = 500
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)

@app.route('/customers/<customer_id>', methods=['GET','PUT','DELETE'])
def customers_with_id(customer_id):
    if request.method == 'GET':
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            customer = collection_customers.find_one({"guid":customer_id})
            customer_obj = Customer.fromDict(customer)
            data = customer_obj
            responseStatusCode = 200
        except KeyError as e:
            data = {"error":"Invalid id for the recording."}
            responseStatusCode = 400
        except Exception as e:
            data = data={"error":"Something went wrong. Please try again later. "+str(e)}
            responseStatusCode = 500    
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)
    
    if request.method == 'PUT':
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            customer = collection_customers.find_one({"guid":customer_id})
            customer_obj = Customer.fromJson(request.data)
            #store the recording in the recording collection
            collection_customers.update({'guid':customer_id},{"$set": customer_obj.toDict()},upsert=True) #upsert creates the object if not existing
            data = customer_obj
            responseStatusCode = 200
        except TypeError as e:
            data = {"error":"Customer could not be created because the data in the body of the request was bad." + str(e)}
            responseStatusCode = 400
        except Exception as e:
            data = {"error":"Something went wrong. Please try again later. "+ str(e)}
            responseStatusCode = 500
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime) 

    if request.method == 'DELETE':
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            collection_customers.update({'guid':customer_id},{"$set": {"status": "deleted"}})
            data = {"success":"Customer with guid: "+customer_id+" deleted successfully."}
            responseStatusCode = 200
        except KeyError as e:
            data = {"error":"Invalid id for the customer. "+str(e)}
            responseStatusCode = 400
        except Exception as e:
            data = data={"error":"Something went wrong. Please try again later. "+str(e)}
            responseStatusCode = 401
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)


@app.route('/customers/<customer_id>/assets', methods=['GET','POST'])
def customer_with_assets(customer_id):
    if request.method == 'GET':
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            assets = collection_assets.find({"customer_guid":customer_id})
            response = []
            for asset_dict in assets:
                asset_obj = Asset.fromDict(asset_dict)
                response.append(asset_obj)
            data = {'assets':response}
            responseStatusCode = 200
            
        except Exception as e:
            data = data={"error":"Something went wrong. Please try again later. "+str(e)}
            responseStatusCode = 500    
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)
    
    if request.method == 'POST':
        data={"error":"Something went wrong. Please try again later."}
        responseStatusCode = 500
        try:
            asset_obj = Asset.fromJson(request.data)
            collection_assets.insert(asset_obj.toDict())
            data = {'asset':asset_obj}
            (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
            responseStatusCode = 200
            job = startTranscodingjob("2014-03-06 20.45.17.mp4",customer_id + "/" + asset_obj.guid)
            if job == 0:
                app.logger.error('Changing status for asset from init to transcoded with guid ' + asset_obj.guid)
                collection_assets.update({'guid': asset_obj.guid},{"$set": {"status": "transcoded"}})
                app.logger.error('Transcoding job finished successfully')
                Notifications()
            else:
                app.logger.error('Sth went wrong with the transcoding')


        except TypeError as e:
            data = {"error":"Customer could not be created because the data in the body of the request was bad." + str(e)}
            responseStatusCode = 400
        except Exception as e:
            data = {"error":"Something went wrong. Please try again later."+ str(e)}
            app.logger.error('Error in POST /customers: '+str(e)) 
            responseStatusCode = 500
        (data,mime) = (jsonParser.DateTimeJSONEncoder().encode(data),'application/json')
        return Response(data, status=responseStatusCode, mimetype=mime)        

@app.route('/<anything>', methods=['GET'])
def catchall(anything):
    data = {"Error":"Not found"}
    responseStatusCode = 404
    mime = 'application/json'
    return Response(data, status=responseStatusCode, mimetype=mime)

def Notifications():
    sns = boto.connect_sns()
    #topics = sns.get_all_topics()
    #app.logger.error('Topics: '+str(topics)) 
    #mytopics = topics["ListTopicsResponse"]["ListTopicsResult"]["Topics"]
    #app.logger.error('Mytopics: '+str(mytopics)) 
    #mytopic_arn = mytopics[0]["TopicArn"]
    #app.logger.error('TopicArn: '+str(mytopic_arn)) 
    #subscriptions = sns.get_all_subscriptions_by_topic(mytopic_arn)
    #app.logger.error('Subscriptions: '+str(subscriptions)) 
    #msg = "Hi there\nI am sending this message over boto.\nYour booty Jan"
    #subj = "SNS message over boto"
    #res = sns.publish(mytopic_arn, msg, subj)
    #app.logger.error('res: '+str(res)) 
    #sns.subscribe(mytopic_arn, "email", "wauterw@gmail.com")
    #res = sns.publish(mytopic_arn, msg, "Second msg over boto")
    #app.logger.error('res: '+str(res)) 
    msg="Dit is een test bericht SNS"
    subj="testing SNS"
    res= sns.publish("arn:aws:sns:us-east-1:745665279123:Topic_Transcoder_Completed", msg, subj)
    app.logger.error('res: '+str(res)) 

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=environ["PORT"])
