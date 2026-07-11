#!/usr/bin/env python3
"""RQF site page generator - builds subpages sharing the Apex design system.
Run from site/: python3 build_pages.py"""
import os, re

idx = open('index.html').read()
CSS = re.search(r'<style>(.*?)</style>', idx, re.S).group(1)
MODAL = re.search(r'(<!-- GET FUNDED MODAL -->.*?)(?=<!-- LEARN DRAWER -->)', idx, re.S).group(1)
SCRIPT = re.search(r'<script>(.*?)</script>', idx, re.S).group(1)
# null-safe for pages that lack some calculator elements
SCRIPT = SCRIPT.replace("function num(id){return +(document.getElementById(id).value.replace(/[^0-9]/g,''))||0}",
 "function num(id){var el=document.getElementById(id);return el?(+(el.value.replace(/[^0-9]/g,''))||0):0}")
SCRIPT = SCRIPT.replace("stack();echo();","if(document.getElementById('s_res'))stack();if(document.getElementById('e_res'))echo();")
FOOTER = re.search(r'(<footer>.*?</footer>)', idx, re.S).group(1)

NAV = '''<div style="background:var(--orange);color:#141311;text-align:center;padding:20px 16px;font-size:clamp(18px,2.8vw,26px);font-weight:800;line-height:1.35">🚧 This site is under construction — to submit deals, please visit <a href="https://txfhub.com" style="text-decoration:underline;color:#141311">txfhub.com</a></div>
<nav><div class="wrap nav-in">
  <a class="brand" href="/"><img src="/assets/lockup_dark.png" alt="RealQuick Funds"></a>
  <div class="nav-links"><a href="/#types">Funding</a><a href="/calculators/">Calculators</a><a href="/#types">Learn</a><a href="/affiliates/">Become an Affiliate</a><a href="https://www.skool.com/fundinghub">Community</a></div>
  <button class="btn" onclick="openModal()">Get Funded</button>
</div></nav>'''

EXTRA_CSS = '''
.pagehero{background:var(--deep);color:#fff;padding:84px 0 64px;position:relative;overflow:hidden}
.pagehero:before{content:"";position:absolute;width:600px;height:600px;border-radius:50%;background:rgba(254,149,6,.18);filter:blur(110px);top:-280px;right:-120px}
.pagehero .wrap{position:relative;z-index:2}
.pagehero h1{color:#fff;font-size:clamp(34px,4.6vw,56px)}
.pagehero .sub{color:#b3b1a9}
.content{padding:72px 0}
.content h2{font-size:clamp(24px,3vw,34px);margin-top:48px}
.content h2:first-child{margin-top:0}
.content p,.content li{font-size:16px;color:#54524b;max-width:760px}
.content ul{padding-left:22px;display:grid;gap:8px;margin-top:10px}
.steps{display:grid;gap:12px;margin-top:18px;max-width:760px}
.step{display:flex;gap:16px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.step b{font-family:var(--mono);color:var(--orange-d)}
.ctaband{background:var(--deep);border-radius:24px;padding:56px;text-align:center;color:#fff;margin-top:64px}
.ctaband h2{color:#fff;margin:0 0 10px}
.ctaband p{color:#b7b4ab;margin-bottom:26px;max-width:none}
.faqi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px 24px;margin-top:12px;max-width:820px}
.faqi h3{font-family:var(--disp);font-size:17px;font-weight:700}
.faqi p{margin-top:8px;font-size:15px}
.sched{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
.duo2{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:920px;margin-top:20px}
@media(max-width:760px){.duo2{grid-template-columns:1fr}}
.toolgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:20px;max-width:1080px}
@media(max-width:960px){.toolgrid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.toolgrid{grid-template-columns:1fr}}
.tool{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px;display:flex;flex-direction:column;gap:10px;box-shadow:0 20px 50px -30px rgba(21,20,18,.25);text-decoration:none;color:inherit;transition:.15s}
a.tool:hover{transform:translateY(-3px);box-shadow:0 26px 60px -30px rgba(21,20,18,.35)}
.tool .ic{width:44px;height:44px;border-radius:12px;background:#fff2df;color:var(--orange-d);display:flex;align-items:center;justify-content:center;font-size:20px}
.tool h3{font-family:var(--disp);font-size:19px;font-weight:800}
.tool p{font-size:13.5px;color:#54524b;line-height:1.55;flex:1;max-width:none}
.tool .go{font-weight:800;color:var(--orange-d);font-size:14px}
.tool .tag{display:inline-block;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;background:#eceef4;color:#3d4b66;border-radius:20px;padding:3px 10px;width:fit-content}
.tool.soon{opacity:.8;border-style:dashed}
.calcwrap{max-width:560px}
.pagehero .btn-ghost{background:rgba(255,255,255,.06);color:#fff;border:1px solid rgba(255,255,255,.18);box-shadow:none}
.pagehero .btn-ghost:hover{border-color:var(--orange);color:var(--orange)}
'''

def page(path, title, desc, kicker, h1, sub, body, cta_type=None, cta_label="Get Funded", cta_href=None, band=None, cta2=None):
    cta = "openModal('%s')" % cta_type if cta_type else "openModal()"
    cta_btn = '<a class="btn" href="%s">%s</a>' % (cta_href, cta_label) if cta_href else '<button class="btn" onclick="%s">%s</button>' % (cta, cta_label)
    cta2_btn = '<a class="btn btn-ghost" href="%s">%s</a>' % (cta2[1], cta2[0]) if cta2 else ''
    band_h, band_p = band if band else ('Got a deal? Get funded. <span class="grad">Real quick.</span>', 'Two-minute form &middot; same-day decisions on most deals &middot; all 50 states.')
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>%s%s</style>
</head>
<body>
<div class="aurora"><div class="a2"></div></div>
<main>
%s
<header class="pagehero"><div class="wrap">
  <div class="k" style="color:var(--orange)">%s</div>
  <h1>%s</h1>
  <p class="sub" style="max-width:640px">%s</p>
  <div class="hero-ctas" style="margin-top:26px">%s%s</div>
