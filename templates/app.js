// ========================================
// 中医智慧平台 - Frontend API Layer
//
// 注意: 当前版本 JS 已内联至 templates/index.html。
// 此文件仅供历史参考，修改 index.html 中的 <script> 块生效。
// ========================================

function showToast(m) {
    var t = document.getElementById('toast');
    t.textContent = m;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(function() { t.classList.remove('show'); }, 2000);
}

function showPage(id) {
    document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
    var el = document.getElementById(id);
    if (el) el.classList.add('active');
    document.querySelectorAll('.nav-item').forEach(function(n) {
        n.classList.toggle('active', n.dataset.page === id);
    });
}

function switchNav(el, p) { showPage(p); }

function updateUser() {
    user = JSON.parse(localStorage.getItem('user') || 'null');
    token = localStorage.getItem('token') || '';
}

async function api(path, opts) {
    var headers = {'Content-Type': 'application/json'};
    if (token) headers['Authorization'] = 'Bearer ' + token;
    var conf = {headers: headers};
    if (opts) {
        if (opts.method) conf.method = opts.method;
        if (opts.body) conf.body = JSON.stringify(opts.body);
    }
    var resp = await fetch(API + path, conf);
    var data = await resp.json();
    if (!resp.ok && data.error) throw new Error(data.error);
    return data;
}

// === HOME ===
async function loadHome() {
    try {
        var cats = await api('/api/categories');
        var g = document.getElementById('categoryGrid');
        if (!g) return;
        var h = [];
        for (var i = 0; i < cats.length; i++) {
            var c = cats[i];
            h.push('<div class="cat-item" onclick="showCategory(' + c.id + ')">' +
                '<div class="cat-icon" style="background:' + c.color + '">' + c.icon + '</div>' +
                '<div class="cat-name">' + c.name + '</div></div>');
        }
        g.innerHTML = h.join('');
        loadRecs();
    } catch(e) { showToast('加载失败'); }
}

async function loadRecs() {
    try {
        var treats = await api('/api/treatments');
        var el = document.getElementById('recommendList');
        if (!el) return;
        var ids = [10101, 10201, 50101, 60101, 30202, 30101];
        var data = [];
        for (var i = 0; i < ids.length; i++)
            for (var j = 0; j < treats.length; j++)
                if (treats[j].id === ids[i]) { data.push(treats[j]); break; }
        var h = [];
        for (var i = 0; i < data.length; i++) {
            var t = data[i];
            var tags = '';
            for (var j = 0; j < t.types.length; j++) tags += '<span class="tag">' + t.types[j] + '</span>';
            var sp = t.is_special ? '<span class="tag tag-spec">特殊疗效</span>' : '';
            h.push('<div class="treatment-card" onclick="showTreatment(' + t.id + ')">' +
                '<div class="tc-header"><div class="tc-title">' + t.title + '</div><div class="tc-price">¥' + t.price + '</div></div>' +
                '<div class="tc-tags">' + tags + sp + '</div>' +
                '<div class="tc-meta"><span>⭐' + t.rating + '</span><span>💬' + t.feedback_count + '条反馈</span><span>✅' + t.effective_rate + '%有效</span></div></div>');
        }
        el.innerHTML = h.join('');
    } catch(e) {}
}

// === CATEGORY ===
async function showCategory(cid) {
    try {
        var cats = await api('/api/categories');
        var cat = null;
        for (var i = 0; i < cats.length; i++) { if (cats[i].id === cid) { cat = cats[i]; break; } }
        document.getElementById('diseaseCatTitle').textContent = cat ? cat.name : '分类';
        var ds = await api('/api/diseases?category_id=' + cid);
        var h = [];
        for (var i = 0; i < ds.length; i++) {
            var d = ds[i];
            h.push('<div class="dl-item" onclick="showDiseaseDetail(' + d.id + ')">' +
                '<div class="dl-icon" style="font-size:24px">' + d.icon + '</div>' +
                '<div class="dl-info"><div class="dl-name">' + d.name + '</div>' +
                '<div class="dl-count">' + d.treatment_count + '个治疗方案</div></div>' +
                '<span class="dl-arrow">›</span></div>');
        }
        document.getElementById('diseaseList').innerHTML = h.join('');
        showPage('pageDisease');
    } catch(e) { showToast('加载失败'); }
}

