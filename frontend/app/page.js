'use client';
import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const Card = ({ title, value, sub }) => (
  <div style={{background:'#fff',padding:20,borderRadius:14,border:'1px solid #e5e7eb'}}>
    <div style={{fontSize:13,color:'#6b7280'}}>{title}</div>
    <div style={{fontSize:30,fontWeight:700}}>{value}</div>
    <div style={{fontSize:12,color:'#6b7280'}}>{sub}</div>
  </div>
);

function RiskBadge({risk}) {
  const critical = risk === 'production-critical';
  const warning = risk === 'warning';
  return <span style={{padding:'4px 8px',borderRadius:999,fontSize:12,fontWeight:700,background:critical?'#fee2e2':warning?'#fef3c7':'#dcfce7',color:critical?'#991b1b':warning?'#92400e':'#166534'}}>{risk}</span>;
}

export default function Home() {
  const [data,setData] = useState(null);
  const [file,setFile] = useState(null);
  const [upload,setUpload] = useState(null);
  const [loading,setLoading] = useState(false);
  const [msg,setMsg] = useState('');

  const load = () => fetch(API+'/api/dashboard').then(r=>r.json()).then(setData);
  useEffect(() => { load(); }, []);

  async function refresh() {
    setLoading(true);
    await fetch(API+'/api/demo/refresh',{method:'POST'});
    await load();
    setLoading(false);
  }

  async function processDocument() {
    if (!file) return;
    setLoading(true);
    setMsg('Gemini is processing the document...');
    const form = new FormData();
    form.append('file',file);
    const response = await fetch(API+'/api/documents/upload',{method:'POST',body:form});
    const result = await response.json();
    setUpload(result);
    setMsg(response.ok ? `Processed: ${result.document_type} · ${Math.round((result.confidence||0)*100)}% confidence · ${result.alerts_created||0} review alerts` : (result.detail || 'Upload failed'));
    await load();
    setLoading(false);
  }

  async function decide(id,action) {
    await fetch(API+'/api/alerts/'+id+'/decision',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action,comment:''})
    });
    load();
  }

  if (!data) return <main style={{padding:40}}>Loading SupplyChain Sentinel...</main>;

  return <main style={{maxWidth:1250,margin:'auto',padding:28,fontFamily:'Arial,sans-serif',background:'#f8fafc',minHeight:'100vh'}}>
    <header style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:28}}>
      <div>
        <h1 style={{marginBottom:6}}>SupplyChain Sentinel</h1>
        <p style={{color:'#6b7280',margin:0}}>Evidence-backed procurement and production risk visibility</p>
      </div>
      <button onClick={refresh} disabled={loading}>{loading?'Working...':'Refresh Risk Analysis'}</button>
    </header>

    <section style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:14}}>
      <Card title="Suppliers" value={data.summary.suppliers} sub="Tracked supplier records"/>
      <Card title="Materials" value={data.summary.materials} sub="Inventory runway tracked"/>
      <Card title="Open Orders" value={data.summary.open_orders} sub="Purchase orders"/>
      <Card title="Pending Review" value={data.summary.review_alerts} sub="Human-review items"/>
    </section>

    <section style={{marginTop:22,background:'#fff',padding:20,borderRadius:14,border:'1px solid #e5e7eb'}}>
      <h2>Open-order risk</h2>
      <table style={{width:'100%',borderCollapse:'collapse'}}>
        <thead><tr>{['PO','Supplier','Material','Runway','Predicted delay','Risk'].map(x=><th key={x} style={{textAlign:'left',padding:9}}>{x}</th>)}</tr></thead>
        <tbody>{data.orders.map(o=><tr key={o.id}>
          <td style={{padding:9,borderTop:'1px solid #eee'}}>{o.po_number}</td>
          <td style={{padding:9,borderTop:'1px solid #eee'}}>{o.supplier}</td>
          <td style={{padding:9,borderTop:'1px solid #eee'}}>{o.material}</td>
          <td style={{padding:9,borderTop:'1px solid #eee'}}>{o.runway_days??'—'} d</td>
          <td style={{padding:9,borderTop:'1px solid #eee'}}>{o.predicted_delay_days} d</td>
          <td style={{padding:9,borderTop:'1px solid #eee'}}><RiskBadge risk={o.risk}/></td>
        </tr>)}</tbody>
      </table>
    </section>

    <section style={{marginTop:22,display:'grid',gridTemplateColumns:'1fr 1fr',gap:18}}>
      <div style={{background:'#fff',padding:20,borderRadius:14,border:'1px solid #e5e7eb'}}>
        <h2>Document ingestion</h2>
        <p style={{color:'#6b7280'}}>PDF, images, CSV and Excel documents are extracted with Gemini structured output.</p>
        <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,.csv,.xlsx,.xls" onChange={e=>setFile(e.target.files?.[0]||null)}/>
        <button onClick={processDocument} disabled={!file||loading} style={{display:'block',marginTop:12}}>Process document</button>
        <p>{msg}</p>
        {upload?.extracted && <details open>
          <summary>Extraction result</summary>
          <pre style={{whiteSpace:'pre-wrap',fontSize:12,background:'#f8fafc',padding:12,borderRadius:8}}>{JSON.stringify(upload.extracted,null,2)}</pre>
        </details>}
      </div>

      <div style={{background:'#fff',padding:20,borderRadius:14,border:'1px solid #e5e7eb'}}>
        <h2>Supplier scorecards</h2>
        {data.suppliers.map(s=><div key={s.id} style={{borderTop:'1px solid #eee',padding:'10px 0'}}>
          <b>{s.name}</b>
          <div>Category: {s.category} · Score: {s.score}/100</div>
          <div>On-time: {Math.round(s.on_time_rate*100)}% · Accuracy: {Math.round(s.order_accuracy*100)}% · Quality issues: {s.quality_issues}</div>
        </div>)}
      </div>
    </section>

    <section style={{marginTop:22,background:'#fff',padding:20,borderRadius:14,border:'1px solid #e5e7eb'}}>
      <h2>Evidence-backed alerts</h2>
      {data.alerts.length===0 ? <p>No pending alerts. Refresh risk analysis or process a document.</p> :
      data.alerts.map(a=><div key={a.id} style={{border:'1px solid #e5e7eb',borderRadius:10,padding:16,marginBottom:12}}>
        <div style={{display:'flex',justifyContent:'space-between',gap:12}}>
          <b>{a.title}</b><RiskBadge risk={a.severity==='critical'?'production-critical':'warning'}/>
        </div>
        <p>{a.message}</p>
        <p><b>Next step:</b> {a.recommendation}</p>
        <details><summary>Evidence chain</summary><pre style={{whiteSpace:'pre-wrap',fontSize:12}}>{JSON.stringify(a.evidence,null,2)}</pre></details>
        {a.status==='pending' && <div style={{marginTop:12}}>{['approve','modify','reject'].map(x=><button key={x} onClick={()=>decide(a.id,x)} style={{marginRight:8}}>{x}</button>)}</div>}
        <small style={{color:'#6b7280'}}>Status: {a.status}</small>
      </div>)}
    </section>
  </main>;
}