</div></header>
<div class="content"><div class="wrap">
%s
<div class="ctaband"><h2>%s</h2>
<p>%s</p>
%s</div>
</div></div>
%s
</main>
%s
<div class="doverlay" id="doverlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer"><div class="dr-head"><button class="x" onclick="closeDrawer()">&times;</button><div class="k" id="dr_k"></div><h3 id="dr_title"></h3></div><div class="dr-body" id="dr_body"></div></div>
<script>%s</script>
</body>
</html>''' % (title, desc, CSS, EXTRA_CSS, NAV, kicker, h1, sub, cta_btn, cta2_btn, body, band_h, band_p, cta_btn, FOOTER, MODAL, SCRIPT)
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path,'index.html'),'w').write(html)
    print('built', path)

def steps(items):
    return '<div class="steps">' + ''.join('<div class="step"><b>0%d</b><span>%s</span></div>' % (i+1,s) for i,s in enumerate(items)) + '</div>'
def ul(items):
    return '<ul>' + ''.join('<li>%s</li>' % x for x in items) + '</ul>'

DEALS = {
 'morby-method': dict(kicker='Creative Finance', name='Morby Method', cta='morby', req='Start a Morby request', calc=('Morby Calculator','/calculators/morby-stack/'),
   title='Morby Method (Stack Method) Funding | RealQuick Funds',
   desc='Morby Method (Stack Method) funding - seller carry + primary lender stacked into one creative close. All 50 states. Same-day decisions on most deals.',
   sub='Stack seller carry with a primary lender and acquire property with little - sometimes zero - of your own cash. In the right structure, you can even receive cash back at closing.',
   body='''
<h2>What the Morby Method is</h2>
<p>The Morby Method is a creative-finance acquisition structure that combines a seller-carried note with a primary lender so the total capital stack covers - or exceeds - the purchase price and closing costs. You'll also hear it called the <b>Stack Method</b> - same structure, same math; the name comes from stacking funding sources on one deal. Done right, the buyer closes with minimal cash out of pocket, and in some structures walks away from the closing table with funds in hand.</p>
<h2>When to use it</h2>
''' + ul(['The seller is open to carrying part of the purchase price','You have a primary lender (DSCR, private, or hard money) covering most of the purchase','You want to preserve cash while still closing quickly','The numbers work - run them in the <a href="/calculators/morby-stack/">Morby Calculator</a> first']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(['Submit your structure - purchase price, seller carry, primary lender amount, closing date.','We verify the stack and issue written terms — same day on most submissions.','Capital wires to title for closing. Escrow repays us per the structure.']) + '''
<h2>What you'll need</h2>
''' + ul(['Executed purchase contract','Seller carry terms (amount and position)','Primary lender term sheet or approval','Title/escrow contact'])),
 'echo-method': dict(kicker='Creative Finance', name='Echo Method', cta='echo', req='Start an Echo request', calc=('Echo Calculator','/calculators/echo/'),
   desc='Echo Method funding - down-payment capital for the end buyer on the back half of a double close, repaid from the spread at one closing. All 50 states.',
   sub="Down-payment funding for your end buyer on the back half of a double close - repaid from the deal's spread on the same settlement. One closing. Everybody cashes out.",
   body='''
<h2>What the Echo Method is</h2>
<p>Echo is short-term funding for the end buyer's down payment on the back half of a double close. The end buyer closes with their primary lender plus our capital - and we're repaid out of the deal's spread on that same settlement statement. Funds in, funds out, one closing. That's the echo.</p>
<p>Compare that to a gap loan: no recorded second-position note, no debt sitting on the deal for six to nine months. The funding is in and out of a single closing, and every party - seller, wholesaler, end buyer, lender - cashes out at the table.</p>
<h2>When to use it</h2>
''' + ul(["You wholesale, and good buyers keep stalling because they can't cover the down payment","You're the end buyer purchasing from a wholesaler and don't want second-position gap debt","The B-C price is supported by the appraisal - that's what sizes the primary loan and creates the spread",'Run the legs in the <a href="/calculators/echo/">Echo Calculator</a> first - if the spread covers the funding, we can move fast']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(["Submit both legs - A-B and B-C contracts, the end buyer's primary lender terms, and the closing date.",'We verify the spread covers the funding and issue written terms - same day on most submissions.','Primary lender funds land at title first; we wire the down payment; title repays us from the spread on the same settlement.']) + '''
<h2>What you'll need</h2>
''' + ul(['A-B and B-C purchase contracts',"The end buyer's primary lender term sheet or approval",'Title/escrow contact comfortable with back-to-back closings'])),
 'double-close': dict(kicker='Transactional Funding', name='Double Close', cta='dc', req='Start a Double Close request',
   sub='100% A-to-B funding for back-to-back closings. Your end buyer never sees your contract price - your spread stays private.',
   body='''
<h2>What a double close is</h2>
<p>A double close (or back-to-back close) is two closings on the same property, the same day: you buy from the seller (A-to-B), then sell to your end buyer (B-to-C). RealQuick Funds provides 100% of the A-to-B purchase capital, and escrow repays us from your B-to-C proceeds. Unlike an assignment, your contract price and your profit are never disclosed to the end buyer.</p>
<h2>When to use it</h2>
''' + ul(['Assignments are restricted in your market or by the contract',"You don't want your fee visible to buyer or seller",'Your end buyer is ready and funded','You need same-day in-and-out capital with zero of your own cash']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(['Submit both contracts and the closing date.','Written terms same day on most submissions. No credit pull.','We fund A-to-B; escrow repays us from your B-to-C proceeds.']) + '''
<h2>What you'll need</h2>
''' + ul(['A-to-B and B-to-C contracts','End buyer proof of funds or loan approval','One title/escrow office handling both legs (preferred)'])),
 'emd': dict(kicker='Transactional Funding', name='EMD Funding', cta='emd', req='Start an EMD request',
   sub='Earnest money wired before your deadline. Never lose a contract waiting on capital.',
   body='''
<h2>What EMD funding is</h2>
<p>We wire your earnest money deposit to escrow so you can lock the contract without pulling from your own reserves. Built for high-velocity wholesalers and Gator-style operators juggling multiple contracts at once.</p>
<h2>When to use it</h2>
''' + ul(["You're juggling multiple contracts and need EMD liquidity",'A deadline is hours away and your capital is deployed elsewhere','You want to keep dry powder available for the deals that need it']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(['Submit the contract, EMD amount, and escrow details.','Fast verification and written terms - typically same business day.','EMD wires to escrow; repayment per the agreement at closing or termination.']) + '''
<h2>What you'll need</h2>
''' + ul(['Executed purchase contract','Escrow/title wiring instructions','Clear EMD refundability terms'])),
 'hard-money': dict(kicker='Leverage', name='Hard Money Loans', cta='hml', req='Start a Hard Money request',
   sub='Asset-based loans for flips and value-add projects - underwritten on the property and the plan, not your W-2.',
   body='''
