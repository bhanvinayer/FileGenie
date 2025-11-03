#!/usr/bin/env python3
import os, json, time, shutil, re, math, requests
from pathlib import Path
from dotenv import load_dotenv
files = []
meta = {}
sem = {}
rel = {}
q = ""
res = ""
ai = None
cmd = {}
def init_agent():
    global ai, meta, q, res, cmd
    load_dotenv()
    meta.clear(); meta.update({"mode":"offline","safe":True,"history":[],"operations":0,"directory":"."})
    q = os.getenv("OPENAI_API_KEY","")
    if q and len(q) > 20:
        try:
            class _AI:
                def __init__(self,k): self.k=k
                def _post(self,url,payload):
                    h={"Authorization":f"Bearer {self.k}","Content-Type":"application/json"}
                    r=requests.post(url, headers=h, json=payload, timeout=20)
                    try: return r.json()
                    except: return {}
                def chat(self,prompt,max_tokens=120):
                    p={"model":"gpt-3.5-turbo","messages":[{"role":"system","content":"You are FileGenie, concise file assistant."},
                                                         {"role":"user","content":prompt}],"max_tokens":max_tokens}
                    return self._post("https://api.openai.com/v1/chat/completions", p).get("choices",[{}])[0].get("message",{}).get("content","")
                def embed(self,text):
                    p={"model":"text-embedding-3-small","input":text[:2000]}
                    return self._post("https://api.openai.com/v1/embeddings", p).get("data",[{}])[0].get("embedding",[])
            ai = _AI(q); meta["mode"]="online"; print("🧞‍♂️ FileGenie AI: AWAKENED! Ready to grant your file wishes! ✨")
        except Exception:
            ai = None; meta["mode"]="offline"; print("📴 FileGenie AI: OFFLINE")
    else:
        ai = None; meta["mode"]="offline"; print("📴 FileGenie AI: OFFLINE (set OPENAI_API_KEY for AI features)")
def scan_workspace(root="."):
    global files, meta, sem, rel, q, res, cmd
    files.clear(); sem.clear(); rel.clear(); cmd.clear()
    cmd.update({"exts":{".py",".js",".html",".css",".json",".csv",".txt",".md",".log",".yaml",".pdf",".docx"},
                "stats":{"count":0,"size":0,"types":{},"large":0,"duplicates":0},"names":{}})
    print(f"🧞‍♂️ Exploring the mystical realm of '{root}'... Seeking digital treasures! 🔮")
    for r,dirs,fns in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fn in fns:
            if fn.startswith('.'): continue
            p=os.path.join(r,fn); ext=Path(p).suffix.lower()
            try:
                st=os.stat(p)
                cmd["stats"]["count"]+=1; cmd["stats"]["size"]+=st.st_size
                cmd["stats"]["types"][ext]=cmd["stats"]["types"].get(ext,0)+1
                if st.st_size>1000000: cmd["stats"]["large"]+=1
                if ext in cmd["exts"]:
                    files.append(p); meta[p]={"size":st.st_size,"modified":st.st_mtime,"type":ext,"name":fn,"analyzed":False}
                    key=re.sub(r'[_\-\d]+','',fn.lower())[:8]
                    if key and len(key)>3 and key in cmd["names"]:
                        rel.setdefault("duplicates",[]).extend([p,cmd["names"][key]]); cmd["stats"]["duplicates"]+=1
                    else:
                        cmd["names"][key]=p
            except Exception:
                continue
    meta.update({"stats":cmd["stats"],"scan_time":time.time(),"directory":os.path.abspath(root)})
    s=f"{cmd['stats']['size']//(1024*1024)}MB" if cmd['stats']['size']>1024*1024 else f"{cmd['stats']['size']//1024}KB"
    print(f"📁 Found {len(files)} tracked files | Duplicates: {cmd['stats']['duplicates']} | Size: {s}")
def read_excerpt(path, n=800):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f: return f.read(n)
    except Exception:
        return ""
def generate_summary(name, content, ftype):
    cmd["content"]= (content or "").lower()
    if ftype==".py": s = f"Python file: {name}" + (" (class defs)" if "class " in cmd["content"] else "")
    elif ftype==".js": s = f"JavaScript file: {name}" + (" (react component)" if "react" in cmd["content"] else "")
    elif ftype in [".json",".csv"]: s = f"Data file: {name} ({len(content)} chars)"
    elif ftype in [".md",".txt"]: s = f"Doc: {' '.join((content or '').split()[:8])}"
    else: s = f"File: {name} ({ftype})"
    return {"summary":s,"embedding":[],"type":"offline"}
