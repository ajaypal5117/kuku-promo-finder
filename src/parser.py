import re
from dataclasses import dataclass, asdict
from pathlib import Path

TIME = r"\d{2}:\d{2}(?:\.\d+)?"
BLOCK_RE = re.compile(r"(?m)^\*\*(?P<label>.+?)\*\*\s*\nStart:\s*\((?P<start>"+TIME+r")\)\s*\|\s*End:\s*\((?P<end>"+TIME+r")\)\s*\n(?P<body>.*?)(?=\n\*\*[^\n]+\*\*\s*\nStart:|\nSCENE\s+\d+|\Z)", re.S)
SCENE_RE = re.compile(r"(?m)^SCENE\s+(\d+)")

def to_seconds(t):
    m=re.fullmatch(r"(\d{2}):(\d{2})(?:\.(\d+))?",t.strip())
    if not m: raise ValueError(f"Invalid timestamp: {t}")
    return int(m.group(1))*60+int(m.group(2))+float('0.'+(m.group(3) or '0'))

def fmt_time(sec):
    sec=max(0,sec); mm=int(sec//60); ss=sec-mm*60
    return f"{mm:02d}:{ss:05.2f}"

def parse_script(text, filename=''):
    def field(name):
        m=re.search(rf"(?m)^{re.escape(name)}:\s*(.*)$",text)
        return m.group(1).strip() if m else ''
    epm=re.search(r"(?i)EPISODE NUMBER:\s*(?:Episode\s*)?(\d+)",text)
    episode=int(epm.group(1)) if epm else None
    beats=[]; warnings=[]
    for i,m in enumerate(BLOCK_RE.finditer(text),1):
        try:
            start,end=to_seconds(m.group('start')),to_seconds(m.group('end'))
            if end < start: warnings.append(f"block {i}: end before start"); continue
            label=m.group('label').strip(); body=m.group('body').strip()
            beats.append({'beat_id':f"E{episode or 0:03d}-B{i:03d}",'label':label,'start':start,'end':end,'text':body,'kind': 'dialogue' if not any(x in label.upper() for x in ['CAMERA','ACTION','SOUND FX']) else label.split('(')[0].strip().upper()})
        except Exception as e: warnings.append(f"block {i}: {e}")
    if not beats: warnings.append('No timed blocks parsed')
    # Check for timestamp-like blocks not captured, useful for format drift diagnostics.
    starts=len(re.findall(r"(?m)^Start:\s*\(",text))
    if starts != len(beats): warnings.append(f"found {starts} Start markers but parsed {len(beats)} blocks")
    return {'episode':episode,'filename':filename,'logline':field('EPISODE LOGLINE'),'continuity':field('CONTINUITY NOTES'),'beats':beats,'warnings':warnings,'duration':max((b['end'] for b in beats),default=0),'raw_text':text}

def parse_path(path): return parse_script(Path(path).read_text(encoding='utf-8',errors='replace'),Path(path).name)
