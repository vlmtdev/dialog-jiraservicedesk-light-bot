# dialog-jiraservicedesk-light-bot
* Service Desk Light Bot for Jira *

* Bot will work only with LDAP Dialog configuration and LDAP Jira configuration with same catalog, because bot associates nickname in Dialog and Jira when it works. *

This bot allows users to create issues (tickets) in any Jira service desk project.  
Bot can operate in three modes (variable ISSUE_TYPE_MODE):  
0 - in this mode bot doesn't ask about service desk request type. It just picks first ID of type in variable ISSUE_TYPE_CONFIG.  
1 - in this mode bot asks about request type, but choosing time is limited with env variable ISSUE_TYPE_TIME. If user don't want to choose request type or user is too slow to choose, bot creates issue with first ID of type in variable ISSUE_TYPE_CONFIG  
2 - in this mode it's necessary to choose request type. If user is too slow to choose (time variable REQUEST_TIMEOUT), request will be rejected.  
  
Variables guide:  
BOT_API_KEY - Api key of Dialog bot  
ENDPOINT - URL of Dialog endpoint  
ISSUE_TYPE_MODE - Bot mode (described above)  
ISSUE_TYPE_TIME - Time to choose request type (only in mode 1, described above)  
ISSUE_TYPE_CONFIG - Request types of Service desk in Jira (IDs separated with comma without spaces)  
SEND_DELAY - Send delay, prevents flood from single user  
REQUEST_TIMEOUT - Time to choose request type (only in mode 2, described above)  
PROJECT_KEY - Key of service desk project in Jira  
JIRA_CREDS - Credentials for jira in format: username:password@https://jira.example.com  
LANGUAGE - Language of bot (only russian "ru", maybe somebody will add another translations in translation.py)  
REQUEST_NAME_CHARS_COUNT - Count of chars in Summary field in Jira, another chars will go to Description field  
All time variables accepts integer numbers - seconds.
  
How to launch bot:  
- build Docker container (dockerfile included)  
- launch container as described:  
```
docker run -d --name dialog-servicedesk_light-bot-TECHSUP -i -t --restart always \
	-v /etc/localtime:/etc/localtime:ro \
	-e BOT_API_KEY="place_your_bot_api_key_here" \
	-e ENDPOINT="eem.dlg.im" \
	-e ISSUE_TYPE_MODE="1" \
	-e ISSUE_TYPE_TIME="12" \
	-e ISSUE_TYPE_CONFIG="8,21" \
	-e SEND_DELAY="300" \
	-e REQUEST_TIMEOUT="120" \
	-e PROJECT_KEY="TECHSUP" \
	-e JIRA_CREDS="username:password@https://jira.example.com" \
	-e LANGUAGE="ru" \
	-e REQUEST_NAME_CHARS_COUNT="45" \
	-d dialog-servicedesk_light-bot
```  
- enjoy