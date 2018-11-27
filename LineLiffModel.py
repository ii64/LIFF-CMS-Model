# -*- coding: utf-8 -*-
import sys
import requests
class View(object):
    def __init__(self, type=None, url=None):
        self.type,self.url=type,url
    def read(self, map_array):
        try: self.type = map_array.get('type',None); self.url  = map_array.get('url', None)
        except: self.type,self.url=type,url
    def write(self):
        return {'type':self.type,'url':self.url}
    def __repr__(self):
        L = ['%s=%r' % (key, value) for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
class LiffApp(object):
    def __init__(self, liffId=None, view=None):
        self.liffId,self.view = liffId,view 
    def read(self, map_array):
        try:
            view = View(); view.read(map_array.get('view',{}))
            self.liffId,self.view=map_array.get('liffId',None),view
        except: self.liffId,self.view = liffId,view 
    def write(self):
        return {'liffId':self.liffId, 'view': self.view.write()}
    def __repr__(self):
        L = ['%s=%r' % (key, value) for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
class ChannelLoginResult(object):
    def __init__(self, access_token=None,expires_in=None,token_type=None):
        self.access_token,self.expires_in,self.token_type=access_token,expires_in,token_type
    def read(self, map_array):
        try:
            self.access_token = map_array.get('access_token', None)
            self.expires_in   = map_array.get('expires_in', None)
            self.token_type   = map_array.get('token_type', None)
        except: self.access_token,self.expires_in,self.token_type=access_token,expires_in,token_type
    def write(self):
        return {'access_token':self.access_token,'expires_in':self.expires_in,'token_type':self.token_type}
    def __repr__(self):
        L = ['%s=%r' % (key, value) for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
class LiffException(Exception):
    if (2, 6, 0) <= sys.version_info < (3, 0):
        def _get_message(self):
            return self._message
        def _set_message(self, message):
            self._message = message
        message = property(_get_message, _set_message)
    def __init__(self, code, headers, message=None):
        Exception.__init__(self, code, headers, message)
class LINELiff(object):
    channelId = None
    channelSecret = None
    liffId = []
    _logged_in = False
    headers = {}
    def __init__(self, log=True, debug=True):
        self.en_log,self.en_debug = log, debug
    def _error(self, *args, **kws):
        f = '->'
        x = ['[Error]']
        for arg in args:
            x += [arg]
            if args.index(arg) < len(args) - 1:
                x += [f]
        if self.en_debug == True:
            print(*x)
    def _log(self, *args, **kws):
        f = '->'
        x = ['[Log]']
        for arg in args:
            x += [arg]
            if args.index(arg) < len(args) - 1:
                x += [f]
        if self.en_log == True:
            print(*x)
    def issueChannelAccessToken(self, channelId, channelSecret=None):
        api = 'https://api.line.me/v2/oauth/accessToken'
        ret = requests.post(api, 
            data={
                'grant_type':'client_credentials', 
                'client_id'    : channelId,
                'client_secret': channelSecret
        })
        if ret.status_code != 200:
            self._error('login respose code != 200', ret.status_code)
            try: raise LiffException(ret.status_code, ret.headers, ret.json())
            except: raise LiffException(ret.status_code, ret.headers, ret.content)
        try:
            jsn = ret.json()
            access_token = jsn.get('access_token', '')
            if access_token == '':
                self._error('No access_token returned', ret.content)
            else:
                self.headers.update({
                    'Authorization': f'Bearer {access_token}'
                    })
                self.channelId, self.channelSecret = channelId, channelSecret
                self._logged_in = True
                rx = ChannelLoginResult()
                rx.read(jsn)
                self._log('AccessToken', access_token)
                self._log('Expires', jsn.get('expires_in', 'null'))
        except Exception as e:
            self._error(e)
        return rx
    login = issueChannelAccessToken
    def updateLiffApp(self, LiffAppReq):
        #liffId, type, view_url
        liffId = LiffAppReq.liffId
        assert liffId != None, 'LiffId is null'
        api = f'https://api.line.me/liff/v1/apps/{liffId}/view'
        assert self._logged_in, 'You must be logged in.'
        assert LiffAppReq.view.type in ('compact', 'tall', 'full'), f'Invalid type "{type}". Only compact, tall, or full'
        ret = requests.put(api, 
            headers=self.headers,
            json=LiffAppReq.view.write())
        if ret.status_code != 200:
            self._error('updateLiffApp respose code != 200', ret.status_code)
            try: raise LiffException(ret.status_code, ret.headers, ret.json())
            except: raise LiffException(ret.status_code, ret.headers, ret.content)
        return True
    def getLiffApp(self):
        api = 'https://api.line.me/liff/v1/apps'
        assert self._logged_in, 'You must be logged in.'
        ret = requests.get(api, 
            headers=self.headers)
        if ret.status_code != 200:
            self._error('getLiffApp respose code != 200', ret.status_code)
            try: raise LiffException(ret.status_code, ret.headers, ret.json())
            except: raise LiffException(ret.status_code, ret.headers, ret.content)
        rx = []
        try:
            jsn = ret.json()
            apps = jsn.get('apps', [])
            if apps == []:
                pass
            else:
                for app in apps:
                    fx = LiffApp()
                    fx.read(app)
                    rx += [fx]
        except Exception as e:
            self._error(e)
        return rx
    def deleteLiffApp(self, liffId):
        api = f'https://api.line.me/liff/v1/apps/{liffId}'
        assert self._logged_in, 'You must be logged in.'
        ret = requests.delete(api, 
            headers=self.headers)
        if ret.status_code != 200:
            self._error('deleteLiffApp respose code != 200', ret.status_code)
            try: raise LiffException(ret.status_code, ret.headers, ret.json())
            except: raise LiffException(ret.status_code, ret.headers, ret.content)
        return True
    def createLiffApp(self, type, view_url):
        api = 'https://api.line.me/liff/v1/apps'
        assert self._logged_in, 'You must be logged in.'
        assert type in ('compact', 'tall', 'full'), f'Invalid type "{type}". Only compact, tall, or full'
        ret = requests.post(api,
            headers=self.headers,
            json={
                'view': {
                    'type': type,
                    'url' : view_url,
                }
        })
        if ret.status_code != 200:
            self._error('createLiffApp respose code != 200', ret.status_code)
            try: raise LiffException(ret.status_code, ret.headers, ret.json())
            except: raise LiffException(ret.status_code, ret.headers, ret.content)
        try:
            jsn = ret.json()
            liffId = jsn.get("liffId", '')
            if liffId == '':
                self._error('No liffId returned', ret.content)
            else:
                self._log('LiffId', liffId)
                self.liffId.append(liffId)
                fx = LiffApp()
                fx.read(jsn)
        except Exception as e:
            self._error(e)
        return fx

if __name__ == '__main__':
    boom = LINELiff()
    # Rin - Connect! LINE OAuth Platform
    ssc = boom.login('your_channel_id','your_channel_secret')
    print(ssc)
    allx = boom.createLiffApp('full', 'https://echobots.net/')
    allx = boom.getLiffApp()
    print(allx)