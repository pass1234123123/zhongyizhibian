fp = r'F:\AI\codex\zhongyizhiban\templates\admin.html'
with open(fp, 'r', encoding='utf-8-sig') as f:
    c = f.read()

sq = chr(39)

# 1. Replace adminLogin with better error handling
old_login = '''async function adminLogin(){
  var phone=document.getElementById('adminPhone').value.trim();
  var password=document.getElementById('adminPassword').value;
  var err=document.getElementById('loginError');
  try{
    var r=await api('/api/auth/login',{method:'POST',body:{phone:phone,password:password}});
    if(r.user.role!=='admin'){err.textContent= '''' + sq + '该账号非管理员' + sq + ''';err.style.display='block';return;}
    token=r.token;
    document.getElementById('loginScreen').style.display='none';
    document.getElementById('dashboard').style.display='block';
    loadPending();loadMemberSettings();loadMemberList();loadApplications();loadAISettings();
  }catch(e){err.textContent=e.message;err.style.display='block';}
}'''

new_login = '''async function adminLogin(){
  var btn=document.querySelector('.''login-btn''');
  var phone=document.getElementById('adminPhone').value.trim();
  var password=document.getElementById('adminPassword').value;
  var err=document.getElementById('loginError');
  btn.textContent='登录中...';btn.disabled=true;err.style.display='none';
  console.log('adminLogin: trying...');
  try{
    var r=await api('/api/auth/login',{method:'POST',body:{phone:phone,password:password}});
    console.log('adminLogin: ok', r);
    if(r.user.role!=='admin'){err.textContent='该账号非管理员';err.style.display='block';btn.textContent='登录';btn.disabled=false;return;}
    token=r.token;
    document.getElementById('loginScreen').style.display='none';
    document.getElementById('dashboard').style.display='block';
    loadPending();loadMemberSettings();loadMemberList();loadApplications();loadAISettings();
  }catch(e){
    console.error('adminLogin error:', e);
    err.textContent='登录失败: '+e.message;err.style.display='block';
    btn.textContent='登录';btn.disabled=false;
  }
}
async function testApi(){
  try{
    var r=await fetch('/api/categories');
    var d=await r.json();
    t('API连接成功！分类数: '+d.length);
    console.log('API test ok');
  }catch(e){
    t('API连接失败: '+e.message);
    console.error('API test error:', e);
  }
}'''

c = c.replace(old_login, new_login)

# 2. Add test button after login button
old_btn = '<button class=' + sq + 'login-btn' + sq + ' onclick=' + sq + 'adminLogin()' + sq + '>' + chr(30331) + chr(24405) + '</button>'
new_btn = '<button class=' + sq + 'login-btn' + sq + ' onclick=' + sq + 'adminLogin()' + sq + ' id=' + sq + 'loginBtn' + sq + '>' + chr(30331) + chr(24405) + '</button><br><span style=' + sq + 'font-size:12px;color:#999;margin-top:4px;display:inline-block' + sq + '><a href=' + sq + 'javascript:testApi()' + sq + ' style=' + sq + 'color:#1565C0;text-decoration:none' + sq + '>测试连接</a> | <a href=' + sq + 'javascript:console.log(adminLogin.toString().substring(0,200))' + sq + ' style=' + sq + 'color:#999;text-decoration:none' + sq + '>调试</a></span>'
c = c.replace(old_btn, new_btn)

with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('OK')
