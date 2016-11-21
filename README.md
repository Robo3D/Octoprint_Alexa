# Octoprint-Alexa
Connect Octoprint with Octoprint Alexa Skill

# Run manually 

## Setup

1. This setup assumes that you have the "My Robo" skill on your Alexa enabled device 

2. Login to the printers octoprint page using your printers hostname (IE: galactic-galileo.local/)

3. Click on the settings option

4. In the left hand column choose the plugin manager 

5. Click Get More

6. Either enter this repository's URL or Upload the Zip file

7. Plugin manager should take over and install Alexa Voice Services

8. Reload OctoPrint

9. Re-Open the settings tab

10. Click on Alexa Voice Services (You may have to scroll down)

11. Click on Enable Alexa Voice Plugin if the "Service Status" is Disabled

12. Once the "Service Status" is Enabled, Click on Register Device

13. Make sure your Alexa enabled device is active and say "Alexa ask My Robo to set code" Then say your Alexa Code

14. Once Alexa Confirms that the code has been set click Save
    a. If you do not click save Your device will not be enabled

15. Say "Alexa ask My Robo for it's status"

16. If Alexa Responds with a status then you are all set up! Try out other commands such as "Pause Print" and "Cancel Print"


## Usage

There are a few key phrases that Alexa can understand 

After saying "Alexa ask My Robo" you can supplement a few commands. They are:

1. "to Pause Print" or just "to Pause"
2. "to Resume Print" or "to Continue Print"
3. "for it's Status"

So for example we can ask "Alexa ask My Robo to Pause Print" and the active print should pause
