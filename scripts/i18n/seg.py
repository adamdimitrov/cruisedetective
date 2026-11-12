import re, html as H
TEXT=re.compile(r'>([^<>]+)<')
ATTR=re.compile(r'\b(alt|data-cap|aria-label|title)="([^"]*)"')
def segments(block):
    out=[]
    for m in TEXT.finditer(block):
        t=m.group(1)
        if t.strip() and re.search(r'[A-Za-z]',t): out.append(t.strip())
    for m in ATTR.finditer(block):
        if re.search(r'[A-Za-z]',m.group(2)): out.append(m.group(2).strip())
    return out
def cards(h):
    res=[]
    for mm in re.finditer(r'<div class="bpa-card"',h):
        d=mm.start()
        c=re.search(r'<!-- #\d+: [^>]*-->\s*$',h[max(0,d-300):d])
        s=d-len(c.group(0)) if c else d
        depth=0
        for m in re.compile(r'<(/?)div\b[^>]*>').finditer(h,d):
            depth+= -1 if m.group(1) else 1
            if depth==0: res.append((s,m.end())); break
    return res
