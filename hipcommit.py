#!/usr/bin/env python3

import datetime
import configparser
import time
import logging
import html
import xml.dom.minidom
import urllib.request
import urllib.parse

logging.basicConfig(filename='hipcommit.log', level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini')

last_poll_time = datetime.datetime.utcnow()

message_url = ('https://api.hipchat.com/v1/rooms/message'
               '?auth_token={}&room_id={}&from={}&message={}')
changeset_list_url = 'https://{}/source/rest-service-fe/revisionData-v1/changesetList/EXTGWT?FEAUTH={}&path=%2F&start={}&end={}&maxReturn=10'
changeset_url = 'https://{}/source/rest-service-fe/revisionData-v1/changeset/EXTGWT/{}?FEAUTH={}'

urii = 'https://sencha.jira.com/builds'

template5 = 'https://sencha.jira.com/builds/rest/api/latest/result/EXTGWT?os_authType=basic'

last_broken_build = None

def send_room_message(message):
    """Send a notification message to the predetermined room on HipChat."""
    room_id = config['hipchat']['room_id']
    logging.info("Sending message to room {}:".format(room_id))
    logging.info(message)
    url_encoded_message = urllib.parse.quote(message)
    request_url = message_url.format(config['hipchat']['notification_token'],
                                     room_id,
                                     urllib.parse.quote(config['hipchat']['name']),
                                     url_encoded_message)
    urllib.request.urlopen(request_url)

def get_commit_ids(from_time, to_time):
    """Fetch the commits from from_time to to_time and return a list of changeset IDs."""
    logging.info("Fetching commits from {} to {}".format(from_time, to_time))

    encoded_from_time = urllib.parse.quote(str(from_time))
    encoded_to_time = urllib.parse.quote(str(to_time))
    request_url = changeset_list_url.format(config['atlassian']['host'],
                                            config['atlassian']['auth_token'],
                                            encoded_from_time,
                                            encoded_to_time)

    response = urllib.request.urlopen(request_url)
    response_text = response.read().decode()
    logging.debug("Commits from {} to {}".format(from_time, to_time))
    logging.debug(response_text)
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
    request_url = changeset_url.format(config['atlassian']['host'],
                                       id,
                                       config['atlassian']['auth_token'])
    response = urllib.request.urlopen(request_url)
    response_text = response.read().decode()
    logging.debug("Commits for {}".format(id))
    logging.debug(response_text)
    document = xml.dom.minidom.parseString(response_text)

    details = {}
    changeset_element = document.firstChild
    details['changeset_id'] = changeset_element.attributes['csid'].nodeValue
    details['author'] = changeset_element.attributes['author'].nodeValue
    details['comment'] = changeset_element.getElementsByTagName('comment')[0].firstChild.nodeValue
    return details

def poll(last_poll_time, this_poll_time):
    for id in get_commit_ids(last_poll_time, this_poll_time):
        details = get_commit_details(id)
        mesage = '<a href="https://sencha.jira.com/source/changelog/EXTGWT?cs={changeset_id}">Commit {changeset_id}</a> by {author}:<br><br>{comment}'.format(**details)
        send_room_message(mesage)

    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password('protected-area',
                              urii,
                              config['atlassian']['username'],
                              config['atlassian']['password'])
    opener = urllib.request.build_opener(auth_handler)
    bamdoc = opener.open(template5).read().decode()
    logging.debug("Bamdoc follows")
    logging.debug(bamdoc)
    bamdoc = xml.dom.minidom.parseString(bamdoc)
    bamstate = bamdoc.firstChild.firstChild.firstChild.attributes['state'].nodeValue
    bamstate = bamstate
    if bamstate != 'Successful':
        bamkey = bamdoc.firstChild.firstChild.firstChild.attributes['key'].nodeValue
        if bamkey != last_broken_build:
            last_broken_build = bamkey
            bamlink = bamdoc.firstChild.firstChild.firstChild.firstChild.attributes['href'].nodeValue
            messsage = 'Build <a href="{}">{}</a> is {}'.format(bamlink, bamkey, bamstate)
            send_room_message(messsage)

def start_polling():
    while True:
        try:
            this_poll_time = datetime.datetime.utcnow()
            poll(last_poll_time, this_poll_time)
            last_poll_time = this_poll_time
        except urllib.error.URLError:
            pass
        time.sleep(60)

if __name__ == '__main__':
    start_polling()
