from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")
original = text

old_meta = '<meta name="paira-build" content="v19.7-benefits-preview">'
if old_meta not in text:
    raise SystemExit("Expected v19.7 build marker not found")
text = text.replace(old_meta, '<meta name="paira-build" content="v19.8-partner-businesses-qr">', 1)

css = r'''
/* PAIRA v19.8 - partner businesses + member QR */
.partner-admin-toolbar{display:flex;gap:9px;margin:10px 0 14px}
.partner-admin-toolbar .gold{flex:1}
.partner-admin-row{border:1px solid #76582f;border-radius:16px;background:linear-gradient(145deg,#17110d,#090705);padding:13px;margin:10px 0}
.partner-admin-row .partner-title{color:#f1d49a;font-size:17px;font-weight:800}
.partner-admin-row .partner-meta{color:#bba98d;font-size:12px;line-height:1.45;margin-top:4px}
.partner-admin-row .partner-offer{display:inline-block;margin-top:8px;padding:6px 9px;border-radius:999px;border:1px solid #9b7138;background:#160f09;color:#f1cc83;font-weight:800}
.partner-admin-actions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:10px}
.partner-photo{width:100%;max-height:170px;object-fit:cover;border-radius:14px;border:1px solid #6d512e;margin-top:10px}
.qr-shell{background:#fff;border-radius:18px;padding:14px;width:230px;min-height:230px;margin:16px auto;display:grid;place-items:center}
.qr-shell img,.qr-shell canvas{max-width:202px!important;max-height:202px!important}
.qr-member{text-align:center;color:#f3dfb5;font-size:20px;font-weight:800}
.qr-couple{text-align:center;color:#bdae98;margin-top:4px}
.qr-expiry{text-align:center;color:#d8ae63;font-size:12px;margin-top:9px}
.verify-good{border:1px solid #2f7a50;background:#0a1b12;color:#bdf3cf;border-radius:18px;padding:18px;text-align:center}
.verify-bad{border:1px solid #8f3f3f;background:#1a0b0b;color:#ffc2bc;border-radius:18px;padding:18px;text-align:center}
.verify-icon{font-size:48px;margin-bottom:8px}
.partner-empty{border:1px dashed #71532f;border-radius:16px;padding:20px;text-align:center;color:#b9aa95}
'''
if "</style>" not in text:
    raise SystemExit("style close not found")
text = text.replace("</style>", css + "\n</style>", 1)

admin_event_btn = '''  <button class="listbtn" onclick="pairaRequireAdmin('adminEvents')"><b>📅 Etkinlik Yönetimi</b><br><span class="muted">Etkinlik ekle, düzenle ve duyuru yayınla</span></button>'''
if admin_event_btn not in text:
    raise SystemExit("admin event button anchor not found")
text = text.replace(admin_event_btn, admin_event_btn + '''
  <button class="listbtn" onclick="pairaRequireAdmin('adminPartners')"><b>🤝 Üye İşyeri Yönetimi</b><br><span class="muted">Anlaşmalı mekan ekle, indirimi düzenle veya pasife al</span></button>''', 1)

admin_members_anchor = '<section id="adminMembers" class="screen page">'
if admin_members_anchor not in text:
    raise SystemExit("adminMembers anchor not found")
partner_sections = r'''
<section id="adminPartners" class="screen page">
  <div class="head">
    <button class="back" onclick="show('adminPanel')">‹</button>
    <div><div class="logo" style="font-size:32px">PAIRA</div><div class="sub">ÜYE İŞYERLERİ</div></div>
    <button class="circle" onclick="openPartnerBusinessForm()">＋</button>
  </div>
  <div class="card">
    <h2 style="color:#efc97d;margin:0 0 6px">Anlaşmalı İşyerleri</h2>
    <div class="muted">Buradan eklediğiniz aktif işyerleri PAIRA Ayrıcalıkları bölümünde tüm üyelere görünür.</div>
  </div>
  <div class="partner-admin-toolbar"><button class="gold" onclick="openPartnerBusinessForm()">＋ Yeni İşyeri Ekle</button></div>
  <div id="partnerAdminList"><div class="partner-empty">İşyeri listesi yükleniyor…</div></div>
</section>

<section id="memberVerify" class="screen page">
  <div class="head">
    <div style="width:44px"></div>
    <div><div class="logo" style="font-size:32px">PAIRA</div><div class="sub">ÜYELİK DOĞRULAMA</div></div>
    <div style="width:44px"></div>
  </div>
  <div id="memberVerifyBox" class="card" style="text-align:center"><div class="muted">Üyelik kontrol ediliyor…</div></div>
</section>

'''
text = text.replace(admin_members_anchor, partner_sections + admin_members_anchor, 1)

