import type {Job, Result} from '../types'
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
async function request<T>(path:string, init:RequestInit={}):Promise<T>{
  const response = await fetch(`${BASE}${path}`, init)
  if(!response.ok){ const body = await response.json().catch(()=>({detail:response.statusText})); throw new Error(body.detail || 'Request failed') }
  return response.json()
}
export const api = {
  dashboard:()=>request<any>('/dashboard'),
  jobs:()=>request<Job[]>('/jobs'),
  createJob:(data:Partial<Job>)=>request<Job>('/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}),
  archiveJob:(id:number,archived:boolean)=>request<any>(`/jobs/${id}/archive?archived=${archived}`,{method:'PATCH'}),
  results:(id:number)=>request<{items:Result[];total:number}>(`/jobs/${id}/results?page_size=100`),
  upload:(id:number,files:FileList)=>{const data=new FormData();Array.from(files).forEach(f=>data.append('files',f));return request<any>(`/jobs/${id}/resumes`,{method:'POST',body:data})},
  decision:(resumeId:number,decision:string,note='')=>request<any>(`/resumes/${resumeId}/decision`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({decision,note})}),
  notes:(id:number)=>request<any[]>(`/resumes/${id}/notes`),
  addNote:(id:number,note:string)=>request<any>(`/resumes/${id}/notes`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({note})}),
  rescreen:(id:number)=>request<Result>(`/results/${id}/rescreen`,{method:'POST'}),
  deleteResume:(id:number)=>request<any>(`/resumes/${id}`,{method:'DELETE'})
}
