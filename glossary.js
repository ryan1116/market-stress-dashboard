const glossary={
  "regime": {
    "aliases": [
      "CURRENT REGIME",
      "현재 시장 국면"
    ],
    "title": {
      "en": "Market regime",
      "ko": "시장 국면"
    },
    "lines": {
      "en": [
        "Combines valuation vulnerability, discount-rate pressure and earnings confirmation.",
        "The five categories describe the current mix of risks; they are not probabilities or trading instructions."
      ],
      "ko": [
        "밸류에이션 취약성·할인율 부담·이익 방어력을 종합한 시장 상태입니다.",
        "5개 구간은 현재 위험의 조합을 나타내며, 확률이나 매매 지시가 아닙니다."
      ]
    }
  },
  "valuation": {
    "aliases": [
      "Valuation Vulnerability"
    ],
    "title": {
      "en": "Valuation vulnerability",
      "ko": "밸류에이션 취약성"
    },
    "lines": {
      "en": [
        "Measures how much valuation cushion equities have relative to real Treasury yields.",
        "A smaller earnings-yield gap indicates less room to absorb shocks, not an imminent market decline."
      ],
      "ko": [
        "주식이 실질 국채금리에 비해 얼마나 밸류에이션 완충력을 갖는지 측정합니다.",
        "이익수익률 격차가 작을수록 충격 흡수 여력이 줄지만, 곧 하락한다는 뜻은 아닙니다."
      ]
    }
  },
  "discount": {
    "aliases": [
      "Discount-Rate Shock"
    ],
    "title": {
      "en": "Discount-rate shock",
      "ko": "할인율 충격"
    },
    "lines": {
      "en": [
        "Tracks changes in real yields over one and three months, with eligible term-premium data as an additional input.",
        "Higher discount rates put pressure on the present value of future earnings."
      ],
      "ko": [
        "실질금리의 1·3개월 변화와 유효한 기간 프리미엄 데이터를 함께 봅니다.",
        "할인율이 상승하면 미래 이익의 현재가치에 하락 압력이 생깁니다."
      ]
    }
  },
  "earnings": {
    "aliases": [
      "Earnings Confirmation"
    ],
    "title": {
      "en": "Earnings confirmation",
      "ko": "이익 방어력"
    },
    "lines": {
      "en": [
        "Assesses whether changes in earnings expectations may offset discount-rate pressure.",
        "The classification uses revision relative to a provisional seasonal benchmark, whose definition remains under research."
      ],
      "ko": [
        "기업이익 전망 변화가 할인율 부담을 상쇄할 수 있는지 살펴봅니다.",
        "잠정 계절 기준 대비 수정률로 분류하며, 계절 기준의 정의는 추가 연구 중입니다."
      ]
    }
  },
  "pe": {
    "aliases": [
      "Forward P/E",
      "Forward P/E · earnings yield"
    ],
    "title": {
      "en": "Forward P/E and earnings yield",
      "ko": "선행 PER과 이익수익률"
    },
    "lines": {
      "en": [
        "Forward P/E compares price with expected earnings; its inverse, 100 / P/E, gives earnings yield in percent.",
        "The dashboard subtracts the 10-year real yield from earnings yield to calculate the equity yield gap."
      ],
      "ko": [
        "선행 PER은 주가를 예상 이익과 비교한 배수이며, 100 / PER이 이익수익률(%)입니다.",
        "이익수익률에서 10년 실질금리를 뺀 값이 대시보드의 주식 이익수익률 격차입니다."
      ]
    }
  },
  "pedate": {
    "aliases": [
      "P/E as of"
    ],
    "title": {
      "en": "P/E reference date",
      "ko": "PER 기준일"
    },
    "lines": {
      "en": [
        "The date attached to the manually entered forward P/E, not the page refresh time.",
        "An input older than the configured validity limit is excluded from the active regime assessment."
      ],
      "ko": [
        "수동 입력된 선행 PER의 기준일이며, 화면을 새로고침한 시각이 아닙니다.",
        "설정된 유효기간을 넘긴 입력값은 현재 시장 국면 판정에서 제외합니다."
      ]
    }
  },
  "real": {
    "aliases": [
      "10Y real",
      "10Y real yield · 1M / 3M changes"
    ],
    "title": {
      "en": "10-year real yield",
      "ko": "10년 실질금리"
    },
    "lines": {
      "en": [
        "Uses the FRED DFII10 series for the yield on 10-year inflation-protected Treasuries.",
        "It is a discount-rate reference for equities; the level and speed of change convey different information."
      ],
      "ko": [
        "물가연동국채의 10년 수익률인 FRED DFII10 시계열을 사용합니다.",
        "주식의 할인율을 살피는 기준이며, 금리 수준과 변화 속도는 서로 다른 정보를 줍니다."
      ]
    }
  },
  "change": {
    "aliases": [
      "Real yield 3M Δ"
    ],
    "title": {
      "en": "Real-yield change",
      "ko": "실질금리 변화"
    },
    "lines": {
      "en": [
        "Shows the change from approximately three calendar months earlier, using available observations.",
        "One basis point is 0.01 percentage point; +50 bp means a rise of 0.50 percentage point."
      ],
      "ko": [
        "약 3개월 전과 비교한 실질금리 변화이며, 해당 시점의 가용 관측값을 사용합니다.",
        "1bp는 0.01%p입니다. +50bp는 금리가 0.50%p 올랐다는 뜻입니다."
      ]
    }
  },
  "term": {
    "aliases": [
      "Term premium / as of",
      "10Y term premium · 1M change"
    ],
    "title": {
      "en": "Term premium",
      "ko": "기간 프리미엄"
    },
    "lines": {
      "en": [
        "The Kim–Wright model estimates the extra compensation for holding a long-term bond rather than rolling over short-term debt.",
        "This is a model estimate with its own observation date and publication lag, not a directly observed market price."
      ],
      "ko": [
        "Kim–Wright 모델이 장기채 보유에 대해 단기채 차환 대비 요구되는 추가 보상을 추정합니다.",
        "별도의 관측일과 발표 시차를 갖는 모델 추정치이며, 직접 관측되는 시장가격은 아닙니다."
      ]
    }
  },
  "termstatus": {
    "aliases": [
      "Term premium status"
    ],
    "title": {
      "en": "Term-premium data status",
      "ko": "기간 프리미엄 자료 상태"
    },
    "lines": {
      "en": [
        "Indicates whether the observation is current enough to contribute to the shock classification.",
        "Outdated values remain visible for reference but are excluded from the active signal."
      ],
      "ko": [
        "관측값이 할인율 충격 판정에 사용할 만큼 최신인지 표시합니다.",
        "오래된 값은 참고용으로 보여주지만 현재 신호 계산에서는 제외합니다."
      ]
    }
  },
  "termchange": {
    "aliases": [
      "Term premium 1M Δ"
    ],
    "title": {
      "en": "One-month term-premium change",
      "ko": "기간 프리미엄 1개월 변화"
    },
    "lines": {
      "en": [
        "Measures the term-premium change in basis points, ending on its own latest observation date.",
        "A rise suggests greater required compensation for long-duration risk; outdated observations are not used in the signal."
      ],
      "ko": [
        "기간 프리미엄의 최신 관측일을 종료일로 삼아 약 1개월 변화를 bp로 표시합니다.",
        "상승은 장기 위험에 대한 요구 보상의 증가를 시사하며, 오래된 관측값은 신호에 사용하지 않습니다."
      ]
    }
  },
  "epsdate": {
    "aliases": [
      "Earnings date / status"
    ],
    "title": {
      "en": "Earnings date and status",
      "ko": "이익 기준일과 상태"
    },
    "lines": {
      "en": [
        "For the automated proxy, the date is the collection date, not each analyst estimate’s update time.",
        "The status reflects freshness and coverage requirements; a fallback is a separately dated manual input."
      ],
      "ko": [
        "자동 프록시의 날짜는 수집일이며, 개별 애널리스트 추정치의 수정 시각이 아닙니다.",
        "상태는 유효기간과 표본 기준을 반영하며, 대체값은 별도 기준일을 가진 수동 입력입니다."
      ]
    }
  },
  "revision": {
    "aliases": [
      "60D EPS revision",
      "EPS revisions · analyst breadth · SPY coverage"
    ],
    "title": {
      "en": "EPS revision",
      "ko": "EPS 수정률"
    },
    "lines": {
      "en": [
        "Measures the change in future fiscal-year EPS estimates over 60 days, weighted by the covered SPY holdings.",
        "It uses 100 × (current − prior) / |prior|; zero prior EPS is excluded, and a small denominator can magnify the result."
      ],
      "ko": [
        "향후 회계연도 EPS 추정치의 60일 변화를 수집된 SPY 보유비중으로 가중합니다.",
        "100 × (현재−과거) / |과거|를 사용합니다. 과거 EPS가 0이면 제외하며, 분모가 작으면 수정률이 크게 나타날 수 있습니다."
      ]
    }
  },
  "seasonal": {
    "aliases": [
      "Seasonal baseline (provisional)"
    ],
    "title": {
      "en": "Seasonal baseline",
      "ko": "계절 기준"
    },
    "lines": {
      "en": [
        "A provisional reference for how earnings estimates would normally change over a comparable period.",
        "Revision surprise subtracts this benchmark from actual revision; comparability with the automated proxy is not yet validated."
      ],
      "ko": [
        "비교 가능한 기간에 이익 추정치가 통상 얼마나 변하는지를 나타내는 잠정 기준입니다.",
        "실제 수정률에서 이 기준을 빼면 수정 서프라이즈가 됩니다. 자동 프록시와의 비교 가능성은 아직 검증되지 않았습니다."
      ]
    }
  },
  "coverage": {
    "aliases": [
      "SPY weight coverage"
    ],
    "title": {
      "en": "SPY weight coverage",
      "ko": "SPY 비중 커버리지"
    },
    "lines": {
      "en": [
        "The combined SPY holding weight of companies with usable EPS estimates.",
        "It is not a percentage of company count; missing large holdings can materially affect the proxy."
      ],
      "ko": [
        "사용 가능한 EPS 추정치를 확보한 기업들의 SPY 보유비중 합계입니다.",
        "기업 수의 비율이 아닙니다. 대형 종목이 누락되면 프록시가 크게 달라질 수 있습니다."
      ]
    }
  },
  "breadth": {
    "aliases": [
      "Analyst breadth"
    ],
    "title": {
      "en": "Analyst revision breadth",
      "ko": "애널리스트 수정 확산도"
    },
    "lines": {
      "en": [
        "Calculated as (upward revisions − downward revisions) / (upward revisions + downward revisions) over 30 days.",
        "The range is −1 to +1; a positive value means more upward revisions within the collected sample."
      ],
      "ko": [
        "30일간 (상향 수정 수−하향 수정 수) / (상향 수정 수+하향 수정 수)로 계산합니다.",
        "범위는 −1~+1이며, 양수는 수집 표본 내 상향 수정 건수가 더 많다는 뜻입니다."
      ]
    }
  },
  "nominal": {
    "aliases": [
      "10Y nominal Treasury yield"
    ],
    "title": {
      "en": "10-year nominal Treasury yield",
      "ko": "미국 10년 명목금리"
    },
    "lines": {
      "en": [
        "The stated yield on a conventional 10-year U.S. Treasury, before adjusting for inflation.",
        "It provides market context; the absolute nominal level does not directly determine the dashboard regime."
      ],
      "ko": [
        "인플레이션을 차감하기 전 일반 미국 10년 국채의 수익률입니다.",
        "시장 참고 정보로 사용하며, 명목금리의 절대 수준만으로 시장 국면을 결정하지 않습니다."
      ]
    }
  },
  "breakeven": {
    "aliases": [
      "10Y breakeven inflation"
    ],
    "title": {
      "en": "Breakeven inflation",
      "ko": "기대인플레이션 (BEI)"
    },
    "lines": {
      "en": [
        "The gap between nominal Treasury and inflation-protected Treasury yields of comparable maturity.",
        "It reflects inflation compensation, including risk and liquidity effects, rather than a pure inflation forecast."
      ],
      "ko": [
        "만기가 유사한 명목국채와 물가연동국채 수익률의 차이입니다.",
        "인플레이션 보상뿐 아니라 위험·유동성 요인이 포함되어 순수한 물가 전망과는 다릅니다."
      ]
    }
  },
  "credit": {
    "aliases": [
      "AI credit premium (context)"
    ],
    "title": {
      "en": "AI credit premium",
      "ko": "AI 신용 프리미엄"
    },
    "lines": {
      "en": [
        "A manually entered reference for financing pressure related to the AI investment cycle.",
        "It is contextual and does not enter the three-pillar regime calculation; the source record is shown below."
      ],
      "ko": [
        "AI 투자 사이클과 관련된 자금조달 부담을 살피기 위한 수동 참고 입력입니다.",
        "3개 축의 시장 국면 계산에는 포함되지 않으며, 기록된 출처는 하단 표에서 확인할 수 있습니다."
      ]
    }
  },
  "GREEN": {
    "aliases": [
      "GREEN"
    ],
    "title": {
      "en": "GREEN",
      "ko": "GREEN"
    },
    "lines": {
      "en": [
        "Relatively supportive pillar combination, with a wider valuation cushion and strong earnings confirmation.",
        "This is a qualitative regime classification, not a crash probability or a trading instruction."
      ],
      "ko": [
        "밸류에이션 완충력이 비교적 넓고 이익 방어력이 강한 우호적 지표 조합입니다.",
        "정성적 시장 구간이며, 폭락 확률이나 매매 지시를 뜻하지 않습니다."
      ]
    }
  },
  "YELLOW": {
    "aliases": [
      "YELLOW"
    ],
    "title": {
      "en": "YELLOW",
      "ko": "YELLOW"
    },
    "lines": {
      "en": [
        "A mixed combination of valuation, rates and earnings calls for continued monitoring.",
        "This is a qualitative regime classification, not a crash probability or a trading instruction."
      ],
      "ko": [
        "밸류에이션·금리·이익 신호가 혼재되어 지속적인 관찰이 필요한 구간입니다.",
        "정성적 시장 구간이며, 폭락 확률이나 매매 지시를 뜻하지 않습니다."
      ]
    }
  },
  "YELLOW-ORANGE": {
    "aliases": [
      "YELLOW-ORANGE"
    ],
    "title": {
      "en": "YELLOW-ORANGE",
      "ko": "YELLOW-ORANGE"
    },
    "lines": {
      "en": [
        "High valuation vulnerability and rate pressure are accompanied by strong earnings confirmation.",
        "This is a qualitative regime classification, not a crash probability or a trading instruction."
      ],
      "ko": [
        "높은 밸류에이션 취약성과 금리 부담을 강한 이익 신호가 상쇄하는 구간입니다.",
        "정성적 시장 구간이며, 폭락 확률이나 매매 지시를 뜻하지 않습니다."
      ]
    }
  },
  "ORANGE": {
    "aliases": [
      "ORANGE"
    ],
    "title": {
      "en": "ORANGE",
      "ko": "ORANGE"
    },
    "lines": {
      "en": [
        "The pillar combination indicates heightened vulnerability, with less reassuring offsets.",
        "This is a qualitative regime classification, not a crash probability or a trading instruction."
      ],
      "ko": [
        "지표 조합상 취약성이 높아지고 이를 상쇄할 근거가 약해진 경계 구간입니다.",
        "정성적 시장 구간이며, 폭락 확률이나 매매 지시를 뜻하지 않습니다."
      ]
    }
  },
  "RED": {
    "aliases": [
      "RED"
    ],
    "title": {
      "en": "RED",
      "ko": "RED"
    },
    "lines": {
      "en": [
        "High valuation vulnerability, high rate pressure and negative earnings confirmation coincide.",
        "This is a qualitative regime classification, not a crash probability or a trading instruction."
      ],
      "ko": [
        "높은 밸류에이션 취약성·높은 금리 부담·부정적 이익 신호가 동시에 나타난 구간입니다.",
        "정성적 시장 구간이며, 폭락 확률이나 매매 지시를 뜻하지 않습니다."
      ]
    }
  },
  "gap": {
    "aliases": [],
    "title": {
      "en": "Equity yield gap",
      "ko": "주식 이익수익률 격차"
    },
    "lines": {
      "en": [
        "Forward earnings yield minus the 10-year real Treasury yield, expressed in percentage points.",
        "A smaller gap indicates a thinner valuation cushion; it is not a forecast of near-term returns."
      ],
      "ko": [
        "선행 이익수익률에서 10년 실질국채금리를 뺀 값이며, 단위는 %p입니다.",
        "격차가 작을수록 밸류에이션 완충력이 얇다는 뜻이며, 단기 수익률 전망은 아닙니다."
      ]
    }
  },
  "real1m": {
    "aliases": [],
    "title": {
      "en": "One-month real-yield change",
      "ko": "실질금리 1개월 변화"
    },
    "lines": {
      "en": [
        "The change in the 10-year real yield over approximately 30 calendar days, expressed in basis points.",
        "A positive number indicates an increase in real discount-rate pressure; 100 bp equals 1 percentage point."
      ],
      "ko": [
        "약 30일간 10년 실질금리가 얼마나 변했는지 bp로 표시합니다.",
        "양수는 실질 할인율 부담의 증가를 나타냅니다. 100bp는 1%p입니다."
      ]
    }
  },
  "surprise": {
    "aliases": [],
    "title": {
      "en": "EPS revision surprise",
      "ko": "EPS 수정 서프라이즈"
    },
    "lines": {
      "en": [
        "The 60-day EPS revision minus the provisional seasonal baseline, expressed in percentage points.",
        "A positive result is stronger than that benchmark, but the benchmark’s comparability with this proxy remains under research."
      ],
      "ko": [
        "60일 EPS 수정률에서 잠정 계절 기준을 뺀 값이며, 단위는 %p입니다.",
        "양수는 해당 기준보다 강하다는 뜻이지만, 프록시와 계절 기준의 비교 가능성은 연구 중입니다."
      ]
    }
  }
};
let helpAnchor=null;
const helpPanel=document.createElement('div');
helpPanel.id='term-help-panel';helpPanel.className='term-popover';helpPanel.hidden=true;
helpPanel.setAttribute('role','dialog');helpPanel.setAttribute('aria-labelledby','term-help-title');
const helpTitle=document.createElement('strong');helpTitle.id='term-help-title';
const helpClose=document.createElement('button');helpClose.type='button';helpClose.className='help-close';helpClose.textContent='×';
const helpBody=document.createElement('div');helpPanel.append(helpTitle,helpClose,helpBody);document.body.appendChild(helpPanel);
function closeTermHelp(restore=false){
 const old=helpAnchor;if(old)old.setAttribute('aria-expanded','false');helpPanel.hidden=true;helpAnchor=null;
 if(restore&&old?.isConnected)old.focus();
}
function positionTermHelp(){
 if(!helpAnchor)return;
 if(!helpAnchor.isConnected){closeTermHelp();return;}
 const box=helpAnchor.getBoundingClientRect(),width=helpPanel.offsetWidth,height=helpPanel.offsetHeight;
 const left=Math.max(10,Math.min(box.left,window.innerWidth-width-10));
 const top=box.bottom+10+height<=window.innerHeight-10?box.bottom+10:Math.max(10,box.top-height-10);
 helpPanel.style.left=left+'px';helpPanel.style.top=top+'px';
}
function showTermHelp(button,key){
 if(helpAnchor===button){closeTermHelp(true);return;}
 closeTermHelp();helpAnchor=button;const lang=document.documentElement.lang==='ko'?'ko':'en';const term=glossary[key];
 helpTitle.textContent=term.title[lang];helpClose.setAttribute('aria-label',lang==='ko'?'설명 닫기':'Close explanation');
 helpBody.replaceChildren(...term.lines[lang].map(text=>{const p=document.createElement('p');p.textContent=text;return p;}));
 button.setAttribute('aria-expanded','true');helpPanel.hidden=false;positionTermHelp();helpClose.focus();
}
window.installTermHelp=function(){
 closeTermHelp();
 const lang=document.documentElement.lang==='ko'?'ko':'en';
 document.querySelectorAll('#grid .big,#grid .row > .muted,#grid .metric > span:first-child,#sources td:first-child,#regime-caption,#regime-scale .step-label').forEach(label=>{
  const text=Array.from(label.childNodes).filter(node=>node.nodeType===Node.TEXT_NODE).map(node=>node.textContent).join('').trim().replace(/ · \d \/ 5$/,'');
  const headline=label.matches('#grid .big')?['gap','real1m','surprise'][Array.from(document.querySelectorAll('#grid .big')).indexOf(label)]:null;
  const key=label.dataset.helpKey||headline||Object.keys(glossary).find(key=>glossary[key].aliases.some(alias=>alias===text||(typeof translations!=='undefined'&&translations[alias]===text)));
  if(!key)return;label.dataset.helpKey=key;
  let button=label.querySelector('.term-help');
  if(!button){button=document.createElement('button');button.type='button';button.className='term-help';button.textContent='?';button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-controls',helpPanel.id);button.addEventListener('click',event=>{event.stopPropagation();showTermHelp(button,key);});label.appendChild(button);}
  button.setAttribute('aria-expanded','false');button.setAttribute('aria-label',(lang==='ko'?'용어 설명: ':'Explain: ')+glossary[key].title[lang]);
 });
};
helpClose.addEventListener('click',()=>closeTermHelp(true));
document.addEventListener('click',event=>{if(!helpPanel.contains(event.target)&&event.target!==helpAnchor)closeTermHelp();});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&helpAnchor){event.preventDefault();closeTermHelp(true);}});
document.addEventListener('focusin',event=>{if(helpAnchor&&!helpPanel.contains(event.target)&&event.target!==helpAnchor)closeTermHelp();});
window.addEventListener('resize',positionTermHelp);window.addEventListener('scroll',positionTermHelp,true);