<h2>What hard money is</h2>
<p>Hard money is asset-based lending: the loan is underwritten primarily on the property, the purchase price, the rehab plan, and the after-repair value - not your personal income documentation. It is the standard tool for fix-and-flip acquisitions and value-add projects that banks move too slowly for.</p>
<h2>When to use it</h2>
''' + ul(['Fix-and-flip acquisitions and rehab budgets',"Value-add projects on a timeline banks can't meet",'Bridge situations before longer-term financing']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(['Submit property, purchase price, rehab budget, and exit plan.','Deal-first underwriting with clear terms in writing.','Fund at closing; draws structured to your project.']) + '''
<h2>What you'll need</h2>
''' + ul(['Purchase contract and rehab scope/budget','Exit strategy (sale or refinance)','Entity documents'])),
 'dscr': dict(kicker='Long-Term Financing', name='DSCR Loans', cta='dscr', req='Start a DSCR request', calc=('DSCR Calculator','/calculators/dscr/'),
   title='DSCR Loans - If It Rents, It Funds | RealQuick Funds',
   desc="What a DSCR loan is, who it's for, and how rates are actually determined - a live market index plus the five dials lenders price from. Options down to a 0.75 DSCR.",
   sub='If it rents, it funds. The property qualifies on its own rent - no W-2s, no tax returns, no paperwork circus.',
   body='''
<h2>What a DSCR loan actually is</h2>
<p>A DSCR loan is a 30-year mortgage for rental property where the property does the qualifying. No W-2s, no tax returns, no employment verification - the lender asks one question: does the rent cover the payment? You can close in an LLC, own as many financed properties as you want, and your personal tax strategy - all those write-offs that make your returns look thin - never works against you.</p>
<h2>Who it's for</h2>
<p>Three investors live on DSCR loans: the self-employed, whose tax returns understate what they actually make; the portfolio builder who's maxed out conventional financing - banks cap you around ten financed properties, DSCR lenders don't; and the investor who simply doesn't want to hand over two years of personal financials to buy a rental. If any of those is you, this is your product.</p>
<h2>How the ratio works</h2>
<p>One fraction: monthly rent &divide; the full monthly payment (principal, interest, taxes, insurance, HOA). Above 1.0, the rent carries the loan. Run your numbers in the <a href="/calculators/dscr/">DSCR Calculator</a> - it computes the ratio the way lenders underwrite it and shows the biggest loan your rent supports.</p>
<h2>How your rate is actually determined</h2>
<p>There's no single "DSCR rate." Pricing starts with a market index - most lenders price off the <b>5-year U.S. Treasury</b> - and adds a risk premium built from your file. The index moves daily; the premium is set by five dials:</p>
''' + ul(['<b>Your DSCR.</b> Stronger coverage, lower rate. Crossing 1.25 typically unlocks the best tier; below 1.0 adds a real premium.','<b>Your down payment.</b> Every extra 5% down buys the rate down a notch. 20% is the standard entry; 25%+ gets rewarded.','<b>Your credit score.</b> Pulled to price risk, not to verify income. Low-to-mid 600s can qualify; the best pricing generally starts in the 720s.','<b>Your prepayment penalty choice.</b> Most DSCR loans carry a stepdown penalty - say 3% year one, 2% year two, 1% year three. Accepting a longer penalty lowers the rate; buying it off raises it. Planning to refinance soon? This dial matters most.','<b>The extras.</b> Interest-only, short-term-rental income, small loan sizes, and cash-out refinances each nudge the rate up; larger loans and vanilla long-term rentals price best.']) + '''
<div class="faqi" style="border:2px solid var(--orange);max-width:760px"><h3>Estimated current market rates</h3>
<p style="font-family:var(--mono);font-size:16px;margin-top:10px">5-yr Treasury <b id="mk_t5">&mdash;</b> <span id="mk_asof" style="color:#9a978d;font-size:12px"></span> &nbsp;+&nbsp; risk premium &nbsp;=&nbsp; <b id="mk_lo">&mdash;</b> to <b id="mk_hi">&mdash;</b></p>
<p style="font-size:13px;color:#9a978d;margin-top:8px">Updated each business day from the U.S. Treasury's published par yield curve. Estimates only - your exact rate comes with your written terms, and it can fall outside this range in either direction.</p></div>
<h2>What lenders typically expect</h2>
''' + ul(['Down payment of 20-25% - more for sub-1.0 ratios','Credit floors starting in the low 600s; best pricing in the 720s and up','A few months of payments in liquid reserves','Minimum loan sizes around $100K - smaller properties are hard to place','An appraisal with a market-rent schedule. Notice what is missing from this list: your income.']) + '''
<h2>Short-term rentals</h2>
<p>Airbnb income can qualify, but lenders count it conservatively - the appraiser's estimate, a 12-month revenue history, or market data, usually with a haircut. Verify your city allows STRs before you tie up the property; underwriters check.</p>
<h2>Where DSCR fits in a creative deal</h2>
<p>In most <a href="/morby-method/">Morby / Stack</a> structures, the DSCR loan is the primary lender - the base of the stack that the seller carry and transactional funding build on. It also serves as the end loan in an <a href="/echo-method/">Echo Method</a> structure. Run the whole structure in the <a href="/calculators/morby-stack/">Morby / Stack Calculator</a> and check the rent coverage in the <a href="/calculators/dscr/">DSCR Calculator</a>. When both pencil, you have a deal.</p>
<h2>How it works with us</h2>
''' + steps(['Submit the property and rents (actual or market) through the two-minute form.','We route your scenario across our DSCR lender network - including options below 1.0, down to 0.75.','Written terms on the funding side typically same day; DSCR closings generally run a few weeks with the appraisal.']) + '''
<h2>DSCR questions, answered</h2>
<div class="faqi"><h3>What's a good DSCR?</h3><p>1.25 and up typically unlocks the best pricing tier. Anything above 1.0 qualifies broadly.</p></div>
<div class="faqi"><h3>Can I get a DSCR loan below 1.0?</h3><p>Yes - we have lender options down to 0.75. Expect a bigger down payment and reserves.</p></div>
<div class="faqi"><h3>Do DSCR lenders check credit?</h3><p>Yes - to price the loan, not to verify income. Your score sets your tier; your rent does the qualifying.</p></div>
<div class="faqi"><h3>Can I close in an LLC?</h3><p>Yes - entity vesting is normal on DSCR loans. Many investors prefer it.</p></div>
<div class="faqi"><h3>Can I live in the property?</h3><p>No. DSCR is investment-property financing only, and lenders verify occupancy.</p></div>
<div class="faqi"><h3>Does the lender use my lease or the appraisal rent?</h3><p>Generally the lower of your actual lease and the appraiser's market-rent schedule.</p></div>
<div class="faqi"><h3>Is a DSCR loan hard money?</h3><p>No - it's 30-year term financing for holds, not a short-term bridge.</p></div>
<div class="faqi"><h3>How fast can it close?</h3><p>Weeks, not months - the appraisal is usually the long pole.</p></div>'''),
}
def meta_desc(s, n=155):
    if len(s) <= n: return s
    return s[:n].rsplit(' ', 1)[0].rstrip(' -,;:') + '…'
for slug,d in DEALS.items():
    page(slug, d.get('title', "%s Funding | RealQuick Funds" % d['name']), meta_desc(d.get('desc', d['sub'])),
         d['kicker'], d['name'], d['sub'], d['body'], cta_type=d['cta'],
         cta_label=d.get('req', "Start a %s request" % d['name']), cta2=d.get('calc'))

CALC_BODY = '''
<h2>The deal tool library.</h2>
<p>Built by the funder - not a blog. Run your structure, adjust the estimates for your market, and know whether the deal works before you talk to anyone. Every calculator feeds straight into a two-minute funding request.</p>
<div class="toolgrid">
  <a class="tool" href="/calculators/morby-stack/"><div class="ic">&#9672;</div><h3>Morby / Stack Calculator</h3><span class="tag">Purchase + cash flow analysis</span><p>Can you close the stack - and should you keep it? Carry-coverage math plus a full rental P&amp;L with DSCR and balloon planning.</p><div class="go">Open calculator &rarr;</div></a>
  <a class="tool" href="/calculators/echo/"><div class="ic">&#9678;</div><h3>Echo Calculator</h3><span class="tag">The only one on the internet</span><p>Does the spread cover the Echo? Run both legs and see what's left for the wholesaler after funding is repaid on the same settlement.</p><div class="go">Open calculator &rarr;</div></a>
  <a class="tool" href="/calculators/dscr/"><div class="ic">&#8962;</div><h3>DSCR Calculator</h3><span class="tag">The way lenders underwrite</span><p>Gross rent &divide; PITIA &mdash; with interest-only compare, max loan at your target DSCR, and the rent you'd need. Some of our lenders fund down to 0.75.</p><div class="go">Open calculator &rarr;</div></a>
  <div class="tool soon"><div class="ic">&#8644;</div><h3>More tools on the way</h3><span class="tag">Coming soon</span><p>Double Close, EMD, and Hard Money calculators are in the workshop. Got a request? Tell us in the community.</p><div class="go" style="color:#9a978d">In the workshop</div></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:20px">Estimates only. Exact figures arrive with your written terms, typically the same day.</p>'''