def analyze_content():
    global sem, q, res, cmd
    print("🧞‍♂️ Casting wisdom spells on your files... Reading their secrets! ✨")
    for fp in files:
        if meta.get(fp,{}).get("analyzed"): continue
        nm = meta[fp]["name"]
        try:
            txt = read_excerpt(fp,1200) if meta[fp]["size"]<200000 else f"[Large:{meta[fp]['size']}]"
        except: txt = f"[Unreadable:{nm}]"
        if meta.get("mode")=="online" and ai:
            try:
                summ = ai.chat(f"Summarize briefly: {nm}\n{txt}", max_tokens=120).strip()
            except Exception:
                summ = None
            if summ:
                emb = ai.embed(summ or txt)
                sem[fp] = {"summary":summ,"embedding":emb,"type":"ai"}
            else:
                sem[fp] = generate_summary(nm, txt, meta[fp]["type"])
        else:
            sem[fp] = generate_summary(nm, txt, meta[fp]["type"])
        meta[fp]["analyzed"]=True
def cosine(a,b):
    if not a or not b: return 0.0
    la=math.sqrt(sum(x*x for x in a)) or 1.0; lb=math.sqrt(sum(y*y for y in b)) or 1.0
    return sum(x*y for x,y in zip(a,b))/(la*lb)
def build_relationships(threshold=0.75):
    global rel, cmd
    rel["semantic"]={}; cmd["paths"]=list(sem.keys())
    for i,a in enumerate(cmd["paths"]):
        rel["semantic"][a]=[]
        for j in range(i+1,len(cmd["paths"])):
            b=cmd["paths"][j]
            e1=sem.get(a,{}).get("embedding",[]); e2=sem.get(b,{}).get("embedding",[])
            if e1 and e2:
                sc=cosine(e1,e2)
                if sc>=threshold:
                    rel["semantic"][a].append((b,round(sc,3)))
                    if b not in rel["semantic"]: rel["semantic"][b]=[]
                    rel["semantic"][b].append((a,round(sc,3)))
    print("🧞‍♂️ Mystical bonds revealed! Files now speak to each other! 🔮✨")
def semantic_search(query, top=8):
    global q, cmd
    q = query.strip()
    cmd.clear(); cmd["results"]=[]
    print(f"🔎 Semantic search for: '{q}'")
    if meta.get("mode")=="online" and ai:
        try:
            qemb = ai.embed(q)
            cand=[]
            for p,info in sem.items():
                e = info.get("embedding",[])
                if e: cand.append((p,cosine(qemb,e), info.get("summary","")))
            cand.sort(key=lambda x: x[1], reverse=True)
            cmd["results"] = [(p,round(s,3),su) for p,s,su in cand[:top] if s>0.01]
        except Exception: cmd["results"]=[]
    if not cmd["results"]:
        terms=set(q.lower().split())
        for p,info in sem.items():
            txt=(info.get("summary","")+" "+meta[p]["name"]).lower()
            score = sum(1 for t in terms if t in txt)
            if score>0: cmd["results"].append((p,score,info.get("summary","")))
        cmd["results"].sort(key=lambda x:x[1], reverse=True)
        cmd["results"]=cmd["results"][:top]
    print(f"🎯 {len(cmd['results'])} hits:")
    for p,sc,su in cmd["results"][:top]:
        badge = "🔥" if sc>2 else "⭐" if sc>0.9 else "📄"
        print(f"{badge} {Path(p).name} ({sc}) → {su[:120]}")
    return cmd["results"]
def smart_organize(confirm=True):
    global cmd, q, res
    if confirm and not confirm_action("AUTO-ORGANIZE: Move files into categorized folders?"): print("Cancelled"); return 0
    cmd.clear(); cmd["moved"]=0; cats={"code":[".py",".js",".java"],"docs":[".txt",".md",".pdf",".docx"],"data":[".csv",".json",".xlsx"],"misc":[".log",".cfg"]}
    for fp in files:
        t=meta[fp]["type"]; target=None
        for k,exts in cats.items():
            if t in exts: target=k; break
        if not target:
            s=sem.get(fp,{}).get("summary","").lower()
            target="data" if "data" in s else "code" if "python" in s or "js" in s else "misc"
        os.makedirs(target, exist_ok=True)
        new=os.path.join(target, Path(fp).name)
        if perform_operation("move", fp, new, False): cmd["moved"]+=1
    meta["history"].append(f"[{time.strftime('%H:%M')}] Organized {cmd['moved']} files")
    return cmd["moved"]
