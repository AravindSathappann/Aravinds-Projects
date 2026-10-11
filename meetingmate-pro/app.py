"""MeetingMate Pro — Deepgram-powered meeting intelligence dashboard."""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from engine import analyze, format_time, search_evidence, speaker_metrics, tone_signals

st.set_page_config(page_title='MeetingMate Pro', page_icon='🎙️', layout='wide')
DB = Path(__file__).with_name('meetingmate_history.db')
MIME={'wav':'audio/wav','mp3':'audio/mpeg','m4a':'audio/mp4','mp4':'audio/mp4','ogg':'audio/ogg','webm':'audio/webm','flac':'audio/flac'}


def transcribe(audio_bytes, filename, key):
    ext=filename.rsplit('.',1)[-1].lower()
    try:
        r=requests.post('https://api.deepgram.com/v1/listen',
            headers={'Authorization':f'Token {key}','Content-Type':MIME.get(ext,'application/octet-stream')},
            params={'model':'nova-3','smart_format':'true','punctuate':'true','utterances':'true','diarize':'true','language':'en'},
            data=audio_bytes,timeout=240)
        r.raise_for_status()
        payload=r.json()
        transcript=payload['results']['channels'][0]['alternatives'][0]['transcript']
        utterances=payload.get('results',{}).get('utterances',[])
        return {'transcript':transcript,'utterances':utterances,'duration':payload.get('metadata',{}).get('duration',0),'demo':False,'created':datetime.now().isoformat(timespec='seconds')}
    except requests.HTTPError as exc:
        raise ValueError(f'Deepgram returned HTTP {r.status_code}: {r.text[:250]}') from exc
    except (requests.RequestException,KeyError,IndexError,ValueError) as exc:
        raise ValueError(f'Could not transcribe audio: {exc}') from exc


def demo_report():
    turns=[
        (0,9,0,'Welcome to the product meeting. Our goal is to reduce onboarding friction and improve customer activation.'),
        (10,22,1,'The dashboard is complete, but we have a risk with the signup experiment. The testing team is blocked by missing analytics events.'),
        (23,34,0,'We decided to ship the smaller experiment first. Sam will send the missing event specification by Friday.'),
        (35,47,2,'I will update the dashboard and review the customer feedback before Monday. We should schedule a follow-up next week.'),
        (48,56,1,'Agreed. The team confirmed the new experiment for next Wednesday. Great progress overall.')]
    utterances=[{'start':a,'end':b,'speaker':c,'transcript':d} for a,b,c,d in turns]
    return {'transcript':' '.join(t[3] for t in turns),'utterances':utterances,'duration':56,'demo':True,'created':datetime.now().isoformat(timespec='seconds')}


def conn():
    db=sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS meetings (id INTEGER PRIMARY KEY, title TEXT NOT NULL, created TEXT NOT NULL, report TEXT NOT NULL)')
    return db


def save_report(title, report):
    with conn() as db:
        db.execute('INSERT INTO meetings (title,created,report) VALUES (?,?,?)',(title,report['created'],json.dumps(report)))


st.title('🎙️ MeetingMate Pro')
st.caption('Deepgram Nova-3 transcription · speaker analytics · transcript-grounded search · action tracking')
with st.sidebar:
    st.header('Connect Deepgram')
    key=st.text_input('API key',os.getenv('DEEPGRAM_API_KEY',''),type='password')
    st.link_button('Get a Deepgram key','https://console.deepgram.com/')
    st.caption('Only recordings you choose to analyze are uploaded to Deepgram. Local history is optional and off by default.')
    keep=st.checkbox('Save analyzed meetings on this computer',value=False)
    st.divider()
    st.subheader('Meeting history')
    with conn() as db:
        old=db.execute('SELECT id,title,created FROM meetings ORDER BY id DESC LIMIT 40').fetchall()
    if not old: st.caption('No saved meetings yet.')
    for ident,title,created in old:
        if st.button(f'📁 {title} · {created[:10]}',key=f'open_{ident}',use_container_width=True):
            with conn() as db:
                payload=db.execute('SELECT report FROM meetings WHERE id=?',(ident,)).fetchone()
            if payload: st.session_state.report=json.loads(payload[0]);st.rerun()
    if old and st.button('Delete all local history',use_container_width=True):
        with conn() as db: db.execute('DELETE FROM meetings')
        st.rerun()

upload_tab,mic_tab=st.tabs(['📂 Upload recording','🎤 Record in browser'])
with upload_tab:
    uploaded=st.file_uploader('Choose audio',type=list(MIME),help='MP3, WAV, M4A, MP4, OGG, WEBM, FLAC')
with mic_tab:
    mic=st.audio_input('Record audio, then stop recording to analyze',help='Recording happens in your browser. This is not real-time streaming.')
name=st.text_input('Meeting name (optional)','Team sync')
a,b=st.columns(2)
with a: run=st.button('✨ Analyze with Deepgram',type='primary',use_container_width=True)
with b: demo=st.button('▶ Instant demo — no key needed',use_container_width=True)
if demo:
    st.session_state.report=demo_report()
    st.rerun()
