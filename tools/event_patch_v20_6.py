from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
s = s.replace('v20.5-event-attendance-all-devices-2026-09-12', 'v20.6-event-attendance-shared-account-2026-09-12')

old_id = """function sharedProfileAccountId(){
  const p = getDevicePartnerIdentity();
  // Ortak profil için iki telefonda da kesin aynı olan anahtar davet kodudur.
  // Eski sürümlerde memberId öne alındığı için aynı çift iki farklı profile düşebiliyordu.
  return String((p && (p.inviteCode || p.memberId)) || '').trim().toUpperCase();
}"""
new_id = """function sharedProfileAccountId(){
  const p = getDevicePartnerIdentity();
  const direct = String((p && (p.inviteCode || p.memberId)) || '').trim().toUpperCase();
  if(direct) return direct;
  const coupleName = String((state.profile && state.profile.name) || currentChatIdentity().coupleName || '').trim();
  if(!coupleName) return '';
  const folded = coupleName
    .toLocaleUpperCase('tr-TR')
    .normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')
    .replace(/[^A-Z0-9]+/g,'_')
    .replace(/^_+|_+$/g,'')
    .slice(0,90);
  return folded ? `COUPLE_${folded}` : '';
}"""
if old_id not in s:
    raise SystemExit('sharedProfileAccountId block not found')
s = s.replace(old_id, new_id, 1)

pat = re.compile(r"if\(accountId\)\{\s*const existing = await api\.getEventAttendance\(eventId, accountId\);\s*applyEventAttendance\(eventId, existing\);\s*eventAttendanceUnsub = api\.subscribeEventAttendance\(eventId, accountId, \(row\)=>\{\s*applyEventAttendance\(eventId, row\);\s*\}, \(err\)=>\{\s*console\.warn\('PAIRA event attendance sync', err\);\s*\}\);\s*\}")
m = pat.search(s)
if not m:
    raise SystemExit('attendance sync block not found')
repl = """if(accountId){
      let existing = await api.getEventAttendance(eventId, accountId);
      if((!existing || existing.joined !== true) && state.joinedEvents && state.joinedEvents[eventId]){
        const me = currentChatIdentity();
        await api.setEventAttendance(eventId, accountId, {
          joined:true,
          inviteCode:accountId,
          coupleName:me.coupleName,
          partnerName:me.partnerName,
          deviceId:getDeviceId()
        });
        existing = await api.getEventAttendance(eventId, accountId);
      }
      applyEventAttendance(eventId, existing);
      eventAttendanceUnsub = api.subscribeEventAttendance(eventId, accountId, (row)=>{
        applyEventAttendance(eventId, row);
      }, (err)=>{
        console.warn('PAIRA event attendance sync', err);
      });
    }"""
s = s[:m.start()] + repl + s[m.end():]
p.write_text(s, encoding='utf-8')
print('Patched v20.6')
