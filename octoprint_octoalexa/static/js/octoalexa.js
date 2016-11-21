/*
 * View model for OctoPrint-Octoalexa
 *
 * Author: You
 * License: AGPLv3
 */
$(function() {
    
    function OctoalexaViewModel(parameters) {
        var self = this;

        self.toggle_service = function(){ 
            var data = {};
            data['command'] = "toggle_service"  ;
            $.ajax({
                url: API_BASEURL + "plugin/octoalexa",
                type: "POST",
                datatype: "json",
                data: JSON.stringify(data),
                contentType: "application/json",
                success: self.get_response
            });
            
        };
        //This gets called when a get request succeeds
        self.get_response = function(_response){
            response = JSON.parse(_response);
            document.getElementById("plugin_toggle_service").innerHTML = response.service_text;
            document.getElementById("service").innerHTML = response.service_enabled_text;
            console.log(_response);
        };

        self.register_pi = function(){
            var data = {};
            data['command'] = "regiser_device"  ;
            $.ajax({
                url: API_BASEURL + "plugin/octoalexa",
                type: "POST",
                datatype: "json",
                data: JSON.stringify(data),
                contentType: "application/json",
                success: self.populate_data
            });
        };

        self.populate_data = function(_response){
            response = JSON.parse(_response);
            console.log(_response);
            document.getElementById("mfakey").innerHTML = response.mfa_key;
        }
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        OctoalexaViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ ],

        // e.g. #settings_plugin_octoalexa, #tab_plugin_octoalexa, ...
        document.getElementById('octoalexa')
    ]);
});
