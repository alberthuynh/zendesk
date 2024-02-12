import requests
import json
import time
import base64

#Script that deletes 100 tickets per request every 5 second. Based on search string: https://support.zendesk.com/hc/en-us/articles/4408886879258-Zendesk-Support-search-reference
#https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/searching-with-the-zendesk-api/
#Search string located in access.json along with api credentials. 

#custom domain for fetching api
domain = 'zendesk'
subdomain = 'skybelltechnologies'
##using basic auth with api token.
#File called access.json. 
apiaccess = "access.json"
file = open(apiaccess, "r")
data = json.load(file)
try:
    username = data['username']
    api_key = data['apikey']
    searchstring = data['searchstring']
except:
    print("No username/api_key/string found")

#function to call the search count api returning the amount of tickets found, api call doesnt always return the correct search. 
def searchcount():
    url = "https://" + subdomain + "." + domain + ".com/api/v2/search/count?query=" + searchstring
    headers = {
            "Content-Type": "application/json",
    }
    response = requests.request(
        "GET",
        url,
        auth = (username+"/token", api_key),
        headers = headers
    )
    #returns the amount of ticket ids found
    return (response.json()['count'])
        
def searchticketid():
    url = "https://" + subdomain + "." + domain + ".com/api/v2/search/export?query=" + searchstring +"&page[size]=1000&filter[type]=ticket"
    headers = {
            "Content-Type": "application/json",
    }
    #uses zendesk api and gets the response from them
    response = requests.request(
            "GET",
            url,
            auth=(username+"/token", api_key),
            headers=headers
    )
    count=0
    ticketidfilename = "ticket_ids.txt"
    #opens up file to enter in ticket ids 
    file_object = open(ticketidfilename, "w+")
    #writes the ticket id found in search to file per line
    for i in response.json()['results']:
        file_object.write(str(i['id']))
        file_object.write("\n")
        count += 1
    #closes file
    file_object.close()
    print("Tickets written to file:" + ticketidfilename)
    print("Number of ids found: ", count)
    return count
###################################
#function code base from https://support.zendesk.com/hc/en-us/community/posts/5482557038106-Deleting-a-lot-of-tickets-from-your-Zendesk-instance-Not-a-big-deal-#:~:text=Use%20the%20Zendesk%20API%20to,ticket%20using%20the%20Zendesk%20API.
def deletetickets():
# Read the ticket IDs from a text file, one ID per line
    with open('ticket_ids.txt', 'r') as f:
        ticket_ids = f.read().splitlines()

    # Set the maximum number of tickets to delete per API request
    MAX_TICKETS_PER_REQUEST = 100

    # Split the ticket IDs into batches of maximum size MAX_TICKETS_PER_REQUEST
    ticket_id_batches = [ticket_ids[i:i+MAX_TICKETS_PER_REQUEST] for i in range(0, len(ticket_ids), MAX_TICKETS_PER_REQUEST)]

    # Set up the API request headers with Basic authentication
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f"{username}/token:{api_key}".encode("utf-8")).decode("ascii")}',
    }

    total_deleted_tickets = 0
    last_successful_ticket_id = None

    # Loop over each ticket ID batch and delete the tickets

    for ticket_ids_batch in ticket_id_batches:
        # Construct the URL to delete the tickets
        url = f'https://{subdomain}.zendesk.com/api/v2/tickets/destroy_many.json?ids={",".join(ticket_ids_batch)}'

        # Send the API request to delete the tickets with timeout of 60 seconds
        response = requests.delete(url, headers=headers, timeout=60)

        # Check if the request was successful
        if response.status_code == 200:
            num_deleted_tickets = len(ticket_ids_batch)
            total_deleted_tickets += num_deleted_tickets
            last_successful_ticket_id = ticket_ids_batch[-1]
            print(f'{num_deleted_tickets} tickets deleted successfully. Total deleted: {total_deleted_tickets}.')
        else:
            error_ticket_id = None
            if len(ticket_ids_batch) == 1:
                error_ticket_id = ticket_ids_batch[0]
            else:
                # Find the first ticket ID in the batch that was not deleted successfully
                response_json = response.json()
                for ticket_id in ticket_ids_batch:
                    if str(ticket_id) not in response_json['results']:
                        error_ticket_id = ticket_id
                        break

            print(f'Error deleting tickets. Last successful ticket ID: {last_successful_ticket_id}. Error ticket ID: {error_ticket_id}. Response: {response.text}')
            break

        # Print a loader to indicate that the code is still running
        for i in range(5):
            print('.', end='', flush=True)
            time.sleep(1)
        print()

        # Wait for 10 seconds before sending the next request
        time.sleep(5)

amountoftickets = 0
amountoftickets = searchcount()
#calls searchticketid and deletetickets function and continously runs them until the amount of tickets is less than the ones that are left. 
while amountoftickets > 0:
    amountoftickets -= searchticketid()
    deletetickets()
    #Not exact amount as the delete function may not able to delete some tickets. 
    print("Amount of tickets left to delete: ", amountoftickets)

print("All done")
