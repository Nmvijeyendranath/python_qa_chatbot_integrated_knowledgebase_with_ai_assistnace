from __future__ import annotations
import json, re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Chunk:
    id: str
    text: str
    source: str
    heading: str = ""
    kind: str = "prose"
    language: str = ""
    version: str = ""

def _split_markdown(text: str):
    """Preserve fenced code and heading metadata; prose paragraphs split independently."""
    lines=text.splitlines(keepends=True); blocks=[]; buf=[]; in_fence=False; fence=None; heading=""; lang=""
    def flush():
        nonlocal buf
        value=''.join(buf).strip()
        if value: blocks.append((value,heading,"code" if in_fence else "prose",lang))
        buf=[]
    for line in lines:
        m=re.match(r'^\s*(#{1,6})\s+(.+?)\s*#*\s*$',line)
        fm=re.match(r'^\s*(```+|~~~+)(.*)$',line)
        if not in_fence and m:
            flush(); heading=m.group(2).strip(); blocks.append((heading,heading,"heading","")); continue
        if fm:
            if not in_fence:
                flush(); in_fence=True; fence=fm.group(1); lang=fm.group(2).strip().split()[0] if fm.group(2).strip() else ""; buf=[line]
            elif fm.group(1)[0]==fence[0]:
                buf.append(line); flush(); in_fence=False; fence=None; lang=""
            else: buf.append(line)
            continue
        if in_fence: buf.append(line); continue
        if not line.strip(): flush()
        else: buf.append(line)
    flush()
    return blocks

def _overlap_units(text: str, max_chars: int, overlap: int) -> list[str]:
    # Split prose at sentence/line boundaries first; only hard-cut an oversized single unit.
    units=re.split(r'(?<=[.!?])\s+|\n+',text.strip()); out=[]; current=''
    for unit in filter(None,units):
        while len(unit)>max_chars:
            if current: out.append(current); current=''
            cut=unit.rfind(' ',0,max_chars+1); cut=cut if cut>0 else max_chars
            out.append(unit[:cut].strip()); unit=unit[cut:].strip()
        candidate=(current+' '+unit).strip()
        if len(candidate)>max_chars and current:
            out.append(current); tail=current[-overlap:] if overlap else ''; current=(tail+' '+unit).strip()
        else: current=candidate
    if current: out.append(current)
    return out

def chunk_document(text: str, source: str, *, max_chars: int=1200, overlap: int=160, version: str="") -> list[Chunk]:
    if max_chars<1 or overlap<0 or overlap>=max_chars: raise ValueError('Require max_chars >= 1 and 0 <= overlap < max_chars')
    result=[]; seen=set(); counter=0
    for block,heading,kind,language in _split_markdown(text):
        # Code blocks are atomic to avoid breaking syntax/indentation. Oversized code remains intact.
        pieces=[block] if kind in ('code','heading') or len(block)<=max_chars else _overlap_units(block,max_chars,overlap)
        for piece in pieces:
            normalized=piece.strip()
            if not normalized or normalized in seen: continue
            seen.add(normalized); counter+=1
            result.append(Chunk(f'{source}#{counter}',normalized,source,heading,kind,language,version))
    return result

def load_documents(paths: Iterable[Path]) -> list[Chunk]:
    all_chunks=[]
    for path in sorted(paths):
        if path.suffix.lower() not in {'.md','.markdown','.txt','.json'}: continue
        # Streaming file reads limit peak memory; one logical document is decoded at a time.
        with path.open(encoding='utf-8') as f: text=f.read()
        version=''
        if path.suffix.lower()=='.json':
            try:
                obj=json.loads(text); version=str(obj.get('version','')) if isinstance(obj,dict) else ''
                text=json.dumps(obj,ensure_ascii=False,indent=2)
            except json.JSONDecodeError: pass
        all_chunks.extend(chunk_document(text,path.as_posix(),version=version))
    return all_chunks

class Retriever:
    def __init__(self,chunks:list[Chunk],threshold:float=.10,rerank:bool=False):
        self.chunks=chunks; self.threshold=threshold; self.reranker=None
        self.word=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,lowercase=True,token_pattern=r'(?u)\b[\w.-]+\b')
        self.char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1,sublinear_tf=True,lowercase=True)
        corpus=[f"{c.heading}\n{c.text}".strip() for c in chunks] or ['empty corpus sentinel']
        self.wmat=self.word.fit_transform(corpus); self.cmat=self.char.fit_transform(corpus)
        if rerank:
            try:
                from sentence_transformers import CrossEncoder
                self.reranker=CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            except Exception: self.reranker=None
    def search(self,query:str,top_k:int=5):
        if not query.strip() or not self.chunks:return []
        w=cosine_similarity(self.word.transform([query]),self.wmat).ravel(); c=cosine_similarity(self.char.transform([query]),self.cmat).ravel(); scores=.65*w+.35*c
        order=scores.argsort()[::-1][:max(top_k*3,top_k)]
        if self.reranker:
            pairs=[[query,self.chunks[i].text] for i in order]
            rs=self.reranker.predict(pairs); order=sorted(zip(order,rs),key=lambda x:x[1],reverse=True)[:top_k]
            ranked=[(int(i),float(s)) for i,s in order]
        else: ranked=[(int(i),float(scores[i])) for i in order[:top_k]]
        return [{'chunk':self.chunks[i],'score':score} for i,score in ranked]
    def answer(self,query:str,top_k:int=5):
        hits=self.search(query,top_k); accepted=[h for h in hits if h['score']>=self.threshold]
        if not accepted:return {'answer':"I don't have enough information in the available knowledge base to answer that confidently.",'abstained':True,'confidence':hits[0]['score'] if hits else 0.0,'sources':[],'matches':[] }
        refs=[]; snippets=[]
        for h in accepted:
            ch=h['chunk']; refs.append({'id':ch.id,'source':ch.source,'heading':ch.heading,'score':round(h['score'],4),'kind':ch.kind,'language':ch.language,'version':ch.version}); snippets.append(ch.text)
        # Excerpts are returned verbatim rather than synthesized, preventing unsupported claims.
        return {'answer':'Relevant knowledge-base excerpts (verbatim):\n\n'+'\n\n---\n\n'.join(snippets),'abstained':False,'confidence':round(accepted[0]['score'],4),'sources':refs,'matches':refs}

def save_chunks(chunks:list[Chunk],path:Path):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps([asdict(c) for c in chunks],ensure_ascii=False,indent=2),encoding='utf-8')
def load_chunks(path:Path)->list[Chunk]:
    return [Chunk(**x) for x in json.loads(path.read_text(encoding='utf-8'))]
