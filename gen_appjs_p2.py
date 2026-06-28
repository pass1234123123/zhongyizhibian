import os
j = []

j.append('')
j.append('// ===== TREATMENT =====')
j.append('async function showTreatment(tid) { updateUser(); if(!token) { showToast("请先登录"); showPage("pageProfile"); return; } currentTreatmentId=tid; try { var t=await api("/api/treatments/"+tid); var tags="<div class=\\"detail-tags\\">"; for(var i=0;i<t.types.length;i++) tags+="<span class=\\"card-tag\\">"+esc(t.types[i])+"</span>"; if(t.is_special) tags+="<span class=\\"card-tag special\\">推荐</span>"; tags+="</div>"; document.getElementById("treatmentHeader").innerHTML="<div class=\\"detail-title\\">"+esc(t.title)+"</div>"+tags+"<div class=\\"detail-stats\\"><div class=\\"detail-stat\\"><div class=\\"num\\">"+stars(t.rating)+" "+t.rating+"</div><div class=\\"label\\">评分</div></div><div class=\\"detail-stat\\"><div class=\\"num\\">"+t.feedback_count+"</div><div class=\\"label\\">反馈</div></div><div class=\\"detail-stat\\"><div class=\\"num\\">"+t.effective_rate+"%</div><div class=\\"label\\">有效</div></div></div>"; document.getElementById("previewContent").textContent=t.preview||""; if(t.can_view) { document.getElementById("paywall").style.display="none"; document.getElementById("fullContent").classList.add("show"); renderFullContent(t); } else { document.getElementById("paywall").style.display="block"; document.getElementById("fullContent").classList.remove("show"); document.getElementById("payPrice").innerHTML="<span>非会员每日仅可查看1个方案</span>"; document.getElementById("payDesc").textContent="开通会员可查看全部"; document.getElementById("payBtn").textContent="开通会员 随时查看"; document.getElementById("payBtn").onclick=function(){showPage("pageMember");loadMemberStatus();}; } renderFeedback(tid); showPage("pageTreatment"); } catch(e) { showToast("加载失败: "+e.message); } }')

j.append('function renderFullContent(t) { var fs=document.getElementById("formulaSection"), as=document.getElementById("acupointSection"); document.getElementById("fullContentText").textContent=t.full_content||""; var h=[]; if(t.formulas&&t.formulas.length) { for(var i=0;i<t.formulas.length;i++) { var f=t.formulas[i]; h.push("<div class=\\"formula-box\\">"+(f.formula_name?"<div class=\\"formula-name\\">"+esc(f.formula_name)+"</div>":"")+(f.ingredients?"<div class=\\"formula-detail\\"><strong>组成：</strong>"+esc(f.ingredients)+"</div>":"")+(f.usage_text?"<div class=\\"formula-detail\\"><strong>用法：</strong>"+esc(f.usage_text)+"</div>":"")+(f.note?"<div class=\\"formula-detail\\"><strong>备注：</strong>"+esc(f.note)+"</div>":"")+"</div>"); } } fs.innerHTML=h.join(""); h=[]; if(t.acupoints&&t.acupoints.length) { for(var i=0;i<t.acupoints.length;i++) { var a=t.acupoints[i]; h.push("<div class=\\"acupoint-box\\">"+(a.points?"<div class=\\"acupoint-detail\\"><strong>取穴：</strong>"+esc(a.points)+"</div>":"")+(a.method?"<div class=\\"acupoint-detail\\"><strong>手法：</strong>"+esc(a.method)+"</div>":"")+(a.course?"<div class=\\"acupoint-detail\\"><strong>疗程：</strong>"+esc(a.course)+"</div>":"")+"</div>"); } } as.innerHTML=h.join(""); }')

j.append('async function buyTreatment(){ showToast("请先开通会员"); showPage("pageMember"); loadMemberStatus(); }')

# Favorites
j.append('')
j.append('// ===== FAVORITES =====')
j.append('async function toggleFav() { try { var r=await api("/api/favorites/toggle",{method:"POST",body:{treatment_id:currentTreatmentId}}); showToast(r.message); showTreatment(currentTreatmentId); } catch(e) { showToast(e.message); } }')
j.append('async function loadFavs() { var el=document.getElementById("favList"); if(!el) return; try { var favs=await api("/api/favorites"); var h=[]; if(!favs.length) { showEmpty(el,"❤️","还没有收藏的内容",""); return; } for(var i=0;i<favs.length;i++) renderTreatmentCard(h,favs[i]); el.innerHTML=h.join(""); } catch(e) {} }')

