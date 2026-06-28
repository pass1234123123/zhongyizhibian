import os
j = []

# Member
j.append('')
j.append('// ===== MEMBER =====')
j.append('async function loadMemberStatus() { if(!token||!user){ return; } try { var s=await api("/api/member/status"); var el=document.getElementById("memberStatus"); if(el) el.textContent=s.is_member?"已开通":"未开通"; var el2=document.getElementById("memberType"); if(el2) el2.textContent=s.member_type||"-"; var el3=document.getElementById("memberEnd"); if(el3) el3.textContent=s.member_end?s.member_end.substring(0,10):"-"; var el4=document.getElementById("memberUploads"); if(el4) el4.textContent=s.approved_uploads||0; var el5=document.getElementById("memberAnnualFee"); if(el5) el5.textContent="¥"+s.annual_fee+"/年"; var upBtn=document.getElementById("memberUpgradeBtn"); var conBtn=document.getElementById("contributorApplyBtn"); if(upBtn) upBtn.style.display=s.is_member?"none":"inline-flex"; if(conBtn) conBtn.style.display=(s.approved_uploads>=10&&!s.is_member)?"inline-flex":"none"; var pmi=document.getElementById("profileMemberInfo"); if(pmi) pmi.textContent=s.is_member?"已开通":"未开通"; } catch(e) {} }')
j.append('async function upgradeMember() { try { var r=await api("/api/member/apply",{method:"POST",body:{action:"upgrade"}}); showToast(r.message); loadMemberStatus(); } catch(e) { showToast(e.message); } }')
j.append('async function applyContributor() { try { var r=await api("/api/member/apply",{method:"POST",body:{action:"renewal"}}); showToast(r.message); } catch(e) { showToast(e.message); } }')

# Admin Member
j.append('')
j.append('// ===== ADMIN MEMBER =====')
j.append('async function saveMemberSettings() { try { var r=await api("/api/admin/member/settings",{method:"POST",body:{annual_fee:parseFloat(document.getElementById("memberFee").value),free_duration_days:parseInt(document.getElementById("memberDays").value)}}); showToast(r.message); } catch(e) { showToast(e.message); } }')
j.append('async function loadAdminMembers() { try { var s=await api("/api/admin/member/settings"); var feeEl=document.getElementById("memberFee"); var daysEl=document.getElementById("memberDays"); if(feeEl) feeEl.value=s.annual_fee; if(daysEl) daysEl.value=s.free_duration_days; var members=await api("/api/admin/member/list"); var mel=document.getElementById("adminMemberList"); if(mel){ if(!members.length){ showEmpty(mel,"📋","暂无会员记录",""); return; } var h=[]; for(var i=0;i<members.length;i++){ var m=members[i]; h.push("<div class=\\"member-card\\"><h4>"+esc(m.username)+"</h4><p>手机: "+esc(m.phone)+" | 类型: "+esc(m.type)+" | 状态: "+esc(m.status)+"</p><p style=\\"font-size:12px;color:#999\\">到期: "+(m.end_date?m.end_date.substring(0,10):"-")+"</p></div>"); } mel.innerHTML=h.join(""); } var apps=await api("/api/admin/member/applications"); var ael=document.getElementById("adminApplications"); if(ael){ if(!apps.length){ showEmpty(ael,"📋","暂无待审核申请",""); return; } var h2=[]; for(var i=0;i<apps.length;i++){ var a=apps[i]; h2.push("<div class=\\"member-card\\"><h4>"+esc(a.username)+"</h4><p>类型: "+esc(a.type)+" | 状态: "+esc(a.status)+"</p>"+(a.status==="pending"?"<div class=\\"admin-actions\\"><button class=\\"btn-approve\\" onclick=\\"approveApp("+a.id+")\\">通过</button><button class=\\"btn-reject\\" onclick=\\"rejectApp("+a.id+")\\">驳回</button></div>":"")+"</div>"); } ael.innerHTML=h2.join(""); } } catch(e) {} }')
j.append('async function approveApp(id){ try{ await api("/api/admin/member/applications",{method:"POST",body:{application_id:id,action:"approve"}}); showToast("已通过"); loadAdminMembers(); } catch(e) { showToast(e.message); } }')
j.append('async function rejectApp(id){ var r=prompt("请输入驳回理由："); if(!r) return; try{ await api("/api/admin/member/applications",{method:"POST",body:{application_id:id,action:"reject",review_note:r}}); showToast("已驳回"); loadAdminMembers(); } catch(e) { showToast(e.message); } }')

# Init
j.append('')
j.append('// ===== INIT =====')
j.append('document.addEventListener("DOMContentLoaded",function(){ renderProfile(); loadHome(); loadMemberStatus(); });')

with open('static/js/app.js','a',encoding='utf-8') as f:
    f.write('\n'.join(j))
print('part 3 written')