MS_BODY = '''
<div class="calcwrap">
  <div class="calc"><div style="font-family:var(--disp);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--mut);margin-bottom:10px">Morby / Stack</div>
    <div class="ctabs" id="mtabs"><button class="on" onclick="ctab2('pa',this)">Purchase analysis</button><button onclick="ctab2('cf',this)">Cash flow analysis</button></div>
    <div id="pane_pa">
    <div class="purpose">Will you bring cash to close - or walk away with some?</div>
    <div class="cgrid">
      <div class="fld"><label>Purchase price</label><div class="inwrap"><span>$</span><input id="s_pp" value="400,000" oninput="fmt(this);stack()"></div></div>
      <div class="fld"><label>Seller carry</label><div class="inwrap"><span>$</span><input id="s_sc" value="80,000" oninput="fmt(this);stack()"></div></div>
      <div class="fld"><label>Primary lender <span class="hint" id="s_pl_d"></span></label><div class="inwrap"><input class="pctin" id="s_plp" value="80.0" oninput="fmtp(this);stack()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Est. closing costs <span class="hint" id="s_cc_d"></span></label><div class="inwrap"><input class="pctin" id="s_ccp" value="3.0" oninput="fmtp(this);stack()"><span class="sfx">%</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Funding fee <span class="hint" id="s_fp_d"></span></label><div class="inwrap"><input class="pctin" id="s_fp" value="2.5" oninput="fmtp(this);stack()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>TC fee</label><div class="inwrap"><span>$</span><input id="s_tc" value="3,000" oninput="fmt(this);stack()"></div></div>
      <div class="fld"><label>2nd closing</label><div class="inwrap"><span>$</span><input id="s_x2" value="1,200" oninput="fmt(this);stack()"></div></div>
    </div>
    <div class="result bring" id="s_res"><div class="rl" id="s_rl">Estimated cash to close</div><div class="rv" id="s_rv">$0</div><div class="rsub" id="s_sub"></div></div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('morby',true)">Submit this deal</button>
    </div>
    <div id="pane_cf" style="display:none">
    <div class="purpose">Keep it as a rental? Full monthly P&amp;L - uses the price, loan and carry from your purchase analysis tab.</div>
    <div class="note" style="text-align:left;margin:0 0 12px" id="cf_ctx"></div>
    <div class="mkline" style="display:none;font-size:12.5px;line-height:1.5;color:#8a5a00;background:#fff2df;border-radius:10px;padding:8px 12px;margin:0 0 12px"></div>
    <div class="cgrid">
      <div class="fld"><label>Monthly rent</label><div class="inwrap"><span>$</span><input id="cf_rent" value="4,000" oninput="fmt(this);cashflow()"></div></div>
      <div class="fld"><label>Vacancy</label><div class="inwrap"><input class="pctin" id="cf_vac" value="5.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Annual taxes</label><div class="inwrap"><span>$</span><input id="cf_tax" value="3,000" oninput="fmt(this);cashflow()"></div></div>
      <div class="fld"><label>Annual insurance</label><div class="inwrap"><span>$</span><input id="cf_ins" value="1,500" oninput="fmt(this);cashflow()"></div></div>
      <div class="fld"><label>Primary rate <span class="hint" id="cf_r1_d"></span></label><div class="inwrap"><input class="pctin" id="cf_r1" value="7.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Primary amort</label><div class="inwrap"><input class="pctin" id="cf_a1" value="30" oninput="fmtp(this);cashflow()"><span class="sfx">yrs</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Carry rate <span class="hint" id="cf_r2_d"></span></label><div class="inwrap"><input class="pctin" id="cf_r2" value="5.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Carry amort</label><div class="inwrap"><input class="pctin" id="cf_a2" value="30" oninput="fmtp(this);cashflow()"><span class="sfx">yrs</span></div></div>
      <div class="fld"><label>Balloon</label><div class="inwrap"><input class="pctin" id="cf_by" value="5" oninput="fmtp(this);cashflow()"><span class="sfx">yr</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Maintenance</label><div class="inwrap"><input class="pctin" id="cf_mnt" value="5.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>CapEx</label><div class="inwrap"><input class="pctin" id="cf_cap" value="5.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Prop Mgmt</label><div class="inwrap"><input class="pctin" id="cf_mgm" value="10.0" oninput="fmtp(this);cashflow()"><span class="sfx">%</span></div></div>
    </div>
    <div class="pnl">
      <div class="prow"><span>Gross rent</span><b id="cf_gr"></b></div>
      <div class="prow"><span>Vacancy</span><b id="cf_vc"></b></div>
      <div class="prow tot"><span>Effective income</span><b id="cf_eg"></b></div>
      <div class="prow"><span>Taxes + insurance</span><b id="cf_ti"></b></div>
      <div class="prow"><span>Maintenance + CapEx</span><b id="cf_mc"></b></div>
      <div class="prow"><span>Property management</span><b id="cf_mg"></b></div>
      <div class="prow tot"><span>Net operating income</span><b id="cf_noi"></b></div>
      <div class="prow"><span>Primary loan P&amp;I</span><b id="cf_p1"></b></div>
      <div class="prow"><span>Seller carry P&amp;I</span><b id="cf_p2"></b></div>
      <div class="prow tot" id="cf_blr" style="display:none"><span id="cf_bll">Carry balloon due</span><b id="cf_bl"></b></div>
    </div>
    <div class="result bring" id="cf_res"><div class="rl" id="cf_rl">Estimated monthly cash flow</div><div class="rv" id="cf_rv">$0</div><div class="rsub" id="cf_sub"></div></div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('morby',true)">Submit this deal</button>
    </div></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:14px">Estimates only. Exact figures arrive with your written terms, typically the same day.</p>
<h2>What this calculator tells you</h2>
<p>The Morby Method - also called the Stack Method - combines a seller-carried note with a primary lender so the capital stack covers the purchase. The purchase analysis tab answers the question that decides the deal: can you close this structure? It checks that the seller carry can repay the transactional funding and fees, caps the funding accordingly, and shows exactly what lands on you at the closing table - cash to bring, or cash back.</p>
<p>Then flip to the cash flow analysis tab: a full monthly rental P&amp;L on the same numbers - vacancy, taxes, insurance, maintenance, CapEx, property management, both loan payments, the carry balloon, and your DSCR. Whether you can close it and whether you should keep it, on one card.</p>
<h2>How to use it</h2>
<ul><li>Enter the purchase price, the seller carry, and the primary lender's percentage - the dollar equivalents show beside each field.</li><li>The fee fields are pre-filled estimates and every one of them is editable - exact figures come with your written terms.</li><li>Watch the result flip between cash to close and cash back as you adjust the structure.</li><li>Flip to cash flow analysis to see the property as a rental - payments, balloon, and DSCR included.</li></ul>
<p>Want the full mechanics? Read the <a href="/morby-method/">Morby Method deep dive</a> or ask in <a href="https://www.skool.com/fundinghub">the community</a>. When the numbers work, hit Submit - the funding request pre-fills from your calculator inputs.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
ECHO_CALC_BODY = '''
<div class="calcwrap">
  <div class="calc"><div class="ctabs" style="pointer-events:none"><button class="on">Echo</button></div>
    <div class="purpose">Does the spread cover the Echo? Run both legs of the deal.</div>
    <div class="cgrid">
      <div class="fld"><label>A-B purchase price</label><div class="inwrap"><span>$</span><input id="e_ab" value="500,000" oninput="fmt(this);echo()"></div></div>
      <div class="fld"><label>B-C sale price <span class="hint">must appraise</span></label><div class="inwrap"><span>$</span><input id="e_bc" value="725,000" oninput="fmt(this);echo()"></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Primary lender <span class="hint" id="e_ln_d"></span></label><div class="inwrap"><input class="pctin" id="e_lv" value="75.0" oninput="fmtp(this);echo()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Closing costs <span class="hint" id="e_cc_d"></span></label><div class="inwrap"><input class="pctin" id="e_ccp" value="2.0" oninput="fmtp(this);echo()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Funding fee <span class="hint" id="e_ff_d"></span></label><div class="inwrap"><input class="pctin" id="e_fp" value="2.5" oninput="fmtp(this);echo()"><span class="sfx">%</span></div></div>
    </div>
    <div class="result out" id="e_res"><div class="rl" id="e_rl">Spread covers the Echo</div><div class="rv" id="e_rv">$0</div><div class="rsub" id="e_sub"></div></div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('echo',true)">Submit this deal</button></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:14px">Estimates only. Exact figures arrive with your written terms, typically the same day.</p>
