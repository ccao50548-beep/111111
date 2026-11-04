import unittest,sys,pathlib,tempfile
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]))
import core,official,report

class EndToEnd(unittest.TestCase):
 def test_verified_segregated_and_report(self):
  with tempfile.TemporaryDirectory() as temp:
   old_a,old_b=official.DB,core.DB
   official.DB=core.DB=pathlib.Path(temp)/'test.sqlite3'
   try:
    n=official.store([{'jc_no':'周三001','date':'2026-11-04','kickoff':'2026-11-04 20:00','league':'模拟','home':'Team H','away':'Team A'}],'测试CSV')
    self.assertEqual(n,1)
    match=official.load('2026-11-04')[0]
    self.assertEqual(match['review_state'],'待核对')
    self.assertIsNone(match['home_xg'])
    official.record_confirmation('2026-11-04','周三001',True)
    self.assertEqual(official.load('2026-11-04')[0]['review_state'],'用户已核对官方页面')
    out=pathlib.Path(temp)/'report.html';report.export(out,'2026-11-04')
    self.assertIn('暂无充分赛前数据',out.read_text(encoding='utf-8'))
   finally:
    official.DB,core.DB=old_a,old_b
 def test_historical_matching_no_future(self):
  with tempfile.TemporaryDirectory() as temp:
   old_a,old_b=official.DB,core.DB
   official.DB=core.DB=pathlib.Path(temp)/'test.sqlite3'
   try:
    official.store([{'jc_no':'周三001','date':'2026-11-04','kickoff':'2026-11-04 20:00','league':'模拟','home':'Home United','away':'Away City'}],'mock')
    target=datetime(2026,11,4,12,tzinfo=timezone.utc)
    entries=[]
    for k in range(6):
     entries.append({'id':100+k,'utcDate':(target-timedelta(days=(k+1)*7)).isoformat(),'status':'FINISHED',
       'homeTeam':{'id':1,'name':'Home United'},'awayTeam':{'id':2,'name':'Away City'},'score':{'fullTime':{'home':2,'away':1}}})
    entries.append({'id':999,'utcDate':target.isoformat(),'status':'TIMED',
       'homeTeam':{'id':1,'name':'Home United'},'awayTeam':{'id':2,'name':'Away City'},'score':{'fullTime':{'home':None,'away':None}}})
    with patch('sources.request_json',return_value={'matches':entries}):
     n,errors=official.enrich_from_football_data('2026-11-04','fake',['PL'])
    self.assertEqual(n,1,str(errors))
    r=official.load('2026-11-04')[0]
    self.assertIsNotNone(r['home_xg'])
    self.assertGreaterEqual(r['history_home'],5)
    future=dict(entries[0]);future['id']=777;future['utcDate']=(target+timedelta(days=5)).isoformat();future['score']={'fullTime':{'home':50,'away':0}}
    with patch('sources.request_json',return_value={'matches':entries+[future]}):
     official.enrich_from_football_data('2026-11-04','fake',['PL'])
    self.assertAlmostEqual(r['home_xg'],official.load('2026-11-04')[0]['home_xg'])
   finally:
    official.DB,core.DB=old_a,old_b
if __name__=='__main__':unittest.main()