# Feedback
j.append('')
j.append('// ===== FEEDBACK =====')
j.append('var fbRating=5; var fbEfficacy="effective";')
j.append('function setFbRating(r) { fbRating=r; }')
j.append('function setFbEfficacy(v) { fbEfficacy=v; }')
j.append('async function renderFeedback(tid) { var el=document.getElementById("feedbackSection"); if(!el) return; try { var fb=await api("/api/feedback/"+tid); var h=[]; if(!fb.total) { el.innerHTML=""; return; } h.push("<div class=\\"feedback-summary\\"><div class=\\"fb-stats-overview\\"><div class=\\"fb-avg-score\\">"+fb.avg_rating+"<small>/5</small></div><div style=\\"flex:1\\"><span style=\\"font-size:13px;color:#666\\">"+fb.total+"条反馈</span></div></div></div>"); for(var i=0;i<fb.list.length;i++) { var r=fb.list[i]; h.push("<div class=\\"fb-item\\"><div class=\\"fb-stars\\">"+stars(r.rating)+"</div><div class=\\"fb-text\\">"+esc(r.description||"")+"</div><div class=\\"fb-meta\\"><span>"+esc(r.username||"匿名")+"</span><span>"+esc(r.efficacy||"")+"</span><span>"+(r.course_days||0)+"天</span></div></div>"); } document.getElementById("feedbackList").innerHTML=h.join(""); } catch(e) {} }')
j.append('async function submitFeedback() { try { var r=await api("/api/feedback",{method:"POST",body:{treatment_id:currentTreatmentId,rating:fbRating,efficacy:fbEfficacy,description:document.getElementById("fbDesc").value,course_days:parseInt(document.getElementById("fbDays").value)||0}}); showToast(r.message); showTreatment(currentTreatmentId); } catch(e) { showToast(e.message); } }')

# Upload
j.append('')
j.append('// ===== UPLOAD =====')
j.append('function togglePaste() { var ta=document.getElementById("pasteArea"); ta.classList.toggle("show"); if(ta.classList.contains("show")) ta.querySelector("textarea").focus(); }')
j.append('function handleFiles() { showToast("请使用粘贴文字上传"); }')
j.append('async function submitPaste() { var ta=document.getElementById("pasteArea").querySelector("textarea"); var content=ta.value.trim(); if(!content||content.length<10) { showToast("请输入更多内容"); return; } try { var result=await api("/api/upload",{method:"POST",body:{content:content}}); showToast("上传成功，等待审核"); ta.value=""; document.getElementById("pasteArea").classList.remove("show"); loadUploads(); } catch(e) { showToast("上传失败: "+e.message); } }')
j.append('async function loadUploads() { var el=document.getElementById("uploadHistory"); if(!el) return; try { var uploads=await api("/api/uploads"); if(!uploads.length) { showEmpty(el,"📤","暂无上传记录",""); return; } var h=[]; for(var i=0;i<uploads.length;i++) { var r=uploads[i]; var icon=r.status==="approved"?"✅":r.status==="rejected"?"❌":"⏳"; var badgeClass=r.status==="approved"?"badge-approved":r.status==="rejected"?"badge-rejected":"badge-pending"; var label=r.status==="approved"?"已发布":r.status==="rejected"?"已驳回":"待审核"; var title=(r.ai_result&&r.ai_result.title)?r.ai_result.title:"上传内容"; h.push("<div class=\\"treatment-card\\" style=\\"padding:12px 14px\\"><div style=\\"display:flex;align-items:center;gap:10px\\"><div style=\\"font-size:22px\\">"+icon+"</div><div style=\\"flex:1\\"><div style=\\"font-size:13px;font-weight:500\\">"+esc(title)+"</div><div style=\\"font-size:11px;color:#999\\">"+esc(r.created_at||"")+"</div></div><span class=\\"badge "+badgeClass+"\\">"+label+"</span></div></div>"); } el.innerHTML=h.join(""); } catch(e) {} }')

