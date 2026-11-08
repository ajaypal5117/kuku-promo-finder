import re, itertools
try:
    from .parser import fmt_time
except ImportError:
    from parser import fmt_time
HOOK=re.compile(r"\b(slaps?|betray|marry|marrying|dead|murder|poison|secret|duke|traitor|who|stop|no!|never|you lied|you're|you are|can't|cannot|help|blood|kill|caught|kiss|pregnant|heir|arrest|confess|confession|reveal|shocking|how dare|what have you done|you'll pay)\b",re.I)
CLIFF=re.compile(r"\b(who\??|what\??|why\??|how\??|unless|if you|before it's too late|you have no idea|not yet|wait|stop|don't|do not|i know what|the truth|secret|poison|kill|murder|betray|exposed|caught|reveal|cliffhanger)\b",re.I)
EMOTION=re.compile(r"\(([^)]*(?:angry|furious|terrified|shocked|desperate|devastated|seething|urgent|alarmed|whispering|pleading|cold|dangerous|incredulous|gasping)[^)]*)\)",re.I)

def beat_score(b):
    t=b['text']; s=0
    if b['kind']=='dialogue': s+=2
    s+=min(4,len(HOOK.findall(t))*1.4)
    s+=min(2,len(EMOTION.findall(b['label']))*.8)
    if re.search(r"(?i)\b(cut to black|cliffhanger|scream|gasp|slap|crash|gunshot|thunder)\b",t): s+=2
    if '?' in t or '!' in t: s+=.8
    return s

def candidate_windows(ep):
    beats=sorted(ep['beats'],key=lambda b:(b['start'],b['end']))
    out=[]
    for i,a in enumerate(beats):
        # Window starts at a beat boundary and ends at a later beat boundary; durations 20-60 sec.
        for j in range(i,min(len(beats),i+30)):
            b=beats[j]; dur=b['end']-a['start']
            if dur<20: continue
            if dur>60: break
            # Do not cut through a dialogue beat even when camera/action beats overlap.
            if any(x['kind']=='dialogue' and ((x['start'] < a['start'] < x['end']) or (x['start'] < b['end'] < x['end'])) for x in beats):
                continue
            clip=[x for x in beats if x['end']>a['start'] and x['start']<b['end']]
            if not clip: continue
            first=[x for x in clip if x['start']<a['start']+3.0]
            last=clip[-1]
            hook_text=' '.join(x['text'] for x in first)
            ending_text=' '.join(x['text'] for x in clip[-3:])
            hs=beat_score(a)+min(3,len(HOOK.findall(hook_text)))
            cs=min(5,len(CLIFF.findall(ending_text))) + (1.5 if '?' in ending_text or '!' in ending_text else 0)
            context=min(3,len(set(re.findall(r"\b[A-Z][a-z]{2,}\b",' '.join(x['text'] for x in clip))))/3)
            target= max(0,3-abs(dur-36)/8)
            # Penalize ending on generic camera/action without narrative consequence.
            if last['kind'] in ('CAMERA','ACTION') and not CLIFF.search(last['text']): cs*=.65
            score=hs*1.5+cs*1.8+context+target
            if hs<1.5: continue
            out.append({'episode':ep['episode'],'start':a['start'],'end':b['end'],'duration':round(dur,2),'start_beat':a['beat_id'],'end_beat':b['beat_id'],'hook_score':round(hs,2),'cliffhanger_score':round(cs,2),'score':round(score,2),'hook':hook_text[:350],'cliffhanger':ending_text[-500:],'segments':[{'episode':ep['episode'],'start':fmt_time(a['start']),'end':fmt_time(b['end'])}],'why':'Heuristic candidate: strong opening signal and an ending with unresolved/question/threat cues; editor review required.'})
    # Deduplicate near-identical overlapping windows, keep strongest candidates.
    out.sort(key=lambda x:x['score'],reverse=True); kept=[]
    for c in out:
        if any(c['start']<k['end'] and c['end']>k['start'] and min(c['end'],k['end'])-max(c['start'],k['start']) > .75*min(c['duration'],k['duration']) for k in kept): continue
        kept.append(c)
        if len(kept)>=12: break
    return kept

def rank_all(candidates, early_weight=.15):
    ranked=[]
    for c in candidates:
        x=dict(c); x['rank_score']=round(x['score']+early_weight*max(0,50-x['episode'])/50,3); ranked.append(x)
    ranked.sort(key=lambda x:x['rank_score'],reverse=True)
    # Greedy diversity: cap 2 picks per episode and avoid highly similar time windows.
    chosen=[]; counts={}
    for c in ranked:
        ep=c['episode']
        if counts.get(ep,0)>=2: continue
        if any(x['episode']==ep and abs(x['start']-c['start'])<45 for x in chosen): continue
        chosen.append(c); counts[ep]=counts.get(ep,0)+1
        if len(chosen)==15: break
    for i,c in enumerate(chosen,1): c['rank']=i
    return chosen
