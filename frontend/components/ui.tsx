"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertTriangle, ArrowRight, Bell, Check, ChevronDown, CloudUpload, ClipboardList,
  Gauge, Inbox, LayoutDashboard, Menu, PackageSearch, Settings, ShieldCheck, Truck, UserRound, X
} from "lucide-react";
import { useState, type ReactNode } from "react";
import { cn } from "../lib/utils";

export function Button({children, href, variant="primary", className, ...props}: any) {
  const c = cn("inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-200 active:scale-[.98] disabled:cursor-not-allowed disabled:opacity-50", {
    "bg-primary text-paper shadow-soft hover:-translate-y-0.5 hover:shadow-lift": variant==="primary",
    "border border-line bg-panel text-ink hover:bg-paper": variant==="secondary",
    "bg-critical/10 text-critical hover:bg-critical/15": variant==="danger",
    "text-primary hover:bg-primary/10": variant==="ghost"
  }, className);
  if (href) return <Link className={c} href={href}>{children}</Link>;
  return <button className={c} {...props}>{children}</button>;
}
export function Card({children,className="",...props}:any){return <div className={cn("rounded-2xl border border-line bg-panel shadow-soft",className)} {...props}>{children}</div>}
export function Badge({children,tone="info",className=""}:any){
  const tones:any={critical:"bg-critical/10 text-critical border-critical/20",warning:"bg-amber/10 text-amber border-amber/20",success:"bg-success/10 text-success border-success/20",info:"bg-info/10 text-info border-info/20"};
  return <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold",tones[tone],className)}>{children}</span>;
}
export function StatusPill({risk}: {risk:string}) {
  const map:any={critical:["Critical", "critical"],"at-risk":["At risk","warning"],"on-track":["On track","success"],info:["Info","info"]};
  const [label,tone]=map[risk]||map.info;
  return <Badge tone={tone}><span className="h-1.5 w-1.5 rounded-full bg-current"/>{label}</Badge>;
}
export function ConfidenceBadge({value}:{value:number}){return <Badge tone={value>=90?"success":value>=75?"warning":"critical"}><ShieldCheck size={13}/> {value}% confidence</Badge>}
export function RunwayBar({days,delay}:{days:number,delay:number}) {
  const pct=Math.min(100, Math.max(8,(days/15)*100));
  const critical=days<delay;
  return <div className="min-w-[150px]"><div className="mb-1 flex justify-between text-xs text-muted"><span>{days}d runway</span><span>{delay > 0 ? `+${delay}d delay` : "No delay"}</span></div><div className="h-2 overflow-hidden rounded-full bg-line/60"><div className={cn("h-full rounded-full",critical?"bg-critical":"bg-success")} style={{width:`${pct}%`}}/></div></div>;
}
export function Skeleton({className=""}:{className?:string}){return <div aria-hidden="true" className={cn("animate-pulse rounded-xl bg-line/50",className)}/>}
export function EmptyState({icon:Icon=Inbox,title,description,action}:{icon?:any,title:string,description:string,action?:ReactNode}){return <Card className="flex flex-col items-center justify-center p-12 text-center"><div className="mb-4 rounded-2xl bg-primary/10 p-4 text-primary"><Icon size={25}/></div><h3 className="font-display text-xl">{title}</h3><p className="mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>{action&&<div className="mt-5">{action}</div>}</Card>}
export function Modal({open,onClose,title,children}:any){if(!open)return null;return <div className="fixed inset-0 z-50 grid place-items-center bg-ink/30 p-4 backdrop-blur-sm" role="dialog" aria-modal="true"><Card className="w-full max-w-lg p-6 shadow-lift"><div className="flex items-center justify-between"><h2 className="font-display text-2xl">{title}</h2><button aria-label="Close" onClick={onClose} className="rounded-lg p-2 hover:bg-paper"><X size={18}/></button></div><div className="mt-5">{children}</div></Card></div>}
export function Input({label,error,...props}:any){return <label className="block text-sm font-medium">{label&&<span className="mb-2 block">{label}</span>}<input className={cn("h-12 w-full rounded-xl border border-line bg-paper px-3.5 text-sm text-ink placeholder:text-muted/70 focus:border-primary",error&&"border-critical")} {...props}/>{error&&<span className="mt-1 block text-xs text-critical">{error}</span>}</label>}
export function Textarea({label,...props}:any){return <label className="block text-sm font-medium">{label&&<span className="mb-2 block">{label}</span>}<textarea className="min-h-28 w-full rounded-xl border border-line bg-paper p-3.5 text-sm text-ink placeholder:text-muted/70 focus:border-primary" {...props}/></label>}
export function Toast({message,onClose}:{message:string,onClose?:()=>void}){if(!message)return null;return <div className="fixed bottom-5 right-5 z-50 flex items-center gap-3 rounded-xl border border-line bg-panel px-4 py-3 text-sm shadow-lift"><Check size={17} className="text-success"/>{message}{onClose&&<button onClick={onClose}><X size={15}/></button>}</div>}
export function AlertCard({alert,compact=false}:{alert:any,compact?:boolean}){
 return <Card className={cn("p-5 transition hover:-translate-y-0.5",alert.risk==="critical"&&"border-critical/30 shadow-[0_12px_35px_rgba(166,67,57,.10)]")}>
   <div className="flex items-start justify-between gap-4"><div className="flex items-start gap-3"><div className={cn("mt-0.5 rounded-xl p-2",alert.risk==="critical"?"bg-critical/10 text-critical":"bg-paper text-muted")}><AlertTriangle size={17}/></div><div><StatusPill risk={alert.risk}/><h3 className="mt-2 font-semibold">{alert.title}</h3></div></div><span className="text-xs text-muted">{alert.time}</span></div>
   {!compact&&<><p className="mt-3 text-sm leading-6 text-muted">{alert.message}</p><div className="mt-4 rounded-xl bg-paper p-3 text-sm"><span className="font-semibold">Next step:</span> {alert.next}</div><Link href={`/alerts/${alert.id}`} className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-primary hover:gap-2 transition-all">Open evidence <ArrowRight size={15}/></Link></>}
 </Card>
}
export function EvidenceChain({items}:any){return <div className="space-y-0">{items.map((item:any,i:number)=><div key={item.label} className="relative flex gap-4 pb-6 last:pb-0"><div className="flex flex-col items-center"><div className="grid h-9 w-9 place-items-center rounded-full border border-line bg-panel text-primary text-xs font-bold">{String(i+1).padStart(2,"0")}</div>{i<items.length-1&&<div className="mt-1 h-full w-px bg-line"/>}</div><div className="min-w-0 flex-1 rounded-xl border border-line bg-paper p-3"><div className="flex flex-wrap items-center justify-between gap-2"><div><p className="text-xs font-semibold uppercase tracking-wider text-muted">{item.label}</p><p className="mt-1 text-sm font-medium">{item.detail}</p></div><ConfidenceBadge value={item.confidence}/></div></div></div>)}</div>}
export function DataTable({headers,rows}:any){return <div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead><tr className="border-b border-line text-xs uppercase tracking-wider text-muted">{headers.map((h:string)=><th key={h} className="px-4 py-3 font-semibold">{h}</th>)}</tr></thead><tbody>{rows}</tbody></table></div>}
export function AppShell({children,title,subtitle}:{children:ReactNode,title?:string,subtitle?:string}){
 const path=usePathname();
 const [open,setOpen]=useState(true);
 const nav=[
  ["/dashboard","Dashboard",LayoutDashboard],
  ["/review","Needs review",Inbox],
  ["/orders","Orders & documents",ClipboardList],
  ["/suppliers","Suppliers",Truck],
  ["/stock","Stock & runway",PackageSearch],
  ["/capture","Quick capture",CloudUpload],
  ["/settings","Settings",Settings]
 ];
 return <div className="min-h-screen bg-paper">
   {open&&<button aria-label="Close navigation overlay" onClick={()=>setOpen(false)} className="fixed inset-0 z-30 bg-ink/15 lg:hidden"/>}
   <aside className={cn(
     "fixed inset-y-0 left-0 z-40 w-64 border-r border-line bg-panel px-4 py-5 shadow-soft transition-transform duration-200 ease-out",
     open ? "translate-x-0" : "-translate-x-full"
   )}>
     <div className="flex items-center justify-between gap-2 px-2">
       <div className="flex items-center gap-3 min-w-0">
         <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-paper"><Gauge size={20}/></div>
         <div className="min-w-0"><div className="font-display text-lg">Sentinel</div><div className="truncate text-[10px] uppercase tracking-[.2em] text-muted">Supply chain control</div></div>
       </div>
       <button onClick={()=>setOpen(false)} className="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-muted hover:bg-paper hover:text-ink lg:hidden" aria-label="Close navigation"><X size={18}/></button>
     </div>
     <nav className="mt-8 space-y-1">
       {nav.map(([href,label,Icon]:any)=><Link key={href} href={href} onClick={()=>setOpen(false)} className={cn(
         "flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium transition",
         path===href?"bg-primary text-paper":"text-muted hover:bg-paper hover:text-ink"
       )}><Icon size={17}/>{label}</Link>)}
     </nav>
     <div className="absolute bottom-5 left-4 right-4 rounded-xl border border-line bg-paper p-3">
       <div className="flex items-center gap-2 text-xs font-semibold"><ShieldCheck size={15} className="text-success"/> Nothing sends without approval</div>
       <p className="mt-1 text-[11px] leading-4 text-muted">Evidence and audit trail stay attached to every action.</p>
     </div>
   </aside>

   <div className={cn("min-h-screen transition-[padding] duration-200 ease-out",open?"lg:pl-64":"lg:pl-0")}>
     <header className="sticky top-0 z-20 border-b border-line bg-paper/95 px-4 py-3 backdrop-blur md:px-7">
       <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-4">
         <div className="flex min-w-0 items-center gap-3">
           <button
             className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-line bg-panel text-ink hover:bg-paper"
             onClick={()=>setOpen(v=>!v)}
             aria-label={open ? "Hide navigation" : "Show navigation"}
             aria-expanded={open}
           >
             {open ? <PanelLeftClose size={19}/> : <PanelLeftOpen size={19}/>}
           </button>
           <div className="min-w-0">
             {title&&<h1 className="truncate font-display text-xl md:text-2xl">{title}</h1>}
             {subtitle&&<p className="hidden text-xs text-muted sm:block">{subtitle}</p>}
           </div>
         </div>
         <div className="ml-auto flex shrink-0 items-center gap-2">
           <button className="relative rounded-xl border border-line bg-panel p-2.5" aria-label="Notifications"><Bell size={18}/><span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-critical"/></button>
           <div className="hidden items-center gap-2 rounded-xl border border-line bg-panel px-3 py-2 text-sm sm:flex"><div className="grid h-7 w-7 place-items-center rounded-full bg-primary/10 text-primary"><UserRound size={15}/></div>Dh<ChevronDown size={14}/></div>
         </div>
       </div>
     </header>
     <main className="mx-auto max-w-[1440px] px-4 py-6 md:px-7 md:py-8">{children}</main>
   </div>
 </div>
}
export function Logo(){return <Link href="/" className="flex items-center gap-2"><div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-paper"><Gauge size={18}/></div><span className="font-display text-xl">SupplyChain Sentinel</span></Link>}
export function Metric({label,value,sub,icon:Icon=Gauge,tone="primary"}:any){return <Card className="p-5"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</p><p className="mt-2 font-display text-3xl">{value}</p><p className="mt-1 text-xs text-muted">{sub}</p></div><div className={cn("rounded-xl p-2.5",tone==="critical"?"bg-critical/10 text-critical":"bg-primary/10 text-primary")}><Icon size={18}/></div></div></Card>}
export function SectionHeading({eyebrow,title,description,action}:any){return <div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[.18em] text-primary">{eyebrow}</p><h2 className="mt-2 font-display text-3xl tracking-tight">{title}</h2>{description&&<p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>}</div>{action}</div>}