// === DISEASE DETAIL ===
async function showDiseaseDetail(did) {
    try {
        var treats = await api('/api/treatments?disease_id=' + did);
        var tf = 0, tr = 0;
        for (var i = 0; i < treats.length; i++) { tf += treats[i].feedback_count; tr += treats[i].rating; }
        var avg = treats.length ? (tr / treats.length).toFixed(1) : 0;
        var hdr = '<div class="name"> ' + (treats.length > 0 ? treats[0].title.replace(/^(\S+).*$/, '$1') : '疾病详情') +
            '</div><div class="sub">' + treats.length + '个治疗方案</div>' +
            '<div class="stats"><div class="stat"><div class="stat-num">' + treats.length + '</div><div class="stat-label">方案</div></div>' +
            '<div class="stat"><div class="stat-num">' + tf + '</div><div class="stat-label">反馈</div></div>' +
            '<div class="stat"><div class="stat-num">' + avg + '</div><div class="stat-label">评分</div></div></div>';
        document.getElementById('diseaseDetailHeader').innerHTML = hdr;
        var h = [];
        for (var i = 0; i < treats.length; i++) {
            var t = treats[i];
            var sp = t.is_special ? '<span class="tag tag-spec">特殊疗效</span>' : '';
            var tags = '';
            for (var j = 0; j < t.types.length; j++) tags += '<span class="tag">' + t.types[j] + '</span>';
            h.push('<div class="treatment-card" onclick="showTreatment(' + t.id + ')">' +
                '<div class="tc-header"><div class="tc-title">' + t.title + '</div><div class="tc-price">¥' + t.price + '</div></div>' +
                '<div class="tc-tags">' + tags + sp + '</div>' +
                '<div class="tc-meta"><span>⭐' + t.rating + '</span><span>💬' + t.feedback_count + '条反馈</span><span>✅' + t.effective_rate + '%有效</span></div></div>');
        }
        document.getElementById('diseaseTreatments').innerHTML = h.join('');
        showPage('pageDiseaseDetail');
    } catch(e) { showToast('加载失败'); }
}

// === TREATMENT ===
async function showTreatment(tid) {
    updateUser();
    if (!token) { showToast('请先登录'); showPage('pageProfile'); return; }
    try {
        currentTreatmentId = tid;
        var t = await api('/api/treatments/' + tid);
        document.getElementById('favBtn').textContent = t.is_favorited ? '❤️' : '🤍';
        var tags = '<div class="tc-tags" style="margin-top:6px">';
        for (var i = 0; i < t.types.length; i++) tags += '<span class="tag">' + t.types[i] + '</span>';
        if (t.is_special) tags += '<span class="tag tag-spec">特殊疗效</span>';
        tags += '</div>';
        document.getElementById('treatmentHeader').innerHTML =
            '<div class="name">' + t.title + '</div>' + tags +
            '<div class="stats"><div class="stat"><div class="stat-num">⭐' + t.rating + '</div><div class="stat-label">评分</div></div>' +
            '<div class="stat"><div class="stat-num">' + t.feedback_count + '</div><div class="stat-label">反馈</div></div>' +
            '<div class="stat"><div class="stat-num">' + t.effective_rate + '%</div><div class="stat-label">有效</div></div></div>';
        document.getElementById('previewContent').textContent = t.preview || '';
        if (t.is_purchased) {
            document.getElementById('paywall').style.display = 'none';
            document.getElementById('fullContent').classList.add('show');
            renderFull(t);
        } else {
            document.getElementById('paywall').style.display = 'block';
            document.getElementById('fullContent').classList.remove('show');
            document.getElementById('payPrice').innerHTML = '¥' + t.price + ' <span>一次性付费，永久查看</span>';
        }
        loadFeedback(tid);
        showPage('pageTreatment');
    } catch(e) { showToast('加载失败: ' + e.message); }
}