def detect_duplicates():
    global cmd
    cmd.clear(); cmd["groups"]={}
    seen={}
    for fp in files:
        key=re.sub(r'[\W_]+','', Path(fp).stem.lower())[:10]
        seen.setdefault(key,[]).append(fp)
    for k,v in seen.items():
        if len(v)>1: cmd["groups"][k]=v
    rel["duplicates"]=sum(len(v) for v in cmd["groups"].values())>0 and [item for grp in cmd["groups"].values() for item in grp] or []
    return cmd["groups"]
def confirm_remove_duplicates():
    global cmd, res
    groups=detect_duplicates()
    if not groups:
        print("✅ No duplicate groups found.")
        return
    print("⚠️ Duplicate groups detected:")
    for k,v in groups.items():
        print(f"\nGroup '{k}':")
        for i,p in enumerate(v): print(f"  [{i}] {Path(p).name} ({meta[p]['size']//1024}KB)")
    to_delete=[]
    for k,v in groups.items():
        keep = input(f"Which index to KEEP in group '{k}' (enter number or 'a' to keep all): ").strip()
        if keep.lower()=="a": continue
        try:
            keep_i=int(keep)
            for i,p in enumerate(v):
                if i!=keep_i: to_delete.append(p)
        except:
            print("Skipping group")
    if not to_delete: print("No files selected for deletion.")
    else:
        print(f"\nReady to delete {len(to_delete)} files:")
        for p in to_delete: print(" -", Path(p).name)
        if confirm_action("PERMANENTLY delete these files?"):
            for p in to_delete:
                try: os.remove(p); files.remove(p) if p in files else None; meta.pop(p,None); sem.pop(p,None)
                except Exception as e: print("Failed:", p, str(e))
            print("🧞‍♂️ Alakazam! Duplicates banished to the digital void! ✨")
            meta["history"].append(f"[{time.strftime('%H:%M')}] Removed {len(to_delete)} duplicate files")
        else:
            print("Aborted deletion.")
def smart_cleanup():
    global cmd
    cmd.clear(); now=time.time(); cmd["temp"]=[]; cmd["large"]=[]; cmd["old"]=[]
    for fp in files:
        name=meta[fp]["name"].lower()
        if any(t in name for t in ["temp","tmp","backup","copy","~"]): cmd["temp"].append(meta[fp]["name"])
        if meta[fp]["size"]>5_000_000: cmd["large"].append(f"{meta[fp]['name']} ({meta[fp]['size']//1024//1024}MB)")
        if (now - meta[fp]["modified"])>30*24*3600: cmd["old"].append(meta[fp]["name"])
    cmd["has_cleanup"] = any(cmd[k] for k in ("temp","large","old"))
    if cmd["has_cleanup"]:
        print("🧹 Cleanup suggestions:")
        for k in ("temp","large","old"):
            if cmd[k]: print(f"{k.upper()}: {len(cmd[k])} -> {', '.join(cmd[k][:6])}")
    else:
        print("🧞‍♂️ FileGenie is delighted! ✨ Your workspace sparkles - no cleanup needed!")
    return cmd
def confirm_action(desc):
    global res
    print(f"\n⚠️ {desc}")
    res = input("Proceed? (y/N): ").strip().lower()
    return res=='y'
