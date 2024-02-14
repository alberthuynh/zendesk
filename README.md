# zendesk
Zendesk Ticket deleting script
Tested with python 3.12 https://www.python.org/downloads/

Script requires a zendesk username and API key. Replace the fields in access.json with your username and API key. 
Put your search key in access.json as well. You can check if your search returns anything by searching in the normal search bar in zendesk. 

Script will run until most tickets are deleted. You may need to run script multiple times as it does not rerun tickets that were not able to deleted. Deletes about 100 tickets every 5 seconds. 
