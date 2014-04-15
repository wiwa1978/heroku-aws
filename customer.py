import datetime
import uuid
import jsonParser
import app

#######################################
## Customer class
#######################################
class Customer(object):
    def __init__(self, name, email, guid=None, status='active'):
         #generate new uuid if not provided
        if (guid==None):
            guid = str(uuid.uuid4())
        if isinstance(guid, basestring):
            self.guid=guid
        else:
            raise TypeError('could not create customer','id is not of type str')
        if isinstance(name, basestring):           
            self.name = name
        else:
            raise TypeError('could not create customer','name is not of type str')
        if isinstance(email, basestring):
            self.email=email
        else:
            raise TypeError('could not create customer','email is not of type str')   
        if isinstance(status, basestring):
            self.status=status
        else:
            raise TypeError('could not create customer','status is not of type str')

    def __repr__(self):
        return str(self.toDict())

    def __dict__(self):
        return toDict()

    def toDict(self):
        return {'guid':self.guid, 'name':self.name, 'email':self.email, 'status':self.status}

    @classmethod
    def fromDict(cls,customer_dict):
        return cls(customer_dict['name'],customer_dict['email'], customer_dict['guid'], customer_dict['status'])


    @classmethod
    def fromJson(cls, jsonstring):
        customer_dict = jsonParser.DateTimeJSONDecoder().decode(jsonstring)
        return cls(customer_dict['name'],customer_dict['email'])

    def toJson(self):
        return jsonParser.DateTimeJSONEncoder().encode(self.toDict())

    def serializeToJsonResponse(self):
        return (self.toJson(),'application/json')
