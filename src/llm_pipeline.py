import json,time,hashlib
from pathlib import Path
from llm import call_model,json_from_response
from heuristic import rank_all
from parser import fmt_time
from pydantic import BaseModel, Field, ValidationError

class CandidateItem(BaseModel):
    beat_ids: list[str]
    hook_reason: str = ''
    cliffhanger_reason: str = ''
    why: str = ''

class CandidateResponse(BaseModel):
    candidates: list[CandidateItem] = Field(default_factory=list)

class JudgeResponse(BaseModel):
    hook: float = 0
    cliffhanger: float = 0
    standalone: float = 0
    emotional_appeal: float = 0
    cold_viewer_characters: str = ''
    cold_viewer_stakes: str = ''
    passed: bool = Field(default=False, alias='pass')
    reason: str = ''
    model_config = {'populate_by_name': True}

def _beat_context(ep):
    return '\n'.join(f"{b['beat_id']} | {fmt_time(b['start'])}-{fmt_time(b['end'])} | {b['label']} | {b['text']}" for b in ep['beats'])

def _ask(prompt,provider,model,cache_dir,retries=5):
    cache_dir=Path(cache_dir); cache_dir.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256((provider+'|'+str(model)+'|'+prompt).encode()).hexdigest()
    cache_file=cache_dir/(key+'.json')
    if cache_file.exists(): return json.loads(cache_file.read_text(encoding='utf-8')), True
    last=None
    for attempt in range(retries):
        try:
            data=json_from_response(call_model(prompt,provider,model))
            cache_file.write_text(json.dumps(data,indent=2),encoding='utf-8')
            return data, False
        except Exception as e:
            last=e
            if attempt+1<retries: time.sleep(min(60,2**attempt*2))
    raise RuntimeError(f'Model call failed after {retries} attempts: {last}')

def run_llm(episodes,provider='gemini',model=None,output_dir='raw_outputs/llm',run_label='run1'):
    out=Path(output_dir)/'llm'/run_label; out.mkdir(parents=True,exist_ok=True)
    all_candidates=[]; failures=[]; call_count=0; start_time=time.time()
    for ep in episodes:
        beats=ep['beats']; valid={b['beat_id']:b for b in beats}
        prompt=f'''You are selecting short-form vertical microdrama ad moments. Analyze ONLY this episode and its story context. Return JSON: {{"candidates":[{{"beat_ids":["first beat id","last beat id"],"hook_reason":"...","cliffhanger_reason":"...","why":"..."}}]}}.\nRules: choose 1-4 promising continuous stretches; first beat must create a hook within 3 seconds of clip start; ending must leave a concrete unresolved question/danger/reveal; cold viewers need enough context; choose only beat IDs below; no invented timestamps or dialogue; candidate duration should be 20-60 seconds based on listed beat timestamps. Prefer 25-45 seconds.\nLogline: {ep['logline']}\nContinuity: {ep['continuity']}\nTIMED BEATS:\n{_beat_context(ep)}'''
        try:
            data,cached=_ask(prompt,provider,model,out/'cache'); call_count+=0 if cached else 1
            response=CandidateResponse.model_validate(data)
            for item in response.candidates:
                ids=item.beat_ids
                if len(ids)<2 or ids[0] not in valid or ids[-1] not in valid: continue
                first,last=valid[ids[0]],valid[ids[-1]]
                # Snap to code-owned boundaries and validate ordered timeline.
                s,e=first['start'],last['end']; dur=e-s
                if e<s or not 20<=dur<=60: continue
                # Reject any boundary that cuts through a dialogue block.
                if any(b['kind']=='dialogue' and ((b['start'] < s < b['end']) or (b['start'] < e < b['end'])) for b in beats): continue
                selected=[b for b in beats if b['end']>s and b['start']<e]
                if not selected: continue
                c={'episode':ep['episode'],'start':s,'end':e,'duration':round(dur,2),'start_beat':ids[0],'end_beat':ids[-1], 'segments':[{'episode':ep['episode'],'start':fmt_time(s),'end':fmt_time(e)}], 'hook_reason':item.hook_reason,'cliffhanger_reason':item.cliffhanger_reason,'why':item.why,'hook':' '.join(b['text'] for b in selected[:5])[:600], 'cliffhanger':' '.join(b['text'] for b in selected[-4:])[-800:], 'provider':provider}
                # Timestamp/source check and no-mid-line cut: beat IDs map to full beat boundaries.
                c['valid']=first['beat_id']==ids[0] and last['beat_id']==ids[-1] and dur>=20 and dur<=60
                all_candidates.append(c)
            (out/f"episode_{ep['episode']:03d}_candidate_response.json").write_text(json.dumps(data,indent=2),encoding='utf-8')
        except Exception as e: failures.append({'episode':ep['episode'],'error':str(e)})
    # Separate judge pass; cold-viewer sees only clip text, not logline/continuity.
    judged=[]
    for idx,c in enumerate(all_candidates):
        ep=next(x for x in episodes if x['episode']==c['episode']); selected=[b for b in ep['beats'] if b['end']>c['start'] and b['start']<c['end']]
        clip='\n'.join(f"{b['label']}: {b['text']}" for b in selected)
        prompt=f'''Judge this promo candidate for a vertical microdrama ad. Return JSON only: {{"hook":0,"cliffhanger":0,"standalone":0,"emotional_appeal":0,"cold_viewer_characters":"...","cold_viewer_stakes":"...","pass":true,"reason":"..."}}. Score each numeric dimension 0-5. Cold-viewer test: infer characters and stakes using ONLY clip text; if unclear, score standalone low. Penalize spoilers, repetition, context dependence and a weak first 3 seconds. Be strict.\nCLIP TEXT:\n{clip}'''
        try:
            j,cached=_ask(prompt,provider,model,out/'cache'); call_count+=0 if cached else 1
            judge=JudgeResponse.model_validate(j)
            scores={k:max(0,min(5,float(getattr(judge,k)))) for k in ['hook','cliffhanger','standalone','emotional_appeal']}
            c.update(scores); c.update({'cold_viewer_characters':judge.cold_viewer_characters,'cold_viewer_stakes':judge.cold_viewer_stakes,'reason':judge.reason})
            c['score']=round(c['hook']*1.5+c['cliffhanger']*1.8+c['standalone']*1.5+c['emotional_appeal'],2)
            c['valid']=bool(c['valid'] and judge.passed); judged.append(c)
            (out/f"judge_{idx+1:04d}.json").write_text(json.dumps(j,indent=2),encoding='utf-8')
        except Exception as e: failures.append({'candidate':idx,'episode':c['episode'],'error':str(e)})
    eligible=[c for c in judged if c.get('valid')]
    ranked=rank_all(eligible,early_weight=.15)
    (out/'candidates_judged.json').write_text(json.dumps(judged,indent=2),encoding='utf-8')
    (out/'ranked_top15.json').write_text(json.dumps(ranked,indent=2),encoding='utf-8')
    summary={'provider':provider,'model':model,'episodes':len(episodes),'candidate_count':len(all_candidates),'judged_count':len(judged),'valid_count':len(eligible),'ranked_count':len(ranked),'model_calls':call_count,'runtime_seconds':round(time.time()-start_time,2),'failures':failures}
    (out/'run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary,ranked
