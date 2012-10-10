#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,xmpp,time,datetime,select
import pipes
import signal,os,sys,threading,time
import twitter,urllib2;
import sensor, camera
  
reload(sys) 
sys.setdefaultencoding('utf-8') 

class Bot:
  
    def __init__(self,jabber, thisjid, remotejids, serverinfo):
        self.jabber = jabber
        self.thisjid = thisjid
        self.remotejids = remotejids
        self.serverinfo = serverinfo
  
    def register_handlers(self):
        pass
#        self.jabber.RegisterHandler('message',self.xmpp_message)
#  
#    def xmpp_message(self, con, event):
#        type = event.getType()
#        fromjid = event.getFrom().getStripped()
#        if type in ['message', 'chat', None] and fromjid in self.remotejids.values() and event.getBody():
#            sys.stdout.write(event.getBody() + '\n')
#            process_message(event.getBody(), fromjid, self.remotejids)
  
    def stdio_message(self, remotejid, message):
        m = xmpp.protocol.Message(to=remotejid,body=message,typ='chat')
        self.jabber.send(m)
        pass

    def send_weibo_message(self, message):
        self.stdio_message(self.remotejids['weibo_id'], message)
  
    def send_master_message(self, message):
        self.stdio_message(self.remotejids['master_id'], message)

    def xmpp_connect(self):
        #con=self.jabber.connect(server=self.serverinfo, secure=1)
        con=self.jabber.connect(server=self.serverinfo)
        if not con:
            sys.stderr.write('could not connect!\n')
            return False
        sys.stderr.write('connected with %s\n'%con)
        auth=self.jabber.auth(self.thisjid.getNode(),glparams['gtalk_password'],resource=self.thisjid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!\n')
            return False
        sys.stderr.write('authenticated using %s\n'%auth)
        self.register_handlers()
        return con






#my own codes

        
def send_yeelink_image(time, v, url):
    s= '@%s'%(v)
#s= '{ \n     "timestamp":"%s",  \n           "value":@%s  \n    }'%(time, v)
    sys.stdout.write('curl --request POST --data-binary \'%s\' --header "U-ApiKey: %s" %s\n'%(s, glparams['yeelink_key'], url))
    os.system('curl --request POST --data-binary \'%s\' --header "U-ApiKey: %s" %s'%(s, glparams['yeelink_key'], url))

def send_yeelink_message(time, v, url):
    s= '{ \n     "timestamp":"%s",  \n           "value":%s  \n    }'%(time, v)
    sys.stdout.write('curl --request POST --data-binary \'%s\' --header "U-ApiKey: %s" %s\n'%(s, glparams['yeelink_key'], url))
    os.system('curl --request POST --data-binary \'%s\' --header "U-ApiKey: %s" %s'%(s, glparams['yeelink_key'], url))
        
def send_weibo_message(message):
    global bot
    bot.send_weibo_message(message)

def send_twitter_message(message):
    try:
        status = tapi.PostUpdate(message);
        print "%s just posted: %s" % (status.user.name, status.text)
    except UnicodeDecodeError:
        print "Your message could not be encoded.  Perhaps it contains non-ASCII characters? "
        print "Try explicitly specifying the encoding with the --encoding flag"
        sys.exit(2)
    except urllib2.HTTPError,e:
        print "HTTPError: %s" % e

def sig_exit():
    global cl
    cl.disconnect()
    print "disconnected."
    sys.exit()

def handler(signum, frame):
    if signum == 2:
        sig_exit()
    if signum == 9:
        sig_exit()
        return None

signal.signal(signal.SIGINT,handler)
signal.signal(signal.SIGTERM,handler)


#global variables
glparams={}
cl=None
bot=None
  
if __name__ == '__main__':
  
    now = datetime.datetime.now()
  
    if os.access('config',os.R_OK):
        for ln in open('config').readlines():
            if not ln[0] in ('#',';'):
                key,val=ln.strip().split('=',1)
                glparams[key.lower()]=val

    for mandatory in ['gtalk_id','gtalk_password','tweetusername','tweetpassword']:
        if mandatory not in glparams.keys():
            #open('config','w').write('#Uncomment fields before use and type in correct credentials.\n#JID=romeo@montague.net/resource (/resource is optional)\n#PASSWORD=juliet\n')
            print 'Please point config file to valid JID for sending messages.'
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
    bot=Bot(cl,botjid, remote_jids,(gserver, gport))

  
    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\n")
        sys.exit(1)
    print "Connected to gtalk server"

    tapi = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                    access_token_key=access_key, access_token_secret=access_secret)
    #,                    input_encoding=encoding)
    #tapi.SetCredentials(tid, tpassword); 
  
    cl.sendInitPresence(requestRoster=0)   # you may need to uncomment this for old server
  
    socketlist = {cl.Connection._sock:'xmpp',sys.stdin:'stdio'}
  
    temper_str = ""
    temper_code, temper = sensor.read_temperature()
    if temper_code<0:
        if glparams['psend_gtalk'] == 'true':
            bot.send_master_message("read temperature error: %s"%temper)
        sys.stderr.write("read temperature error: %s\n"%temper);
#       sig_exit()
#            exit()
    else:
        temper_str="温度是%s摄氏度，"%temper
        
    bright_str = ""
    bright_code, brightness = sensor.read_brightness()
    if bright_code<0:
        if glparams['psend_gtalk'] == 'true':
            bot.send_master_message("read brightness error:%s"%brightness)
        sys.stderr.write("read brightness error:%s\n"%brightness);
#        sig_exit()
#        exit()
    else:
        bright_str="亮度是%s"%brightness

    nowtime = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime()) 
    msg = u'【定时监测】marvel家现在的%s%s 时间：%s'%(temper_str, bright_str, nowtime)

    sendmsg = -1
    if  now.hour%10==0 and now.minute>0 and now.minute<=12 and (temper_code>=0 or bright_code>=0):
        sendmsg = 1
    elif glparams['morning_call']=='true' and bright_code>=0 and brightness>int(glparams['morning_brightness']):
        nowdate = time.strftime("%Y-%m-%d", time.localtime()) 
        tmpfile = "./.dates/%s"%nowdate
        if os.path.exists(tmpfile):
            sys.stdout.write("called, ignore\n")
        else:
            msg = u'现在的温度是%s摄氏度，时间是%s，该起床了'%(temper, nowtime)
            os.system("/bin/touch %s"%tmpfile)
            sendmsg = 1
    print "msg:%s, send:%s"%(msg, sendmsg)


    nowtime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) 
    #every 10 hours at [0,12) execute
    if glparams['psend_gtalk'] == 'true':
        bot.send_master_message(msg)
    if glparams['psend_weibo'] == 'true' and sendmsg>0: 
        send_weibo_message(msg)
        print "weibo message sent"
    if glparams['psend_twitter'] == 'true' and sendmsg>0: 
        send_twitter_message(msg)
        print "twitter message sent"
    if glparams['psend_yeelink'] == 'true':
        if temper_code>=0:
            send_yeelink_message(nowtime, temper, glparams['yeelink_temp_url'])
        if bright_code>=0:
            send_yeelink_message(nowtime, brightness, glparams['yeelink_brig_url'])
        cm = camera.init_camera(glparams['tmp_image_file'])
        if camera.capture_camera(cm) > 0:
            send_yeelink_image(nowtime, glparams['tmp_image_file'], glparams['yeelink_camera_url'])
        del(cm)
        print "yeelink message sent"
    sig_exit()
        

