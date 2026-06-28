import os

j = []

# Helper functions
j.append("let token = localStorage.getItem('token') || '';")
j.append("let user = JSON.parse(localStorage.getItem('user') || 'null');")
j.append("let currentTreatmentId = null;")
j.append("let currentDiseaseId = null;")
j.append("let currentCategoryId = null;")

j.append("function esc(v) { return String(v==null?'':v).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c];}); }")
j.append("function stars(r) { var s=''; for(var i=1;i<=5;i++) s+= i<=Math.floor(r) ? '\u2605' : '\u2606'; return s; }")
j.append("function updateUser(){ user=JSON.parse(localStorage.getItem('user')||'null'); token=localStorage.getItem('token')||''; }")

j.append("function showToast(m) { var t=document.getElementById('toast'); t.textContent=m; t.classList.add('show'); clearTimeout(t._timer); t._timer=setTimeout(function(){t.classList.remove('show');},2000); }")

j.append("function showPage(id) { document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');}); var el=document.getElementById(id); if(el) el.classList.add('active'); document.querySelectorAll('.nav-item').forEach(function(n){ n.classList.toggle('active',n.dataset.page===id); }); }")
j.append("function switchNav(el,p){ showPage(p); }")

j.append("async function api(path,opts) { var headers={'Content-Type':'application/json'}; if(token) headers['Authorization']='Bearer '+token; var conf={headers:headers}; if(opts) { if(opts.method) conf.method=opts.method; if(opts.body) conf.body=JSON.stringify(opts.body); } var resp=await fetch(path, conf); var data=await resp.json(); if(!resp.ok && data.error) throw new Error(data.error); return data; }")

j.append("function showLoading(el) { el.innerHTML='<div class=\"loading-spinner\"><div class=\"spinner\"></div><span class=\"loading-text\">\u52a0\u8f7d\u4e2d...</span></div>'; }")
j.append("function showEmpty(el, icon, text, sub) { el.innerHTML='<div class=\"empty-state\"><div class=\"empty-icon\">'+icon+'</div><div class=\"empty-text\">'+esc(text)+'</div>'+(sub?'<div class=\"empty-sub\">'+esc(sub)+'</div>':'')+'</div>'; }")

# Home
j.append("async function loadHome() { var g=document.getElementById('categoryGrid'); if(!g) return; showLoading(g); try { var cats=await api('/api/categories'); var h=[]; for(var i=0;i<cats.length;i++) { var c=cats[i]; h.push('<div class=\"category-item\" onclick=\"showCategory('+c.id+')\"><div class=\"cat-icon\" style=\"background:'+esc(c.color)+'\">'+esc(c.icon)+'</div><div class=\"cat-name\">'+esc(c.name)+'</div></div>'); } g.innerHTML=h.join(''); var cc=document.getElementById('catCount'); if(cc) cc.textContent='\u517113\u79d1'; loadRecs(); } catch(e) { showToast('\u52a0\u8f7d\u5206\u7c7b\u5931\u8d25'); g.innerHTML='<div class=\"empty-state\"><div class=\"empty-text\">\u52a0\u8f7d\u5931\u8d25</div></div>'; } }")

j.append("async function loadRecs() { var el=document.getElementById('recommendList'); if(!el) return; try { var treats=await api('/api/treatments'); var ids=[10101,10201,50101,60101,30202,30101]; var data=[]; for(var i=0;i<ids.length;i++) for(var j=0;j<treats.length;j++) if(treats[j].id===ids[i]) { data.push(treats[j]); break; } var h=[]; for(var i=0;i<data.length;i++) renderTreatmentCard(h,data[i]); el.innerHTML=h.join(''); } catch(e) {} }")

j.append("function renderTreatmentCard(h, t) { var tags=''; for(var j=0;j<t.types.length;j++) tags+='<span class=\"card-tag\">'+esc(t.types[j])+'</span>'; if(t.is_special) tags+='<span class=\"card-tag special\">\u63a8\u8350</span>'; h.push('<div class=\"treatment-card\" onclick=\"showTreatment('+t.id+')\"><div class=\"card-header\"><div class=\"card-title\">'+esc(t.title)+'</div><div class=\"card-price\">\u00a5'+t.price+'</div></div><div class=\"card-tags\">'+tags+'</div><div class=\"card-meta\"><span class=\"rating\">'+stars(t.rating)+' '+t.rating+'</span><span>\u53cd\u9988 '+t.feedback_count+'</span><span class=\"effective\">\u6709\u6548 '+t.effective_rate+'%</span></div></div>'); }")

# Category / Disease
j.append("async function showCategory(cid) { currentCategoryId=cid; try { var cats=await api('/api/categories'); var cat=null; for(var i=0;i<cats.length;i++) { if(cats[i].id===cid) { cat=cats[i]; break; } } document.getElementById('diseaseCatTitle').textContent=cat?cat.name:'\u5206\u7c7b'; var ds=await api('/api/diseases?category_id='+cid); var h=[]; if(!ds.length) { showEmpty(document.getElementById('diseaseList'),'\U0001f50d','\u6682\u65e0\u75be\u75c5',''); } else { for(var i=0;i<ds.length;i++) { var d=ds[i]; h.push('<div class=\"disease-item\" onclick=\"showDiseaseDetail('+d.id+')\"><div class=\"disease-icon\">'+esc(d.icon)+'</div><div class=\"disease-info\"><div class=\"disease-name\">'+esc(d.name)+'</div><div class=\"disease-count\">'+d.treatment_count+'\u4e2a\u6cbb\u7597\u65b9\u6848</div></div><span class=\"disease-arrow\">></span></div>'); } } document.getElementById('diseaseList').innerHTML=h.join(''); showPage('pageDisease'); } catch(e) { showToast('\u52a0\u8f7d\u5931\u8d25'); } }")

j.append("async function showDiseaseDetail(did) { currentDiseaseId=did; try { var treats=await api('/api/treatments?disease_id='+did); var tf=0, tr=0; for(var i=0;i<treats.length;i++) { tf+=treats[i].feedback_count; tr+=treats[i].rating; } var avg=treats.length?(tr/treats.length).toFixed(1):0; document.getElementById('diseaseDetailHeader').innerHTML='<div class=\"disease-name\">'+(treats.length>0?esc(treats[0].title):'\u75be\u75c5\u8be6\u60c5')+'</div><div class=\"disease-sub\">'+treats.length+'\u4e2a\u6cbb\u7597\u65b9\u6848</div><div class=\"stats-row\"><div class=\"stat-item\"><div class=\"stat-num\">'+treats.length+'</div><div class=\"stat-label\">\u65b9\u6848</div></div><div class=\"stat-item\"><div class=\"stat-num\">'+tf+'</div><div class=\"stat-label\">\u53cd\u9988</div></div><div class=\"stat-item\"><div class=\"stat-num\">'+avg+'</div><div class=\"stat-label\">\u8bc4\u5206</div></div></div>'; var h=[]; for(var i=0;i<treats.length;i++) renderTreatmentCard(h,treats[i]); document.getElementById('diseaseTreatments').innerHTML=h.join(''); showPage('pageDiseaseDetail'); } catch(e) { showToast('\u52a0\u8f7d\u5931\u8d25'); } }")

with open(os.path.join('static','js','app.js'),'w',encoding='utf-8') as f:
    f.write('\n'.join(j))
print('part 1 written')
