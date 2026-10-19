'use strict';
function validateSnapshot(d){
 const finite=x=>typeof x==='number'&&Number.isFinite(x);
 if(!d.assumptions||!finite(d.assumptions.wacc)||d.assumptions.wacc<=-1||!finite(d.assumptions.tax)||!finite(d.assumptions.wc_ratio)||!finite(d.assumptions.opening_wc)||!finite(d.assumptions.shares)||d.assumptions.shares<=0)throw Error('핵심 가정 누락');
 if(d.schema_version!==1||!Array.isArray(d.scenarios)||d.scenarios.length!==3)throw Error('지원하지 않는 자료 형식');
 if(!finite(d.price.value)||d.price.value<=0)throw Error('주가 누락 또는 오류');
 for(const s of d.scenarios){
  if(!finite(s.value)||!finite(s.weight)||s.weight<0||s.weight>1||!finite(s.terminal_growth)||s.terminal_growth>=d.assumptions.wacc)throw Error('시나리오 값 검증 실패');
  if(s.growth.length!==10||s.margins.length!==10||![...s.growth,...s.margins].every(finite))throw Error('10년 가정 누락');
 }
 if(Math.abs(d.scenarios.reduce((n,s)=>n+s.weight,0)-1)>1e-6)throw Error('가중치 합계가 100%가 아님');
 const value=d.scenarios.reduce((n,s)=>n+s.value*s.weight,0);
 if(!finite(d.weighted_value)||Math.abs(value-d.weighted_value)>.01)throw Error('시트와 가중가치 불일치');
 for(const date of [d.model_as_of,d.reviewed_at,d.price.as_of])if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!Number.isFinite(Date.parse(date))||new Date(date).toISOString().slice(0,10)!==date)throw Error('기준일 오류');
 return d;
}
function gap(value,price){return Number.isFinite(price)&&price>0?value/price-1:null;}
if(typeof module!=='undefined')module.exports={validateSnapshot,gap};
if(typeof document!=='undefined'){
 const money=n=>Math.round(n).toLocaleString('ko-KR')+'원',pct=n=>(n*100).toFixed(1)+'%',escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const put=(id,html)=>document.getElementById(id).innerHTML=html;
 const safeURL=s=>{const u=new URL(s);if(u.protocol!=='https:')throw Error('출처 링크 오류');return u.href;};
 async function loadDisclosures(){
  try{
   const res=await fetch('data/investments/disclosures.json',{cache:'no-store'});if(!res.ok)throw Error('공시 자료를 불러오지 못했습니다');
   const d=await res.json();if(d.corp_code!=='00269922'||!Array.isArray(d.items)||d.total!==d.items.length)throw Error('공시 목록 검증 실패');
   const today=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Seoul'});
   document.getElementById('disclosures-status').textContent=`${d.from} ~ ${d.to} · 총 ${d.total}건 · DART 조회 ${d.as_of}${d.as_of<today?' · 최신 조회일 이후 공시는 미반영':''}`;
   put('disclosures',d.items.length?d.items.map(r=>`<tr><td>${escape(r.date)}</td><td><a href="${escape(safeURL(r.url))}" target="_blank" rel="noopener">${escape(r.title)} ↗</a></td><td>${escape(r.filer)}</td><td>${escape(r.remarks.includes('정')?'정정 공시 존재':r.title.includes('정정')?'정정 보고서':'—')}</td></tr>`).join(''):'<tr><td colspan="4">조회 기간 내 공시 없음</td></tr>');
  }catch(e){document.getElementById('disclosures-status').textContent='공시 표시 중단 · '+e.message;put('disclosures','');}
 }
 loadDisclosures();
 async function start(){
  const res=await fetch('data/investments/inbody.json',{cache:'no-store'});if(!res.ok)throw Error('자료를 불러올 수 없음');const d=validateSnapshot(await res.json());
  const today=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Seoul'}),age=(Date.parse(today)-Date.parse(d.price.as_of))/86400000;
  document.getElementById('status').textContent=`주가 ${d.price.as_of} · 모델 ${d.model_as_of} · 검토 ${d.reviewed_at} · ${age<0?'미래 기준일 확인 필요':age>4?'주가 갱신 필요 · 과거 참고값':'기준 자료 표시'} · ${d.reviewed_at<today?'오늘 점검 미완료':'기준 검토일'}`;
  const link=document.getElementById('sheet-link');link.href=safeURL(d.sheet_url);link.target='_blank';link.rel='noopener';
  put('headline',[["비교 주가",money(d.price.value),d.price.as_of],["Normal 주당가치",money(d.scenarios.find(s=>s.name==='Normal').value),'DCF · 검토용'],["가중 주당가치",money(d.weighted_value),`가치 괴리율 ${pct(gap(d.weighted_value,d.price.value))}`],["Low 주당가치",money(d.scenarios.find(s=>s.name==='Low').value),'DCF · 보수 시나리오']].map(([a,b,c])=>`<article class="card"><div class="row"><span class="muted">${escape(a)}</span></div><div class="big">${escape(b)}</div><p class="quality">${escape(c)}</p></article>`).join(''));
  document.getElementById('decision').textContent=d.review.decision;document.getElementById('review-status').textContent=d.review.status;
  put('scenarios',d.scenarios.map(s=>`<tr><th scope="row">${escape(s.name)}</th><td>${money(s.value)}</td><td>${pct(gap(s.value,d.price.value))}</td><td>${pct(s.weight)}</td><td>${pct(s.terminal_growth)}</td></tr>`).join(''));
  const a=d.assumptions;put('assumptions',[["WACC",(a.wacc*100).toFixed(2)+"%"],["정상 세율",pct(a.tax)],["β / Kd / ERP",`${a.beta} / ${pct(a.kd)} / ${pct(a.erp)}`],["운전자본 / 매출",pct(a.wc_ratio)],["기초 운전자본",(a.opening_wc/1e8).toFixed(2)+'억원'],["필요 운영현금",(a.operating_cash/1e8).toFixed(0)+'억원']].map(([k,v])=>`<div class="metric"><span>${escape(k)}</span><b>${escape(v)}</b></div>`).join(''));
  const input=document.getElementById('price-test');input.value=d.price.value;const update=()=>{const g=gap(d.weighted_value,Number(input.value));document.getElementById('price-result').textContent=g===null?'양수 주가를 입력하세요.':`가중가치 대비 괴리율 ${pct(g)}`;};input.addEventListener('input',update);update();
  const select=document.getElementById('scenario-choice');const forecast=()=>{const s=d.scenarios.find(s=>s.name===select.value);put('forecast',d.years.map((y,i)=>`<tr><th scope="row">${y}</th><td>${pct(s.growth[i])}</td><td>${pct(s.margins[i])}</td></tr>`).join(''));const max=Math.max(.01,...s.growth.map(Math.abs));put('growth-chart',s.growth.map((g,i)=>`<div class="growth-column">${pct(g)}<div class="growth-bar" style="height:${Math.abs(g)/max*115}px"></div><small>${d.years[i]}</small></div>`).join(''));};select.addEventListener('change',forecast);forecast();
  put('triggers',d.review.triggers.map(x=>`<tr>${[x.item,x.baseline,x.check,x.status].map(v=>`<td>${escape(v)}</td>`).join('')}</tr>`).join(''));
  put('limitations',d.limitations.map(s=>`<li>${escape(s)}</li>`).join(''));put('sources',d.sources.map(s=>`<p><a href="${escape(safeURL(s.url))}" target="_blank" rel="noopener">${escape(s.label)} ↗</a> <span class="muted">${escape(s.date)}</span></p>`).join('')+`<p class="quality">주가 출처: ${escape(d.price.source)}</p>`);
  try{const h=await fetch('data/investments/history.json',{cache:'no-store'});if(!h.ok)throw Error();const history=await h.json();put('history',history.slice().reverse().map(x=>`<article class="history-item"><time>${escape(x.date)}</time><p>${escape(x.note)}</p><p class="quality">가중가치 ${money(x.weighted_value)} · Normal ${money(x.normal_value)}</p></article>`).join(''));}catch{document.getElementById('history').textContent='변경 이력을 불러오지 못했습니다.';}
 }
 start().catch(e=>{document.getElementById('status').textContent='표시 중단 · '+e.message;for(const id of ['headline','scenarios','forecast','assumptions','growth-chart'])put(id,'');});
}
