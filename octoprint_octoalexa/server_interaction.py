import random
import string
import uuid
import boto3
import json
import requests
from threading import Timer

class Authenticate():
    """This class authenticates the device to the lambda server"""
    def __init__(self, oprint):
        self._oprint = oprint
        self.mfakey = ''
        self.deviceID = ''
        self.lambda_arn = 'arn:aws:lambda:us-east-1:543913421320:function:alexa_auth'
        self.client = boto3.client('lambda')

    def register_pi(self):
     
       
        pl = json.dumps({
            "Action" : "REGISTER_DEVICE",
            
            })
        r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = pl ,
            Qualifier = '$LATEST'
            )
        
       
        raw_text = r['Payload'].read()
        js = json.loads(raw_text)
        credentials = json.loads(js)
    
        self.mfa_key = credentials['mfa_key']
        self.devid = credentials['devid']

        self._oprint._logger.info("Set new device id: " + self.devid + " and new mfa key: " + self.mfa_key + "#######################################")
        self._oprint._settings.set(['deviceid'], self.devid)
        self._oprint._settings.set(['mfakey'], self.mfa_key)

        #start the polling process
        self.timer = Timer(1,self.poll_to_complete_registration)
        self.timer.start()

    def poll_to_complete_registration(self):
        update = json.dumps({
            "MFAKey" : self.mfa_key ,
        })

        pl = json.dumps({
                "Action" : "POLL_REGISTRATION",
                "Device" : update,
                })

        r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = pl ,
            Qualifier = '$LATEST'
            )
        response = r['Payload'].read()
        response = response.replace("\"", "")
        self._oprint._logger.info(response)
        
        while response == "No Device":
            r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = pl ,
            Qualifier = '$LATEST'
            )
            response = r['Payload'].read()
            response = response.replace("\"", "")
            self._oprint._logger.info("Response: " + response)

        #save session_id
        self.session_id = response
        update = json.dumps({
            "MFAKey" : self.mfa_key ,
            "session_id" : self.session_id
        })

        pl = json.dumps({
                "Action" : "COMPLETE_REGISTRATION",
                "Device" : update,
                })

        #self._oprint._logger.info(pl)


        r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = pl ,
            Qualifier = '$LATEST'
            )

        response = r['Payload'].read()
        response = response.replace("\"", "")

        while  response != "Success":
            r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = pl ,
            Qualifier = '$LATEST'
            )
            response = r['Payload'].read()
            response = response.replace("\"", "")
            self._oprint._logger.info("Response: " + response)

        self._oprint._logger.info("successfully registered device with Alexa!")
        
        self._oprint._settings.set(['session_id'], self.session_id)
            
   
class Update_Status():
    """This pushes updates to the server that the alexa app can pick up on"""
    def __init__(self, oprint):
        self._oprint = oprint
        self.lambda_arn = 'arn:aws:lambda:us-east-1:543913421320:function:alexa_auth'
        self.client = boto3.client('lambda')

    def update(self, state):
        #check if the alexa services are enables
        self.service_enabled = self._oprint._settings.get(['service_enabled'])

        if self.service_enabled == True:
            if self._oprint._settings.get(['session_id']) != None:
                update = json.dumps({
                    "session_id" : self._oprint._settings.get(['session_id']),
                    "device_id" : self._oprint._settings.get(['deviceid']),
                    "Status" : state,
                })
    
                pl = json.dumps({
                        "Action" : "POST_UPDATE",
                        "Update" : update,
                })
                r = self.client.invoke(
                    FunctionName = self.lambda_arn,
                    InvocationType = 'RequestResponse',
                    Payload = pl ,
                    Qualifier = '$LATEST'
                )
        
                self._oprint._logger.info("State is now: " + state)
            else:
                self._oprint._logger.info("Session ID has not been set. Please Register the device correctly! (Did you click save after registering?)")
        else:
            self._oprint._logger.info("Alexa Services are not service_enabled: " + str(self.service_enabled))

    def poller(self):
        if self._oprint._settings.get(['service_enabled']) != True:
            return False
        else:
            device = json.dumps({
                "session_id" : self._oprint._settings.get(['session_id']),
                "device_id" : self._oprint._settings.get(['deviceid']),
            })

            poll = json.dumps({
                "Action" : "POLL_STATUS",
                "Device" : device    
            })   

            r = self.client.invoke(
                FunctionName = self.lambda_arn,
                InvocationType = 'RequestResponse',
                Payload = poll ,
                Qualifier = '$LATEST'
            )
            l = r['Payload'].read()
            js = json.loads(l)
            return js

    def complete_action(self):

        device = json.dumps({
                "session_id" : self._oprint._settings.get(['session_id']),
                "device_id" : self._oprint._settings.get(['deviceid']),
            })

        poll = json.dumps({
            "Action" : "COMPLETE_ACTION",
            "Device" : device    
        })   
        r = self.client.invoke(
            FunctionName = self.lambda_arn,
            InvocationType = 'RequestResponse',
            Payload = poll ,
            Qualifier = '$LATEST'
        )