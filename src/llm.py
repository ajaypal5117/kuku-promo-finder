"""Optional model adapter. Gemini via REST; Groq/OpenAI-compatible and Anthropic adapters are swappable."""
import os,json,time,hashlib
from pathlib import Path

def call_model(prompt, provider='gemini', model=None):
    if provider=='heuristic': raise ValueError('Heuristic mode does not call a model')
    if provider=='gemini':
        from google import genai
        key=os.getenv('GEMINI_API_KEY')
        if not key: raise RuntimeError('Set GEMINI_API_KEY')
        client=genai.Client(api_key=key); m=model or os.getenv('GEMINI_MODEL')
        if not m: raise RuntimeError('Set GEMINI_MODEL or pass --model')
        return client.models.generate_content(model=m,contents=prompt,config={'response_mime_type':'application/json'}).text
    if provider in ('groq','openai'):
        from openai import OpenAI
        key=os.getenv('GROQ_API_KEY' if provider=='groq' else 'OPENAI_API_KEY')
        if not key: raise RuntimeError(f'Set {provider.upper()}_API_KEY')
        base=os.getenv('OPENAI_BASE_URL','https://api.groq.com/openai/v1' if provider=='groq' else None)
        client=OpenAI(api_key=key,base_url=base)
        m=model or os.getenv('GROQ_MODEL','llama-3.3-70b-versatile')
        return client.chat.completions.create(model=m,messages=[{'role':'user','content':prompt}],response_format={'type':'json_object'}).choices[0].message.content
    if provider=='anthropic':
        import anthropic
        key=os.getenv('ANTHROPIC_API_KEY')
        if not key: raise RuntimeError('Set ANTHROPIC_API_KEY')
        c=anthropic.Anthropic(api_key=key); m=model or os.getenv('ANTHROPIC_MODEL','claude-3-5-haiku-latest')
        r=c.messages.create(model=m,max_tokens=5000,messages=[{'role':'user','content':prompt}]); return ''.join(x.text for x in r.content if x.type=='text')
    raise ValueError('provider must be gemini, groq, openai, anthropic or heuristic')

def json_from_response(s):
    s=s.strip();
    if s.startswith('```'): s=s.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(s)
