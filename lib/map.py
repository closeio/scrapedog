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
            elif (response['results'][0].has_key('partial_match')
            and response['results'][0]['partial_match'] == True):
                formatted = response['results'][0]['formatted_address']
                _address = set(address.replace('\n', ' ').replace('\t', ' ').replace(',', '').split(' '))
                _address2 = set(formatted.replace('\n', ' ').replace('\t', ' ').replace(',', '').split(' '))
                
                if float(len(_address & _address2)) / max(len(_address), len(_address2)) > 0.5:
                    result = formatted
                else:
                    result = False
            else:
                result = response['results'][0]['formatted_address']
                
            GoogleMap.CACHE[url] = result
            
        return result
        
        
# example:
gm = GoogleMap()
print gm.check_address('11231001 S Main St\nMilpitas, CA')
