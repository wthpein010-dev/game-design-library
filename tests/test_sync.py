import unittest
from scripts.sync import canonical_url, parse_feed, merge_records, relevant

class SyncTests(unittest.TestCase):
    def test_video_part_survives_tracking_cleanup(self):
        self.assertEqual(canonical_url('https://www.bilibili.com/video/BVabc/?p=2&utm_source=x#x'), 'https://www.bilibili.com/video/BVabc/?p=2')
    def test_reject_unsafe_url(self):
        with self.assertRaises(ValueError): canonical_url('javascript:alert(1)')
    def test_rss_text_and_attribution(self):
        xml = b'<rss><channel><item><title>A &amp; B</title><link>https://example.com/a/</link><description>&lt;p&gt;Short note&lt;/p&gt;</description></item></channel></rss>'
        row = parse_feed(xml, {'id':'demo','name':'Example','language':'en','category':'玩法与系统'})[0]
        self.assertEqual(row['title'], 'A & B')
        self.assertEqual(row['summary'], 'Short note')
        self.assertEqual(row['review'], '自动索引')
    def test_update_preserves_first_seen_and_manual_edits(self):
        old=[{'id':'a','url':'https://example.com/a/','title':'Old','first_seen':'2020-01-01','review':'人工整理','summary':'Editor'}]
        new=[{'id':'b','url':'https://example.com/a/?utm_source=x','title':'New','summary':'Feed','review':'自动索引'}]
        rows,changes=merge_records(old,new,'2026-10-13')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['first_seen'],'2020-01-01')
        self.assertEqual(rows[0]['summary'],'Editor')
    def test_empty_fetch_keeps_previous_records(self):
        rows,changes=merge_records([{'id':'a','url':'https://example.com/','title':'A'}],[],'today')
        self.assertEqual(len(rows),1)
        self.assertEqual(changes,[])
    def test_known_site_http_https_are_same_resource(self):
        self.assertEqual(canonical_url('http://www.designer-notes.com/a/'),canonical_url('https://www.designer-notes.com/a/'))
    def test_source_exclusions_remove_off_topic_announcements(self):
        source={'exclude_pattern':'election|hello-world'}
        self.assertFalse(relevant({'title':'Thoughts on the election','url':'https://example.com/a'},source))
        self.assertTrue(relevant({'title':'Game balance','url':'https://example.com/b'},source))

if __name__=='__main__': unittest.main()
