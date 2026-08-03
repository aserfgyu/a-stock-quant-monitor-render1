class QM {
    constructor() {
        this.ws=null; this.d={}; this.c={}; this.rc=5000;
        this.api=window.location.origin;
        this.init();
    }
    init() {
        this.sk();
        this.cw();
        this.fd();
    }
    sk() {
        const app=document.getElementById('app');
        if(!app)return;
        app.innerHTML=`<div class="header"><div><h1>A股量化全景监控中心</h1><div class="sub">多因子评分 · 技术信号 · 资金流向 · 实时量化 · Tushare数据源</div></div><div class="header-right"><div class="dot"></div><span id="cs">连接中...</span><span style="margin:0 6px;color:var(--tt)">|</span><span id="ut">--</span></div></div>
        <div class="g4">${['000001_SH','399001_SZ','399006_SZ','000300_SH'].map(k=>`<div class="card" data-key="${k}" onclick="qm.dl('${k}')"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span class="n">${this.nm(k)}</span><span class="score" id="${k}-sc">--</span></div><div class="p" id="${k}-pr">--</div><div class="f"><span id="${k}-ch">--</span><span id="${k}-si" style="font-size:11px;color:var(--tt)">--</span></div></div>`).join('')}</div>
        <div class="g2"><div class="card" data-key="000688_SH" onclick="qm.dl('000688_SH')"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span class="n">科创50</span><span class="score" id="000688_SH-sc">--</span></div><div class="p" id="000688_SH-pr">--</div><div class="f"><span id="000688_SH-ch">--</span><span id="000688_SH-si" style="font-size:11px;color:var(--tt)">--</span></div></div>
        <div class="panel" style="cursor:default"><div style="font-size:12px;color:var(--tt);margin-bottom:10px">市场情绪雷达</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px"><div style="text-align:center"><div style="font-size:11px;color:var(--tt)">恐慌指数</div><div id="sf" style="font-size:17px;font-weight:600;color:var(--warn);margin-top:3px">--</div></div><div style="text-align:center"><div style="font-size:11px;color:var(--tt)">涨跌比</div><div id="sa" style="font-size:17px;font-weight:600;margin-top:3px">--</div></div><div style="text-align:center"><div style="font-size:11px;color:var(--tt)">资金流向</div><div id="sfl" style="font-size:17px;font-weight:600;color:var(--up);margin-top:3px">--</div></div></div></div></div>
        <div id="dp" class="panel hid"><div class="t"><span id="dt">--</span><button class="close" onclick="qm.cd()">×</button></div><div class="dg"><div class="ch"><svg id="dc" width="100%" height="170"></svg></div><div class="mg"><div class="mb"><div class="l">RSI(14)</div><div class="v" id="dr">--</div></div><div class="mb"><div class="l">MACD柱</div><div class="v" id="dm">--</div></div><div class="mb"><div class="l">布林带位置</div><div class="v" id="db">--</div></div><div class="mb"><div class="l">量比</div><div class="v" id="dv">--</div></div><div class="mb"><div class="l">5日涨跌</div><div class="v" id="d5">--</div></div><div class="mb"><div class="l">20日涨跌</div><div class="v" id="d20">--</div></div></div></div>
        <div class="fr"><div class="fi"><div class="l">趋势</div><div class="v" id="st">--</div></div><div class="fi"><div class="l">动量</div><div class="v" id="sm">--</div></div><div class="fi"><div class="l">量能</div><div class="v" id="sv">--</div></div><div class="fi"><div class="l">位置</div><div class="v" id="sp">--</div></div><div class="fi"><div class="l">表现</div><div class="v" id="spe">--</div></div></div>
        <div class="sb"><div class="sbl"><span style="font-size:12px;color:var(--ts)">量化信号:</span><span class="badge" id="ds">--</span></div><span style="font-size:12px;color:var(--tt)" id="drk">--</span></div></div>
        <div class="panel"><div class="t">个股量化精选</div><div class="g3">${['600519_SH','000001_SZ','300750_SZ'].map(k=>`<div class="card" data-key="${k}" onclick="qm.dl('${k}')"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span class="n">${this.nm(k)}</span><span class="score" id="${k}-sc">--</span></div><div class="p" id="${k}-pr">--</div><div class="f"><span id="${k}-ch">--</span><span id="${k}-si" style="font-size:11px;color:var(--tt)">--</span></div></div>`).join('')}</div></div>
        <div class="panel"><div class="t">策略建议</div><div class="strat" id="stc"><div class="load"><div class="spin"></div>正在加载策略分析...</div></div></div>`;
    }
    nm(k){return{'000001_SH':'上证指数','399001_SZ':'深证成指','399006_SZ':'创业板指','000300_SH':'沪深300','000688_SH':'科创50','600519_SH':'贵州茅台','000001_SZ':'平安银行','300750_SZ':'宁德时代'}[k]||k}
    cw(){
        const proto=window.location.protocol==='https:'?'wss:':'ws:';
        const url=`${proto}//${window.location.host}/ws`;
        try{
            this.ws=new WebSocket(url);
            this.ws.onopen=()=>{document.getElementById('cs').textContent='实时连接';document.getElementById('cs').style.color='var(--down)'};
            this.ws.onmessage=e=>{try{const m=JSON.parse(e.data);this.hm(m)}catch(err){}};
            this.ws.onclose=()=>{document.getElementById('cs').textContent='重连中...';setTimeout(()=>this.cw(),this.rc)};
        }catch(e){setTimeout(()=>this.cw(),this.rc)}
    }
    async fd(){
        try{const r=await fetch('/api/data');const j=await r.json();if(j.data)this.hm({type:'init',data:j.data,chart_data:j.chart_data,strategy:j.strategy,timestamp:j.last_update});}
        catch(e){document.getElementById('cs').textContent='REST API'}
    }
    hm(m){
        if(m.data){this.d=m.data;this.c=m.chart_data||{};this.rd()}
        if(m.strategy)document.getElementById('stc').innerHTML=m.strategy;
        if(m.timestamp)document.getElementById('ut').textContent=m.timestamp.slice(11,19);
    }
    rd(){
        for(const k in this.d){
            const d=this.d[k];
            this.st(`${k}-pr`,d.close.toLocaleString());
            this.st(`${k}-ch`,(d.change_pct>=0?'+':'')+d.change_pct+'%');
            this.sc(`${k}-ch`,d.change_pct>=0?'var(--up)':'var(--down)');
            this.st(`${k}-sc`,d.total_score+'分');
            this.ssc(`${k}-sc`,d.total_score);
            this.st(`${k}-si`,d.signal+' · '+d.risk);
        }
        const idx=['000001_SH','399001_SZ','399006_SZ','000300_SH'].map(k=>this.d[k]?.total_score||50);
        const avg=idx.reduce((a,b)=>a+b,0)/idx.length;
        document.getElementById('sf').textContent=avg<40?'恐慌':avg<55?'中性':'贪婪';
        document.getElementById('sf').style.color=avg<40?'var(--down)':avg<55?'var(--warn)':'var(--up)';
        document.getElementById('sa').textContent='1:1.2';
        document.getElementById('sfl').textContent='-128亿';
    }
    st(id,t){const el=document.getElementById(id);if(el)el.textContent=t}
    sc(id,c){const el=document.getElementById(id);if(el)el.style.color=c}
    ssc(id,s){
        const el=document.getElementById(id);if(!el)return;
        let c='var(--tt)';if(s>=75)c='var(--up)';else if(s>=60)c='var(--warn)';else if(s>=45)c='var(--ac)';else if(s>=35)c='var(--ts)';else if(s<25)c='var(--down)';
        el.style.color=c;el.style.background=c+'18';
    }
    dl(k){
        const d=this.d[k];if(!d)return;
        document.getElementById('dp').classList.remove('hid');
        document.getElementById('dt').textContent=d.name+' · '+d.close;
        document.getElementById('dr').textContent=d.rsi;document.getElementById('dr').style.color=d.rsi>70?'var(--up)':d.rsi<30?'var(--down)':'var(--tp)';
        document.getElementById('dm').textContent=(d.macd_hist>=0?'+':'')+d.macd_hist;document.getElementById('dm').style.color=d.macd_hist>=0?'var(--up)':'var(--down)';
        document.getElementById('db').textContent=(d.bb_pos*100).toFixed(0)+'%';
        document.getElementById('dv').textContent=d.vol_ratio+'x';
        document.getElementById('d5').textContent=(d.change_pct_5d>=0?'+':'')+d.change_pct_5d+'%';document.getElementById('d5').style.color=d.change_pct_5d>=0?'var(--up)':'var(--down)';
        document.getElementById('d20').textContent=(d.change_pct_20d>=0?'+':'')+d.change_pct_20d+'%';document.getElementById('d20').style.color=d.change_pct_20d>=0?'var(--up)':'var(--down)';
        document.getElementById('st').textContent=d.scores.trend+'/25';
        document.getElementById('sm').textContent=d.scores.momentum+'/25';
        document.getElementById('sv').textContent=d.scores.volume+'/20';
        document.getElementById('sp').textContent=d.scores.position+'/15';
        document.getElementById('spe').textContent=d.scores.performance+'/15';
        const se=document.getElementById('ds');se.textContent=d.signal;se.style.background=d.signal.includes('买入')?'rgba(239,68,68,0.15)':d.signal.includes('卖出')?'rgba(34,197,94,0.15)':'rgba(107,114,128,0.15)';se.style.color=d.signal.includes('买入')?'var(--up)':d.signal.includes('卖出')?'var(--down)':'var(--ts)';
        document.getElementById('drk').textContent=d.risk;
        this.dc(k);
        document.getElementById('dp').scrollIntoView({behavior:'smooth'});
    }
    dc(k){
        const c=this.c[k];if(!c||!c.close||!c.close.length)return;
        const svg=document.getElementById('dc');const w=svg.clientWidth||400;const h=170;const p=10;
        const prices=c.close;const minP=Math.min(...prices)*0.998;const maxP=Math.max(...prices)*1.002;const range=maxP-minP||1;
        const x=i=>p+(i/(prices.length-1))*(w-p*2);const y=v=>h-p-((v-minP)/range)*(h-p*2);
        let path='';for(let i=0;i<prices.length;i++)path+=(i===0?'M':'L')+x(i)+','+y(prices[i]);
        let area=path+' L'+x(prices.length-1)+','+(h-p)+' L'+x(0)+','+(h-p)+' Z';
        const vols=c.volume;const maxV=Math.max(...vols)||1;let vb='';
        for(let i=0;i<vols.length;i++){const vx=x(i);const vh=(vols[i]/maxV)*(h-p*2)*0.2;vb+=`<rect x="${vx-1}" y="${h-p-vh}" width="2" height="${vh}" fill="var(--tt)" opacity="0.25"/>`;}
        svg.innerHTML=`<defs><linearGradient id="g${k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--ac)" stop-opacity="0.3"/><stop offset="100%" stop-color="var(--ac)" stop-opacity="0"/></linearGradient></defs><path d="${area}" fill="url(#g${k})"/><path d="${path}" fill="none" stroke="var(--ac)" stroke-width="1.5"/>${vb}`;
    }
    cd(){document.getElementById('dp').classList.add('hid')}
}
const qm=new QM();