# Auth
j.append('')
j.append('// ===== AUTH =====')
j.append('function switchToRegister() { document.getElementById("authTitle").textContent="注册"; document.getElementById("authSubmitBtn").textContent="注册"; document.getElementById("authToggle").innerHTML="已有账号？<a onclick=\\"switchToLogin()\\">立即登录</a>"; document.getElementById("authIsRegister").value="true"; document.getElementById("authUsernameRow").style.display="block"; showPage("pageAuth"); }')
j.append('function switchToLogin() { document.getElementById("authTitle").textContent="登录"; document.getElementById("authSubmitBtn").textContent="登录"; document.getElementById("authToggle").innerHTML="还没有账号？<a onclick=\\"switchToRegister()\\">立即注册</a>"; document.getElementById("authIsRegister").value="false"; document.getElementById("authUsernameRow").style.display="none"; showPage("pageAuth"); }')
j.append('async function submitAuth() { var isRegister=document.getElementById("authIsRegister").value==="true"; var phone=document.getElementById("authPhone").value.trim(); var password=document.getElementById("authPassword").value; var username=document.getElementById("authUsername").value.trim(); if(!phone||!password) { showToast("请填写手机号和密码"); return; } try { var result; if(isRegister) result=await api("/api/auth/register",{method:"POST",body:{phone:phone,password:password,username:username||""}}); else result=await api("/api/auth/login",{method:"POST",body:{phone:phone,password:password}}); localStorage.setItem("token",result.token); localStorage.setItem("user",JSON.stringify(result.user)); updateUser(); showToast("登录成功！"); renderProfile(); showPage("pageProfile"); } catch(e) { showToast(e.message); } }')
j.append('function logout() { localStorage.removeItem("token"); localStorage.removeItem("user"); token=""; user=null; showToast("已退出登录"); renderProfile(); showPage("pageProfile"); }')

# Profile
j.append('')
j.append('// ===== PROFILE =====')
j.append('function renderProfile() { updateUser(); var loginDiv=document.getElementById("profileLogin"); var contentDiv=document.getElementById("profileContent"); if(user&&user.id) { if(loginDiv) loginDiv.style.display="none"; if(contentDiv) { contentDiv.style.display="block"; document.getElementById("profileName").textContent=user.username||"用户"; document.getElementById("profilePoints").textContent=user.points||0; document.getElementById("profileBalance").textContent="¥"+(user.balance||"0.00"); document.getElementById("profileRole").textContent=user.role==="admin"?"管理员":"普通用户"; } } else { if(loginDiv) loginDiv.style.display="block"; if(contentDiv) contentDiv.style.display="none"; } }')

# Admin
j.append('')
j.append('// ===== ADMIN =====')
j.append('async function loadAdmin() { try { updateUser(); if(!user||user.role!=="admin") { showToast("需要管理员权限"); showPage("pageProfile"); return; } var pending=await api("/api/admin/pending?status=pending"); var el=document.getElementById("adminPendingList"); if(!pending.length) { showEmpty(el,"🔍","暂无待审核内容",""); return; } var h=[]; for(var i=0;i<pending.length;i++) { var r=pending[i]; var title=(r.ai_result&&r.ai_result.title)?r.ai_result.title:"待审核内容"; h.push("<div class=\\"admin-card\\"><div class=\\"card-header\\"><div class=\\"card-title\\">"+esc(title)+"</div></div><div style=\\"font-size:12px;color:#999\\">上传者: "+esc(r.uploader_name||"")+" | "+esc(r.created_at||"")+"</div><div class=\\"admin-content\\">"+esc((r.content||"").substring(0,200))+"</div><div class=\\"admin-actions\\"><button class=\\"btn-approve\\" onclick=\\"approveUpload("+r.id+")\\">通过</button><button class=\\"btn-reject\\" onclick=\\"rejectUpload("+r.id+")\\">驳回</button></div></div>"); } el.innerHTML=h.join(""); } catch(e) { showToast("加载失败: "+e.message); } }')
j.append('async function approveUpload(id) { try { await api("/api/admin/review",{method:"POST",body:{upload_id:id,action:"approve"}}); showToast("已通过审核"); loadAdmin(); } catch(e) { showToast("操作失败: "+e.message); } }')
j.append('async function rejectUpload(id) { var reason=prompt("请输入驳回理由："); if(!reason) return; try { await api("/api/admin/review",{method:"POST",body:{upload_id:id,action:"reject",review_note:reason}}); showToast("已驳回"); loadAdmin(); } catch(e) { showToast("操作失败: "+e.message); } }')

with open('static/js/app.js','a',encoding='utf-8') as f:
    f.write('\n'.join(j))
print('part 2 written')
