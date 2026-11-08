import argparse,json,csv,sys
from pathlib import Path
from parser import parse_path
from heuristic import candidate_windows,rank_all

def main():
 p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--provider',default='heuristic',choices=['gemini','groq','anthropic','openai','heuristic']); p.add_argument('--model'); p.add_argument('--output',default='raw_outputs'); p.add_argument('--run-label',default='run1'); args=p.parse_args()
 src=Path(args.input); paths=sorted(src.glob('*.txt')) if src.is_dir() else []
 if src.is_file() and src.suffix.lower()=='.zip':
  import zipfile,tempfile
  tmp=Path(tempfile.mkdtemp()); zipfile.ZipFile(src).extractall(tmp); paths=sorted(tmp.rglob('*.txt'))
 if not paths: raise SystemExit('No .txt screenplays found')
 eps=[]; errors=[]
 for f in paths:
  try:
   ep=parse_path(f); eps.append(ep)
   if ep['warnings']: errors.extend([f'{f.name}: {w}' for w in ep['warnings']])
  except Exception as e: errors.append(f'{f.name}: {e}')
 if args.provider=='heuristic':
  allc=[]
  for ep in eps:
   cs=candidate_windows(ep); allc.extend(cs)
   out=Path(args.output)/'heuristic'/f"episode_{ep['episode']:03d}.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps({'episode':ep['episode'],'duration':ep['duration'],'warnings':ep['warnings'],'candidates':cs},indent=2),encoding='utf-8')
  ranked=rank_all(allc); dest=Path(args.output)/'heuristic'; dest.mkdir(exist_ok=True,parents=True)
  summary={'episodes_found':len(eps),'parsed_beats':sum(len(e['beats']) for e in eps),'candidates':len(allc),'ranked_promos':len(ranked),'parse_warnings':errors,'provider':'heuristic'}
  (dest/'ranked_top15.json').write_text(json.dumps(ranked,indent=2),encoding='utf-8')
  with (dest/'ranked_top15.csv').open('w',newline='',encoding='utf-8') as f:
   w=csv.DictWriter(f,fieldnames=['rank','episode','start','end','duration','rank_score','hook','cliffhanger','why']); w.writeheader()
   for c in ranked: w.writerow({k:c.get(k,'') for k in w.fieldnames})
  (dest/'run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 else:
  from llm_pipeline import run_llm
  summary,ranked=run_llm(eps,args.provider,args.model,args.output,args.run_label)
  summary['parsed_beats']=sum(len(e['beats']) for e in eps); summary['parse_warnings']=errors
  dest=Path(args.output)/'llm'/args.run_label; (dest/'run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