<h2>What this calculator tells you</h2>
<p>Echo is short-term funding for the end buyer's down payment on the back half of a double close - repaid out of the deal's spread on the same settlement statement. This calculator runs the one check that decides every Echo: is the spread between the A-B price and the B-C price big enough to cover the funding plus the fee? If it is, you'll see what's left for the wholesaler. If it isn't, you'll see exactly how short it is - and the usual fix is raising the B-C price, appraisal permitting.</p>
<p>The B-C price has to be supported by the appraisal - that's what sizes the primary loan and creates the spread in the first place.</p>
<h2>How to use it</h2>
<ul><li>Enter both legs: what the wholesaler is paying (A-B) and what the end buyer is paying (B-C).</li><li>Set the primary lender's percentage of the B-C price - the loan amount shows beside it.</li><li>The fee is a pre-filled estimate with a minimum floor - editable like everything else.</li><li>Slate result: the spread covers the funding. Orange: it comes up short, and by how much.</li></ul>
<p>New to the structure? Read the <a href="/echo-method/">Echo Method deep dive</a> or ask in <a href="https://www.skool.com/fundinghub">the community</a>. When the spread covers it, hit Submit - the funding request pre-fills the funded amount.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
page('calculators','Deal Calculators for Creative Finance | RealQuick Funds',
 'Free deal calculators built by a transactional funder - Morby/Stack purchase and rental cash flow analysis, Echo spread coverage, and more tools on the way.',
 'Deal Tools','Run your numbers.','The deal tool library - free calculators built by the funder. Know whether the deal works before you talk to anyone.',CALC_BODY)
