import json
import sqlite3
import unittest
from scripts.build import ROOT,sanitize

class BuildTests(unittest.TestCase):
    def test_sanitize_removes_scripts_handlers_and_javascript_urls(self):
        value=sanitize('<p onclick="bad()">OK<script>bad()</script><a href="javascript:bad()">text</a></p>')
        self.assertNotIn('bad',value)
        self.assertIn('OK',value)
    def test_database_matches_catalog_and_course_coverage(self):
        data=json.loads((ROOT/'site/data/catalog.json').read_text(encoding='utf8'))
        db=sqlite3.connect(ROOT/'site/data/knowledge.sqlite')
        self.assertEqual(db.execute('pragma integrity_check').fetchone()[0],'ok')
        self.assertEqual(db.execute('select count(*) from resources').fetchone()[0],len(data['resources']))
        self.assertEqual(db.execute('select count(*) from lessons').fetchone()[0],50)
        videos=[r for r in data['resources'] if r['kind']=='视频']
        self.assertEqual(len(videos),63)
        self.assertEqual(len({(r['bvid'],r['page']) for r in videos}),63)
        ids={r['id'] for r in data['resources']}
        self.assertTrue(all(set(t['resources'])<=ids for t in data['topics']))
        self.assertEqual(len(ids),len(data['resources']))
        db.close()

if __name__=='__main__':unittest.main()