function renderFull(t) {
    var el = document.getElementById('fullContentText');
    el.textContent = t.full_content || '暂无完整内容';
    var fs = document.getElementById('formulaSection');
    var as = document.getElementById('acupointSection');
    var h = [];
    if (t.formulas && t.formulas.length) {
        h.push('<h4 style="margin-top:14px;font-size:14px;color:#5a3e36">🌿 方剂明细</h4>');
        for (var i = 0; i < t.formulas.length; i++) {
            var f = t.formulas[i];
            h.push('<div class="formula-box"><div class="fn">' + (f.formula_name || '') +
                '</div><div class="fd"><strong>组成：</strong>' + (f.ingredients || '') +
                '</div><div class="fd"><strong>用法：</strong>' + (f.usage_text || '') +
                '</div>' + (f.note ? '<div class="fd"><strong>备注：</strong>' + f.note + '</div>' : '') + '</div>');
        }
    }
    fs.innerHTML = h.join('');
    h = [];
    if (t.acupoints && t.acupoints.length) {
        h.push('<h4 style="margin-top:14px;font-size:14px;color:#5a3e36">📍 针灸方案</h4>');
        for (var i = 0; i < t.acupoints.length; i++) {
            var a = t.acupoints[i];
            h.push('<div class="acupoint-box"><div class="ap">取穴：' + (a.points || '') +
                '</div><div class="apd"><strong>手法：</strong>' + (a.method || '') +
                '</div><div class="apd"><strong>疗程：</strong>' + (a.course || '') + '</div></div>');
        }
    }
    as.innerHTML = h.join('');
}

// === SEARCH ===
var searchTimer = null;
function searchDisease(val) {
    clearTimeout(searchTimer);
    if (!val.trim()) { loadRecs(); return; }
    searchTimer = setTimeout(function() { doSearch(val.trim()); }, 300);
}

async function doSearch(q) {
    try {
        var treats = await api('/api/treatments?search=' + encodeURIComponent(q));
        var el = document.getElementById('searchResults');
        document.getElementById('searchTitle').textContent = '"' + q + '" 搜索结果 · ' + treats.length + '条';
        if (!treats.length) {
            el.innerHTML = '<div style="text-align:center;padding:40px 20px;color:#bbb;font-size:14px">未找到相关结果<br><span style="font-size:12px">试试其他关键词</span></div>';
            showPage('pageSearch'); return;
        }
        var typeOrder = ['针灸', '拔罐', '放血', '推拿手法', '方剂内服', '方剂外用', '食疗药膳', '导引气功'];
        var grouped = {};
        for (var i = 0; i < treats.length; i++) {
            for (var j = 0; j < treats[i].types.length; j++) {
                var tp = treats[i].types[j];
                if (!grouped[tp]) grouped[tp] = [];
                var dup = false;
                for (var gi = 0; gi < grouped[tp].length; gi++) { if (grouped[tp][gi].id === treats[i].id) { dup = true; break; } }
                if (!dup) grouped[tp].push(treats[i]);
            }
        }
        var h = [];
        for (var oi = 0; oi < typeOrder.length; oi++) {
            var tp = typeOrder[oi];
            if (grouped[tp] && grouped[tp].length) {
                h.push('<div class="type-group"><div class="tg-title">🏷 ' + tp + ' (' + grouped[tp].length + ')</div>');
                for (var gi = 0; gi < grouped[tp].length; gi++) {
                    var t = grouped[tp][gi];
                    var tags = '';
                    for (var j = 0; j < t.types.length; j++) tags += '<span class="tag">' + t.types[j] + '</span>';
                    h.push('<div class="treatment-card" onclick="showTreatment(' + t.id + ')"><div class="tc-header"><div class="tc-title">' + t.title + '</div><div class="tc-price">¥' + t.price + '</div></div><div class="tc-tags">' + tags + '</div><div class="tc-meta"><span>⭐' + t.rating + '</span></div></div>');
                }
                h.push('</div>');
            }
        }
        el.innerHTML = h.join('');
        showPage('pageSearch');
    } catch(e) { showToast('搜索失败'); }
}

// === FEEDBACK ===
function openFeedback() {
    fbRating = 0;
    var ss = document.querySelectorAll('#starInput span');
    for (var i = 0; i < ss.length; i++) ss[i].classList.remove('active');
    document.getElementById('fbEffect').value = 'effective';
    document.getElementById('fbDays').value = 7;
    document.getElementById('fbDesc').value = '';
    document.getElementById('feedbackModal').classList.add('show');
}