page('calculators/morby-stack','Morby Method Calculator (Stack Method) - Free | RealQuick Funds',
 'Free Morby Method / Stack Method calculator: carry-coverage purchase analysis plus a full rental cash flow P&L with DSCR and balloon planning. Built by the funder.',
 'Deal Tools','Morby / Stack Calculator','Can you close it - and should you keep it? Purchase analysis with carry-coverage math, plus a full rental cash flow P&L.',MS_BODY, cta_type='morby', cta_label='Start a Morby request', cta2=('What is the Morby Method?','/morby-method/'))
page('calculators/echo','Echo Method Calculator - Free | RealQuick Funds',
 "The only Echo calculator on the internet: see whether the deal's spread covers the funding on the B-C close. Built by RealQuick Funds.",
 'Deal Tools','Echo Calculator','Does the spread cover the Echo? Run both legs and know in thirty seconds.',ECHO_CALC_BODY, cta_type='echo', cta_label='Start an Echo request', cta2=('What is the Echo Method?','/echo-method/'))
DSCR_TOOL_BODY = '''
<div class="calcwrap">
  <div class="calc"><div style="font-family:var(--disp);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--mut);margin-bottom:10px">DSCR Calculator</div>
    <div class="mkline" style="display:none;font-size:12.5px;line-height:1.5;color:#8a5a00;background:#fff2df;border-radius:10px;padding:8px 12px;margin:0 0 12px"></div>
    <div class="cgrid">
      <div class="fld"><label>Purchase price</label><div class="inwrap"><span>$</span><input id="d_pp" value="360,000" oninput="fmt(this);dscr()"></div></div>
      <div class="fld"><label>Monthly rent</label><div class="inwrap"><span>$</span><input id="d_rent" value="2,800" oninput="fmt(this);dscr()"></div></div>
      <div class="fld"><label>Down payment <span class="hint" id="d_dp_d"></span></label><div class="inwrap"><input class="pctin" id="d_dp" value="20.0" oninput="fmtp(this);dscr()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Interest rate <span class="hint" id="d_rt_d"></span></label><div class="inwrap"><input class="pctin" id="d_rt" value="7.25" oninput="fmtp(this);dscr()"><span class="sfx">%</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Term</label><div class="inwrap"><input class="pctin" id="d_tm" value="30" oninput="fmtp(this);dscr()"><span class="sfx">yrs</span></div></div>
      <div class="fld"><label>Annual taxes</label><div class="inwrap"><span>$</span><input id="d_tax" value="3,000" oninput="fmt(this);dscr()"></div></div>
      <div class="fld"><label>Annual insurance</label><div class="inwrap"><span>$</span><input id="d_ins" value="1,380" oninput="fmt(this);dscr()"></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>HOA /mo</label><div class="inwrap"><span>$</span><input id="d_hoa" value="0" oninput="fmt(this);dscr()"></div></div>
      <div class="fld"><label>Interest-only?</label><div class="inwrap" style="padding-left:6px"><select id="d_io" onchange="dscr()" style="width:100%;border:none;background:transparent;font-family:Inter;font-size:14.5px;padding:10px 8px;outline:none;color:var(--ink)"><option>No</option><option>Yes</option></select></div></div>
      <div class="fld"><label>Target DSCR</label><div class="inwrap"><input class="pctin" id="d_tg" value="1.25" oninput="fmtp(this);dscr()"><span class="sfx">&nbsp;</span></div></div>
    </div>
    <div class="pnl">
      <div class="prow"><span>Principal &amp; interest</span><b id="ds_pi"></b></div>
      <div class="prow"><span>Taxes + insurance</span><b id="ds_ti"></b></div>
      <div class="prow"><span>HOA</span><b id="ds_hoa"></b></div>
      <div class="prow tot"><span>PITIA - what lenders divide by</span><b id="ds_tot"></b></div>
    </div>
    <div class="result back" id="ds_res" style="margin-top:10px"><div class="rl" id="ds_rl">DSCR</div><div class="rv" id="ds_rv">-</div><div class="rsub" id="ds_sub"></div></div>
    <div class="solves">
      <div class="solve"><div class="sl" id="ds_mll">Max loan at DSCR 1.25</div><div class="sv" id="ds_ml">-</div></div>
      <div class="solve"><div class="sl" id="ds_rnl">Rent needed at 1.25</div><div class="sv" id="ds_rn">-</div></div>
    </div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('dscr',true)">Submit this deal</button></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:14px">Estimates only - rates and terms vary by scenario. Exact figures arrive with your written terms.</p>
<h2>What DSCR actually is</h2>
<p>One fraction. Rent on top, payment on the bottom. DSCR = monthly rent &divide; the full monthly payment - principal, interest, taxes, insurance, and any HOA (PITIA). The rent figure comes from your lease or the appraiser's market-rent schedule. Repairs, management, utilities, and vacancy never enter the math - lenders qualify the payment, not your operating budget.</p>
<p>Most free calculators get this wrong by subtracting operating expenses first. This one runs the same fraction the lender runs.</p>
<h2>Run one in your head</h2>
<p>A property rents for $2,800. The all-in payment is $2,330 - that's $1,965 of principal and interest, $250 of taxes, $115 of insurance, no HOA. 2,800 &divide; 2,330 = <b>1.20</b>. The rent clears the payment with room to spare - a deal most DSCR lenders will look at.</p>
<h2>What your number means</h2>
<ul><li><b>1.25 and above</b> - strong. This is the classic best-pricing tier.</li><li><b>1.0 to 1.24</b> - qualifies. A DSCR above 1.0 means better terms.</li><li><b>Below 1.0</b> - not dead. We have lender options down to 0.75 - expect a bigger down payment and reserves.</li><li><b>Under 0.75</b> - restructure: more down payment, interest-only, or higher rent.</li></ul>
<h2>How to use this calculator</h2>
<ul><li>Enter the purchase price, expected rent, and your down payment - the loan amount and monthly payment show beside the fields.</li><li>The rate is an editable estimate - exact terms come with your written quote.</li><li>Flip Interest-only to Yes to see how an IO period changes your ratio - it can rescue a marginal deal.</li><li>The two boxes under the result answer the questions that matter: the biggest loan this rent supports at your target DSCR, and the rent you'd need to hit it.</li></ul>
<p>Running a Morby / Stack deal? The DSCR loan is usually the primary lender in the stack - check the whole structure in the <a href="/calculators/morby-stack/">Morby / Stack Calculator</a>, or read the <a href="/dscr/">DSCR loan deep dive</a>. Questions? Ask in <a href="https://www.skool.com/fundinghub">the community</a>.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
page('calculators/dscr','DSCR Calculator - Rental Property Loan Qualifier | RealQuick Funds',
 'Free DSCR calculator that computes it the way lenders actually underwrite - gross rent divided by PITIA. Interest-only compare, max-loan and rent-needed solves. Some of our lenders fund down to 0.75.',
 'Deal Tools','DSCR Calculator','If it rents, it funds. Run the rent against PITIA - with the max-loan and rent-needed answers no other calculator gives you.',DSCR_TOOL_BODY, cta_type='dscr', cta_label='Start a DSCR request', cta2=('What is DSCR?','/dscr/'))

AFF_BODY = '''
<h2>What an affiliate is here</h2>
<p>An affiliate is anyone who brings us deals - a member of our <a href="https://www.skool.com/fundinghub">Funding Hub</a> community, or a non-member sending deals straight through this site. We prefer you come into the community first and learn how we do things, so your deals arrive in the right format with the right understanding - but it's not a requirement. Inside the community we call affiliates our acquisition team members. Same people, same pay.</p>
<h2>Why the math is different here</h2>
<p>On escrow-secured funding - EMD, Double Close, Morby/Stack, and Echo - we're the <b>direct lender</b>, not a broker. It's our capital, so there's no middleman taking a cut ahead of you: when a deal you bring funds, we split <b>actual profits 50/50</b>. You earn dollar for dollar alongside us. On the business we refer out - hard money and DSCR - we've negotiated a strong referral rate with our lending network, and <b>the majority of it goes to you</b>.</p>
<h2>Two paths</h2>
<div class="duo2">
  <div class="faqi"><h3>Free Affiliate <span style="font-family:var(--mono);font-size:11px;color:#9a978d;letter-spacing:.08em">START TODAY - $0</span></h3>
  <ul>
   <li>Send deals straight through this site - you bring the deal, you're on it, and you earn when it funds</li>
   <li>50/50 split of actual profits on deals we fund directly; the majority of the referral on placed lending</li>
   <li>No application, no approval step, no cost</li>
   <li>Want a head start? The free tier of the <a href="https://www.skool.com/fundinghub">Funding Hub</a> gets you oriented</li>
  </ul>
  <p style="margin-top:14px;font-size:13.5px;color:#9a978d"><em>Best for agents, wholesalers, and investors bringing their first deals.</em></p></div>
  <div class="faqi" style="border:2px solid var(--orange)"><h3>VIP Affiliate <span style="font-family:var(--mono);font-size:11px;color:var(--orange-d);letter-spacing:.08em">THE FULL MACHINE</span></h3>
  <ul>
   <li>The complete education - full Morby/Stack and Echo playbooks, step-by-step deal SOPs, and every call replay</li>
   <li>Your own <b>white-label funding website</b> covering the full product line under your brand, with <b>automated nurture campaigns</b> already built and running</li>
   <li><b>Proof-of-funds letters on demand</b>, whenever your buyers need them</li>
   <li>Underwriting, docs, transaction coordination, and capital - all handled behind the scenes by RealQuick Funds</li>
   <li>No application here either - join VIP inside the community and go</li>
  </ul>
  <p style="margin-top:14px;font-size:13.5px;color:#9a978d"><em>Best for operators ready to run funding as a business under their own brand.</em></p></div>
