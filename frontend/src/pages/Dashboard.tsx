import {useEffect,useState} from 'react'
import {ArrowUpRight,BriefcaseBusiness,Users,FileCheck2,Clock3,UserCheck,Plus,ArrowRight} from 'lucide-react'
import {Link} from 'react-router-dom'
import {api} from '../services/api'
export default function Dashboard(){
 const [data,setData]=useState<any>(null),[error,setError]=useState('')
 useEffect(()=>{api.dashboard().then(setData).catch(e=>setError(e.message))},[])
 const stats=[['Active jobs',data?.active_jobs??'—',BriefcaseBusiness,'blue'],['Total candidates',data?.total_candidates??'—',Users,'violet'],['Candidates analyzed',data?.analyzed??'—',FileCheck2,'green'],['Awaiting review',data?.awaiting_review??'—',Clock3,'amber']]
 return <><div className="page-heading"><div><div className="eyebrow">MONDAY, OCTOBER 26</div><h1>Good evening 👋</h1><p>Here’s what’s happening with your hiring pipeline.</p></div><Link className="primary-btn" to="/jobs"><Plus size={17}/> Create a job</Link></div>
 {error&&<div className="alert">Could not connect to the API: {error}. Start the backend and refresh.</div>}
 <div className="stats-grid">{stats.map(([label,value,Icon,color])=><div className="stat-card" key={String(label)}><div className="stat-top"><span>{label}</span><span className={`stat-icon ${color}`}><Icon size={18}/></span></div><div className="stat-value">{value}</div><div className="stat-foot">Across your workspace</div></div>)}</div>
 <div className="dashboard-grid"><section className="panel"><div className="panel-heading"><div><h2>Recent screening activity</h2><p>Latest candidates processed by the screening engine</p></div><Link to="/history" className="text-link">View history <ArrowRight size={15}/></Link></div>
 {data?.recent_activity?.length ? <div className="activity-list">{data.recent_activity.map((r:any,i:number)=><div className="activity-row" key={i}><div className="candidate-avatar">{r.candidate?.split(' ').map((x:string)=>x[0]).join('').slice(0,2)}</div><div className="activity-main"><b>{r.candidate}</b><small>{r.job}</small></div><div className="score-pill">{Math.round(r.score)}% match</div></div>)}</div>:<div className="empty-state"><div className="empty-icon"><FileCheck2 size={24}/></div><h3>No screening activity yet</h3><p>Create a job, then upload resumes to see evidence-based matches here.</p><Link to="/jobs" className="text-link">Get started <ArrowUpRight size={15}/></Link></div>}</section>
 <section className="panel"><div className="panel-heading"><div><h2>Shortlist overview</h2><p>Human-reviewed candidate decisions</p></div><UserCheck size={19} className="muted"/></div><div className="shortlist-number">{data?.shortlisted??0}<span> candidates shortlisted</span></div><div className="progress-track"><div style={{width:`${data?.analyzed?Math.min(100,(data.shortlisted/data.analyzed)*100):0}%`}}/></div><div className="hint">AI scores support review; they never make hiring decisions.</div><div className="mini-callout"><SparklesIcon/><div><b>Keep your process explainable</b><p>Review skill evidence and missing requirements before deciding.</p></div></div></section></div>
 </>}
function SparklesIcon(){return <span className="mini-sparkle">✦</span>}
