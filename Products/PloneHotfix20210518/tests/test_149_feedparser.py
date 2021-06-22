# -*- coding: utf-8 -*-
from plone.app.portlets.portlets.rss import RSSFeed
from plone.namedfile.file import NamedBlobFile
from Products.PloneHotfix20210518.tests import AcceptanceTest

import os
import transaction


# Take a sample feed.  In this case an atom feed instead of RSS.
# Taken from https://maurits.vanrees.org/weblog/topics/plone/@@atom.xml
here = os.path.dirname(__file__)
sample_feed = os.path.join(here, "atom_feed_maurits.xml")


class TestAttackVector(AcceptanceTest):
    def test_rss_feed_file(self):
        # We pass a url and a timeout in minutes
        feed = RSSFeed("file://" + sample_feed, 1)
        feed._retrieveFeed()
        self.assertTrue(feed._loaded)
        self.assertTrue(feed._failed)
        self.assertFalse(feed.ok)
        self.assertFalse(feed.siteurl)
        self.assertEqual(len(feed.items), 0)

    def test_rss_feed_http(self):
        with open(sample_feed, "rb") as myfile:
            data = myfile.read()
        file_field = NamedBlobFile(data, filename=u"feed.xml")
        feed_id = self.portal.invokeFactory("File", "feed")
        feed = self.portal[feed_id]
        if hasattr(feed, "setFile"):
            # Archetypes on 4.3 cannot handle passing a NamedBlobFile.
            feed.setFile(data, filename=u"feed.xml")
        else:
            feed.file = file_field
        transaction.commit()

        # Eat the feed.
        feed = RSSFeed(feed.absolute_url(), 1)
        feed._retrieveFeed()
        self.assertTrue(feed._loaded)
        self.assertFalse(feed._failed)
        self.assertTrue(feed.ok)
        self.assertEqual(feed.siteurl, u"https://maurits.vanrees.org/weblog")
        self.assertEqual(len(feed.items), 15)
