import streamlit as st,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from parser import parse_script
from heuristic import candidate_windows,rank_all
st.set_page_config(page_title='Kuku Promo Finder',layout='wide')
st.title('Kuku Promo Finder')
st.caption('Screenplay-to-promo candidate finder · human approval required')
up=st.file_uploader('Upload a screenplay ZIP',type=['zip'])
provider=st.selectbox('Mode',['Heuristic baseline'])
if up:
 import zipfile,tempfile
 tmp=Path(tempfile.mkdtemp()); zpath=tmp/'input.zip'; zpath.write_bytes(up.getvalue())
 with zipfile.ZipFile(zpath) as z: z.extractall(tmp/'scripts')
 eps=[]
 for f in sorted((tmp/'scripts').rglob('*.txt')):
  ep=parse_script(f.read_text(encoding='utf-8',errors='replace'),f.name); eps.append(ep)
 allc=[]
 for ep in eps: allc.extend(candidate_windows(ep))
 ranked=rank_all(allc)
 st.metric('Episodes parsed',len(eps)); st.metric('Candidates',len(allc))
 st.subheader('Ranked promo candidates')
 for c in ranked:
  with st.expander(f"#{c['rank']} · Episode {c['episode']} · {c['segments'][0]['start']}–{c['segments'][0]['end']} · {c['duration']}s"):
   st.write('**Hook evidence**',c['hook']); st.write('**Ending evidence**',c['cliffhanger']); st.write(c['why'])
   st.radio('Editor decision', ['Not reviewed','Accept','Reject'],key=f"decision_{c['rank']}",horizontal=True)
 st.download_button('Download ranked JSON',json.dumps(ranked,indent=2),file_name='ranked_promos.json')
 st.download_button('Download ranked CSV','rank,episode,start,end,duration,score,hook,cliffhanger\n'+'\n'.join(f"{c['rank']},{c['episode']},{c['start']},{c['end']},{c['duration']},{c['score']},\"{c['hook'][:100].replace(chr(34),chr(39))}\",\"{c['cliffhanger'][:100].replace(chr(34),chr(39))}\"" for c in ranked),file_name='ranked_promos.csv')
