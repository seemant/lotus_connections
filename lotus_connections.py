"""
A simple python wrapper around the Lotus Connections API.  This code is based
on Rajiv Manglani's simple ruby wrapper, called lotus_connections.rb (Copyright 2009-2010 Rajiv Aaron Manglani.) found at: https://github.com/rajiv/lotus_connections

Copyright 2011 Seemant Kulleen. All rights reserved.

Released under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
"""

import pycurl
from urllib import urlencode
import feedparser
import re

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

BASE_URI = 'https://connections.mmm.com/profiles/atom/'


class LotusConnections( object ):
    def __init__( self, username=None, password=None ):
        if not all([username, password]):
            raise Exception, "Username and password cannot be blank"

        self.connection = pycurl.Curl()
        self.connection.setopt(
            pycurl.USERPWD,
            '%s:%s' % (username, password)
        )


        self.connection.setopt(
            pycurl.HTTPHEADER,
            [
                """Connection: keep-alive""",
                """Accept: application/xml""",
            ]
        )

        self.tel = re.compile(r'(="tel".*="value">(?P<tel>[\d-]*)</span></div>)')



    def find_by_name( self, name='' ):
        try:
            return self.find_by({'name': name,})
        except:
            raise


    def find_by_email( self, email='' ):
        try:
            return self.find_by({'email': email,})
        except:
            raise

    def find_by_name_or_email( self, query ):
        try:
            result = set(self.find_by_name(query))
            return result.union(set(self.find_by_email(query)))
        except:
            raise

    def find_by(self, params):
    """
    Returns a set of tuples (name, email, phone)
    """

        uri = BASE_URI + 'search.do' + '?%s' % urlencode(params)
        self.connection.setopt(pycurl.URL, uri)

        resp = StringIO()
        self.connection.setopt(pycurl.WRITEFUNCTION, resp.write)

        try:
            self.connection.perform()
        except pycurl.error:
            raise

        return self._parse_feed(resp.getvalue())

    def _parse_feed( self, feed ):
        results = []
        for entry in feedparser.parse(feed)['entries']:
            result = [i for i in entry['contributors'][0].itervalues()]
            match = self.tel.search(entry['content'][0]['value'])
            try:
                result.append(match.groupdict()['tel'])
            except AttributeError:
                result.append('')
            results.append(tuple(result))

        return results