/* The public sheet contains data only. Never execute cells as code or HTML. */
function parseCSV(text) {
 const rows=[]; let row=[],value='',quoted=false;
 for(let i=0;i<text.length;i++){
  const c=text[i];
  if(c==='"') {if(quoted&&text[i+1]==='"'){value+='"';i++;}else quoted=!quoted;}
  else if(!quoted&&(c===','||c==='\n'||c==='\r')){
   row.push(value);value='';
   if(c!==','){rows.push(row);row=[];if(c==='\r'&&text[i+1]==='\n')i++;}
  }else value+=c;
 }
 if(quoted)throw Error('Incomplete sheet response');
 if(value||row.length){row.push(value);rows.push(row);}
 return rows;
}
function sheetPayload(text,now=Date.now()) {
 const rows=parseCSV(text.replace(/^\uFEFF/,''));
 if(JSON.stringify(rows.shift())!==JSON.stringify(['msd_path_v1','type','value']))throw Error('Unexpected sheet format');
 const root=Object.create(null),seen=new Set();
 for(const row of rows){
  if(row.every(cell=>cell===''))continue;
  if(row.length!==3)throw Error('Invalid sheet row');
  const [path,type,raw]=row,parts=path.split('.');
  if(!['dashboard','manual'].includes(parts[0])||parts.length<2||parts.some(p=>!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(p)||['constructor','prototype','__proto__'].includes(p))||seen.has(path))throw Error('Invalid or duplicate metric');
  seen.add(path);
  let value=type==='string'?raw:JSON.parse(raw);
  if(!(type==='string'||type==='null'&&value===null||type==='number'&&typeof value==='number'&&Number.isFinite(value)||type==='boolean'&&typeof value==='boolean'||type==='array'&&Array.isArray(value)&&value.every(x=>typeof x==='string')))throw Error('Invalid metric type');
  let target=root;
  for(const key of parts.slice(0,-1)){
   if(Object.hasOwn(target,key)&&(!target[key]||typeof target[key]!=='object'||Array.isArray(target[key])))throw Error('Conflicting metric path');
   target=target[key]??=(Object.create(null));
  }
  if(Object.hasOwn(target,parts.at(-1)))throw Error('Conflicting metric path');
  target[parts.at(-1)]=value;
 }
 const d=root.dashboard,m=root.manual;
 if(!d||!m||!d.pillars||!d.data_quality)throw Error('Missing dashboard data');
 if(!['GREEN','YELLOW','YELLOW-ORANGE','ORANGE','RED','UNDETERMINED'].includes(d.regime))throw Error('Invalid regime');
 for(const key of ['valuation','discount','earnings']){
  const p=d.pillars[key];
  if(!p||typeof p.label!=='string'||!['HIGH','ELEVATED','LOW','MODERATE','EASING','STRONG','NEUTRAL','WEAKENING','NEGATIVE','UNRATED','UNAVAILABLE'].includes(p.state))throw Error('Invalid pillar');
 }
 for(const key of ['forward_pe','eps_fallback','ai_credit_premium_bp'])if(!m[key]||typeof m[key].source!=='string')throw Error('Missing source metadata');
 const stamp=Date.parse(d.generated_at);
 // ponytail: stop displaying an active regime after four days without a completed collection.
 if(!Number.isFinite(stamp)||stamp>now+86400000||now-stamp>4*86400000)throw Error('The sheet snapshot is out of date');
 for(const [value,required] of [[d.as_of,true],[d.pillars.valuation.as_of,true],[d.pillars.earnings.as_of,true],[d.pillars.discount.term_premium_as_of,false]]){
  if(value==null&&!required)continue;
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value)||!Number.isFinite(Date.parse(value)))throw Error('Invalid observation date');
 }
 for(const [p,keys] of [[d.pillars.valuation,['forward_pe','forward_earnings_yield','equity_yield_gap','real10y']],[d.pillars.discount,['real_1m_change_bp','real_3m_change_bp','term_premium','term_premium_1m_change_bp']],[d.pillars.earnings,['revision_60d','revision_surprise','seasonal_benchmark_60d','coverage_weight','companies_used','analyst_revision_breadth']]])
  for(const key of keys)if(!Object.hasOwn(p,key)||(p[key]!==null&&(typeof p[key]!=='number'||!Number.isFinite(p[key]))))throw Error('Missing or invalid metric');
 return [d,m];
}
async function loadDashboardData(){
 const get=async url=>{
  const response=await fetch(url,{signal:AbortSignal.timeout(15000),cache:'no-store',credentials:'omit'});
  if(!response.ok)throw Error('Data request failed');return response;
 };
 const config=await (await get('config/data_backend.json')).json();
 if(config.mode==='repository')return Promise.all(['data/latest.json','config/manual_metrics.json'].map(async path=>(await get(path)).json()));
 if(config.mode!=='google_sheets')throw Error('Unknown data source');
 const url=new URL(config.published_csv_url);
 if(url.protocol!=='https:'||url.hostname!=='docs.google.com'||!url.pathname.startsWith('/spreadsheets/d/e/')||!url.pathname.endsWith('/pub')||url.searchParams.get('output')!=='csv'||!url.searchParams.has('gid')||url.searchParams.get('single')!=='true')throw Error('Expected a published single-tab CSV URL');
 return sheetPayload(await (await get(url.href)).text());
}
if(typeof module!=='undefined')module.exports={parseCSV,sheetPayload};
