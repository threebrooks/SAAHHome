#!/usr/bin/python

import re
import urllib.request
import traceback

class wemo:
    OFF_STATE = '0'
    ON_STATES = ['1', '8']
    ip = None
    ports = [49153, 49152, 49154, 49151, 49155]

    def __init__(self, switch_ip):
        self.ip = switch_ip      
   
    def toggle(self):
        status = self.status()
        if status in self.ON_STATES:
            result = self.off()
            result = 'WeMo is now off.'
        elif status == self.OFF_STATE:
            result = self.on()
            result = 'WeMo is now on.'
        else:
            raise Exception("UnexpectedStatusResponse")
        return result    

    def on(self):
        return self._send('Set', 'BinaryState', 1)

    def off(self):
        return self._send('Set', 'BinaryState', 0)

    def status(self):
        return self._send('Get', 'BinaryState')

    def name(self):
        return self._send('Get', 'FriendlyName')

    def signal(self):
        return self._send('Get', 'SignalStrength')
  
    def _get_header_xml(self, method, obj):
        method = method + obj
        return '"urn:Belkin:service:basicevent:1#%s"' % method
   
    def _get_body_xml(self, method, obj, value=0):
        method = method + obj
        return '<u:%s xmlns:u="urn:Belkin:service:basicevent:1"><%s>%s</%s></u:%s>' % (method, obj, value, obj, method)
    
    def _send(self, method, obj, value=None):
        body_xml = self._get_body_xml(method, obj, value)
        header_xml = self._get_header_xml(method, obj)
        for port in self.ports:
            result = self._try_send(self.ip, port, body_xml, header_xml, obj) 
            if result is not None:
                self.ports = [port]
            return result
        raise Exception("TimeoutOnAllPorts")

    def _try_send(self, ip, port, body, header, data):
        try:
            request = urllib.request.Request('http://%s:%s/upnp/control/basicevent1' % (ip, port))
            request.add_header('Content-type', 'text/xml; charset="utf-8"')
            request.add_header('SOAPACTION', header)
            request_body = '<?xml version="1.0" encoding="utf-8"?>'
            request_body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            request_body += '<s:Body>%s</s:Body></s:Envelope>' % body
            request.data = request_body.encode()
            result = urllib.request.urlopen(request, timeout=3)
            return self._extract(result.read().decode('utf-8'), data)
        except Exception as e:
            print(str(e))
            traceback.print_stack()
            return None

    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
        return response

