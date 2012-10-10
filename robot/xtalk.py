#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,xmpp,time,select,datetime
import pipes
import signal,os,sys,threading,time
import twitter,urllib2;
import errno, traceback
import sensor, camera
import socket

reload(sys) 
sys.setdefaultencoding('utf-8') 
  

class Bot:
  
    def __init__(self, jabber, thisjid, remotejids, serverinfo):
        self.jabber = jabber
        self.thisjid = thisjid
        self.remotejids = remotejids
        self.serverinfo = serverinfo
#       self.cm= cm
  
    def register_handlers(self):
        self.jabber.RegisterHandler('message',self.xmpp_message)
        self.jabber.RegisterDisconnectHandler(self.disconnectHandler)
  
    def xmpp_message(self, con, event):
        type = event.getType()
        fromjid = event.getFrom().getStripped()
        if type in ['message', 'chat', None] and fromjid in self.remotejids.values() and event.getBody():
            sys.stdout.write(event.getBody() + '\n')
            process_message(event.getBody(), fromjid, self.remotejids)
  
    def stdio_message(self, remotejid, message):
        m = xmpp.protocol.Message(to=remotejid,body=message,typ='chat')
        self.jabber.send(m)
        pass

    def send_weibo_message(self, message):
        self.stdio_message(self.remotejids['weibo_id'], message)
  
    def send_master_message(self, message):
        self.stdio_message(self.remotejids['master_id'], message)

    def disconnectHandler(self):
        sys.stderr.write('INFO: Disconnect!\n')
        self.jabber.reconnectAndReauth()
        sys.stdout.write('INFO: Reconnected!\n')

