"""MeetingMate Pro's dependency-free text intelligence engine."""
import math
import re
from collections import Counter, defaultdict

STOP = set('a an the and or but if in on at to from of for with as by is are was were be been it this that we i you he she they them our their your my me us will would can could should have has had do does did not so just about into up out all some more very then than there here what when where who how why okay yeah yes no right its it s next'.split())
ACTION = re.compile(r'\b(?:need to|have to|should|must|will|follow up|send|share|schedule|prepare|review|finish|complete|deliver|create|update|assign|please|by friday|by monday|by tomorrow)\b', re.I)
DECISION = re.compile(r'\b(?:decided|agreed|approved|selected|chosen|confirmed|going with|settled on|decision is)\b', re.I)
RISK = re.compile(r'\b(?:blocked|blocker|delay|risk|issue|problem|concern|stuck|missed|late|cannot|can\x27t)\b', re.I)
POSITIVE = set('good great excellent excited solved improved success completed clear happy confident fixed achieved'.split())
NEGATIVE = set('bad difficult concerned frustrated delay blocked issue failure problem worried risk stuck'.split())


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text.strip()) if s.strip()]


def tokenize(text):
    return [w for w in re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower()) if w not in STOP and len(w)>2]


def analyze(text):
    ss = sentences(text)
    counts = Counter(tokenize(text))
    scored = [(sum(counts[t] for t in tokenize(s))/max(len(tokenize(s)),1) + (.5 if ACTION.search(s) else 0), i, s) for i,s in enumerate(ss)]
    top = sorted(sorted(scored, reverse=True)[:min(4,len(scored))], key=lambda v:v[1])
    return {'summary':' '.join(x[2] for x in top), 'actions':[s for s in ss if ACTION.search(s)][:20], 'decisions':[s for s in ss if DECISION.search(s)][:15], 'risks':[s for s in ss if RISK.search(s)][:15], 'keywords':counts.most_common(12)}


def search_evidence(question, text, utterances=None, limit=4):
    """Transparent TF-IDF cosine retrieval; no generative claims."""
    parts = []
    if utterances:
        for u in utterances:
            for s in sentences(u.get('transcript','')):
                parts.append({'text':s,'start':u.get('start'), 'speaker':u.get('speaker')})
    else:
        parts = [{'text':s,'start':None,'speaker':None} for s in sentences(text)]
    query = tokenize(question)
    if not query or not parts: return []
    docs = [Counter(tokenize(p['text'])) for p in parts]
    df = Counter(t for d in docs for t in d)
    n = len(docs)
    idf = {t: math.log((n+1)/(freq+1))+1 for t,freq in df.items()}
    q = Counter(query)
    def norm(v): return math.sqrt(sum(x*x for x in v.values()))
    qv = {t:f*idf.get(t,0) for t,f in q.items()}
    qn = norm(qv)
    scores=[]
    for idx, d in enumerate(docs):
        dv={t:f*idf[t] for t,f in d.items()}
        score=sum(qv.get(t,0)*v for t,v in dv.items())/(qn*norm(dv)) if qn and norm(dv) else 0
        if score>0: scores.append((score,idx))
    scores.sort(reverse=True)
    return [dict(parts[i], score=round(sc,3)) for sc,i in scores[:limit]]


def speaker_metrics(utterances):
    durations=defaultdict(float)
    turns=Counter()
    for u in utterances:
        who=u.get('speaker')
        label=f'Speaker {who+1}' if isinstance(who,int) else 'Unknown'
        durations[label]+=max(0,float(u.get('end',0))-float(u.get('start',0)))
        turns[label]+=1
    return [{'Speaker':k,'Speaking seconds':round(v,1),'Turns':turns[k]} for k,v in sorted(durations.items())]


def tone_signals(text):
    """Simple lexical signals, not a learned or clinical sentiment model."""
    c=Counter(tokenize(text))
    return {'Positive words':sum(c[t] for t in POSITIVE), 'Concern words':sum(c[t] for t in NEGATIVE)}


def format_time(seconds):
    if seconds is None: return ''
    sec=int(seconds)
    return f'{sec//60:02}:{sec%60:02}'
