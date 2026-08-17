/* ═══════════════════════════════════════════════════════════════════════
   KHOPHIMCHAT — LÕI DÙNG CHUNG (index.html + phim.html + xem-phim.html)
   Toàn bộ phần gọi API / chuẩn hóa dữ liệu / render card đặt ở đây để 2
   trang không lặp code. Trang nào cần logic riêng (hero, player...) thì
   viết thêm trong <script> riêng của trang đó, dùng lại các hàm ở file này.
═══════════════════════════════════════════════════════════════════════ */

var SRC_NAMES={kkphim:'KKPhim',nguonc:'Nguồn C',vsmov:'VSMOV'};
var SRC_LIST=['kkphim','nguonc','vsmov'];

function esc(s){return (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function jsEsc(s){return (s||'').toString().replace(/\\/g,'\\\\').replace(/'/g,"\\'");}
function qs(sel,root){return (root||document).querySelector(sel);}
function qsa(sel,root){return Array.prototype.slice.call((root||document).querySelectorAll(sel));}

/* ── Nguồn đang chọn — lưu localStorage, dùng xuyên suốt mọi trang ── */
function getSource(){return localStorage.getItem('kpc_source')||'kkphim';}
function setSource(s){localStorage.setItem('kpc_source',s);}
var currentSource=getSource();

/* ═══════════════════════════════════════════════════════════════════════
   NGUỒN C — GỌI TRỰC TIẾP TỪ TRÌNH DUYỆT
   Server (Vercel) bị NguonC chặn theo IP hosting, nên riêng nguồn này gọi
   thẳng từ trình duyệt người xem (IP cá nhân không bị chặn kiểu này).
═══════════════════════════════════════════════════════════════════════ */
var NGUONC_BASE='https://phim.nguonc.com/api';

function nguoncUrl(o){
  var page=o.page||'1';
  if(o.slug) return NGUONC_BASE+'/film/'+encodeURIComponent(o.slug);
  if(o.keyword) return NGUONC_BASE+'/films/search?keyword='+encodeURIComponent(o.keyword);
  if(o.cat) return NGUONC_BASE+'/films/the-loai/'+encodeURIComponent(o.cat)+'?page='+page;
  if(o.nation) return NGUONC_BASE+'/films/quoc-gia/'+encodeURIComponent(o.nation)+'?page='+page;
  if(o.year) return NGUONC_BASE+'/films/nam-phat-hanh/'+encodeURIComponent(o.year)+'?page='+page;
  if(o.type) return NGUONC_BASE+'/films/danh-sach/'+encodeURIComponent(o.type)+'?page='+page;
  return NGUONC_BASE+'/films/phim-moi-cap-nhat?page='+page;
}

function nguoncNormItem(raw){
  return {
    name: raw.name||raw.title||'',
    origin_name: raw.origin_name||raw.original_name||'',
    slug: raw.slug||'',
    thumb_url: raw.thumb_url||'',
    poster_url: raw.poster_url||raw.thumb_url||'',
    year: raw.publish_year||raw.year||'',
    quality: raw.quality||'',
    lang: raw.language||raw.lang||'',
    episode_current: raw.current_episode||raw.total_episodes||'',
    time: raw.time||'',
    source: 'nguonc',
  };
}

function nguoncNormList(raw){
  var items=(raw&&raw.items)||(raw&&raw.data&&raw.data.items)||[];
  return items.map(nguoncNormItem);
}

function nguoncNormDetail(raw, slug){
  var movie=raw&&raw.movie;
  if(!movie) return null;
  var category=[],country=[];
  var cf=movie.category;
  if(cf&&typeof cf==='object'&&!Array.isArray(cf)){
    Object.keys(cf).forEach(function(k){
      var grp=cf[k];if(!grp)return;
      var gname=(grp.group_name||'').toLowerCase();
      var lst=(grp.list||[]).map(function(x){return{name:x.name||'',slug:x.slug||x.id||''};});
      if(gname.indexOf('loại')>=0||gname.indexOf('loai')>=0)category=lst;
      else if(gname.indexOf('gia')>=0||gname.indexOf('quốc')>=0)country=lst;
    });
  }
  var casts=movie.casts||movie.actor||'';
  var actor=typeof casts==='string'?casts.split(',').map(function(s){return s.trim();}).filter(Boolean):(Array.isArray(casts)?casts:[]);
  var dirRaw=movie.director||'';
  var director=typeof dirRaw==='string'?dirRaw.split(',').map(function(s){return s.trim();}).filter(Boolean):(Array.isArray(dirRaw)?dirRaw:[]);
  var rawEps=movie.episodes||raw.episodes||[];
  var episodes=rawEps.map(function(sv){
    var its=sv.items||sv.server_data||[];
    return{
      server_name: sv.server_name||'Server',
      server_data: its.map(function(e){return{name:e.name||e.slug||'',slug:e.slug||'',link_embed:e.embed||e.link_embed||'',link_m3u8:e.m3u8||e.link_m3u8||''};}),
    };
  });
  return{
    name: movie.name||'', origin_name: movie.original_name||movie.origin_name||'',
    slug: movie.slug||slug, content: movie.description||movie.content||'',
    thumb_url: movie.thumb_url||'', poster_url: movie.poster_url||movie.thumb_url||'',
    year: movie.publish_year||movie.year||'', quality: movie.quality||'',
    lang: movie.language||movie.lang||'', episode_current: movie.current_episode||'',
    time: movie.time||'', actor: actor, director: director, category: category,
    country: country, episodes: episodes, source: 'nguonc',
  };
}

function fetchNguoncDirect(paramsStr){
  var qp=new URLSearchParams(paramsStr);
  var o={slug:qp.get('path')||'',keyword:qp.get('keyword')||'',cat:qp.get('cat')||'',
    nation:qp.get('nation')||'',year:qp.get('year')||'',type:qp.get('type')||'',page:qp.get('page')||'1'};
  return fetch(nguoncUrl(o),{headers:{'Accept':'application/json'}}).then(function(r){
    if(!r.ok) throw new Error('http '+r.status);
    return r.json();
  }).then(function(raw){
    if(o.slug){
      var item=nguoncNormDetail(raw,o.slug);
      return{status:!!item,source:'nguonc',data:{item:item}};
    }
    return{status:true,source:'nguonc',data:{items:nguoncNormList(raw)}};
  }).catch(function(){
    return qp.get('path')?{status:false,source:'nguonc'}:{status:true,source:'nguonc',data:{items:[]}};
  });
}

/* Lớp trung gian: mọi nơi gọi API đều đi qua đây. */
function apiProxy(paramsStr){
  if(/(^|&)source=nguonc(&|$)/.test(paramsStr)){
    return fetchNguoncDirect(paramsStr);
  }
  return fetch('/api/proxy?'+paramsStr).then(function(r){return r.json();});
}

/* ═══════════════════════════════════════════════════════════════════════
   CACHE NHẸ TRONG BỘ NHỚ — hiện dữ liệu tức thì khi chuyển trang
   Lưu lại info phim (tên, ảnh...) mỗi khi card được render, đồng thời ghi
   vào sessionStorage để trang phim.html (điều hướng thật, không phải
   modal) đọc lại ngay lập tức trong lúc chờ tải chi tiết đầy đủ.
═══════════════════════════════════════════════════════════════════════ */
function cacheItem(m){
  if(!m||!m.slug) return m;
  try{
    sessionStorage.setItem('kpc_quick:'+(m.source||currentSource)+'|'+m.slug, JSON.stringify(m));
  }catch(e){/* storage đầy hoặc bị chặn -> bỏ qua, không quan trọng */}
  return m;
}
function getQuickCache(source,slug){
  try{
    var raw=sessionStorage.getItem('kpc_quick:'+source+'|'+slug);
    return raw?JSON.parse(raw):null;
  }catch(e){return null;}
}

/* ── Ảnh lỗi (thường do CDN chặn hotlink) -> thử lại qua /api/img ── */
window.imgFallback=function(img){
  if(img.dataset.tried){img.style.opacity='0';img.style.background='#1b1b26';img.onerror=null;return;}
  img.dataset.tried='1';
  var src=img.dataset.src||img.src, source=img.dataset.source||currentSource;
  if(!src){img.style.opacity='0';return;}
  img.src='/api/img?url='+encodeURIComponent(src)+'&source='+encodeURIComponent(source);
};

/* ═══════════════════════════════════════════════════════════════════════
   RENDER CARD PHIM — dùng chung cho row ngang, lưới, liên quan
═══════════════════════════════════════════════════════════════════════ */
function cardHtml(m,showSrcBadge){
  cacheItem(m);
  var poster=m.poster_url||m.thumb_url||'';
  var src=m.source||currentSource;
  var href='phim.html?slug='+encodeURIComponent(m.slug)+'&source='+encodeURIComponent(src);
  return '<a class="card" href="'+href+'" data-slug="'+esc(m.slug)+'" data-source="'+src+'">'+
    '<div class="card-img">'+
      (showSrcBadge?'<div class="card-src">'+(SRC_NAMES[src]||src)+'</div>':'')+
      (m.episode_current?'<div class="card-badge">'+esc(m.episode_current)+'</div>':'')+
      '<img src="'+poster+'" data-src="'+esc(poster)+'" data-source="'+src+'" loading="lazy" alt="'+esc(m.name)+'" onerror="imgFallback(this)">'+
      '<div class="card-play"><span>&#9654;</span></div>'+
    '</div>'+
    '<div class="card-title">'+esc(m.name)+'</div>'+
  '</a>';
}

function skeletonCards(n){
  var out='';
  for(var i=0;i<n;i++){out+='<div class="card sk-card"><div class="card-img sk"></div><div class="card-title sk sk-title">&nbsp;</div></div>';}
  return out;
}

/* ═══════════════════════════════════════════════════════════════════════
   ĐIỀU HƯỚNG — thanh loading mỏng trên đầu trang khi chuyển link
═══════════════════════════════════════════════════════════════════════ */
(function(){
  var bar=document.createElement('div');
  bar.className='route-bar';
  document.addEventListener('DOMContentLoaded',function(){document.body.appendChild(bar);});
  document.addEventListener('click',function(e){
    var a=e.target.closest && e.target.closest('a[href]');
    if(!a) return;
    var href=a.getAttribute('href')||'';
    if(href.indexOf('http')===0 || href.indexOf('#')===0 || a.target==='_blank') return;
    bar.className='route-bar on';
  });
})();

/* ═══════════════════════════════════════════════════════════════════════
   NAV DÙNG CHUNG — logo/source-switcher/search/menu mobile/tab-bar
   Gọi initSharedNav('home'|'watch') ở cuối mỗi trang sau khi DOM đã có
   sẵn khung .site-nav / .mobile-menu / .tab-bar (đánh dấu bằng data-page).
═══════════════════════════════════════════════════════════════════════ */
function initSourceSwitcher(onChange){
  var pill=qs('#srcPill'), menu=qs('#srcMenu');
  if(!pill||!menu) return;
  function render(){
    qs('#srcPillLabel').textContent=SRC_NAMES[currentSource]||currentSource;
    qsa('.src-opt',menu).forEach(function(o){o.classList.toggle('on',o.dataset.src===currentSource);});
  }
  render();
  pill.addEventListener('click',function(e){e.stopPropagation();menu.classList.toggle('open');});
  document.addEventListener('click',function(){menu.classList.remove('open');});
  qsa('.src-opt',menu).forEach(function(o){
    o.addEventListener('click',function(e){
      e.stopPropagation();
      currentSource=o.dataset.src;setSource(currentSource);
      render();menu.classList.remove('open');
      if(onChange) onChange(currentSource);
    });
  });
}

function initSearchToggle(onSearch){
  var toggle=qs('#searchToggle'), box=qs('#searchBox');
  if(!toggle||!box) return;
  toggle.addEventListener('click',function(){
    box.classList.toggle('open');
    if(box.classList.contains('open')) box.focus();
  });
  box.addEventListener('keypress',function(e){
    if(e.key==='Enter' && box.value.trim()){ onSearch(box.value.trim()); }
  });
  document.addEventListener('click',function(e){
    if(!box.classList.contains('open')) return;
    if(e.target!==box && e.target!==toggle && !toggle.contains(e.target)){
      if(!box.value.trim()) box.classList.remove('open');
    }
  });
}

function initMobileMenu(){
  var burger=qs('#hamburger'), menu=qs('#mobileMenu');
  if(!burger||!menu) return;
  burger.addEventListener('click',function(){menu.classList.toggle('open');});
}

/* ═══════════════════════════════════════════════════════════════════════
   PHIM LIÊN QUAN — dùng chung cho phim.html (trang thông tin) và
   xem-phim.html (trang player), tránh lặp code fetch/render 2 nơi.
═══════════════════════════════════════════════════════════════════════ */
function loadRelatedMovies(active, source, slug, rowSelector, sectionSelector){
  var cat=(active.category&&active.category[0]&&active.category[0].slug)||(active.country&&active.country[0]&&active.country[0].slug);
  var params=cat?('cat='+cat):'';
  return apiProxy(params+'&source='+encodeURIComponent(source)).then(function(res){
    var items=((res.data&&res.data.items)||[]).filter(function(m){return m.slug!==slug;}).slice(0,12);
    var sectionEl=qs(sectionSelector);
    if(!items.length){if(sectionEl)sectionEl.style.display='none';return;}
    qs(rowSelector).innerHTML=items.map(function(m){return cardHtml(m,false);}).join('');
  }).catch(function(){var sectionEl=qs(sectionSelector);if(sectionEl)sectionEl.style.display='none';});
}

/* ═══════════════════════════════════════════════════════════════════════
   TICKET/CHIP/CREW HTML — dùng chung cho phim.html và xem-phim.html
═══════════════════════════════════════════════════════════════════════ */
function ticketHtml(active, source){
  var t='';
  if(active.quality) t+='<span class="tk gold">'+esc(active.quality)+'</span>';
  if(active.year) t+='<span class="tk">'+esc(active.year)+'</span>';
  if(active.episode_current) t+='<span class="tk teal">'+esc(active.episode_current)+'</span>';
  if(active.lang) t+='<span class="tk">'+esc(active.lang)+'</span>';
  t+='<span class="tk">'+(SRC_NAMES[source]||source)+'</span>';
  return t;
}
function chipsHtml(active){
  var c='';
  (active.category||[]).forEach(function(x){c+='<span class="chip">'+esc(x.name)+'</span>';});
  (active.country||[]).forEach(function(x){c+='<span class="chip">'+esc(x.name)+'</span>';});
  return c;
}
function crewHtml(active){
  var c='';
  if(active.director&&active.director.length) c+='<div class="crew-block"><b>Đạo diễn</b><span>'+esc(active.director.join(', '))+'</span></div>';
  if(active.actor&&active.actor.length) c+='<div class="crew-block"><b>Diễn viên</b><span>'+esc(active.actor.slice(0,10).join(', '))+'</span></div>';
  return c;
}