function closeFeedback() {
    document.getElementById('feedbackModal').classList.remove('show');
}

document.getElementById('starInput').addEventListener('click', function(e) {
    if (e.target.tagName === 'SPAN' && e.target.dataset.v) {
        fbRating = parseInt(e.target.dataset.v);
        var ss = document.querySelectorAll('#starInput span');
        for (var i = 0; i < ss.length; i++) ss[i].classList.toggle('active', i < fbRating);
    }
});

async function submitFeedback() {
    if (!fbRating) { showToast('请选择评分'); return; }
    closeFeedback();
    try {
        var result = await api('/api/feedback', {
            method: 'POST',
            body: {
                treatment_id: currentTreatmentId,
                rating: fbRating,
                efficacy: document.getElementById('fbEffect').value,
                description: document.getElementById('fbDesc').value,
                course_days: parseInt(document.getElementById('fbDays').value) || 0
            }
        });
        showToast(result.message || '反馈提交成功！');
        loadFeedback(currentTreatmentId);
    } catch(e) { showToast('提交失败: ' + e.message); }
}

async function loadFeedback(tid) {
    try {
        var fb = await api('/api/feedback/' + tid);
        var el = document.getElementById('feedbackSection');
        var h = [];
        h.push('<div class="section-title" style="padding:10px 0 8px">💬 疗效反馈 (' + fb.total + ')</div>');
        if (fb.total > 0) {
            h.push('<div class="fb-summary"><div class="fb-stats"><div class="fb-avg">' + fb.avg_rating + ' <small>/5</small></div><div class="fb-bar" style="flex:1">');
            for (var s = 5; s >= 1; s--) {
                var cnt = fb.distribution ? (fb.distribution[String(s)] || 0) : 0;
                var pct = fb.total > 0 ? (cnt / fb.total * 100) : 0;
                h.push('<div class="fb-bar-item"><span>' + s + '星</span><div class="fb-bar-track"><div class="fb-bar-fill" style="width:' + pct + '%"></div></div><span>' + cnt + '</span></div>');
            }
            h.push('</div></div></div>');
            if (fb.list && fb.list.length) {
                for (var i = 0; i < fb.list.length; i++) {
                    var r = fb.list[i];
                    var stars = '';
                    for (var si = 0; si < 5; si++) stars += si < r.rating ? '⭐' : '☆';
                    h.push('<div class="fb-item"><div class="fb-stars">' + stars + '</div><div class="fb-text">' + (r.description || '') + '</div><div class="fb-meta"><span>' + (r.username || '匿名') + '</span><span>' + (r.created_at || '') + '</span><span>🏆' + (r.efficacy || '') + '</span><span>' + (r.course_days || 0) + '天</span></div></div>');
                }
            }
        } else {
            h.push('<div style="text-align:center;padding:20px;color:#bbb;font-size:13px">暂无疗效反馈</div>');
        }
        if (token && currentTreatmentId) {
            h.push('<div style="text-align:center;padding:10px"><button class="pay-btn sm" style="background:#f0ebe6;color:#5a3e36" onclick="openFeedback()">📝 提交疗效反馈</button></div>');
        }
        el.innerHTML = h.join('');
    } catch(e) {}
}

// === FAVORITE ===
async function toggleFav() {
    if (!currentTreatmentId) return;
    try {
        var result = await api('/api/favorites/toggle', { method: 'POST', body: { treatment_id: currentTreatmentId } });
        document.getElementById('favBtn').textContent = result.favorited ? '❤️' : '🤍';
        showToast(result.message || '');
    } catch(e) { showToast('操作失败'); }
}

