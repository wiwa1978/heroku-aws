import datetime
import uuid
import jsonParser

#######################################
## Asset class
#######################################
class Asset(object):
    def __init__(self, customer_guid, title="", guid=None, status="Initialized"):
         #generate new uuid if not provided, 
        if (guid==None):
            guid = str(uuid.uuid4())
        if isinstance(guid, basestring):
            self.guid=guid
        else:
            raise TypeError('Could not create asset','id is not of type str')
        if isinstance(title, basestring):
            self.title=title
        else:
            raise TypeError('Could not create asset','title is not of type str')
        if isinstance(status, basestring):
            self.status=status
        else:
            raise TypeError('could not create asset','id is not of type str')
        if isinstance(customer_guid, basestring):
            self.customer_guid=customer_guid
        else:
            raise TypeError('could not create asset','customer_guid is not of type str')
        if isinstance(title, basestring):
            self.title=title
        else:
            raise TypeError('could not create asset','title is not of type str')
        if isinstance(status, basestring):
            self.status=status
        else:
            raise TypeError('could not create asset','title is not of type str')
     
    
    def __repr__(self):
        return str(self.toDict())

    def __dict__(self):
        return toDict()

    def toDict(self):
        return {'guid':self.guid,'title':self.title, 'status':self.status}

    @classmethod
    def fromDict(cls,asset_dict):
        return cls(asset_dict['customer_guid'],asset_dict['title'], asset_dict['guid'],asset_dict['status'],)

    @classmethod
    def fromJson(cls, jsonstring):
        asset_dict = jsonParser.DateTimeJSONDecoder().decode(jsonstring)
        return cls(asset_dict['asset']['customer_guid'],asset_dict['asset']['title'])

    def toJson(self):
        return jsonParser.DateTimeJSONEncoder().encode(self.toDict())

    def serializeToJsonResponse(self):
        return (self.toJson(),'application/json')



