#!/bin/bash
#service cron start
printenv | grep "BOT_API_KEY" >> /etc/environment
printenv | grep "ENDPOINT" >> /etc/environment
printenv | grep "ISSUE_TYPE_MODE" >> /etc/environment
printenv | grep "ISSUE_TYPE_TIME" >> /etc/environment
printenv | grep "ISSUE_TYPE_CONFIG" >> /etc/environment
printenv | grep "PROJECT_KEY" >> /etc/environment
printenv | grep "JIRA_CREDS" >> /etc/environment
printenv | grep "SEND_DELAY" >> /etc/environment
printenv | grep "REQUEST_TIMEOUT" >> /etc/environment
printenv | grep "LANGUAGE" >> /etc/environment
printenv | grep "REQUEST_NAME_CHARS_COUNT" >> /etc/environment
#rm /var/spool/cron/crontabs/root
#touch /var/spool/cron/crontabs/root
#crontab -l > cronfile
#echo "0 12 * * * python3 /py/start.py" >> cronfile
#crontab cronfile
#rm cronfile
python3 /py/start.py >> /dev/stdout
/bin/bash