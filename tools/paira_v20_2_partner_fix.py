from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")
orig = s

s, n = re.subn(
    r'<meta name="paira-build" content="[^"]+">',
    '<meta name="paira-build" content="v20.2-partner-save-verify">',
    s,
    count=1,
)
if n != 1:
    raise SystemExit(f"build meta patch count={n}")

firebase_block = r'''  async function listPartnerBusinesses(){
    const snap=await getDocs(collection(db,"partnerBusinesses"));
    return snap.docs
      .map(d=>({_firebaseId:d.id,...d.data()}))
      .sort((a,b)=>String(b.updatedAt||"").localeCompare(String(a.updatedAt||"")));
  }
  function subscribePartnerBusinesses(callback){
    const ref=collection(db,"partnerBusinesses");
    return onSnapshot(
      ref,
      snap=>{
        const rows=snap.docs
          .map(d=>({_firebaseId:d.id,...d.data()}))
          .sort((a,b)=>String(b.updatedAt||"").localeCompare(String(a.updatedAt||"")));
        callback(rows,null);
      },
      err=>{
        console.warn("PAIRA partnerBusinesses snapshot",err);
        callback([],err);
      }
    );
  }
  async function savePartnerBusiness(row){
    if(!auth.currentUser) throw new Error("Yönetici girişi gerekli");
    const id=String(row?.id||row?._firebaseId||"").trim();
    if(!id) throw new Error("İşyeri kimliği eksik");
    const clean={...row,id,updatedAt:new Date().toISOString()};
    delete clean._firebaseId;
    const ref=doc(db,"partnerBusinesses",id);
    await setDoc(ref,clean,{merge:true});
    const verify=await getDoc(ref);
    if(!verify.exists()) throw new Error("İşyeri kayıt doğrulaması başarısız");
    return {_firebaseId:verify.id,...verify.data()};
  }
  async function deletePartnerBusiness(id){'''

s, n = re.subn(
    r'  function subscribePartnerBusinesses\(callback\)\{.*?\n  async function deletePartnerBusiness\(id\)\{',
    firebase_block,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"firebase partner block patch count={n}")

if "    listPartnerBusinesses,\n    subscribePartnerBusinesses," not in s:
    s, n = re.subn(
        r'(\n    removeInvitation,\n)(    subscribePartnerBusinesses,)',
        r'\1    listPartnerBusinesses,\n\2',
        s,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"api export patch count={n}")

save_ui = r'''async function savePartnerBusinessFromModal(){
  const name=(document.getElementById('pbName')?.value||'').trim(),
        offer=(document.getElementById('pbOffer')?.value||'').trim();
  if(!name){toast('İşyeri adını yazın');return;}
  if(!offer){toast('PAIRA avantajını yazın');return;}
  const existingId=document.getElementById('pbId')?.value||'',
        id=existingId||('partner_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,7));
  const row={
    id,
    name,
    category:document.getElementById('pbCategory')?.value||'other',
    offer,
    district:(document.getElementById('pbDistrict')?.value||'').trim(),
    city:(document.getElementById('pbCity')?.value||'').trim(),
    description:(document.getElementById('pbDescription')?.value||'').trim(),
    address:(document.getElementById('pbAddress')?.value||'').trim(),
    phone:(document.getElementById('pbPhone')?.value||'').trim(),
    social:(document.getElementById('pbSocial')?.value||'').trim(),
    mapUrl:(document.getElementById('pbMapUrl')?.value||'').trim(),
    photoUrl:(document.getElementById('pbPhotoUrl')?.value||'').trim(),
    active:!!document.getElementById('pbActive')?.checked,
    updatedAt:new Date().toISOString()
  };
  try{
    const api=window.PAIRA_FIREBASE_API || await waitForPairaFirebaseApi();
    if(!api?.savePartnerBusiness) throw new Error('Firebase hazır değil');
    const saved=await api.savePartnerBusiness(row);
    const savedId=String(saved?.id||saved?._firebaseId||id);
    const next=(partnerBusinessRows||[]).filter(x=>String(x?.id||x?._firebaseId||'')!==savedId);
    next.unshift(saved);
    partnerBusinessRows=next.sort((a,b)=>String(b.updatedAt||"").localeCompare(String(a.updatedAt||"")));
    renderPartnerAdmin();
    renderPartnerBusinesses();
    closeModal();
    toast(existingId?'İşyeri güncellendi ✓':'İşyeri yayınlandı ✓');
    setTimeout(()=>startPartnerBusinessRealtime(),250);
  }catch(err){
    console.warn('PAIRA partner save',err);
    toast('İşyeri kaydedilemedi');
  }
}
async function togglePartnerBusiness'''

s, n = re.subn(
    r'async function savePartnerBusinessFromModal\(\)\{.*?\n\}\nasync function togglePartnerBusiness',
    save_ui,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"save UI patch count={n}")

start_block = r'''async function startPartnerBusinessRealtime(){
  const list=document.getElementById('benefitList');
  const adminBox=document.getElementById('partnerAdminList');
  if(list&&!benefitSeedHtml)benefitSeedHtml=list.innerHTML;
  if(adminBox)adminBox.innerHTML='<div class="partner-empty">İşyeri listesi yükleniyor…</div>';
  try{
    const api=window.PAIRA_FIREBASE_API || await waitForPairaFirebaseApi();

    const initialRows=await api.listPartnerBusinesses();
    partnerBusinessRows=Array.isArray(initialRows)?initialRows:[];
    renderPartnerBusinesses();
    renderPartnerAdmin();

    if(partnerBusinessUnsub)partnerBusinessUnsub();
    partnerBusinessUnsub=api.subscribePartnerBusinesses((rows,err)=>{
      if(err){
        console.warn('PAIRA partner subscribe callback',err);
        if(adminBox)adminBox.innerHTML='<div class="partner-empty">İşyeri listesi şu anda alınamadı.<br><br><button class="out" onclick="startPartnerBusinessRealtime()">↻ Tekrar Dene</button></div>';
        return;
      }
      partnerBusinessRows=Array.isArray(rows)?rows:[];
      renderPartnerBusinesses();
      renderPartnerAdmin();
    });
  }catch(err){
    console.warn('PAIRA partner initial load',err);
    if(adminBox)adminBox.innerHTML='<div class="partner-empty">İşyeri listesi şu anda alınamadı.<br><br><button class="out" onclick="startPartnerBusinessRealtime()">↻ Tekrar Dene</button></div>';
  }
}
window.openPartnerBusinessForm'''

s, n = re.subn(
    r'async function startPartnerBusinessRealtime\(\)\{.*?\n\}\nwindow\.openPartnerBusinessForm',
    start_block,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"start realtime patch count={n}")

if s == orig:
    raise SystemExit("no changes made")

for required in [
    'v20.2-partner-save-verify',
    'async function listPartnerBusinesses()',
    'const verify=await getDoc(ref);',
    'const saved=await api.savePartnerBusiness(row);',
    'const initialRows=await api.listPartnerBusinesses();',
    'listPartnerBusinesses,',
]:
    if required not in s:
        raise SystemExit("missing required marker: "+required)

p.write_text(s, encoding="utf-8")
print("PAIRA v20.2 partner save/read verification patch applied")
