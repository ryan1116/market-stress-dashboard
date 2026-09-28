/* Display-only language and regime navigation. Financial classifications stay in latest.json. */
let language='en';
let translations={};
const originalText=new WeakMap();
const stages=['GREEN','YELLOW','YELLOW-ORANGE','ORANGE','RED'];
const colors=['#64df94','#f5d761','#ff9b43','#ff7900','#ff7474'];
function stagePosition(regime){return stages.indexOf(regime);}
function translateText(text){
 const clean=text.trim();
 if(translations[clean])return text.replace(clean,translations[clean]);
 return text.replace(/Observation date · /g,'관측일 · ').replace(/%p gap/g,'%p 격차').replace(/%p surprise/g,'%p 서프라이즈').replace(/bp \/ 1M/g,'bp / 1개월').replace(/\b(STALE|CURRENT|AUTO|MANUAL|UNAVAILABLE|Unknown)\b/g,value=>translations[value]||value);
}
function koreanInterpretation(d){
 const v=d.pillars.valuation,x=d.pillars.discount,e=d.pillars.earnings;
 const number=(n,digits=2)=>n==null?'미확인':Number(n).toFixed(digits);
 const signed=(n,digits=0)=>n==null?'미확인':(n>0?'+':'')+number(n,digits);
 const cushions={HIGH:'밸류에이션 완충력이 얇은',ELEVATED:'밸류에이션 완충력이 제한적인',LOW:'밸류에이션 완충력이 비교적 넓은'};
 const pressure={HIGH:'높음',MODERATE:'보통',EASING:'완화'};
 const implications={
  'YELLOW-ORANGE':'이익은 금리 부담을 상쇄할 가능성을 보여주지만, 밸류에이션 완충력은 여전히 얇습니다.',
  ORANGE:'지표 조합은 취약성 확대를 시사합니다. 이익이 금리 부담을 상쇄할 수 있는지 확인해야 합니다.',
  RED:'높은 밸류에이션 취약성·금리 부담·부정적 이익 신호가 겹쳐 복합 위험이 높아진 상태입니다.',
  GREEN:'밸류에이션 완충력과 강한 이익 신호를 바탕으로 지표 조합이 비교적 우호적입니다.',
  YELLOW:'지표가 혼재되어 있습니다. 이익과 할인율 부담의 변화를 함께 살펴봐야 합니다.',
  UNDETERMINED:'필수 입력이 데이터 품질 기준을 충족할 때까지 시장 국면 판정을 보류합니다.'
 };
 return [
  v.state==='UNAVAILABLE'?'필수 입력이 없거나 오래되어 밸류에이션을 신뢰성 있게 평가할 수 없습니다.':`주식 이익수익률과 실질금리의 격차는 ${number(v.equity_yield_gap)}%p로, ${cushions[v.state]||'확인이 필요한'} 상태입니다.`,
  x.state==='UNAVAILABLE'?'유효한 금리 데이터가 없어 할인율 부담을 평가할 수 없습니다.':`실질금리는 1개월간 ${signed(x.real_1m_change_bp)}bp, 3개월간 ${signed(x.real_3m_change_bp)}bp 변했으며, 할인율 부담은 ‘${pressure[x.state]||'미확인'}’입니다.${x.term_premium_quality!=='AUTO'?' 기간 프리미엄은 판정에서 제외됩니다.':''}`,
  e.state==='UNAVAILABLE'?'추정치 데이터가 유효기간 또는 품질 기준을 충족하지 않아 이익 방어력 확인을 보류합니다.':e.source_mode==='AUTO_PROXY'?`이익 프록시의 60일 수정률은 ${signed(e.revision_60d,2)}%이며, ${e.companies_used??'미확인'}개 기업·SPY 비중 ${number(e.coverage_weight==null?null:e.coverage_weight*100,1)}%를 반영합니다.`:`수동 이익 대체값의 수정률은 ${signed(e.revision_60d,2)}%이며, 입력 기준일은 ${e.as_of||'미기록'}입니다.`,
  (implications[d.regime]||'개별 지표를 확인한 뒤 판단해야 합니다.')+(d.regime==='UNDETERMINED'?'':' 계절 기준은 아직 잠정값입니다.')
 ];
}
function renderRegimeScale(){
 const regime=window.dashboardData?.regime;
 const position=stagePosition(regime);
 const ko=language==='ko';
 const list=document.getElementById('regime-scale');
 list.replaceChildren(...stages.map((stage,index)=>{
  const li=document.createElement('li');li.className='regime-step';li.style.setProperty('--stage',colors[index]);
  const current=index===position;if(current)li.setAttribute('aria-current','step');
  const label=document.createElement('span');label.className='step-label';label.textContent=stage;
  const status=document.createElement('span');status.className='step-position';status.textContent=current?(ko?'▲ 현재':'▲ CURRENT'):String(index+1).padStart(2,'0');
  li.append(label,status);li.setAttribute('aria-label',`${stage}, ${index+1} ${ko?'단계 / 전체 5단계':'of 5'}${current?(ko?', 현재 구간':', current regime'):''}`);return li;
 }));
 document.getElementById('regime-caption').textContent=(ko?'현재 시장 국면':'CURRENT REGIME')+(position>=0?` · ${position+1} / 5`:'');
 document.getElementById('scale-start').textContent=ko?'낮은 경계 수준':'Lower concern';
 document.getElementById('scale-end').textContent=ko?'높은 경계 수준':'Higher concern';
 document.getElementById('scale-note').textContent=position<0?(ko?'판정 대기 · 유효한 신호 확인 전에는 구간을 선택하지 않습니다.':'Awaiting classification · no position is assigned without a valid signal.'):(ko?'정성적 구간 · 확률이나 동일한 위험 간격을 의미하지 않습니다.':'Qualitative categories · not probabilities or equal risk intervals.');
 const badge=document.getElementById('regime');
 if(regime)badge.textContent=regime==='UNDETERMINED'&&ko?'판정 보류':regime;
 else badge.textContent=window.dashboardError?(ko?'데이터 확인 불가':'Data unavailable'):(ko?'불러오는 중':'Loading');
 document.querySelector('.regime-overview').setAttribute('aria-label',ko?'시장 국면 전체 구간 및 현재 위치':'Full market regime range and current position');
}
window.applyLanguage=function(){
 const ko=language==='ko';document.documentElement.lang=language;
 const root=document.querySelector('.wrap');
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
 nodes.forEach(node=>{
  if(node.parentElement.closest('.language-toggle,.regime-overview,#note,#asof,#generated,#quality,script'))return;
  if(!originalText.has(node))originalText.set(node,node.nodeValue);
  const original=originalText.get(node);node.nodeValue=ko?translateText(original):original;
 });
 document.querySelectorAll('[data-language]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.language===language)));
 renderRegimeScale();
 const d=window.dashboardData;
 if(d){
  const lines=ko?koreanInterpretation(d):interpretationLines(d);
  document.getElementById('note').replaceChildren(...lines.map(text=>{const span=document.createElement('span');span.className='interpretation-line';span.textContent=text;return span;}));
  document.getElementById('asof').textContent=(ko?'시장 데이터 기준일: ':'Market data as of ')+d.as_of;
  document.getElementById('generated').textContent=ko?`스냅샷 생성: ${d.generated_at||'미기록'}. 주식 이익수익률 격차는 위의 PER 입력일과 실질금리 관측일을 함께 사용합니다. 이익 수정 서프라이즈는 EPS 입력과 잠정 계절 기준을 사용하며 별도의 원자료 기준일은 없습니다.`:`Snapshot generated: ${d.generated_at||'Not recorded'}. Equity yield gap combines the P/E input date and real-yield observation date shown above. Revision surprise uses the EPS input and provisional baseline; it has no independent source date.`;
  const q=d.data_quality;const status=value=>ko?(translations[value]||value):value;
  const labels=ko?['금리','기간 프리미엄','선행 PER','이익','계절 기준']:['Rates','Term premium','Forward P/E','Earnings','Seasonal baseline'];
  const baseline=d.pillars.earnings.baseline_mode;
  const baselineLabels=ko?{PROVISIONAL_CONFIG:'잠정 기준',FACTSET_FALLBACK:'FactSet 대체 입력',EMPIRICAL_SAME_MONTH_MEDIAN:'동일 월 중앙값'}:{PROVISIONAL_CONFIG:'Provisional',FACTSET_FALLBACK:'FactSet fallback',EMPIRICAL_SAME_MONTH_MEDIAN:'Same-month median'};
  document.getElementById('quality').textContent=[q.rates,q.term_premium,q.forward_pe,q.earnings,baselineLabels[baseline]||baseline||'Unknown'].map((value,index)=>labels[index]+': '+status(value)).join(' · ');
 }else if(window.dashboardError){document.getElementById('note').textContent=ko?'데이터를 불러오지 못해 시장 국면 판정을 보류합니다.':'The regime is unavailable because dashboard data could not be loaded.';}
};
document.querySelectorAll('[data-language]').forEach(button=>button.addEventListener('click',()=>{language=button.dataset.language;window.applyLanguage();}));
window.applyLanguage();
fetch('translations.json?v=2').then(response=>{if(!response.ok)throw Error('Translation request failed');return response.json();}).then(data=>{translations=data;window.applyLanguage();}).catch(()=>{language='en';document.querySelector('[data-language="ko"]').disabled=true;window.applyLanguage();});