plain_anchor = 'window.ensureEventsSeededForAdmin = ensureEventsSeededForAdmin;'
if plain_anchor not in text:
    raise SystemExit("plain script anchor not found")
plain_js = r'''
// ---- PAIRA v19.8 partner businesses + member QR ----
let partnerBusinessRows = [];
let partnerBusinessUnsub = null;
let benefitSeedHtml = '';
function benefitEsc(v){return String(v ?? '').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function partnerCatMeta(cat){const m={food:{icon:'🍽',label:'Cafe & Restoran'},shop:{icon:'🛍',label:'Mağaza'},care:{icon:'✦',label:'Bakım'},stay:{icon:'⌂',label:'Otel & Tatil'},other:{icon:'◆',label:'Diğer'}};return m[cat]||m.other;}
function activePartnerBusinesses(){return (partnerBusinessRows||[]).filter(x=>x&&x.active!==false);}
function renderPartnerBusinesses(){
  const list=document.getElementById('benefitList'); if(!list)return;
  const rows=activePartnerBusinesses();
  if(!rows.length){if(benefitSeedHtml)list.innerHTML=benefitSeedHtml;return;}
  list.innerHTML=rows.map(row=>{const meta=partnerCatMeta(row.category);const place=[row.district,row.city].filter(Boolean).join(' • ');const photo=row.photoUrl?`<img class="partner-photo" src="${benefitEsc(row.photoUrl)}" alt="${benefitEsc(row.name)}">`:'';return `<div class="benefit-card" data-benefit-cat="${benefitEsc(row.category||'other')}"><div class="benefit-card-top"><div class="benefit-icon">${meta.icon}</div><div class="benefit-card-copy"><h3>${benefitEsc(row.name||'PAIRA Üye İşyeri')}</h3><div class="benefit-place">${benefitEsc(place||meta.label)}</div></div><div class="benefit-discount">${benefitEsc(row.offer||'PAIRA')}</div></div>${photo}<div class="benefit-desc">${benefitEsc(row.description||'PAIRA üyelerine özel ayrıcalık.')}</div><div class="benefit-actions"><button class="benefit-small" onclick="openMemberBenefitQr('${benefitEsc(row.id||row._firebaseId||'')}')">Avantajı Kullan</button><button class="benefit-small" onclick="openPartnerMap('${benefitEsc(row.id||row._firebaseId||'')}')">Yol Tarifi</button></div></div>`;}).join('');
}
function renderPartnerAdmin(){
  const box=document.getElementById('partnerAdminList'); if(!box)return; const rows=partnerBusinessRows||[];
  if(!rows.length){box.innerHTML='<div class="partner-empty">Henüz gerçek bir üye işyeri eklenmedi.<br><br>“Yeni İşyeri Ekle” ile başlayabilirsiniz.</div>';return;}
  box.innerHTML=rows.map(row=>{const meta=partnerCatMeta(row.category);const place=[row.district,row.city].filter(Boolean).join(' • ');return `<div class="partner-admin-row"><div class="partner-title">${meta.icon} ${benefitEsc(row.name||'İşyeri')}</div><div class="partner-meta">${benefitEsc(meta.label)}${place?' • '+benefitEsc(place):''}<br>${row.active===false?'Pasif':'Aktif'}</div><div class="partner-offer">${benefitEsc(row.offer||'PAIRA Ayrıcalığı')}</div><div class="partner-admin-actions"><button class="editbtn" onclick="openPartnerBusinessForm('${benefitEsc(row.id||row._firebaseId||'')}')">Düzenle</button><button class="editbtn" onclick="togglePartnerBusiness('${benefitEsc(row.id||row._firebaseId||'')}')">${row.active===false?'Aktifleştir':'Pasife Al'}</button><button class="danger" onclick="removePartnerBusiness('${benefitEsc(row.id||row._firebaseId||'')}')">Sil</button></div></div>`;}).join('');
}
function openPartnerBusinessForm(id=''){
  const row=(partnerBusinessRows||[]).find(x=>(x.id||x._firebaseId)===id)||{};
  modal(`<h2 style="color:#e7bd72;margin-top:0">${id?'Üye İşyerini Düzenle':'Yeni Üye İşyeri'}</h2><input type="hidden" id="pbId" value="${benefitEsc(id)}"><label class="form-label">İşyeri adı</label><input class="form-field" id="pbName" value="${benefitEsc(row.name||'')}" placeholder="Örn. Moda Bistro"><label class="form-label">Kategori</label><select class="form-field" id="pbCategory">${[['food','Cafe & Restoran'],['shop','Mağaza'],['care','Bakım'],['stay','Otel & Tatil'],['other','Diğer']].map(([v,l])=>`<option value="${v}" ${String(row.category||'food')===v?'selected':''}>${l}</option>`).join('')}</select><label class="form-label">PAIRA avantajı</label><input class="form-field" id="pbOffer" value="${benefitEsc(row.offer||'')}" placeholder="Örn. %20 indirim"><div class="form-grid"><div><label class="form-label">Semt</label><input class="form-field" id="pbDistrict" value="${benefitEsc(row.district||'')}" placeholder="Moda"></div><div><label class="form-label">Şehir</label><input class="form-field" id="pbCity" value="${benefitEsc(row.city||'İstanbul')}" placeholder="İstanbul"></div></div><label class="form-label">Kısa açıklama</label><textarea class="form-field" id="pbDescription" placeholder="İndirim hangi ürün veya hizmetlerde geçerli?">${benefitEsc(row.description||'')}</textarea><label class="form-label">Adres</label><textarea class="form-field" id="pbAddress" placeholder="Açık adres">${benefitEsc(row.address||'')}</textarea><label class="form-label">Telefon</label><input class="form-field" id="pbPhone" value="${benefitEsc(row.phone||'')}" placeholder="05…"><label class="form-label">Instagram / web</label><input class="form-field" id="pbSocial" value="${benefitEsc(row.social||'')}" placeholder="@mekan veya web adresi"><label class="form-label">Google Maps bağlantısı</label><input class="form-field" id="pbMapUrl" value="${benefitEsc(row.mapUrl||'')}" placeholder="İsteğe bağlı"><label class="form-label">Fotoğraf bağlantısı</label><input class="form-field" id="pbPhotoUrl" value="${benefitEsc(row.photoUrl||'')}" placeholder="İsteğe bağlı"><label style="display:flex;align-items:center;gap:10px;margin:14px 2px;color:#ecd3a3"><input type="checkbox" id="pbActive" ${row.active===false?'':'checked'}> Aktif olarak yayınla</label><button class="gold" onclick="savePartnerBusinessFromModal()">Kaydet ve Yayınla</button><button class="out" style="margin-top:8px" onclick="closeModal()">Vazgeç</button>`);
}
async function savePartnerBusinessFromModal(){
  const name=(document.getElementById('pbName')?.value||'').trim(),offer=(document.getElementById('pbOffer')?.value||'').trim(); if(!name){toast('İşyeri adını yazın');return;} if(!offer){toast('PAIRA avantajını yazın');return;}
  const existingId=document.getElementById('pbId')?.value||'',id=existingId||('partner_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,7));
  const row={id,name,category:document.getElementById('pbCategory')?.value||'other',offer,district:(document.getElementById('pbDistrict')?.value||'').trim(),city:(document.getElementById('pbCity')?.value||'').trim(),description:(document.getElementById('pbDescription')?.value||'').trim(),address:(document.getElementById('pbAddress')?.value||'').trim(),phone:(document.getElementById('pbPhone')?.value||'').trim(),social:(document.getElementById('pbSocial')?.value||'').trim(),mapUrl:(document.getElementById('pbMapUrl')?.value||'').trim(),photoUrl:(document.getElementById('pbPhotoUrl')?.value||'').trim(),active:!!document.getElementById('pbActive')?.checked,updatedAt:new Date().toISOString()};
  try{if(!window.PAIRA_FIREBASE_API?.savePartnerBusiness)throw new Error('Firebase hazır değil');await window.PAIRA_FIREBASE_API.savePartnerBusiness(row);closeModal();toast(existingId?'İşyeri güncellendi ✓':'İşyeri yayınlandı ✓');}catch(err){console.warn('PAIRA partner save',err);toast('İşyeri kaydedilemedi');}
}
async function togglePartnerBusiness(id){const row=(partnerBusinessRows||[]).find(x=>(x.id||x._firebaseId)===id);if(!row)return;try{await window.PAIRA_FIREBASE_API.savePartnerBusiness({...row,id,active:row.active===false,updatedAt:new Date().toISOString()});toast(row.active===false?'İşyeri aktifleştirildi':'İşyeri pasife alındı');}catch(err){toast('Güncelleme başarısız');}}
async function removePartnerBusiness(id){const row=(partnerBusinessRows||[]).find(x=>(x.id||x._firebaseId)===id);if(!row)return;if(!confirm(`"${row.name}" işyerini silmek istiyor musunuz?`))return;try{await window.PAIRA_FIREBASE_API.deletePartnerBusiness(id);toast('İşyeri silindi');}catch(err){toast('Silme başarısız');}}
function openPartnerMap(id){const row=(partnerBusinessRows||[]).find(x=>(x.id||x._firebaseId)===id);if(!row){benefitLocationPreview();return;}let url=String(row.mapUrl||'').trim();if(!url&&row.address)url='https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(row.address);if(!url){toast('Bu işyerine henüz konum eklenmedi');return;}window.open(url,'_blank','noopener');}
function makeBenefitVerifyUrl(row){const identity=getDevicePartnerIdentity();if(!identity?.inviteCode)return '';const u=new URL(location.origin+location.pathname);u.searchParams.set('verify','paira');u.searchParams.set('invite',identity.inviteCode);u.searchParams.set('device',getDeviceId());u.searchParams.set('bucket',String(Math.floor(Date.now()/120000)));if(row?.id||row?._firebaseId)u.searchParams.set('business',row.id||row._firebaseId);if(row?.offer)u.searchParams.set('offer',row.offer);return u.toString();}
function openMemberBenefitQr(id=''){const row=(partnerBusinessRows||[]).find(x=>(x.id||x._firebaseId)===id)||{id:'preview',name:'PAIRA Üye İşyeri',offer:'Üye Ayrıcalığı'};const identity=getDevicePartnerIdentity();if(!identity?.inviteCode){modal(`<h2 style="color:#e7bd72;margin-top:0">PAIRA Üye Kartı</h2><div class="card"><b>Aktif üyelik bulunamadı.</b><p class="muted">QR doğrulaması yalnız davet koduyla aktifleşmiş PAIRA üyelerinde çalışır.</p></div><button class="gold" onclick="closeModal()">Tamam</button>`);return;}const verifyUrl=makeBenefitVerifyUrl(row);modal(`<h2 style="color:#e7bd72;margin-top:0">${benefitEsc(row.name||'PAIRA Ayrıcalığı')}</h2><div class="qr-member">${benefitEsc(identity.partnerName||'PAIRA Üyesi')}</div><div class="qr-couple">${benefitEsc(identity.coupleName||'')}</div><div class="qr-shell" id="pairaBenefitQr"></div><div style="text-align:center;color:#f0cf8e;font-weight:800">${benefitEsc(row.offer||'PAIRA Üye Ayrıcalığı')}</div><div class="qr-expiry">İşyeri bu kodu telefon kamerasıyla okutur.<br>Kod yaklaşık 2 dakikada bir yenilenir.</div><button class="out" style="margin-top:12px" onclick="closeModal()">Kapat</button>`);setTimeout(()=>{const box=document.getElementById('pairaBenefitQr');if(!box)return;box.innerHTML='';if(window.QRCode){new QRCode(box,{text:verifyUrl,width:202,height:202,correctLevel:QRCode.CorrectLevel.M});}else{box.innerHTML='<div style="color:#111;text-align:center;padding:20px">QR hazırlanamadı.<br>Sayfayı yenileyin.</div>';}},50);}
window.benefitPreview=function(){openMemberBenefitQr('');};
async function verifyMemberQrFromUrl(){const params=new URLSearchParams(location.search);if(params.get('verify')!=='paira')return false;show('memberVerify');const box=document.getElementById('memberVerifyBox'),invite=String(params.get('invite')||'').trim().toUpperCase(),device=String(params.get('device')||'').trim(),bucket=Number(params.get('bucket')||0),offer=String(params.get('offer')||'');if(!invite||!device||!bucket){box.innerHTML='<div class="verify-bad"><div class="verify-icon">✕</div><b>Geçersiz PAIRA kodu</b></div>';return true;}try{const rec=await window.PAIRA_FIREBASE_API.getInvitation(invite),devices=Array.isArray(rec?.partnerDevices)?rec.partnerDevices:[],partnerIndex=devices.indexOf(device),timeOk=Math.abs(Math.floor(Date.now()/120000)-bucket)<=1,active=!!rec&&rec.status==='active'&&devices.filter(Boolean).length>=2&&partnerIndex>=0&&timeOk;if(active){const partnerName=(rec.partnerNames||[])[partnerIndex]||'PAIRA Üyesi';box.innerHTML=`<div class="verify-good"><div class="verify-icon">✓</div><h2 style="margin:0 0 6px">Aktif PAIRA Üyesi</h2><div style="font-size:20px;font-weight:800">${benefitEsc(partnerName)}</div><div style="margin-top:4px">${benefitEsc(rec.name||'')}</div>${offer?`<div style="margin-top:14px;color:#f3d391;font-weight:800">${benefitEsc(offer)}</div>`:''}<div style="margin-top:12px;font-size:12px;opacity:.8">Kod canlı ve geçerli.</div></div>`;}else{box.innerHTML=`<div class="verify-bad"><div class="verify-icon">✕</div><h2 style="margin:0 0 6px">Kod geçerli değil</h2><div>${timeOk?'Üyelik veya cihaz doğrulanamadı.':'Bu QR kodun süresi dolmuş.'}</div></div>`;}}catch(err){console.warn('PAIRA QR verify',err);box.innerHTML='<div class="verify-bad"><div class="verify-icon">!</div><b>Doğrulama yapılamadı.</b><div style="margin-top:8px">İnternet bağlantısını kontrol edin.</div></div>';}return true;}
function startPartnerBusinessRealtime(){const list=document.getElementById('benefitList');if(list&&!benefitSeedHtml)benefitSeedHtml=list.innerHTML;try{if(partnerBusinessUnsub)partnerBusinessUnsub();partnerBusinessUnsub=window.PAIRA_FIREBASE_API.subscribePartnerBusinesses(rows=>{partnerBusinessRows=Array.isArray(rows)?rows:[];renderPartnerBusinesses();renderPartnerAdmin();});}catch(err){console.warn('PAIRA partner subscribe',err);renderPartnerAdmin();}}
window.openPartnerBusinessForm=openPartnerBusinessForm;window.savePartnerBusinessFromModal=savePartnerBusinessFromModal;window.togglePartnerBusiness=togglePartnerBusiness;window.removePartnerBusiness=removePartnerBusiness;window.renderPartnerAdmin=renderPartnerAdmin;window.openMemberBenefitQr=openMemberBenefitQr;window.openPartnerMap=openPartnerMap;
window.addEventListener('paira-firebase-ready',()=>{startPartnerBusinessRealtime();verifyMemberQrFromUrl();},{once:true});
// ---- /PAIRA v19.8 ----
'''
text = text.replace(plain_anchor, plain_js + "\n" + plain_anchor, 1)

