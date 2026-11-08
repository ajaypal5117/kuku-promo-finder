import sys,unittest
sys.path.insert(0,'src')
from parser import parse_script,to_seconds,fmt_time
class ParserTests(unittest.TestCase):
 def test_time(self): self.assertAlmostEqual(to_seconds('01:02.50'),62.5)
 def test_roundtrip(self): self.assertEqual(fmt_time(62.5),'01:02.50')
 def test_blocks(self):
  x='EPISODE NUMBER: Episode 3\nEPISODE LOGLINE: Test\n**HERO (Angry):**\nStart: (00:01.00) | End: (00:03.00)\nStop!\n'
  e=parse_script(x); self.assertEqual(e['episode'],3); self.assertEqual(len(e['beats']),1); self.assertEqual(e['beats'][0]['text'],'Stop!')
if __name__=='__main__': unittest.main()
