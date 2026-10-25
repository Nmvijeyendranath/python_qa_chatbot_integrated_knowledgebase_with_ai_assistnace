import argparse
from pathlib import Path
from .core import load_documents,save_chunks
def main():
    p=argparse.ArgumentParser(description='Chunk Markdown/JSON/text knowledge base into local index corpus')
    p.add_argument('--data',default='data/knowledge'); p.add_argument('--output',default='data/index.json')
    a=p.parse_args(); root=Path(a.data); chunks=load_documents(root.rglob('*') if root.is_dir() else [root]); save_chunks(chunks,Path(a.output))
    print(f'Indexed {len(chunks)} chunks from {root} -> {a.output}')
if __name__=='__main__': main()
