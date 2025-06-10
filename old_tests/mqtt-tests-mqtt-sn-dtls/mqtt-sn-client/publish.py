#! c:\python34\python3
#!/usr/bin/env python
##demo code provided by Steve Cope at www.steves-internet-guide.com
##email steve@steves-internet-guide.com
##Free to use for any purpose
##If you like and use this code you can
##buy me a drink here https://www.paypal.me/StepenCope
import signal
import queue
import struct
import threading
import time
import sys
sys.path.append('c:/python34/steve/mqttsclient/client')



from MQTTSNclient import Callback
from MQTTSNclient import Client
from MQTTSNclient import publish
import MQTTSN
message_q=queue.Queue() # Queue que é usada para armazenar mensagens recebidas



######
def empty_queue(delay=0):
    while not message_q.empty():
      m=message_q.get()
      print(m)
    if delay!=0:
      time.sleep(delay)
########


host="localhost"
port=1885
m_port=1885
m_group="localhost" 

client = Client("linh_pub")






client.registerCallback(Callback())

print ("threads ",threading.activeCount()) 
print("connecting ",host)
client.connected_flag=True # Print the threads as information


client.connect(host,port)
client.loop_start()
client.lookfor(MQTTSN.CONNACK)
connect =  client.waitfor(MQTTSN.CONNACK)
print("Connected ",connect) 
try:
  if connect==None:
      print("connection failed")
      raise SystemExit("no Connection quitting")
except:
  print("connection failed")
  raise SystemExit("no Connection quitting")


topic1="11"

msg="aaaaa"
time.sleep(1)
print("topic id=",topic1)
client.publish(topic1,msg)
client.publish(topic1,msg)

client.publish(topic1,msg)

client.publish(topic1,msg)


print("disconnecting")
client.disconnect()
print("disconnecting2")
time.sleep(10)
print("Before threads")
print ("threads ",threading.activeCount())
empty_queue(4)
client.loop_stop()



