#!/usr/bin/env python3.2

import datetime
import time
import urllib.request
import xml.dom.minidom
import html

import constants

last_poll_time = datetime.datetime.utcnow()

def send_room_message(message):
    """Send a notification message to the predetermined room on HipChat."""
    print("Sending message to room {}:".format(constants.ROOM_ID))
    print(message)
    html_encoded_message = html.escape(message).replace('\n', '<br>')
    url_encoded_message = urllib.request.pathname2url(html_encoded_message)
    urllib.request.urlopen(constants.template3.format(constants.HIPCHAT_NOTIFICATION_TOKEN, constants.ROOM_ID, url_encoded_message))

def get_commit_ids(from_time, to_time):
    """Fetch the commits from from_time to to_time and return a list of changeset IDs."""
    print("Fetching commits from {} to {}".format(from_time, to_time))

    encoded_from_time = urllib.request.pathname2url(str(from_time))
    encoded_to_time = urllib.request.pathname2url(str(to_time))
    request_url = constants.template1.format(encoded_from_time, encoded_to_time)

    response = urllib.request.urlopen(request_url)
    response_text = response.read().decode()
    document = xml.dom.minidom.parseString(response_text)
    changeset_id_elements = document.firstChild.childNodes
    changeset_ids = [element.firstChild.nodeValue for element in changeset_id_elements]
    return changeset_ids

def get_commit_details(id):
    """Fetch the details for the specified commit and return a dict of its details.

    The resulting dict will have the following keys:
        * changeset_id: The ID of the changeset
        * author: The author's email address
        * comment: The commit message
    """
    request_url = constants.template2.format(id)
    response = urllib.request.urlopen(request_url)
    response_text = response.read().decode()
    document = xml.dom.minidom.parseString(response_text)

    details = {}
    changeset_element = document.firstChild
    details['changeset_id'] = changeset_element.attributes['changeset_id'].nodeValue
    details['author'] = changeset_element.attributes['author'].nodeValue
    details['comment'] = changeset_element.getElementsByTagName('comment')[0].firstChild.nodeValue
    return details

while True:
    this_poll_time = datetime.datetime.utcnow()

    for id in get_commit_ids(last_poll_time, this_poll_time):
        details = get_commit_details(id)
        # Try to convert author into HipChat username format
        try:
            details['author'] = constants.author_by_email[details['author']]
        except KeyError:
            # Leave the author as an email address
            pass
        mesage = "Commit {changeset_id} by {author}:\n\n{comment}".format(**details)
        send_room_message(mesage)
    osahu = urllib.request.HTTPBasicAuthHandler()
    osahu.add_password('protected-area', constants.urii, constants.usernamee, constants.passy)
    osahu = urllib.request.build_opener(osahu)
    bamdoc = osahu.open(constants.template5).read().decode()
    bamdoc = xml.dom.minidom.parseString(bamdoc)
    bamstate = bamdoc.firstChild.firstChild.firstChild.attributes['state'].nodeValue
    bamstate = bamstate
    if bamstate != 'Successful':
        bamkey = bamdoc.firstChild.firstChild.firstChild.attributes['key'].nodeValue
        bamlink = bamdoc.firstChild.firstChild.firstChild.firstChild.attributes['href'].nodeValue
        messsage = "Build {} is {}<br>See {}".format(bamkey, bamstate, bamlink)
        send_room_message(messsage)

    last_poll_time = this_poll_time
    time.sleep(60)