def perform_operation(op, source, target="", confirm=True):
    global q, res, cmd
    q = source if os.path.exists(source) else next((f for f in files if Path(f).name==source), "")
    if not q: print(f"❌ Not found: {source}"); return False
    if confirm and meta.get("safe",True):
        print(f"{op.upper()}: {Path(q).name}"); 
        if target: print(" → ", target)
        if input("Confirm (y/N): ").strip().lower()!='y': return False
    try:
        ts=time.strftime("[%H:%M]")
        if op=="delete":
            os.remove(q); files.remove(q) if q in files else None; meta.pop(q,None); sem.pop(q,None); print(f"✅ Deleted: {Path(q).name}")
        elif op=="rename":
            new=os.path.join(os.path.dirname(q), target); os.rename(q,new)
            if q in files: files[files.index(q)]=new
            if q in meta: meta[new]=meta.pop(q); meta[new]["name"]=target
            if q in sem: sem[new]=sem.pop(q)
            print(f"✅ Renamed: {Path(q).name} → {target}")
        elif op=="move":
            os.makedirs(os.path.dirname(target), exist_ok=True); shutil.move(q, target)
            if q in files: files[files.index(q)]=target
            if q in meta: meta[target]=meta.pop(q)
            if q in sem: sem[target]=sem.pop(q)
            print(f"✅ Moved: {Path(q).name} → {target}")
        elif op=="copy":
            shutil.copy2(q,target); print(f"✅ Copied: {Path(q).name} → {target}")
        meta["history"].append(f"{ts} {op.upper()} {Path(q).name}"); meta["operations"]=meta.get("operations",0)+1
        return True
    except Exception as e:
        print("❌ Operation failed:", str(e)[:80]); return False
def parse_command(text):
    global q, cmd
    q = text.strip().lower()
    if meta.get("mode")=="online" and ai:
        try:
            flist=", ".join([Path(f).name for f in files[:30]])
            out = ai.chat(f"Parse to JSON: '{text}'. Files: {flist}. Return only JSON with keys action,target,dest,pattern.")
            try: return json.loads(out)
            except: pass
        except: pass
    cmd.clear()
    if any(w in q for w in ["delete","remove","del"]):
        cmd["action"]="delete"
        for w in q.split():
            if len(w)>3 and w not in ["delete","remove","del","file","files"]:
                for fp in files:
                    if w in Path(fp).name.lower(): cmd["target"]=Path(fp).name; break
                if "target" in cmd: break
    elif "rename" in q and " to " in q:
        parts=q.split(" to "); cmd["action"]="rename"; cmd["target"]=parts[0].split()[-1]; cmd["dest"]=parts[1].strip()
    elif "move" in q and " to " in q:
        parts=q.split(" to "); cmd["action"]="move"; cmd["dest"]=parts[1].strip()
    elif any(w in q for w in ["organize","sort"]): cmd["action"]="organize"
    elif any(w in q for w in ["cleanup","clean"]): cmd["action"]="cleanup"
    elif any(w in q for w in ["find","search","show"]):
        cmd["action"]="search"; terms=[w for w in q.split() if len(w)>2 and w not in ["find","search","show","file","files"]]; cmd["pattern"]=" ".join(terms)
    return cmd
def show_menu():
    print("\n================ FileGenie – Your File Wizard ================")
    print(f"Mode: {meta.get('mode','offline').upper()} | Files: {len(files)} | Safe: {'ON' if meta.get('safe') else 'OFF'}")
    print("1. 💬 Conversational Commands    - 'organize python files', 'delete temp files'")
    print("2. 🧠 Quick Semantic Summaries   - AI-powered content analysis")
    print("3. 🗂️  Smart Organize            - Auto-categorization by type/content")
    print("4. 🔗 Detect & Remove Duplicates - Find and manage duplicate files")
    print("5. 🧹 Smart Cleanup              - Find temp, old, large files")
    print("6. 🔍 Semantic Search            - Find files by meaning and content")
    print("7. 🔗 Build Relationships        - Discover semantic file connections")
    print("8. 📊 Analytics                  - Comprehensive workspace insights")
    print("9. 🚀 Quick Ops                  - Direct file rename/move/delete")
    print("10. 💡 Smart Suggestions         - AI-powered workspace recommendations")
    print("11. 🏷️ Auto-Tagging              - Semantic file categorization")
    print("12. 📊 Mini Dashboard            - Quick workspace analytics")
    print("13. 📂 Explain Folder           - AI folder content analysis")
    print("14. ✨ Smart Rename              - Auto-fix messy filenames")
    print("0. ❌ Exit                       - Safe shutdown")
    print("💡 Type 'help' to see example usage commands")
