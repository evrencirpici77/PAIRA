from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='v20.8-global-event-participants-2026-09-12'
if marker in s:
    print('Already patched')
    raise SystemExit(0)

# The previous implementation subscribed to a nested collection path that can differ
# between legacy event ids. Use a collectionGroup listener and filter by eventId,
# while writes also persist canonical eventId/accountId fields.
old="""function subscribeEventParticipants(eventId, onRows, onError){
    const ref = collection(db, 'eventAttendance', safeEventAttendanceId(eventId,80), 'couples');
    return onSnapshot(ref,(snap)=>{
      const rows = snap.docs
        .map(d=>({...d.data(), _firebaseId:d.id}))
        .filter(r=>r.joined === true)
        .sort((a,b)=>String(a.coupleName || '').localeCompare(String(b.coupleName || ''),'tr'));
      onRows(rows);
    },(err)=>{
      if(onError) onError(err);
    });
  }"""
new="""function subscribeEventParticipants(eventId, onRows, onError){
    const canonicalEventId = safeEventAttendanceId(eventId,80);
    const ref = collectionGroup(db, 'couples');
    return onSnapshot(ref,(snap)=>{
      const rows = snap.docs
        .map(d=>({...d.data(), _firebaseId:d.id, _parentEventId:(d.ref.parent.parent && d.ref.parent.parent.id)||''}))
        .filter(r=>r.joined === true && (safeEventAttendanceId(r.eventId||'',80) === canonicalEventId || r._parentEventId === canonicalEventId))
        .sort((a,b)=>String(a.coupleName || '').localeCompare(String(b.coupleName || ''),'tr'));
      const unique=[]; const seen=new Set();
      rows.forEach(r=>{ const k=String(r.accountId||r.inviteCode||r._firebaseId||'').toUpperCase(); if(!seen.has(k)){seen.add(k);unique.push(r);} });
      onRows(unique);
    },(err)=>{ if(onError) onError(err); });
  }"""
if old not in s:
    raise SystemExit('participant subscription block not found')
s=s.replace(old,new,1)

# Ensure Firestore modular import includes collectionGroup.
s=s.replace('collection, doc, setDoc, getDoc, onSnapshot', 'collection, collectionGroup, doc, setDoc, getDoc, onSnapshot')

# Enrich every attendance write with canonical ids, so all devices can discover it.
needle="""await setDoc(ref, { ...payload, updatedAt: serverTimestamp() }, {merge:true});"""
repl="""await setDoc(ref, { ...payload, eventId:safeEventAttendanceId(eventId,80), accountId:safeEventAttendanceId(accountId,120), updatedAt: serverTimestamp() }, {merge:true});"""
if needle not in s:
    raise SystemExit('setEventAttendance write not found')
s=s.replace(needle,repl,1)

# Stamp build marker without relying on exact previous version.
m=re.search(r'<meta name="paira-build" content="([^"]+)">',s)
if m:
    s=s[:m.start()]+f'<meta name="paira-build" content="{marker}">'+s[m.end():]
else:
    s=s.replace('</head>',f'<meta name="paira-build" content="{marker}">\n</head>',1)

p.write_text(s,encoding='utf-8')
print('Patched v20.8 global participants')
