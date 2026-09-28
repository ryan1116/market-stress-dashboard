const paperMain=document.querySelector('main');
const paperEnglish=paperMain.innerHTML;
const paperKorean=document.getElementById('paper-korean').innerHTML;
function setPaperLanguage(language,focus=false){
 const ko=language==='ko';
 paperMain.innerHTML=ko?paperKorean:paperEnglish;
 document.documentElement.lang=ko?'ko':'en';
 document.title=ko?'화이트페이퍼 | Market Stress Dashboard':'Whitepaper | Market Stress Dashboard';
 paperMain.querySelectorAll('[data-paper-language]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.paperLanguage===language)));
 paperMain.querySelectorAll('a[href="./"]').forEach(link=>link.href='./?lang='+language);
 if(focus)paperMain.querySelector(`[data-paper-language="${language}"]`).focus();
}
document.addEventListener('click',event=>{
 const button=event.target.closest('[data-paper-language]');if(!button)return;
 const language=button.dataset.paperLanguage;
 const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);
 setPaperLanguage(language,true);
});
setPaperLanguage(new URLSearchParams(location.search).get('lang')==='ko'?'ko':'en');