def handle_choice(c):
    global q, res, cmd
    if c=="help":
        cmd["show_extended_help"] = True
        print("🧞‍♂️ Behold! More magical commands revealed below the menu! ✨")
        return True
    if c=="1":
        print("\n🧞‍♂️ Your wish is my command! Tell me what you desire:"); t=input("Master's command: ").strip()
        if t: cmd=parse_command(t); execute_parsed(cmd)
    elif c=="2":
        print("\n🧞‍♂️ Peering into the essence of your files... Unveiling their secrets!"); analyze_content()
        for p,s in list(sem.items())[:10]: print(f"- {Path(p).name} → {s.get('summary')[:120]}")
    elif c=="3":
        print("\n🧞‍♂️ Let me work my magic! Auto-organizing files..."); smart_organize(True)
    elif c=="4":
        print("\n🧞‍♂️ Summoning duplicate detection magic... Seeking twin files!"); groups=detect_duplicates()
        if not groups: print("🧞‍♂️ Your files are unique treasures! No duplicates in this realm! ✨")
        else:
            print(f"Found {len(groups)} groups. Preview:")
            for k,v in groups.items(): print(f"Group '{k}': {[Path(x).name for x in v]}")
            if input("Remove duplicates? (y/N): ").lower()=='y': confirm_remove_duplicates()
    elif c=="5":
        print("\nSmart cleanup suggestions:"); smart_cleanup()
    elif c=="6":
        t=input("Search query (meaning or keywords): ").strip()
        if t: semantic_search(t)
    elif c=="7":
        if meta.get("mode")=="online": build_relationships(); show_relationships()
        else: print("🧞‍♂️ My crystal ball needs AI magic! Grant me OPENAI_API_KEY to see connections! 🔮")
    elif c=="8":
        stats=meta.get("stats",{}); print(f"\nAnalytics: Files={stats.get('count',0)} SizeMB={stats.get('size',0)//(1024*1024)} Dups={stats.get('duplicates',0)}")
        print("Top types:"); 
        for ext,cnt in sorted(stats.get("types",{}).items(), key=lambda x:x[1], reverse=True)[:6]: print(f"  {ext}: {cnt}")
    elif c=="9":
        print("\nQuick Operations Menu:"); print("a) Rename  b) Move  c) Delete  d) Copy  e) Create folder")
        q=input("Select (a-e): ").strip().lower()
        if q=="a":
            res=input("File to rename: ").strip(); cmd["new"]=input("New name: ").strip() if res else ""
            if res and cmd["new"]: perform_operation("rename", res, cmd["new"])
        elif q=="b":
            res=input("File to move: ").strip(); cmd["dest"]=input("Destination: ").strip() if res else ""
            if res and cmd["dest"]: perform_operation("move", res, cmd["dest"])
        elif q=="c":
            res=input("File to delete: ").strip()
            if res: perform_operation("delete", res)
        elif q=="d":
            res=input("File to copy: ").strip(); cmd["dest"]=input("Copy to: ").strip() if res else ""
            if res and cmd["dest"]: perform_operation("copy", res, cmd["dest"])
        elif q=="e":
            res=input("Folder name: ").strip()
            if res: 
                try: os.makedirs(res, exist_ok=True); print(f"🧞‍♂️ Abracadabra! Conjured folder '{res}' from thin air! ✨")
                except Exception as e: print(f"❌ Failed: {str(e)[:50]}")
    elif c=="10": print("\n💡 Smart Suggestions:"); smart_suggestions()
    elif c=="11": print("\n🏷️ Auto-Tagging:"); auto_tagging()
    elif c=="12": print("\n📊 Dashboard:"); mini_dashboard()
    elif c=="13": print("\n📂 Folder Analysis:"); explain_folder()
    elif c=="14": print("\n✨ Smart Rename:"); smart_rename()
    elif c=="0": 
        if confirm_action("Exit FileGenie?"): return False
    else:
        print("🧞‍♂️ That spell is unknown to me! Choose from my magical menu above! ✨")
    input("\n⏎ Continue..."); return True
