#!/usr/bin/env python3.2

import datetime
import time
import urllib.request
import xml.dom.minidom

import constants

lastpoll = datetime.datetime.utcnow()
print(lastpoll)

while True:
    thispoll = datetime.datetime.utcnow()
    print(thispoll)

    output = urllib.request.urlopen(constants.template1.format(urllib.request.pathname2url(str(lastpoll)), urllib.request.pathname2url(str(thispoll))))

    outputtext = output.read().decode()
    document = xml.dom.minidom.parseString(outputtext)
    elements = document.firstChild.childNodes
    for element in elements:
        csidname = element.firstChild.nodeValue
        csidoutput = urllib.request.urlopen(constants.template2.format(csidname))
        outputtextt = csidoutput.read().decode()
        documentt = xml.dom.minidom.parseString(outputtextt)
        pppp = documentt.firstChild
        csidd = pppp.attributes['csid'].nodeValue
        authorr = pppp.attributes['author'].nodeValue
        commentt = pppp.getElementsByTagName('comment')[0].firstChild.nodeValue
        commentt = commentt.replace('\n', '<br>')
        try:
            authorr = constants.author_by_email[authorr]
        except KeyError:
            # Leave the author as an email address
            pass
        mesage = "Commit {} by {}:<br><br>{}".format(csidd, constants.author_by_email[authorr], commentt)
        print(mesage)
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
        urllib.request.urlopen(constants.template3.format(urllib.request.pathname2url(messsage)))
    lastpoll = thispoll
    time.sleep(60)
