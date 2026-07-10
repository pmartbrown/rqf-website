import os
PAGES = ['calculators/morby-stack','calculators/echo','calculators','affiliates','about','faq','privacy','terms','morby-method','echo-method','double-close','emd','hard-money','dscr']
def rewrite(fp, up):
    h = open(fp).read()
    for p in PAGES:
        h = h.replace('href="/%s/"' % p, 'href="%s%s/"' % (up, p))
    h = h.replace('href="/#', 'href="%s#' % ('./' if up=='' else up))
    h = h.replace('href="/"', 'href="%s"' % ('./' if up=='' else up))
    h = h.replace('src="/assets/', 'src="%sassets/' % up)
    h = h.replace("url('/assets/", "url('%sassets/" % up)
    open(fp,'w').write(h)
rewrite('index.html','')
for p in PAGES:
    up = '../' * (p.count('/') + 1)
    rewrite(os.path.join(p,'index.html'), up)
print('paths made relative for GitHub Pages project site')