firebase_comment = '<!-- PAIRA Firebase authentication + admin gate -->'
if firebase_comment not in text:
    raise SystemExit("firebase comment not found")
text = text.replace(firebase_comment, '<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>\n\n' + firebase_comment, 1)

api_anchor = '  window.PAIRA_FIREBASE_API = {'
if api_anchor not in text:
    raise SystemExit("firebase api object anchor not found")
firebase_functions = r'''
  function subscribePartnerBusinesses(callback){
    const q=query(collection(db,"partnerBusinesses"),orderBy("updatedAt","desc"));
    return onSnapshot(q,snap=>callback(snap.docs.map(d=>({_firebaseId:d.id,...d.data()}))),err=>{console.warn("PAIRA partnerBusinesses snapshot",err);callback([]);});
  }
  async function savePartnerBusiness(row){
    if(!auth.currentUser) throw new Error("Yönetici girişi gerekli");
    const id=String(row?.id||row?._firebaseId||"").trim(); if(!id)throw new Error("İşyeri kimliği eksik");
    const clean={...row,id,updatedAt:new Date().toISOString()}; delete clean._firebaseId;
    await setDoc(doc(db,"partnerBusinesses",id),clean,{merge:true}); return clean;
  }
  async function deletePartnerBusiness(id){
    if(!auth.currentUser) throw new Error("Yönetici girişi gerekli");
    const key=String(id||"").trim(); if(!key)return; await deleteDoc(doc(db,"partnerBusinesses",key));
  }
'''
text = text.replace(api_anchor, firebase_functions + api_anchor, 1)

api_remove_anchor = '    removeInvitation,'
if api_remove_anchor not in text:
    raise SystemExit("removeInvitation api anchor not found")
text = text.replace(api_remove_anchor, api_remove_anchor + '''
    subscribePartnerBusinesses,
    savePartnerBusiness,
    deletePartnerBusiness,''', 1)

if text == original:
    raise SystemExit("No changes made")
path.write_text(text, encoding="utf-8")
print("PAIRA v19.8 partner businesses + QR applied")
