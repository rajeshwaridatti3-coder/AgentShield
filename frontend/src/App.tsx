import { useEffect, useState } from 'react'
import { Shield, Activity, FileText, FlaskConical, LockKeyhole, Gauge, LogIn, Upload, Send, RefreshCw } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type AnyObj = Record<string, any>

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('agentshield_token') || '')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [organization, setOrganization] = useState('demo-org')
  const [mode, setMode] = useState<'login'|'register'>('register')
  const [me, setMe] = useState<AnyObj|null>(null)
  const [tab, setTab] = useState('Overview')
  const [notice, setNotice] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<AnyObj|null>(null)
  const [docs, setDocs] = useState<AnyObj[]>([])
  const [traces, setTraces] = useState<AnyObj[]>([])
  const [metrics, setMetrics] = useState<AnyObj>({})
  const [redteam, setRedteam] = useState<AnyObj|null>(null)
  const [approvals, setApprovals] = useState<AnyObj[]>([])
  const [platformText, setPlatformText] = useState('')
  const [platformResult, setPlatformResult] = useState<AnyObj|null>(null)
  const [platformRecords, setPlatformRecords] = useState<AnyObj[]>([])

  async function api(path:string, options:RequestInit = {}) {
    const headers:Record<string,string> = { ...(options.headers as Record<string,string> || {}) }
    if (token) headers.Authorization = `Bearer ${token}`
    if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json'
    const response = await fetch(`${API}${path}`, {...options, headers})
    const data = await response.json().catch(()=>({detail:'Unexpected server response'}))
    if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`)
    return data
  }
  async function authenticate() {
    try {
      const path = mode === 'register' ? '/api/auth/register' : '/api/auth/login'
      const payload = mode === 'register' ? {email,password,organization} : {email,password}
      const data = await fetch(`${API}${path}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(async r=>{const d=await r.json();if(!r.ok)throw new Error(d.detail||'Authentication failed');return d})
      localStorage.setItem('agentshield_token', data.access_token); setToken(data.access_token); setNotice('Authenticated successfully')
    } catch(e:any) { setNotice(e.message) }
  }
  async function refresh() {
    try {
      const [u,d,t,m,a] = await Promise.all([api('/api/auth/me'),api('/api/documents'),api('/api/traces'),api('/api/metrics/summary'),api('/api/tools/approvals')])
      setMe(u);setDocs(d);setTraces(t);setMetrics(m);setApprovals(a)
    } catch(e:any) { setNotice(e.message) }
  }
  useEffect(()=>{if(token) refresh()},[token])
  async function upload(file?:File) {
    if(!file)return
    const form = new FormData();form.append('file',file)
    try { const result=await api('/api/documents',{method:'POST',body:form});setNotice(`Indexed ${result.filename}; ${result.chunks} chunks; ${result.sensitive_items_redacted} sensitive values redacted.`);refresh() }
    catch(e:any){setNotice(e.message)}
  }
  async function ask() {
    try {setAnswer(await api('/api/chat',{method:'POST',body:JSON.stringify({question,top_k:5})}));refresh()}
    catch(e:any){setNotice(e.message)}
  }
  async function runRedteam() {
    try {setRedteam(await api('/api/redteam/run',{method:'POST'}));setNotice('Evaluation suite completed')}
    catch(e:any){setNotice(e.message)}
  }
  async function decide(id:number, decision:string) {
    try {await api(`/api/tools/approvals/${id}/decision`,{method:'POST',body:JSON.stringify({decision,reason:'Reviewed in AgentShield dashboard'})});refresh()}
    catch(e:any){setNotice(e.message)}
  }
  async function runPlatform(path:string, body?:AnyObj) { try { const result=await api(`/api/platform/${path}`,{method:'POST',body:JSON.stringify(body||{})});setPlatformResult(result);setNotice('Completed successfully');refresh() } catch(e:any){setNotice(e.message)} }
  async function loadRecords(kind?:string) { try { setPlatformRecords(await api(`/api/platform/records${kind?`?kind=${kind}`:''}`)) } catch(e:any){setNotice(e.message)} }
  function logout(){localStorage.removeItem('agentshield_token');setToken('');setMe(null);setNotice('Signed out')}
  if(!token) return <main className="auth"><div className="auth-card"><div className="brand"><Shield/> AgentShield</div><p className="muted">Secure Agentic RAG Platform</p><h1>{mode==='register'?'Create your workspace':'Welcome back'}</h1><input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/><input placeholder="Password (10+ characters)" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>{mode==='register'&&<input placeholder="Organization name" value={organization} onChange={e=>setOrganization(e.target.value)}/>}<button onClick={authenticate}><LogIn size={17}/>{mode==='register'?'Create account':'Sign in'}</button><p className="muted switch" onClick={()=>setMode(mode==='register'?'login':'register')}>{mode==='register'?'Already registered? Sign in':'New here? Create an account'}</p>{notice&&<p className="notice">{notice}</p>}</div></main>
  const nav=[['Overview',Activity],['Documents',FileText],['RAG Assistant',Send],['Red Team Lab',FlaskConical],['Policy & Approvals',LockKeyhole],['Observability',Gauge],['Agent Workflow',Activity],['Claim Verification',FileText],['DLP Scanner',LockKeyhole],['Memory Governance',LockKeyhole],['Governance Center',Shield],['Supply Chain',Gauge],['Evaluation Lab',FlaskConical],['Incident Replay',Activity]]
  return <div className="layout"><aside><div className="brand"><Shield/> AgentShield</div><div className="tag">AI SECURITY CONTROL PLANE</div><nav>{nav.map(([name,Icon]:any)=><button key={name} className={tab===name?'active':''} onClick={()=>setTab(name)}><Icon size={18}/>{name}</button>)}</nav><div className="side-bottom"><div className="avatar">{me?.email?.[0]?.toUpperCase()||'A'}</div><div><b>{me?.email||'Workspace'}</b><small>{me?.organization||'Loading...'}</small></div><button className="logout" onClick={logout}>Exit</button></div></aside>
    <main className="main"><header><div><span className="eyebrow">SECURE AI OPERATIONS</span><h1>{tab}</h1></div><button className="ghost" onClick={refresh}><RefreshCw size={16}/> Refresh</button></header>
      {notice&&<div className="notice" onClick={()=>setNotice('')}>{notice} <span>×</span></div>}
      {tab==='Overview'&&<><section className="hero"><div><span className="pill">● LOCAL WORKSPACE</span><h2>Trustworthy AI.<br/><em>Built with security.</em></h2><p>Secure retrieval, policy-controlled tools and measurable AI behavior in one workspace.</p></div><Shield size={100} strokeWidth={1}/></section><div className="stats"><Stat label="Indexed documents" value={docs.length}/><Stat label="Traced events" value={traces.length}/><Stat label="Requests" value={metrics.requests||0}/><Stat label="Avg latency" value={`${metrics.average_latency_ms||0} ms`}/></div><section className="panel"><h3>Platform capabilities</h3><div className="cap-grid">{['Tenant-scoped retrieval','Sensitive-data redaction','Policy-based tool access','Human approval gates','Red-team control checks','Request-level observability'].map(x=><div className="cap" key={x}><Shield size={16}/>{x}</div>)}</div></section></>}
      {tab==='Documents'&&<section className="panel"><div className="panel-head"><div><h3>Secure document ingestion</h3><p className="muted">Supported: TXT, Markdown and text-extractable PDF. Uploads are scoped to your organization.</p></div><label className="upload"><Upload size={16}/> Upload<input type="file" accept=".txt,.md,.pdf" onChange={e=>upload(e.target.files?.[0])}/></label></div>{docs.map(d=><div className="list-row" key={d.id}><FileText/><div><b>{d.filename}</b><small>{d.chunks} chunks · ID {d.id}</small></div></div>)}{!docs.length&&<p className="empty">No documents yet. Upload a policy or knowledge document to begin.</p>}</section>}
      {tab==='RAG Assistant'&&<section className="panel"><h3>Evidence-grounded assistant</h3><p className="muted">Ask questions about documents indexed in your organization. Unsupported questions should be met with abstention.</p><textarea value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask a question about your uploaded documents..."/><button onClick={ask} disabled={question.trim().length<3}><Send size={16}/> Ask AgentShield</button>{answer&&<div className="answer"><div className="answer-meta">MODEL: {answer.model} · {answer.latency_ms} ms · TRACE {answer.trace_id}</div><p>{answer.answer}</p>{answer.abstained&&<span className="pill warn">Insufficient evidence</span>}<h4>Retrieved evidence</h4>{answer.citations?.map((c:any,i:number)=><div className="citation" key={i}><b>{c.filename} · chunk {c.chunk_index}</b><small>Relevance score: {c.score}</small><p>{c.excerpt}</p></div>)}</div>}</section>}
      {tab==='Red Team Lab'&&<section className="panel"><h3>Security control evaluation</h3><p className="muted">Run the built-in synthetic checks against local DLP and policy controls. These checks do not prove model-level attack resistance.</p><button onClick={runRedteam}><FlaskConical size={16}/> Run evaluation suite</button>{redteam&&<><div className="stats compact"><Stat label="Cases" value={redteam.total}/><Stat label="Checks passed" value={redteam.passed}/><Stat label="Pass rate" value={`${Math.round(redteam.pass_rate*100)}%`}/></div>{redteam.results.map((r:any)=><div className="list-row" key={r.id}><span className={r.passed?'ok':'bad'}>{r.passed?'✓':'!'}</span><div><b>{r.id} · {r.category}</b><small>{r.observed}</small></div></div>)}<p className="muted">{redteam.note}</p></>}</section>}
      {tab==='Policy & Approvals'&&<section className="panel"><h3>Server-side policy gate</h3><p className="muted">Try a registered tool proposal using the API docs. Sensitive actions create an approval request; no arbitrary execution is enabled.</p><div className="code">POST /api/tools/propose<br/>{"{ \"tool_name\": \"export_report\", \"arguments\": { \"format\": \"csv\" } }"}</div><h3>Pending and recent approvals</h3>{approvals.map(a=><div className="list-row" key={a.id}><LockKeyhole/><div><b>{a.tool_name} · #{a.id}</b><small>{a.status}</small></div>{a.status==='pending'&&<div className="actions"><button className="small" onClick={()=>decide(a.id,'approved')}>Approve</button><button className="small danger" onClick={()=>decide(a.id,'rejected')}>Reject</button></div>}</div>)}{!approvals.length&&<p className="empty">No approval requests.</p>}</section>}
      {tab==='Agent Workflow'&&<section className="panel"><h3>Multi-agent workflow</h3><p className="muted">Supervisor → research → analysis → evidence verification → security review. Agent messages are structured and scoped to your organization.</p><textarea value={platformText} onChange={e=>setPlatformText(e.target.value)} placeholder="Describe the knowledge task for the agent team..."/><button disabled={platformText.trim().length<3} onClick={()=>runPlatform('agents/run',{task:platformText})}>Run agent workflow</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Claim Verification'&&<section className="panel"><h3>Claim-level evidence verification</h3><p className="muted">Enter one claim per line. The verifier searches your organization’s indexed documents and labels claims as supported candidates or unverified.</p><textarea value={platformText} onChange={e=>setPlatformText(e.target.value)} placeholder={'The policy requires annual review.\nCustomer data is encrypted at rest.'}/><button onClick={()=>runPlatform('claims/verify',{claims:platformText.split('\n').map(x=>x.trim()).filter(Boolean)})} disabled={!platformText.trim()}>Verify claims</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='DLP Scanner'&&<section className="panel"><h3>Sensitive data inspection</h3><p className="muted">Scan text for common email, phone, API-key-like and private-key markers. Findings are redacted in the returned preview.</p><textarea value={platformText} onChange={e=>setPlatformText(e.target.value)} placeholder="Paste sample text to scan..."/><button onClick={()=>runPlatform('dlp/scan',{text:platformText})} disabled={!platformText.trim()}>Scan and redact</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Memory Governance'&&<section className="panel"><h3>Private memory controls</h3><p className="muted">Inspect and delete memories belonging to your signed-in user. New memories expire after 30 days and sensitive content is rejected.</p><button onClick={async()=>{try{setPlatformRecords(await api('/api/memory'))}catch(e:any){setNotice(e.message)}}}>Refresh my memories</button><div>{platformRecords.map((m:any)=><div className="list-row" key={m.id}><div><b>Memory #{m.id}</b><small>{m.content} · Expires {m.expires_at||'never'}</small></div><button className="small danger" onClick={async()=>{await api(`/api/memory/${m.id}`,{method:'DELETE'});setPlatformRecords(await api('/api/memory'))}}>Delete</button></div>)}</div><textarea value={platformText} onChange={e=>setPlatformText(e.target.value)} placeholder="Add a non-sensitive memory..."/><button onClick={async()=>{try{await api('/api/memory',{method:'POST',body:JSON.stringify({content:platformText})});setPlatformText('');setPlatformRecords(await api('/api/memory'));setNotice('Memory saved')}catch(e:any){setNotice(e.message)}}} disabled={!platformText.trim()}>Save memory</button></section>}
      {tab==='Governance Center'&&<section className="panel"><h3>AI governance evidence</h3><p className="muted">Control crosswalk and evidence records. Framework mappings are informational and do not represent certification.</p><button onClick={async()=>{try{setPlatformResult(await api('/api/platform/governance'));}catch(e:any){setNotice(e.message)}}}>Load governance register</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Supply Chain'&&<section className="panel"><h3>AI software supply-chain inventory</h3><p className="muted">Inventory and hash the backend dependency manifest. This local scan does not query vulnerability databases.</p><button onClick={()=>runPlatform('supply-chain/scan')}>Scan dependency manifest</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Evaluation Lab'&&<section className="panel"><h3>Regression evaluation lab</h3><p className="muted">Run deterministic DLP regression cases. Results measure these local controls, not general model robustness.</p><button onClick={()=>runPlatform('evaluations/run')}>Run regression suite</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Incident Replay'&&<section className="panel"><h3>Read-only incident reconstruction</h3><p className="muted">Reconstructs events for a trace ID without repeating external actions.</p><input value={platformText} onChange={e=>setPlatformText(e.target.value)} placeholder="Trace ID (tr-...)"/><button onClick={()=>runPlatform('incidents/replay',{trace_id:platformText})} disabled={!platformText.trim()}>Reconstruct incident</button>{platformResult&&<pre className="result">{JSON.stringify(platformResult,null,2)}</pre>}</section>}
      {tab==='Observability'&&<section className="panel"><h3>Request traces</h3>{traces.map((t,i)=><div className="trace" key={i}><div><b>{t.event_type}</b><small>{t.trace_id} · {new Date(t.created_at).toLocaleString()}</small></div><span>{t.latency_ms.toFixed(1)} ms</span><pre>{JSON.stringify(t.details,null,2)}</pre></div>)}{!traces.length&&<p className="empty">No trace events yet. Ask a RAG question or run a policy action.</p>}</section>}
      <footer>AgentShield · Security-first AI engineering · Local development workspace</footer>
    </main>
  </div>
}
function Stat({label,value}:any){return <div className="stat"><small>{label}</small><strong>{value}</strong></div>}