def show_relationships():
    print("\n🔗 Semantic relationships (top groups):")
    semmap = rel.get("semantic",{})
    items = sorted(semmap.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    for p,neis in items:
        if neis:
            cmd["unique_rels"] = []
            for n,s in neis:
                if (n,s) not in cmd["unique_rels"]: cmd["unique_rels"].append((n,s))
            if cmd["unique_rels"]:
                print(f"\n📄 {Path(p).name}:")
                for n,s in sorted(cmd["unique_rels"], key=lambda x:x[1], reverse=True)[:3]: 
                    print(f"   🔗 {Path(n).name} ({s})")
def execute_parsed(parsed):
    if not parsed or "action" not in parsed: print("Could not parse intent."); return
    a = parsed["action"]
    if a=="organize": smart_organize(True)
    elif a=="search" and parsed.get("pattern"): semantic_search(parsed["pattern"])
    elif a=="cleanup": smart_cleanup()
    elif a in ["delete","rename","move"] and parsed.get("target"):
        perform_operation(a, parsed["target"], parsed.get("dest",""))
def smart_suggestions():
    global cmd, q, res; cmd.clear(); cmd["sugg"]=[]
    stats=meta.get("stats",{}); temp_files=len([f for f in files if any(x in meta[f]["name"].lower() for x in ["temp","tmp","backup","copy"])])
    if stats.get("duplicates",0)>3: cmd["sugg"].append("🔄 Run duplicate cleanup - found duplicates")
    if temp_files>2: cmd["sugg"].append("🗑️ Clean temporary files - declutter workspace")
    if stats.get("large",0)>2: cmd["sugg"].append("📦 Review large files (5MB+) - free up space")
    if meta.get("mode")=="offline": cmd["sugg"].append("🤖 Set OPENAI_API_KEY for AI magic")
    if len(files)>30 and not os.path.exists("code"): cmd["sugg"].append("🗂️ Auto-organize files by type")
    if meta.get("mode")=="online" and ai and len(cmd["sugg"])<3:
        try:
            file_types=", ".join(list(stats.get("types",{}).keys())[:5])
            res=ai.chat(f"Give 3 smart file management tips for workspace with {len(files)} files, types: {file_types}",100)
            cmd["ai_tips"]=[tip.strip() for tip in res.split('\n') if tip.strip()][:2]
            cmd["sugg"].extend([f"🧞‍♂️ {tip}" for tip in cmd["ai_tips"]])
        except: pass
    while len(cmd["sugg"])<3:
        cmd["sugg"].extend(["🏷️ Try auto-tagging to categorize files","📊 Check dashboard for insights","✨ Use smart rename for messy filenames"])
    print("💡 Smart Suggestions:"); [print(f"   {s}") for s in cmd["sugg"][:5]]; return cmd["sugg"]
def auto_tagging():
    global sem, cmd; cmd.clear(); cmd["tags"]={}; cmd["tagged"]=0
    if not sem: print("❌ Run content analysis first (option 2)"); return
    for fp,info in sem.items():
        summary=info.get("summary","").lower(); tags=[]
        if any(w in summary for w in ["config","setting","env",".json",".yaml"]): tags.append("#config")
        if any(w in summary for w in ["test","spec","unit","pytest"]): tags.append("#test")
        if any(w in summary for w in ["doc","readme","guide","manual"]): tags.append("#docs")
        if any(w in summary for w in ["data","csv","database","sql"]): tags.append("#data")
        if any(w in summary for w in ["python","javascript","code","class","function"]): tags.append("#code")
        if any(w in summary for w in ["image","photo","png","jpg"]): tags.append("#media")
        if tags: cmd["tags"][Path(fp).name]=tags; cmd["tagged"]+=1
    print(f"🏷️ Auto-tagged {cmd['tagged']} files:")
    for name,tags in list(cmd["tags"].items())[:8]: print(f"   {name}: {' '.join(tags)}")
def mini_dashboard():
    global cmd; cmd.clear(); stats=meta.get("stats",{}); cmd["folders"]=len([d for d in ["code","docs","data","misc","backup"] if os.path.exists(d)])
    print("📊 MINIMAL DASHBOARD ANALYTICS"); print("="*35)
    print(f"📁 Total Files: {len(files)}"); print(f"🧩 Folders Auto-Created: {cmd['folders']}")
    print(f"🔁 Duplicates Found: {stats.get('duplicates',0)}"); print(f"⚙️ Mode: {meta.get('mode','offline').title()}")
    print(f"📈 Operations Done: {meta.get('operations',0)}"); print(f"💾 Workspace Size: {stats.get('size',0)//(1024*1024)}MB")
def explain_folder():
    global q, cmd, res; q=input("📂 Folder to explain (Enter=current): ").strip() or "."
    if not os.path.exists(q): print("❌ Folder not found"); return
    cmd.clear(); cmd["types"]={}; cmd["large"]=0; cmd["total"]=0; cmd["subdirs"]=[]
    for root,dirs,fns in os.walk(q):
        if root==q: cmd["subdirs"]=dirs[:5]
        if root!=q: break
        for fn in fns:
            fp=os.path.join(root,fn); ext=Path(fp).suffix.lower(); cmd["total"]+=1
            try: 
                if os.path.getsize(fp)>1000000: cmd["large"]+=1
                cmd["types"][ext]=cmd["types"].get(ext,0)+1
            except: pass
    top_types=sorted(cmd["types"].items(),key=lambda x:x[1],reverse=True)[:4]
    if meta.get("mode")=="online" and ai and cmd["total"]>0:
        try: 
            file_desc=f"{cmd['total']} files: "+", ".join([f"{ext or 'misc'}({cnt})" for ext,cnt in top_types])
            folder_desc=f" Subfolders: {', '.join(cmd['subdirs'])}" if cmd["subdirs"] else ""
            res=ai.chat(f"Analyze this folder contents in 2 sentences: {file_desc}{folder_desc}",80)
            print(f"🧞‍♂️ Analysis: {res}")
        except: pass
    print(f"📂 Folder '{q}': {cmd['total']} files, {len(cmd['subdirs'])} subfolders")
    for ext,cnt in top_types: print(f"   {ext or '[no ext]'}: {cnt} files")
    if cmd["subdirs"]: print(f"   📁 Subfolders: {', '.join(cmd['subdirs'])}")
    if cmd["large"]: print(f"   📦 Large files: {cmd['large']}")
def smart_rename():
    global cmd, q; cmd.clear(); cmd["renamed"]=0
    for fp in files:
        name=Path(fp).name; stem=Path(fp).stem; ext=Path(fp).suffix; new_name=None
        if re.match(r"Screenshot.*\(\d+\)",name): new_name=f"Screenshot_{time.strftime('%Y%m%d')}{ext}"
        elif re.match(r"Document.*\(\d+\)",name): 
            num=re.search(r'\((\d+)\)',name); new_name=f"Document_v{num.group(1) if num else '1'}{ext}"
        elif "Copy of" in name: new_name=name.replace("Copy of ","").replace("  "," ")
        elif re.search(r'\s+\(\d+\)',stem): new_name=re.sub(r'\s+\(\d+\)','_copy',stem)+ext
        if new_name and new_name!=name and not os.path.exists(os.path.join(os.path.dirname(fp),new_name)):
            if perform_operation("rename",fp,new_name,False): cmd["renamed"]+=1
    print(f"🧞‍♂️ Poof! Magically renamed {cmd['renamed']} messy files! ✨")
def main():
    global q, meta, ai
    print("========================================================")
    print("FileGenie — Conversational Semantic File Manager ")
    print("8 variables • <=500 lines • Offline/ Online - AI modes")
    print("========================================================")
    init_agent()
    root = input("Workspace directory (Enter=current): ").strip() or "."
    if not os.path.exists(root): print("Directory not found."); return
    scan_workspace(root)
    if meta.get("mode")=="online":
        print(f"\n🤖 AI Available! Choose your mode:")
        print("1. 🚀 FAST Mode (offline) - Instant responses, basic summaries")
        print("2. 🧠 SMART Mode (AI) - Advanced analysis, takes time but intelligent")
        q = input("Choose mode (1=Fast, 2=Smart, Enter=Smart): ").strip()
        if q=="1":
            meta["mode"]="offline"; ai=None;             print("🧞‍♂️ FAST mode selected - I'll be lightning quick!")
        else:
            print("🧞‍♂️ SMART mode chosen! Summoning ancient AI wisdom... (brewing magic potions...)")
    else:
        print("📱 Running in FAST mode (AI unavailable)")
    analyze_content()
    if meta.get("mode")=="online": build_relationships()
    print("\n🧞‍♂️ Your magical file assistant awaits! What shall we conjure today? ✨")
    while True:
        try:
            show_menu()
            if cmd.get("show_extended_help"):
                print("\n✨ EXTENDED MAGICAL COMMANDS:\n'move all images to photos folder' | 'find large files' | 'cleanup workspace' | 'organize python projects' | 'explain my downloads folder'")
                cmd["show_extended_help"] = False
            else:
                print("\nExamples: 'find invoices' | 'organize' | 'delete temp backups' | 'rename draft.txt to final.txt'")
            choice=input("Choice: ").strip()
            if not handle_choice(choice): print("🧞‍♂️ Your wish is my command! FileGenie vanishing... ✨"); break
        except KeyboardInterrupt: print("\nInterrupted — exiting."); break
        except Exception as e: print("Error:", str(e)[:120]); input("Enter to continue...")
if __name__=="__main__": main()