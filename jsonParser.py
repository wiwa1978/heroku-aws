import json
import datetime

#######################################
## Encoding options
#######################################
class DateTimeJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')       
        if isinstance(obj, object):
            return obj.toDict()          
        return super(DateTimeJSONEncoder, self).default(obj)


#######################################
## Decoding options
#######################################
class DateTimeJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.datetime_decoder, *args, **kargs)

    def datetime_decoder(self, d):
        for (k, v) in d.items():
            try:
                if isinstance(v, unicode):
                    d[k] = datetime.datetime.strptime(
                        v, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                continue
        return d