async function renderFavs() {
    try {
        var favs = await api('/api/favorites');
        var el = document.getElementById('favList');
        if (!favs.length) {
            el.innerHTML = '<div style="text-align:center;padding:40px 20px;color:#bbb;font-size:14px">❤️ 还没有收藏的内容<br><span style="font-size:12px">浏览治疗方案时点击🤍即可收藏</span></div>';
            showPage('pageFav'); return;
        }
        var h = [];
        for (var i = 0; i < favs.length; i++) {
            var t = favs[i];
            var tags = '';
            for (var j = 0; j < (t.types || []).length; j++) tags += '<span class="tag">' + t.types[j] + '</span>';
            h.push('<div class="treatment-card" onclick="showTreatment(' + t.treatment_id + ')"><div class="tc-header"><div class="tc-title">' + t.title + '</div><div class="tc-price">¥' + t.price + '</div></div><div class="tc-tags">' + tags + '</div><div class="tc-meta"><span>⭐' + t.rating + '</span></div></div>');
        }
        el.innerHTML = h.join('');
        showPage('pageFav');
    } catch(e) { showToast('加载失败'); }
}

// === PURCHASE ===
function openPay() { document.getElementById('payModal').classList.add('show'); }
function closePay() { document.getElementById('payModal').classList.remove('show'); }

async function doPay() {
    closePay();
    try {
        var result = await api('/api/purchase', { method: 'POST', body: { treatment_id: currentTreatmentId } });
        showToast('✅ ' + (result.message || '购买成功！'));
        showTreatment(currentTreatmentId);
    } catch(e) { showToast('购买失败: ' + e.message); }
}

// === AUTH ===
function switchToLogin() {
    document.getElementById('authTitle').textContent = '登录';
    document.getElementById('authSubmitBtn').textContent = '登录';
    document.getElementById('authToggle').innerHTML = '还没有账号？<a href="javascript:switchToRegister()">立即注册</a>';
    document.getElementById('authIsRegister').value = 'false';
    document.getElementById('authUsernameRow').style.display = 'none';
    showPage('pageAuth');
}

function switchToRegister() {
    document.getElementById('authTitle').textContent = '注册';
    document.getElementById('authSubmitBtn').textContent = '注册';
    document.getElementById('authToggle').innerHTML = '已有账号？<a href="javascript:switchToLogin()">立即登录</a>';
    document.getElementById('authIsRegister').value = 'true';
    document.getElementById('authUsernameRow').style.display = 'block';
    showPage('pageAuth');
}

async function submitAuth() {
    var isRegister = document.getElementById('authIsRegister').value === 'true';
    var phone = document.getElementById('authPhone').value.trim();
    var password = document.getElementById('authPassword').value;
    var username = document.getElementById('authUsername') ? document.getElementById('authUsername').value.trim() : '';
    if (!phone || !password) { showToast('请填写手机号和密码'); return; }
    try {
        var result;
        if (isRegister) {
            result = await api('/api/auth/register', { method: 'POST', body: { phone: phone, password: password, username: username || '' } });
        } else {
            result = await api('/api/auth/login', { method: 'POST', body: { phone: phone, password: password } });
        }
        token = result.token;
        user = result.user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        showToast(isRegister ? '注册成功！' : '登录成功！');
        renderProfile();
        showPage('pageProfile');
    } catch(e) { showToast(e.message); }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    token = '';
    user = null;
    showToast('已退出登录');
    renderProfile();
    showPage('pageProfile');
}

// === UPLOAD ===
function togglePaste() {
    var ta = document.getElementById('pasteArea');
    ta.style.display = ta.style.display === 'block' ? 'none' : 'block';
    if (ta.style.display === 'block') ta.focus();
}

function handleFiles() {
    showToast('📤 文件上传功能（请使用粘贴文字上传）');
}

async function submitPaste() {
    var ta = document.getElementById('pasteArea');
    var content = ta.value.trim();
    if (!content || content.length < 10) { showToast('请输入更多内容'); return; }
    try {
        var result = await api('/api/upload', { method: 'POST', body: { content: content } });
        showToast('📤 上传成功，AI正在处理...');
        ta.value = '';
        ta.style.display = 'none';
        loadUploads();
    } catch(e) { showToast('上传失败: ' + e.message); }
}

