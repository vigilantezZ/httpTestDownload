from umqtt import MQTTClient
import utime
import log
import checkNet
import dataCall
import atcmd
#######################################################################################################################
mqtt_log = log.getLogger("MQTT")
def init_():
    # Set log output level
    log.basicConfig(level=log.INFO)
    mqtt_log.info("Program started v1.1")
    # The APN information that the user needs to configure. Modify it according to the actual situation
    # (dictionary) consists key-value pairs
    #pdpConfig = {'apn': 'www.xlgprs.net', 'username': '', 'password': ''}
    # pdpConfig = {'apn': 'M2MPLNAMR', 'username': '', 'password': ''}
    # pdpConfig = {'apn': 'M2MINTERNET#', 'username': '', 'password': ''}
    pdpConfig = {'apn': 'internet', 'username': '', 'password': ''}
    #dataCall.setPDPContext(profileID, ipType, apn, username, password, authType)
    dataCall.setPDPContext(1, 0, pdpConfig['apn'], pdpConfig['username'], pdpConfig['password'], 0)
    mqtt_log.info("PDP context has been set")
    # Obtains the information of the first APN, confirming whether the currently used APN is the one specified by the user
    pdpCtx = dataCall.getPDPContext(1)
    mqtt_log.info("APN: {}" .format(pdpCtx[1]))
#######################################################################################################################
def cfun_0_1():
    resp=bytearray(50)
    atcmd.sendSync('at+cfun=0\r\n',resp,'',20)
    mqtt_log.info("CFUN set to 0")
    utime.sleep(1)
    atcmd.sendSync('at+cfun=1\r\n',resp,'',20)
    mqtt_log.info("CFUN set to 1")  
    utime.sleep(1)
#######################################################################################################################
mainFlag = 1
recvMsg = ''
def mqtt_cb(topic, msg):
    global mainFlag
    global recvMsg
    mqtt_log.info("Subscribe Recv: Topic={},Msg={}".format(topic.decode(), msg.decode()))
    recvMsg = msg.decode()
    if recvMsg == 'exit()':
        mqtt_log.info("exit() is received")
        mainFlag = 0
#######################################################################################################################
def main():
    mqtt_log.info("Entered Main function")
    #Returns a tuple with (stage, state)
    stage, state = checkNet.waitNetworkReady(15)
    #Success condition stage = 3 and state = 1 indicates successful activation.
    if stage == 3 and state == 1:
        mqtt_log.info("Network connection successful")
    else:
        mqtt_log.info("Network connection failed, stage{}, state{}" .format(stage, state))
        cfun_0_1()
        main()
    #MQTTClient(client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={},reconn=True,version=4)
    myMqtt = MQTTClient("TESTTTT", "139.255.253.74", port=3001, user="edmi-nbiot", password="EDMINBIOT2025#", keepalive=0, ssl=False, ssl_params={},reconn=True,version=4)
    #Sets the callback function of receiving messages.
    myMqtt.set_callback(mqtt_cb)
    #Connects to MQTT server.
    ret = myMqtt.connect()
    if ret != 0:
        mqtt_log.info("MQTT Connection is failed: {}" .format(ret))
        cfun_0_1()
        main()
    mqtt_log.info("Connected to the MQTT server")
    #Subscribes to MQTT topics.
    #MQTTClient.subscribe(topic,qos)
    myMqtt.subscribe("topic/test/55", 2)
    mqtt_log.info("Subscribed to the topic")
    myMqtt.publish("topic/test/66", "Hello from QuecPython")
    mqtt_log.info("Hello message is sent")
    while mainFlag == 1:
        #Block function for monitoring message
        myMqtt.wait_msg()
        #Return Value (year, month, mday, hour, minute, second, weekday, yearday)
        lTime = utime.localtime()
        #Publish a message 
        #MQTTClient.publish(topic,msg, retain=False, qos=0)
        myMqtt.publish("topic/test/66", "[{}:{}:{}]{}".format(lTime[3], lTime[4], lTime[5], recvMsg))
        mqtt_log.info("Received Message ({}) is sent".format(recvMsg))
        utime.sleep(1)
    myMqtt.close()
    mqtt_log.info("Closed the MQTT connection")
    mqtt_log.info("Finished...")
#######################################################################################################################
if __name__ == '__main__':
    init_()
    main()