</div>
<h2>How it works</h2>
''' + steps(['Pick your door - join the Funding Hub (our recommended path), or send your first deal through this site today.','Bring the deal - inside the community you learn the exact structures and vocabulary that get deals funded fast.','Get paid when it funds - 50/50 on deals we fund directly, the majority of the referral on placed lending. We handle underwriting, docs, TC, and capital.']) + '''
<h2>Ready?</h2>
<p>Tier details and pricing live inside the community. And if you want to talk VIP through with Paul before you jump, grab a time - it's optional, not a gate.</p>
<div class="sched"><a class="btn" href="https://www.skool.com/fundinghub/about">Join the Funding Hub →</a><a class="btn btn-dark" href="https://meetings-na2.hubspot.com/realquickfunds/skoolcall">Book an optional call with Paul about joining</a></div>'''
page('affiliates','Become an Affiliate | RealQuick Funds',
 'Become a RealQuick Funds affiliate - bring deals as a community member or straight through this site. Direct-lender 50/50 profit splits on funded deals.',
 'Affiliate Program','Turn your network into funding revenue.','Bring us deals as a community member or straight through this site. We lend our own capital - so when your deal funds, we split actual profits with you 50/50.',AFF_BODY,
 cta_label='Join the Funding Hub →',cta_href='https://www.skool.com/fundinghub/about',
 band=('Bring the deal. <span class="grad">We bring the capital.</span>','Join the Funding Hub and learn the playbook - or send your first deal through this site today.'))

ABOUT_BODY = '''
<h2>Underwritten like an institution. Delivered like a friend in the business.</h2>
<p>RealQuick Funds was founded by Paul Brown after a 30-year career in global insurance - including Chief Underwriting Officer roles at Zurich and AIG across the United States, Japan, and Singapore. Three decades of pricing risk for some of the world's largest financial institutions now works for real estate investors: disciplined underwriting, honest answers, and capital that shows up when the closing table needs it.</p>
<p>Based in Lehi, Utah, RQF has managed 800+ deals and deployed more than $20M across all 50 states - with same-day decisions on most submissions.</p>
<div class="fstrip" style="margin-top:36px">
  <div class="ph" style="background-image:url('/assets/paul.jpg')"></div>
  <div class="fx">
    <blockquote>"My job for twenty years was knowing exactly which risks were worth taking. Your deal gets that same discipline - at startup speed."</blockquote>
    <div class="who"><b>Paul Brown</b> &middot; Founder &middot; Former Chief Underwriting Officer, Zurich &amp; AIG</div>
  </div>
</div>
<h2>Talk to the team</h2>
<p>Questions about a structure, a timeline, or the affiliate program? Grab time directly:</p>
<div class="sched">
  <a class="btn" href="https://meetings-na2.hubspot.com/admin3005" target="_blank" rel="noopener">Schedule with Paul</a>
  <a class="btn btn-ghost" style="background:#fff;color:var(--ink);border:1px solid var(--line)" href="https://meetings-na2.hubspot.com/justin-pilakka" target="_blank" rel="noopener">Schedule with Justin</a>