if run:
    source=uploaded or mic
    if source is None: st.warning('Upload a file or record audio first.')
    elif not key.strip(): st.error('Enter your Deepgram API key, or try the demo.')
    else:
        try:
            with st.spinner('Deepgram is transcribing your recording…'):
                report=transcribe(source.getvalue(),source.name,key.strip())
            if not report['transcript'].strip(): st.warning('No speech detected. Try clearer audio.')
            else:
                st.session_state.report=report
                if keep: save_report(name.strip() or 'Untitled',report)
                st.rerun()
        except ValueError as exc: st.error(str(exc))

if 'report' not in st.session_state:
    st.info('Try the demo now, or enter your Deepgram key and analyze a recording.')
    st.stop()

report=st.session_state.report
text=report['transcript']; utterances=report.get('utterances',[]); insight=analyze(text)
st.divider()
st.subheader('Intelligence dashboard' + (' · SAMPLE DATA' if report.get('demo') else ''))
if report.get('demo'): st.info('This is a built-in sample. No audio was sent to Deepgram.')
c1,c2,c3,c4=st.columns(4)
c1.metric('Words',len(text.split()))
c2.metric('Speakers',len([m for m in speaker_metrics(utterances) if m['Speaker']!='Unknown']))
c3.metric('Action candidates',len(insight['actions']))
c4.metric('Duration',f"{float(report.get('duration') or 0)/60:.1f} min")
summary_tab,ask_tab,speakers_tab,full_tab=st.tabs(['📋 Briefing','🔎 Ask the transcript','🗣️ Speaker analytics','📝 Transcript & exports'])
with summary_tab:
    st.subheader('Extractive meeting highlights')
    st.write(insight['summary'] or 'Not enough speech to summarize.')
    st.caption('Highlights are copied from the transcript. They are not LLM-written summaries.')
    x,y=st.columns(2)
    with x:
        st.markdown('#### Potential action items')
        if insight['actions']:
            for i,s in enumerate(insight['actions']): st.checkbox(s,key=f"act_{report['created']}_{i}")
        else: st.write('No action-language patterns detected.')
        st.markdown('#### Decision signals')
        for s in insight['decisions']: st.write('• '+s)
        if not insight['decisions']: st.caption('No obvious decision phrases.')
    with y:
        st.markdown('#### Risks / blockers')
        for s in insight['risks']: st.write('• '+s)
        if not insight['risks']: st.caption('No obvious risk phrases.')
        st.markdown('#### Frequent terms')
        st.write(', '.join(f'{t} ({n})' for t,n in insight['keywords']) or 'None')
        st.markdown('#### Tone word signals')
        st.bar_chart(tone_signals(text))
        st.caption('Keyword-based signals only; not a trained sentiment classifier.')
with ask_tab:
    st.subheader('Evidence-backed transcript search')
    st.write('Ask something specific. MeetingMate retrieves relevant spoken passages with timestamps where available; it does not invent an answer.')
    question=st.text_input('Your question',placeholder='What was decided about the experiment?')
    if question.strip():
        hits=search_evidence(question,text,utterances)
        if not hits: st.warning('No relevant transcript passage was found. Try different keywords.')
        for hit in hits:
            who=hit['speaker']; label=f'Speaker {who+1}' if isinstance(who,int) else 'Transcript'
            st.markdown(f"**{label} · {format_time(hit['start']) or 'no timestamp'}**")
            st.write(hit['text'])
            st.caption(f"Retrieval similarity: {hit['score']:.2f} (not answer confidence)")
with speakers_tab:
    data=speaker_metrics(utterances)
    if not data: st.info('No speaker timing available for this recording.')
    else:
        st.bar_chart({r['Speaker']:r['Speaking seconds'] for r in data},x_label='Speaker',y_label='Seconds speaking')
        st.dataframe(data,use_container_width=True,hide_index=True)
        st.caption('Speaker labels are anonymous. Speaking duration is estimated from Deepgram utterance boundaries.')
with full_tab:
    st.text_area('Full transcript',text,height=260)
    st.markdown('#### Timestamped turns')
    for u in utterances:
        who=u.get('speaker'); label=f'Speaker {who+1}' if isinstance(who,int) else 'Unknown'
        st.write(f"[{format_time(u.get('start'))}] {label}: {u.get('transcript','')}")
    st.download_button('Download transcript (.txt)',text,'meeting_transcript.txt','text/plain')
    st.download_button('Download structured data (.json)',json.dumps(report,indent=2),'meeting_data.json','application/json')
    markdown='# MeetingMate Pro report\n\n## Highlights\n'+insight['summary']+'\n\n## Action candidates\n'+'\n'.join('- '+s for s in insight['actions'])+'\n\n## Decisions\n'+'\n'.join('- '+s for s in insight['decisions'])+'\n\n## Risks\n'+'\n'.join('- '+s for s in insight['risks'])+'\n\n## Transcript\n'+text
    st.download_button('Download report (.md)',markdown,'meeting_report.md','text/markdown',type='primary')