#cl=xmpp.Client(botjid.getDomain(),debug=[])
#self.jabber = cl
#        sys.stderr.write('INFO: Reconnect!\n')
#       if not self.xmpp_connect():
#            sys.stderr.write("Could not connect to server, or password mismatch!\n")
        self.process_loop()
        #self.xmpp_connect()

    def xmpp_disconnect(self):
        self.jabber.disconnect()
        sys.stdout.write("disconnected.\n")

    def xmpp_connect(self):
        #con=self.jabber.connect(server=self.serverinfo, secure=1)
        sys.stdout.write("connecting server\n")
        con=self.jabber.connect(server=self.serverinfo)
        if not con:
            sys.stderr.write('could not connect!\n')
            return False
        sys.stdout.write('connected with %s\n'%con)
        auth=self.jabber.auth(self.thisjid.getNode(),glparams['gtalk_password'],resource=self.thisjid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!\n')
            return False
        sys.stdout.write('authenticated using %s\n'%auth)
        self.register_handlers()
        return con


    def process_loop(self):

        cl.sendInitPresence(requestRoster=0)   # you may need to uncomment this for old server
        status="at your service"
        pres=xmpp.Presence(priority=5, show='chat',status=status)
        cl.send(pres)
      
        #socketlist = {cl.Connection._sock:'xmpp',sys.stdin:'stdio'}
        socketlist = {cl.Connection._sock:'xmpp'}
        online = 1
      
        while online:
            try:
                (i , o, e) = select.select(socketlist.keys(),[],[],30)
                found = -1  
                for each in i:
                    if socketlist[each] == 'xmpp':
                        cl.Process(1)
                        found = 1 
                    elif socketlist[each] == 'stdio':
                        msg = sys.stdin.readline().rstrip('\r\n')
                        self.send_master_message(msg)
                        found = 1 
                    else:
                        raise Exception("Unknown socket type: %s" % repr(socketlist[each]))
                if found <0:
                    #time out
                    cl.sendPresence()
                    print "%s\tsend present.. %s, %s"%(datetime.datetime.now(), botjid, status)
            except select.error, e:
                if e[0] == errno.EINTR:
                    continue
            except socket.error, e:
                print "22222"
                if not cl.isConnected():
                # if e[0] == errno.EBADF:
                    self.xmpp_connect()
                    socketlist = {cl.Connection._sock:'xmpp'}
                    continue
            except e:
                print "33333"
                traceback.print_exc()
                self.xmpp_connect()
                socketlist = {cl.Connection._sock:'xmpp'}
                continue
    #                cl.reconnectAndReauth()
    #print datetime.datetime.now()







#my own codes
def send_weibo_message(message):
    global bot
    bot.send_weibo_message(message)

def send_twitter_message(message):
    try:
        status = tapi.PostUpdate(message);
        sys.stderr.write("%s just posted: %s\n" % (status.user.name, status.text))
    except UnicodeDecodeError:
        sys.stderr.write("Your message could not be encoded.  Perhaps it contains non-ASCII characters?")
        sys.stderr.write("Try explicitly specifying the encoding with the --encoding flag\n")
        sys.exit(2)
    except urllib2.HTTPError,e:
        sys.stderr.write("HTTPError: %s\n" % e)


#main function of the robot
def process_message(message, fromid, remotejids):
    global bot,glparams
    resp=""
    talkonly = -1
    if fromid == remotejids['master_id']:
        if message.find("hello")>=0 or message.find("hi")>=0:
            resp = u'marvel，欢迎您'
            talkonly = 1
        elif message.find(u"温度")>=0 or message.find(u"多热")>=0 or message.find(u"多冷")>=0  :
            code, temp = sensor.read_temperature()
            if code < 0:
                resp = temp
                talkonly = 1
            else:
                resp = u'marvel，您家里当前温度是%s摄氏度'%temp
        elif message.find(u"亮度")>=0 or message.find(u"多亮")>=0:
            code, brightness = sensor.read_brightness()
            
            if code < 0:
                resp = brightness 
                talkonly = 1
            else:
                desc = sensor.get_brightness_description(brightness)
                resp = u'marvel，您家里当前亮度是%s，%s'%(brightness, desc)
        elif message.find(u"图片")>=0:
            cm = camera.init_camera(glparams['tmp_image_file'])
            if camera.capture_camera(bot.cm) > 0:
                resp = u'已经照完'
            else:
                resp = u'照相失败'
            camera.release_camera(bot.cm)
            talkonly = 1
        else:
            talkonly = 1
            resp = u'marvel，我看不懂您的话，blush'
    
        if message.find(u"谢谢")>=0:
            resp = resp+u'，不客气//%s'%message
        else:
            resp = resp+"//%s"%message
    
        if message.find("talkonly")>=0:
            talkonly = 1
    
        sys.stdout.write("I said:%s\n"%resp)
        if glparams['rep_gtalk']=='true':
            bot.send_master_message(resp)
            sys.stdout.write("gtalk message sent\n")
        if talkonly < 0 and ( glparams['rep_twitter']=='true' or message.find(u'推一下')>=0):
            send_twitter_message(resp)
            sys.stdout.write("twitter message sent\n")
        if talkonly < 0 and glparams['rep_weibo']=='true':
            bot.send_weibo_message(resp)
            sys.stdout.write("weibo message sent\n")
        #os.write(sys.stdin.fileno(), resp)
    elif fromid == remotejids['weibo_id']:
        if message.find(u'[评论]')>=0:
            print "new comment received"
        elif message.find(u'[私信]')>=0:
            print "new mail received"
        return


def sig_exit():
    global bot 
    bot.xmpp_disconnect()
    sys.exit()

def handler(signum, frame):
    print "received signal %s"%signum
    if signum == signal.SIGINT or signum == signal.SIGUSR1:
        sys.stdout.flush()
        sys.stderr.flush()
    elif signum == signal.SIGTERM or signum == signal.SIGQUIT:
        sys.stdout.flush()
        sys.stderr.flush()
        sig_exit()
        return None

signal.signal(signal.SIGINT,handler)
signal.signal(signal.SIGTERM,handler)
signal.signal(signal.SIGUSR1,handler)
signal.signal(signal.SIGQUIT,handler)


#global variables
glparams={}
bot=None
  
if __name__ == '__main__':
  
    sys.stdout.write("--------------------------------------------------------\nstarting robot at %s\n---------------------------------------------------------------\n" %datetime.datetime.now())
  
    if os.access('config',os.R_OK):
        for ln in open('config').readlines():
            if not ln[0] in ('#',';'):
                key,val=ln.strip().split('=',1)
                glparams[key.lower()]=val

    for mandatory in ['gtalk_id','gtalk_password','tweetusername','tweetpassword']:
        if mandatory not in glparams.keys():
            #open('config','w').write('#Uncomment fields before use and type in correct credentials.\n#JID=romeo@montague.net/resource (/resource is optional)\n#PASSWORD=juliet\n')
            sys.stderr.write('Please point config file to valid JID for sending messages.\n')
            sys.exit(0)
  

    remote_jids = {}
    tojid=glparams['gtalk_peer']
    gserver=glparams['gtalk_server']
    gport=int(glparams['gtalk_port'])
    consumer_key=glparams['tweetusername']
    consumer_secret=glparams['tweetpassword']
    access_key=glparams['tweetaccesskey']
    access_secret=glparams['tweetaccesssecret']

    remote_jids['master_id']=tojid
    if(glparams['rep_weibo']=='true'):
        weibo_gtalkid=glparams['weibo_gtalkid']
        remote_jids['weibo_id']=weibo_gtalkid

    botjid=xmpp.protocol.JID(glparams['gtalk_id'])
    cl=xmpp.Client(botjid.getDomain(),debug=[])
#cl=xmpp.Client(botjid.getDomain(),debug=['always', 'nodebuilder'])
    bot=Bot(cl,botjid, remote_jids,(gserver, gport))

  
    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)
    sys.stdout.write("Connected to gtalk server\n")

    tapi = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                    access_token_key=access_key, access_token_secret=access_secret)
    #,                    input_encoding=encoding)
    #tapi.SetCredentials(tid, tpassword); 

    bot.process_loop()
  


