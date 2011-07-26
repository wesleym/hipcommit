#!/usr/bin/env python3.2

import datetime
import time
import urllib.request
import xml.dom.minidom
import html

import constants

last_poll_time = datetime.datetime.utcnow()
print(last_poll_time)

def send_room_message(message):
    print("Sending message to room {}:".format(constants.ROOM_ID))
    print(message)
    html_encoded_message = html.escape(message).replace('\n', '<br>')
    url_encoded_message = urllib.request.pathname2url(html_encoded_message)
    urllib.request.urlopen(constants.template3.format(constants.HIPCHAT_NOTIFICATION_TOKEN, constants.ROOM_ID, url_encoded_message))

def get_commit_ids(from_time, to_time):
    encoded_from_time = urllib.request.pathname2url(str(from_time))
    encoded_to_time = urllib.request.pathname2url(str(to_time))
    request_url = constants.template1.format(encoded_from_time, encoded_to_time)
    response = urllib.request.urlopen(request_url)

    response_text = response.read().decode()
    document = xml.dom.minidom.parseString(response_text)
    csid_elements = document.firstChild.childNodes

    return csid_elements

while True:
    this_poll_time = datetime.datetime.utcnow()
    print(this_poll_time)

    for element in get_commit_ids(last_poll_time, this_poll_time):
        csidname = element.firstChild.nodeValue
        csidoutput = urllib.request.urlopen(constants.template2.format(csidname))
        outputtextt = csidoutput.read().decode()
        documentt = xml.dom.minidom.parseString(outputtextt)
        pppp = documentt.firstChild
        csidd = pppp.attributes['csid'].nodeValue
        authorr = pppp.attributes['author'].nodeValue
        commentt = pppp.getElementsByTagName('comment')[0].firstChild.nodeValue
        try:
            authorr = constants.author_by_email[authorr]
        except KeyError:
            # Leave the author as an email address
            pass
        mesage = "Commit {} by {}:\n\n{}".format(csidd, authorr, commentt)
        send_room_message(mesage)
        urllib.request.urlopen(constants.template3.format(urllib.request.pathname2url(mesage)))
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
