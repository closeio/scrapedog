import json
import requests
import urllib2

class GoogleMap:
    CACHE = {}
    
    def check_address(self, address):
        url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % urllib2.quote(address)
        
        if GoogleMap.CACHE.has_key(url):
            result = GoogleMap.CACHE[url]
        else:
            response = requests.get(url)
            response = json.loads(response.text)
            if response['status'] == 'ZERO_RESULTS':
                result = False
            elif response['partial_match'] == True:
                result = False
            else:
                result = response['results'][0]['formatted_address']
                
            GoogleMap.CACHE[url] = result
            
        return result
        
        
# example:
# gm = GoogleMap()
# print gm.check_address('1001 S Main St\nMilpitas, CA')