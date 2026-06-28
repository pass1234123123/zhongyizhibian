fp = r'F:\AI\codex\zhongyizhiban\templates\admin.html'
with open(fp, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add AI tab button
o1 = '<button class="tab" data-tab="tabApplications" onclick="switchTab(this)">\u7533\u8bf7\u5ba1\u6838</button>'
n1 = '<button class="tab" data-tab="tabApplications" onclick="switchTab(this)">\u7533\u8bf7\u5ba1\u6838</button>\n    <button class="tab" data-tab="tabAISettings" onclick="switchTab(this)">AI\u8bbe\u7f6e</button>'
html = html.replace(o1, n1)
print('1 done')

# 2. Add AI content before Applications
o2 = '<div class="tab-content" id="tabApplications">'
n2 = '<div class="tab-content" id="tabAISettings">\n    <div class="section-title">AI \u5927\u6a21\u578b\u8bbe\u7f6e</div>\n    <div class="settings-group">\n      <label>API Key</label>\n      <input type="password" id="aiApiKey" placeholder="\u8bf7\u8f93\u5165DeepSeek API Key">\n      <label>\u6a21\u578b</label>\n      <input type="text" id="aiModel" value="deepseek-chat">\n      <label>API \u5730\u5740</label>\n      <input type="text" id="aiApiUrl" value="https://api.deepseek.com/v1/chat/completions">\n      <label>\n        <input type="checkbox" id="aiAutoApprove" checked>\n        \u81ea\u52a8\u5ba1\u6838\u901a\u8fc7\uff08AI\u8bc6\u522b\u540e\u76f4\u63a5\u53d1\u5e03\uff0c\u65e0\u9700\u4eba\u5de5\u5ba1\u6838\uff09\n      </label>\n      <br><br>\n      <button class="btn-primary" onclick="saveAISettings()">\u4fdd\u5b58 AI \u8bbe\u7f6e</button>\n    </div>\n  </div>\n\n  <!-- Tab: Applications -->\n  <div class="tab-content" id="tabApplications">'
html = html.replace(o2, n2)
print('2 done')

# 3. Add JS functions before appApprove
o3 = 'async function appApprove(id){try{await api("/api/admin/member/applications",{method:"POST",body:{application_id:id,action:"approve"}});t("\u5df2\u6279\u51c6");loadApplications();loadMemberList();}catch(e){t(e.message);}}'
n3 = 'async function loadAISettings(){try{var s=await api("/api/admin/ai/settings");document.getElementById("aiApiKey").value=s.api_key||"";document.getElementById("aiModel").value=s.model||"deepseek-chat";document.getElementById("aiApiUrl").value=s.api_url||"https://api.deepseek.com/v1/chat/completions";document.getElementById("aiAutoApprove").checked=!!s.auto_approve;}catch(e){}}\n\nasync function saveAISettings(){try{var r=await api("/api/admin/ai/settings",{method:"POST",body:{api_key:document.getElementById("aiApiKey").value,model:document.getElementById("aiModel").value,api_url:document.getElementById("aiApiUrl").value,auto_approve:document.getElementById("aiAutoApprove").checked}});t(r.message);}catch(e){t(e.message);}}\n\n' + o3
html = html.replace(o3, n3)
print('3 done')

# 4. Update login handler
html = html.replace('loadMemberSettings();loadMemberList();loadApplications();', 'loadMemberSettings();loadMemberList();loadApplications();loadAISettings();')
print('4 done')

# 5. Switch tab
o5 = "if(el.dataset.tab==='tabApplications') loadApplications();"
n5 = "if(el.dataset.tab==='tabApplications') loadApplications();\n  if(el.dataset.tab==='tabAISettings') loadAISettings();"
html = html.replace(o5, n5)
print('5 done')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(html)
print('All done!')
