# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

import os
import random
import string
import uuid
import boto3
import json

from .server_interaction import Authenticate, Update_Status
from threading import Timer

class OctoalexaPlugin(octoprint.plugin.SettingsPlugin,
                      octoprint.plugin.AssetPlugin,
                      octoprint.plugin.TemplatePlugin,
                      octoprint.plugin.StartupPlugin,
                      octoprint.plugin.EventHandlerPlugin,
                      octoprint.plugin.SimpleApiPlugin):

    ##~~ StartupPlugin
    def __init__(self):
        super(OctoalexaPlugin, self).__init__()
        self.state = "ready"
        self.last_state = self.state

    def update(self):
        response = self.server.poller()

        if response == False:
            pass
        else:
            if response['command'] == 'cancel':
                self._logger.info("Cancel The Print!")
                self._printer.cancel_print()
                self._printer.unselect_file()
                self.server.complete_action()

            elif response['command'] == 'pause':
                self._logger.info("Pause The Print!")

                if self._printer.is_paused() == False:

                    self._printer.toggle_pause_print()
                else:
                    self._logger.info("Print is already paused")

                self.server.complete_action()

            elif response['command'] == 'resume':
                self._logger.info("resume The Print!")

                if self._printer.is_paused() == True:

                    self._printer.toggle_pause_print()
                else:
                    self._logger.info("Print is not paused")

                self.server.complete_action()

            elif response['command'] == 'ready':
                #do nothing
                pass

        #if the printer is printing and services are enabled then continue else stop
        if self.printing == True and response != False:
            self.timer = Timer(1,self.update)
            self.timer.start()
        else:
            self._logger.info("Command Updater is now stopping")

    def on_after_startup(self):
        self._logger.info("Starting Octo Alexa")
        self.server = Update_Status(self)
        self.auth = Authenticate(self)
        if self._settings.get(['session_id']) != None:
            self.initialize_device()

    def initialize_device(self):
        self.state = "ready"
        self.last_state = self.state
        self.printing = False

        self.service_enabled = self._settings.get(['service_enabled'])
        if self.service_enabled == None:
            self.service_enabled = False
            self._settings.set(['service_enabled'], self.service_enabled)

        self.last_service_enabled = self.service_enabled
        self.server.update(self.state)
        self.server.complete_action()



    def on_event(self,event, payload):
        if event == 'PrintStarted':
            self.state = "printing"
            self.printing = True
            self.server.complete_action()
            self.update()
        elif event == 'PrintFailed':
            self.state = "ready"
            self.printing = False
        elif event == 'PrintDone':
            self.state = "printing finished ready"
            self.printing = False
        elif event == 'PrintCancelled':
            self.state = "ready"
            self.printing = False
        elif event == 'PrintPaused':
            self.state = "print paused"
        elif event == 'PrintResumed':
            self.state = "printing"
        elif event == "FileDeselected":
            self.state = "ready"
            self.printing = False

        if self.last_state != self.state:
            self.server.update(self.state)
            self.last_state = self.state

    #command calls
    def get_assets(self):
        return dict(
            js=["js/octoalexa.js"]
        )
    def get_api_commands(self):
        return dict(
            toggle_service=[],
            regiser_device=[]
        )

    def on_api_get(self, request):
        self._logger.info("Request info made from JS")
        self._logger.info(self._settings.get(['service']))
        return flask.jsonify(service_text=self._settings.get(['service']))


    def on_api_command(self, command, data):
        import flask
        if command == "toggle_service":
            self.service_enabled = not self.service_enabled

            if self.service_enabled == True:
                #enable the service then send the update
                self._settings.set(['service_enabled'], self.service_enabled)
                self.server.update("ready")
                self._logger.info("Alexa services are enabled")
                self.initialize_device()
                if self.printing:
                    self.update()
                return json.dumps({
                    'service_text':"Disable Alexa Voice Services",
                    'service_enabled_text': "Enabled"
                    })

            elif self.service_enabled == False:
                #send the update then disable services
                self.server.update("robo voice services are not enabled.")
                self._settings.set(['service_enabled'], self.service_enabled)
                self._logger.info("Alexa services are disabled")
                return json.dumps({
                    'service_text':"Enable Alexa Voice Services",
                    'service_enabled_text': "Disabled"
                    })
        elif command == "regiser_device":
            self.auth.register_pi()
            self.initialize_device()
            return json.dumps({
                'mfa_key' : self._settings.get(['mfakey'])
                })

    def on_settings_save(self, data):
        self._settings.set(['service_enabled'], self.service_enabled)
        self._logger.info("Settings Saved!")


    def get_settings_defaults(self):
        return dict(
            mfakey=None,
            deviceid=None,
            service_enabled=None,
            session_id = None
        )

    def get_template_vars(self):
        se = self._settings.get(['service_enabled'])
        if se == False or se == None:
            return dict(
                service_enabled="Disabled",
                service="Enable Alexa Voice Services"

            )
        elif se == True:
            return dict(
                service_enabled="Enabled" ,
                service= "Disable Alexa Voice Services"

            )


    ##~~ AssetPlugin mixin
    def get_template_configs(self):
        return [
            #dict(type="navbar", custom_bindings=False),
            #dict(type="settings", custom_bindings=False)
        ]

    ##~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            octoalexa=dict(
                displayName="Octoalexa Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="Robo3D",
                repo="Octoprint_Alexa",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/Robo3D/Octoprint_Alexa/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Alexa Voice Services"
def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoalexaPlugin()
    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