</div>'''
page('about','About RealQuick Funds | 20 Years of Underwriting Discipline',
 'Founded by a former Chief Underwriting Officer of Zurich and AIG. $20M+ deployed, 800+ deals, all 50 states.',
 'About RealQuick Funds','Twenty years of pricing risk.<br>Now pricing your deal.',
 'The funding company built on institutional underwriting and creative-finance fluency.',ABOUT_BODY)

FAQS = [
 ("How fast will I get an answer?","Most complete submissions get a same-day decision. Submit in the morning and you will usually hear back that afternoon; submit late in the day and your answer arrives by the next business morning. No deal waits more than one business day - and it is always a clear written answer, not a maybe."),
 ("Do you run a credit check?","No credit checks on transactional funding (double close, EMD, Morby, Echo). We underwrite the transaction. Longer-term products like DSCR loans qualify on property cash flow and involve standard lending verification."),
 ("What does it cost?","Every deal is priced individually based on structure, timeline, and risk. Submit your deal and you'll have exact written terms - same day on most submissions, and never more than one business day. No obligation."),
 ("What states do you fund in?","All 50 states."),
 ("Do you fund 100% of a double close?","Yes - we fund 100% of the A-to-B purchase. Your B-to-C sale repays us through escrow the same day."),
 ("What is the Morby Method?","A creative-finance structure - also called the Stack Method - stacking seller carry with a primary lender so you close with little or no cash - sometimes with cash back. Morby Method and Stack Method are the same thing. See the full guide on our Morby Method page, and run your numbers in the calculator."),
 ("How does repayment work?","Repayment flows through licensed title/escrow at closing - funds never pass through personal accounts. Every transaction is escrow-secured and title-verified."),
 ("How do I become an affiliate?","Just bring a deal. Affiliates are Funding Hub community members - or non-members submitting straight through realquickfunds.com - who send us deals. We recommend joining the community first to learn how we fund, but it isn't required. Because we lend our own capital on escrow-secured funding, affiliates split actual profits 50/50 on deals we fund directly, and earn the majority of the referral on hard money and DSCR placed through our lending network. VIP adds the full playbooks and a white-label funding site - details and pricing inside the community."),
]
faq_html = ''.join('<div class="faqi"><h3>%s</h3><p>%s</p></div>' % (q,a) for q,a in FAQS)
import json
faq_schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQS]})
FAQ_BODY = '<script type="application/ld+json">%s</script>\n<h2>Frequently asked questions</h2>%s' % (faq_schema, faq_html)
page('faq','FAQ | RealQuick Funds','Answers on speed, credit checks, states, double closes, the Morby Method, repayment, and the affiliate program.',
 'FAQ','Questions, answered.','Everything investors ask before they submit their first deal.',FAQ_BODY)



PRIVACY_BODY = """
<p style="font-size:13px;color:#9a978d">Last updated: July 9, 2026 &middot; <em>Draft pending final legal review.</em></p>
<h2>Who we are</h2>
<p>Real Quick Funds, LLC ("RQF," "we," "us") is a transactional funding company based in Lehi, Utah, providing capital solutions to real estate investors in all 50 states. This policy explains what personal information we collect through realquickfunds.com, how we use it, and the choices you have.</p>
<h2>Information we collect</h2>
""" + ul(['Contact details you submit through our forms - name, email address, phone number','Deal information you provide - property addresses, transaction amounts, dates, and documents you upload','Usage data - pages visited, approximate location, device and browser information, collected via analytics cookies']) + """
<h2>How we use your information</h2>
""" + ul(['To administer your account and provide the products and services you request from us','To underwrite and process funding requests you submit','To contact you about our products, services, and content that may interest you - you can unsubscribe from these communications at any time','To improve our website and services']) + """
<h2>How we share it</h2>
<p>We do not sell your personal information. We share it only with service providers who help us operate (for example, our CRM and escrow/title partners involved in your transaction), and where required by law.</p>
<h2>Your choices</h2>
""" + ul(['Unsubscribe from marketing at any time via the link in any email or by contacting us','Request access to, correction of, or deletion of your personal information by emailing <a href="mailto:admin@realquickfunds.com">admin@realquickfunds.com</a>']) + """
<h2>Data retention & security</h2>
<p>We retain personal information only as long as needed for the purposes described above and protect it with commercially reasonable safeguards. Transaction documents are handled through licensed title and escrow.</p>
<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:admin@realquickfunds.com">admin@realquickfunds.com</a>, Real Quick Funds, LLC, Lehi, Utah.</p>"""
page('privacy','Privacy Policy | RealQuick Funds','How Real Quick Funds, LLC collects, uses, and protects your personal information.',
 'Legal','Privacy Policy','How we collect, use, and protect your information.',PRIVACY_BODY)

TERMS_BODY = """
<p style="font-size:13px;color:#9a978d">Last updated: July 9, 2026 &middot; <em>Draft pending final legal review.</em></p>
<h2>Acceptance of terms</h2>
<p>By using realquickfunds.com you agree to these Terms of Use. If you do not agree, please do not use the site.</p>
<h2>No offer or commitment</h2>
<p>Content on this site - including calculators, guides, and examples - is for informational purposes only and does not constitute a loan offer, commitment to lend, or financial, legal, or tax advice. Calculator outputs are estimates only; actual figures are provided in written terms after underwriting. All funding is subject to underwriting approval and applicable law.</p>
<h2>Not a consumer lender</h2>
<p>Real Quick Funds, LLC provides business-purpose capital to real estate investors. We do not provide consumer or owner-occupant lending.</p>
<h2>Intellectual property</h2>
<p>The RealQuick Funds name, rabbit mark, and site content are the property of Real Quick Funds, LLC and may not be used without permission.</p>
<h2>Limitation of liability</h2>
<p>The site is provided "as is." To the maximum extent permitted by law, Real Quick Funds, LLC is not liable for damages arising from use of the site or reliance on its content.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of the State of Utah. Questions: <a href="mailto:admin@realquickfunds.com">admin@realquickfunds.com</a>.</p>"""
page('terms','Terms of Use | RealQuick Funds','Terms of use for realquickfunds.com.',
 'Legal','Terms of Use','The ground rules for using this site.',TERMS_BODY)

print('LEGAL PAGES BUILT')

print('ALL PAGES BUILT')
