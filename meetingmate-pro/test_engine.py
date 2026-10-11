import unittest
from engine import analyze, search_evidence, speaker_metrics
class Tests(unittest.TestCase):
 def test_actions(self):
  data=analyze('We decided to ship Friday. Sam will send the report. There is a blocker.')
  self.assertEqual(len(data['actions']),1)
  self.assertEqual(len(data['decisions']),1)
  self.assertEqual(len(data['risks']),1)
 def test_retrieval(self):
  hits=search_evidence('Who sends the dashboard?','Sam will send the dashboard by Friday. The weather is warm.')
  self.assertTrue(hits)
  self.assertIn('dashboard',hits[0]['text'])
 def test_speakers(self):
  result=speaker_metrics([{'speaker':0,'start':0,'end':3},{'speaker':0,'start':3,'end':8}])
  self.assertEqual(result[0]['Speaking seconds'],8)
if __name__=='__main__': unittest.main()