async function loadUploads() {
    try {
        var uploads = await api('/api/uploads');
        var el = document.getElementById('uploadHistory');
        if (!el) return;
        if (!uploads.length) {
            el.innerHTML = '<div style="text-align:center;padding:30px;color:#bbb;font-size:13px">暂无上传记录</div>';
            return;
        }
        var h = [];
        for (var i = 0; i < uploads.length; i++) {
            var r = uploads[i];
            var icon = r.status === 'approved' ? '✅' : r.status === 'rejected' ? '❌' : '⏳';
            var badgeClass = r.status === 'approved' ? 'badge-approved' : r.status === 'rejected' ? 'badge-rejected' : 'badge-pending';
            var label = r.status === 'approved' ? '已发布' : r.status === 'rejected' ? '已驳回' : '待审核';
            var title = (r.ai_result && r.ai_result.title) ? r.ai_result.title : '上传内容';
            h.push('<div class="treatment-card" style="padding:12px 14px"><div style="display:flex;align-items:center;gap:10px"><div style="font-size:22px">' + icon + '</div><div style="flex:1"><div style="font-size:13px;font-weight:500">' + title + '</div><div style="font-size:11px;color:#999">' + (r.created_at || '') + '</div></div><span class="badge ' + badgeClass + '">' + label + '</span></div></div>');
        }
        el.innerHTML = h.join('');
    } catch(e) {}
}

// === PROFILE ===
function renderProfile() {
    updateUser();
    var loginDiv = document.getElementById('profileLogin');
    var contentDiv = document.getElementById('profileContent');
    if (user && user.id) {
        if (loginDiv) loginDiv.style.display = 'none';
        if (contentDiv) {
            contentDiv.style.display = 'block';
            document.getElementById('profileName').textContent = user.username || '用户';
            document.getElementById('profilePoints').textContent = user.points || 0;
            document.getElementById('profileBalance').textContent = '¥' + (user.balance && user.balance.toFixed ? user.balance.toFixed(2) : (user.balance || '0.00'));
            document.getElementById('profileRole').textContent = user.role === 'admin' ? '管理员' : '普通用户';
        }
    } else {
        if (loginDiv) loginDiv.style.display = 'block';
        if (contentDiv) contentDiv.style.display = 'none';
    }
}

// === ADMIN ===
async function loadAdmin() {
    try {
        updateUser();
        if (!user || user.role !== 'admin') {
            showToast('需要管理员权限');
            showPage('pageProfile');
            return;
        }
        var pending = await api('/api/admin/pending?status=pending');
        var el = document.getElementById('adminPendingList');
        if (!pending.length) {
            el.innerHTML = '<div style="text-align:center;padding:30px;color:#bbb">暂无待审核内容</div>';
            return;
        }
        var h = [];
        for (var i = 0; i < pending.length; i++) {
            var r = pending[i];
            var title = (r.ai_result && r.ai_result.title) ? r.ai_result.title : '待审核内容';
            h.push('<div class="treatment-card"><div class="tc-header"><div class="tc-title">' + title + '</div></div>' +
                '<div class="tc-meta"><span>上传者: ' + (r.uploader_name || '') + '</span><span>' + (r.created_at || '') + '</span></div>' +
                '<div style="margin-top:8px;font-size:12px;color:#555;max-height:80px;overflow:hidden">' + (r.content || '').substring(0, 200) + '</div>' +
                '<div style="display:flex;gap:8px;margin-top:10px">' +
                '<button class="pay-btn sm" style="background:#e8f5e9;color:#2e7d32" onclick="approveUpload(' + r.id + ')">✅ 通过</button>' +
                '<button class="pay-btn sm" style="background:#ffebee;color:#c62828" onclick="rejectUpload(' + r.id + ')">❌ 驳回</button></div></div>');
        }
        el.innerHTML = h.join('');
    } catch(e) { showToast('加载失败: ' + e.message); }
}

async function approveUpload(id) {
    try {
        await api('/api/admin/review', { method: 'POST', body: { upload_id: id, action: 'approve' } });
        showToast('已通过审核');
        loadAdmin();
    } catch(e) { showToast('操作失败: ' + e.message); }
}

async function rejectUpload(id) {
    var reason = prompt('请输入驳回理由：');
    if (!reason) return;
    try {
        await api('/api/admin/review', { method: 'POST', body: { upload_id: id, action: 'reject', review_note: reason } });
        showToast('已驳回');
        loadAdmin();
    } catch(e) { showToast('操作失败: ' + e.message); }
}
