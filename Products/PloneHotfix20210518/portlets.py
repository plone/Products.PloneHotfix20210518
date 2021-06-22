try:
    # Py 3
    from urllib.parse import urlparse
except ImportError:
    # Py 2
    from urlparse import urlparse


from plone.app.portlets.portlets.rss import RSSFeed


RSSFeed._orig_retrieveFeed = RSSFeed._retrieveFeed


def _retrieveFeed(self):
    # Only load http and https, not file, email, etc.
    if self.url:
        if len(self.url.splitlines()) > 1:
            # More than one line in a url: probably a hacker.
            self.url = ""
        elif urlparse(self.url).scheme not in ("https", "http"):
            self.url = ""
    return self._orig_retrieveFeed()


RSSFeed._retrieveFeed = _retrieveFeed
