#!/usr/bin/env python3
"""RQF site page generator - builds subpages sharing the Apex design system.
Run from site/: python3 build_pages.py"""
import os, re

idx = open('index.html').read()
CSS = re.search(r'<style>(.*?)</style>', idx, re.S).group(1)
MODAL = re.search(r'(<!-- GET FUNDED MODAL -->.*?)(?=<!-- LEARN DRAWER -->)', idx, re.S).group(1)
SCRIPT = max(re.findall(r'<script>(.*?)</script>', idx, re.S), key=len)
# null-safe for pages that lack some calculator elements
SCRIPT = SCRIPT.replace("function num(id){return +(document.getElementById(id).value.replace(/[^0-9]/g,''))||0}",
 "function num(id){var el=document.getElementById(id);return el?(+(el.value.replace(/[^0-9]/g,''))||0):0}")
SCRIPT = SCRIPT.replace("stack();echo();","if(document.getElementById('s_res'))stack();if(document.getElementById('e_res'))echo();")
FOOTER = re.search(r'(<footer[^>]*>.*?</footer>)', idx, re.S).group(1)

NAV = '''<nav><div class="wrap nav-in">
  <a class="brand" href="/"><img src="/assets/lockup_dark.png" alt="RealQuick Funds" width="68" height="46"></a>
  <div class="nav-links"><a href="/#types">Funding</a><a href="/calculators/">Calculators</a><a href="/#types">Learn</a><a href="/affiliates/">Become an Affiliate</a><a href="#contact">Contact</a></div>
  <div style="display:flex;align-items:center;gap:2px"><button class="btn" onclick="openModal()">Get Funded ⚡</button><button class="nav-burger" aria-label="Menu" onclick="toggleNav()"><span></span><span></span><span></span></button></div>
</div></nav>'''

EXTRA_CSS = '''
.pagehero{background:var(--deep);color:#fff;padding:42px 0 42px;position:relative;overflow:hidden}
.pagehero:before{content:"";position:absolute;width:600px;height:600px;border-radius:50%;background:rgba(254,149,6,.18);filter:blur(110px);top:-280px;right:-120px}
.pagehero .wrap{position:relative;z-index:2}
.pagehero h1{color:#fff;font-size:clamp(34px,4.6vw,56px)}
.pagehero .sub{color:#b3b1a9}
.content{padding:48px 0 72px}
.content h2{font-size:clamp(24px,3vw,34px);margin:48px 0 16px;line-height:1.15}
.content h2:first-child{margin-top:0}
.content p,.content li{font-size:16px;color:#54524b;max-width:760px}
.content .wrap>p{margin-top:14px}
.content ul{padding-left:22px;display:grid;gap:8px;margin-top:10px}
.steps{display:grid;gap:12px;margin-top:18px;max-width:760px}
.step{display:flex;gap:16px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.step b{font-family:var(--mono);color:var(--orange-d)}
.ctaband{background:var(--deep);border-radius:24px;padding:56px;text-align:center;color:#fff;margin-top:64px;max-width:760px}
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

SITE_URL = 'https://realquickfunds.com'
OG_IMG = 'https://pmartbrown.github.io/rqf-website/assets/og-image.png'
def page(path, title, desc, kicker, h1, sub, body, cta_type=None, cta_label="Get Funded", cta_href=None, band=None, cta2=None, foot=''):
    canon = SITE_URL + '/' + path + '/'
    cta = "openModal('%s')" % cta_type if cta_type else "openModal()"
    cta_btn = '<a class="btn" href="%s">%s</a>' % (cta_href, cta_label) if cta_href else '<button class="btn" onclick="%s">%s</button>' % (cta, cta_label)
    cta2_btn = '<a class="btn btn-ghost" href="%s">%s</a>' % (cta2[1], cta2[0]) if cta2 else ''
    band_h, band_p = band if band else ('Got a deal? Get funded. <span class="grad">Real quick.</span>', 'Two-minute form &middot; same-day decisions on most deals &middot; all 50 states.')
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GBE4HBBJPZ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-GBE4HBBJPZ');</script>
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" type="image/png" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="canonical" href="%s">
<meta property="og:type" content="website"><meta property="og:site_name" content="RealQuick Funds"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">
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
%s</div></div>
%s
</main>
%s
<div class="doverlay" id="doverlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer"><div class="dr-head"><button class="x" onclick="closeDrawer()">&times;</button><div class="k" id="dr_k"></div><h3 id="dr_title"></h3></div><div class="dr-body" id="dr_body"></div></div>
<script>%s</script>
</body>
</html>''' % (title, desc, canon, title, desc, canon, OG_IMG, title, desc, OG_IMG, CSS, EXTRA_CSS, NAV, kicker, h1, sub, cta_btn, cta2_btn, body, band_h, band_p, cta_btn, foot, FOOTER, MODAL, SCRIPT)
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path,'index.html'),'w').write(html)
    print('built', path)

def steps(items):
    return '<div class="steps">' + ''.join('<div class="step"><b>0%d</b><span>%s</span></div>' % (i+1,s) for i,s in enumerate(items)) + '</div>'
def ul(items):
    return '<ul>' + ''.join('<li>%s</li>' % x for x in items) + '</ul>'

DEALS = {
 'stack': dict(kicker='Creative Finance', name='Stack Method', cta='morby', req='Start a Stack request', calc=('Stack Method Calculator','/calculators/stack/'),
   title='Stack Method (Morby Method) Funding | RealQuick Funds',
   desc='Stack Method (Morby Method) funding - seller carry + primary lender stacked into one creative close. All 50 states. Same-day decisions on most deals.',
   sub='Stack seller carry with a primary lender and acquire property with little - sometimes zero - of your own cash. In the right structure, you can even receive cash back at closing.',
   body='''
<h2>What the Stack Method is</h2>
<p>The Stack Method is a creative-finance structure that combines a seller-carried note with a primary lender so the total capital stack covers the purchase price and closing costs, and sometimes more than covers it. The name comes from stacking funding sources on one deal. You'll also hear it called the <b>Morby Method</b>. Same structure, same math. Done right, the buyer closes with minimal cash out of pocket, and in some structures walks away from the closing table with funds in hand.</p>
<h2>Who it's for</h2>
<p>The classic Stack Method buyer is an investor who wants the property but doesn't want the down payment tied up in it. Maybe you're building a portfolio and would rather spread your capital across three acquisitions than sink all of it into one. Maybe you've found a motivated seller who's open to carrying part of the price, but real cash still has to show up at the table for the deal to close. If the seller is willing to stay in the deal and the numbers support it, this structure turns "I can't cover the down payment" into a closing date.</p>
<h2>The three stacked pieces</h2>
<p>A Stack deal layers three funding sources. Each one has a single job.</p>
''' + steps(['<b>The senior loan.</b> A primary lender covers the big chunk of the purchase. Usually that is a DSCR loan if the buyer is keeping it as a rental, or hard money if it is a flip. First position. The heavy lifter.','<b>The seller&rsquo;s reinvestment.</b> The seller helps cover the rest, most often by carrying back a second-position note for part of the price. A preferred equity position gets to the same place when a deal calls for it. Either way, the seller is staying in the deal instead of cashing all the way out, and that reinvestment is what makes the whole structure work.','<b>Our cash to close.</b> Even with the senior loan and the seller&rsquo;s piece on paper, real cash still has to hit the closing table. That is where we come in. RealQuick Funds wires the cash to close into escrow, the deal records, and the seller&rsquo;s reinvestment repays us. Typically the same day.']) + '''
<h2>How the money actually moves</h2>
<p>A Stack deal is really two closings wearing one contract.</p>
<p><b>The primary close is cash going in.</b> The senior lender's funds and our cash to close land at title. The seller gets paid, the deed records, the buyer owns the property.</p>
<p><b>The secondary close is cash coming out.</b> Think of it as an instant refinance of our short-term funding into the seller's note. The carryback gets documented, and the held funds disburse: seller proceeds, our repayment, the closing fees, and any cash back to the buyer the structure supports.</p>
<p>The whole thing turns on the escrow disbursement instructions. Our funds sit at title and release the moment the deal records. We lock those instructions down with the title company before a dollar moves, which is exactly why our money goes out and comes back the same day with zero drama.</p>
<h2>See the math on a $500K deal</h2>
<div class="pnl" style="max-width:560px">
 <div class="prow"><span>Purchase price</span><b>$500,000</b></div>
 <div class="prow"><span>Est. closing costs (3%)</span><b>$15,000</b></div>
 <div class="prow"><span>Senior loan (75%)</span><b>$375,000</b></div>
 <div class="prow tot"><span>Cash needed to close</span><b>$140,000</b></div>
 <div class="prow"><span>Seller carryback (2nd position)</span><b>$147,700</b></div>
 <div class="prow"><span>RQF funds</span><b>$140,000 - the full gap</b></div>
 <div class="prow tot"><span>Buyer brings</span><b>about $0</b></div>
</div>
<p>The carry is sized to repay our funding plus estimated fees at the secondary close. Push the carry higher and the same structure can put cash back in the buyer's pocket at closing. Shrink it and the buyer brings the difference. Estimates only - run your own numbers in the <a href="/calculators/stack/">Stack Method Calculator</a>, every field is editable, and exact figures always arrive with your written terms.</p>
<h2>The rule that decides every deal</h2>
<p>One test separates a fundable Stack deal from a wish: <b>the seller's carryback has to be big enough to repay our funding, our fee, and the second-close costs.</b> If it is, the deal works. The <a href="/calculators/stack/">calculator</a> caps our funding at exactly what the carry supports and shows you what lands on you at the table, whether that's cash to bring or cash back. If the carry can't cover it, it's not a Stack deal we can fund. Restructure the carry, adjust the price, or bring the difference in cash at the first closing. No exceptions, because this rule is what keeps every party in the deal whole, the seller included.</p>
<h2>Done right: disclosure and structure</h2>
<p>The Stack Method has a reputation problem it doesn't deserve, caused by people doing it wrong. Done right, it's clean:</p>
''' + ul(['<b>The primary lender sees the whole structure.</b> The seller carry and the source of the cash to close are disclosed to your senior lender, and we confirm the lender&rsquo;s seasoning and sourcing rules before funding, not after. If a lender&rsquo;s guidelines can&rsquo;t accommodate the structure, the answer is a different lender.','<b>The carry lives in its own addendum,</b> not buried in the purchase contract. Clean paper for the senior lender&rsquo;s underwriting.','<b>Everything settles through licensed title and escrow.</b> Both settlement statements, airtight disbursement instructions, and funds that never touch personal accounts.','<b>Government-backed primaries are off the table.</b> FHA and VA loans do not permit this structure. Stack deals run on investor financing: DSCR, private money, or hard money.']) + '''
<h2>When it's not a Stack deal</h2>
''' + ul(['<b>The seller wants every dollar at closing.</b> No reinvestment, no Stack deal. But if there is a wholesaler&rsquo;s spread in the deal, look at the <a href="/echo/">Echo Method</a> instead. Same down-payment funding, repaid from the spread rather than the carry.','<b>The carry is too small to repay the funding.</b> See the rule above. Restructure or bring cash.','<b>The senior lender requires seasoned funds</b> and will not work with an alternative. We check this at intake. It is one of the first questions we ask.','<b>The numbers only work at an inflated price.</b> If the deal needs a make-believe value to pencil, it does not pencil.']) + '''
<h2>How RealQuick Funds funds it</h2>
''' + steps(['Submit your structure: purchase price, seller carry, primary lender amount, closing date.','We verify the stack and issue written terms, same day on most submissions.','Capital wires to title for closing. Escrow repays us per the structure.']) + '''
<h2>What you'll need</h2>
''' + ul(['Executed purchase contract','Seller carry terms in a separate addendum','Primary lender term sheet or approval','Title/escrow contact','A transaction coordinator experienced with two-part closings. The TC is required on Stack deals, and if you don&rsquo;t have one, we&rsquo;ll connect you.']) + '''
<h2>Stack Method questions, answered</h2>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "Is the Stack Method legal?", "acceptedAnswer": {"@type": "Answer", "text": "When it&#39;s structured with full disclosure, this is a well-worn path: the seller carry is documented in an addendum, the primary lender underwrites with the structure in view, and everything settles through licensed title and escrow. That&#39;s the only way we fund them.*"}}, {"@type": "Question", "name": "Do I need my own cash?", "acceptedAnswer": {"@type": "Answer", "text": "Often little to none. Whether you bring cash, bring nothing, or walk away with cash depends on one thing: how the seller carry compares to the funding it has to repay. The calculator shows you which side of the line your deal is on."}}, {"@type": "Question", "name": "What if the seller carry is too small?", "acceptedAnswer": {"@type": "Answer", "text": "Then the structure doesn&#39;t self-fund. Your options are to negotiate a larger carry, lower the price, or bring the shortfall in cash at the first closing. We&#39;ll tell you the exact number in your written terms."}}, {"@type": "Question", "name": "Stack vs. Echo: which is my deal?", "acceptedAnswer": {"@type": "Answer", "text": "Both fund a down payment short-term. The difference is who pays us back. In a Stack deal, the seller repays us by staying in the deal, which fits end buyers keeping the property. In an Echo, the deal&#39;s spread repays us on a double close, which fits wholesalers, and everyone cashes out. Seller staying in? Stack. Everyone out? Echo."}}, {"@type": "Question", "name": "What does the seller get out of it?", "acceptedAnswer": {"@type": "Answer", "text": "Most of their price in cash at closing, plus a note that pays them over time, often at better effective terms than a price cut. The carry is their money, secured by the property they know best. The seller signs acknowledgments and their instructions govern the escrow, so the same structure that repays us protects them."}}, {"@type": "Question", "name": "How fast does it move?", "acceptedAnswer": {"@type": "Answer", "text": "Written terms same day on most submissions. The closing timeline is set by your senior lender and title. Our capital is ready when they are."}}, {"@type": "Question", "name": "What does it cost?", "acceptedAnswer": {"@type": "Answer", "text": "Every deal is priced individually based on structure, timeline, and risk. Submit your deal and you&#39;ll have exact written terms, same day on most submissions. The calculator&#39;s fee fields are editable estimates."}}, {"@type": "Question", "name": "Why do I need a transaction coordinator?", "acceptedAnswer": {"@type": "Answer", "text": "Because a Stack closing has two parts, and the paperwork between them decides everything. An experienced TC keeps the addendum, the disbursement instructions, and both settlement statements airtight. If you don&#39;t have one, we&#39;ll introduce you to one who&#39;s done these."}}]}</script>
<div class="faqi"><h3>Is the Stack Method legal?</h3><p>When it's structured with full disclosure, this is a well-worn path: the seller carry is documented in an addendum, the primary lender underwrites with the structure in view, and everything settles through licensed title and escrow. That's the only way we fund them.*</p></div>
<div class="faqi"><h3>Do I need my own cash?</h3><p>Often little to none. Whether you bring cash, bring nothing, or walk away with cash depends on one thing: how the seller carry compares to the funding it has to repay. The calculator shows you which side of the line your deal is on.</p></div>
<div class="faqi"><h3>What if the seller carry is too small?</h3><p>Then the structure doesn't self-fund. Your options are to negotiate a larger carry, lower the price, or bring the shortfall in cash at the first closing. We'll tell you the exact number in your written terms.</p></div>
<div class="faqi"><h3>Stack vs. Echo: which is my deal?</h3><p>Both fund a down payment short-term. The difference is who pays us back. In a Stack deal, the seller repays us by staying in the deal, which fits end buyers keeping the property. In an Echo, the deal's spread repays us on a double close, which fits wholesalers, and everyone cashes out. Seller staying in? Stack. Everyone out? Echo.</p></div>
<div class="faqi"><h3>What does the seller get out of it?</h3><p>Most of their price in cash at closing, plus a note that pays them over time, often at better effective terms than a price cut. The carry is their money, secured by the property they know best. The seller signs acknowledgments and their instructions govern the escrow, so the same structure that repays us protects them.</p></div>
<div class="faqi"><h3>How fast does it move?</h3><p>Written terms same day on most submissions. The closing timeline is set by your senior lender and title. Our capital is ready when they are.</p></div>
<div class="faqi"><h3>What does it cost?</h3><p>Every deal is priced individually based on structure, timeline, and risk. Submit your deal and you'll have exact written terms, same day on most submissions. The calculator's fee fields are editable estimates.</p></div>
<div class="faqi"><h3>Why do I need a transaction coordinator?</h3><p>Because a Stack closing has two parts, and the paperwork between them decides everything. An experienced TC keeps the addendum, the disbursement instructions, and both settlement statements airtight. If you don't have one, we'll introduce you to one who's done these.</p></div>
'''),
 'echo': dict(kicker='Creative Finance', name='Echo Method', cta='echo', req='Start an Echo request', calc=('Echo Calculator','/calculators/echo/'),
   title='Echo Method Funding - Down Payment Capital for Double Closes | RealQuick Funds',
   desc='Echo Method funding - down-payment capital for the end buyer on the back half of a double close, repaid from the spread at one closing. All 50 states.',
   sub="Down-payment funding for your end buyer on the back half of a double close - repaid from the deal's spread on the same settlement. One closing. Everybody cashes out.",
   body='''
<h2>What the Echo Method is</h2>
<p>Echo is short-term funding for the end buyer's down payment on the back half of a double close. The end buyer closes with their primary lender plus our capital - and we're repaid out of the deal's spread on that same settlement statement. Funds in, funds out, one closing. That's the echo.</p>
<p>Compare that to a gap loan: no recorded second-position note, no debt sitting on the deal for six to nine months. The money is in and out of a single closing, and every party - seller, wholesaler, end buyer, lender - cashes out at the table.</p>
<h2>Who it's for</h2>
<p>Two people meet in every Echo, and it solves a problem for both. <b>The wholesaler</b> with a real spread and a buyer who keeps stalling because they can't cover the down payment - Echo turns "my buyer needs three more weeks to raise cash" into a closing date. <b>The end buyer</b> - usually a fix-and-flipper buying from a wholesaler - who has the primary lender lined up but doesn't want to drain reserves or take on second-position gap debt to cover the cash to close. And there's a third profile: the investor wearing both hats, wholesaling a deal to their own buying entity, where Echo covers the down payment on the back leg.</p>
<h2>The two legs and the three players</h2>
<p>A double close is two purchases back to back: the A-B leg, where the wholesaler buys from the seller, and the B-C leg, where the end buyer purchases from the wholesaler at a higher price. Three funding pieces make the B-C leg close: the <b>primary lender</b> (usually hard money, sized as a percentage of the appraisal-supported B-C price) brings the biggest piece; <b>RealQuick Funds</b> wires the end buyer's down payment and closing-cost gap; and the difference between the two legs - <b>the spread</b> - is the wholesaler's profit line on the settlement statement. That spread is what repays us.</p>
<h2>How the money actually moves</h2>
<p>Everything runs through licensed title and escrow, in a strict order. The primary lender's funds land at title first and are confirmed - our capital never leads. We then wire the down payment directly to title, never to a person. The B-C closing records, and on that same settlement statement, title disburses the wholesaler's spread with our repayment carved out and wired back per disbursement instructions locked in before a dollar moves. One settlement statement. Money in and money out on the same paper - which is exactly why our capital can move in a day or two with zero drama.</p>
<h2>See the math on a $725K flip</h2>
<div class="pnl" style="max-width:560px">
 <div class="prow"><span>A-B price (wholesaler buys)</span><b>$500,000</b></div>
 <div class="prow"><span>B-C price (end buyer pays - appraisal-supported)</span><b>$725,000</b></div>
 <div class="prow"><span>Primary lender (75% of B-C)</span><b>$543,750</b></div>
 <div class="prow tot"><span>RQF funds - down payment + est. closing costs (2%)</span><b>$195,750</b></div>
 <div class="prow"><span>Repayment to RQF (funding + est. fee)</span><b>$200,644</b></div>
 <div class="prow"><span>Spread (B-C minus A-B)</span><b>$225,000</b></div>
 <div class="prow tot"><span>Wholesaler keeps after repaying the Echo</span><b>$24,356</b></div>
 <div class="prow tot"><span>End buyer brings</span><b>about $0 down</b></div>
</div>
<p>The end buyer closes a $725,000 purchase without draining reserves, the wholesaler banks the remaining spread at the table, and the seller was cashed out on the A-B leg. Estimates only - run your own legs in the <a href="/calculators/echo/">Echo Calculator</a>, every field is editable, and exact figures always arrive with your written terms.</p>
<h2>The rule that decides every deal</h2>
<p>One test separates a fundable Echo from a wish: <b>the spread has to cover our funding plus our fee.</b> The Stack Method exits through the seller carry; Echo exits through the spread. If the spread covers repayment, everybody cashes out at one table. If it doesn't, it's not an Echo we can fund - period. Raise the B-C price (only if the appraisal supports it), shrink the funded amount, or restructure. And that's the second gate: <b>the B-C price must appraise</b>, because the appraisal sizes the primary loan, and the primary loan sizes everything else.</p>
<h2>Done right: title discipline</h2>
<p>Echo's safety lives in the sequencing, and we don't improvise it:</p>
''' + ul(['<b>Senior funds land first.</b> The primary lender&rsquo;s money is confirmed at title before ours moves.','<b>Our wire goes to title, never to a person.</b> No exceptions.','<b>Repayment comes off the settlement statement</b> per disbursement instructions locked in before funding - not from anyone&rsquo;s promise afterward.','<b>The title company has to be comfortable with back-to-back closings.</b> We can tell within one phone call whether they are.']) + '''
<h2>When it's not an Echo</h2>
<p>Buying directly from the seller with seller carry in the structure? That's a <a href="/stack/">Stack</a>, not an Echo - run it through the <a href="/calculators/stack/">Stack Method Calculator</a> instead. Spread too thin to cover the funding? Not an Echo - restructure before you submit. Need capital that stays in the deal for months? That's gap funding, and it's a different risk animal - Echo is in and out of one settlement. B-C price the appraisal won't support? No primary loan, no Echo.</p>
<h2>How RealQuick Funds funds it</h2>
''' + steps(["Submit both legs - A-B and B-C contracts, the end buyer's primary lender terms, and the closing date.",'We verify the spread covers the funding and issue written terms - same day on most submissions.','Primary lender funds land at title first; we wire the down payment; title repays us from the spread on the same settlement.']) + '''
<h2>What you'll need</h2>
''' + ul(['A-B and B-C purchase contracts',"The end buyer's primary lender term sheet or approval",'Title/escrow contact comfortable with back-to-back closings']) + '''
<h2>Echo questions, answered</h2>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "Who actually repays RealQuick Funds?", "acceptedAnswer": {"@type": "Answer", "text": "The deal does. Title wires our repayment out of the wholesaler&#39;s spread on the same settlement where we funded. Nobody writes us a check afterward."}}, {"@type": "Question", "name": "Is this a loan to the end buyer?", "acceptedAnswer": {"@type": "Answer", "text": "It&#39;s transactional funding into the closing - not a recorded second mortgage, not gap debt that sits on the property."}}, {"@type": "Question", "name": "Echo vs. Double Close funding: what is the difference?", "acceptedAnswer": {"@type": "Answer", "text": "Double Close funding pays for the A-B purchase and is repaid when the B-C closes. Echo funds the down payment on the B-C itself and is repaid on that same settlement. Nine out of ten Echos ride on a double close - we often fund both legs."}}, {"@type": "Question", "name": "Echo vs. a gap lender?", "acceptedAnswer": {"@type": "Answer", "text": "A gap lender records a note and lives in the deal for months. Echo is in and out of one closing - no lien on the flip, no second payment eating the rehab budget."}}, {"@type": "Question", "name": "Does the B-C price have to appraise?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. The appraisal sizes the primary loan, and the primary loan is what makes the spread real. No appraisal support, no Echo."}}, {"@type": "Question", "name": "How fast does it move?", "acceptedAnswer": {"@type": "Answer", "text": "Written terms typically same day; money out typically in a day or two. Repayment happens the moment the closing records."}}, {"@type": "Question", "name": "What does it cost?", "acceptedAnswer": {"@type": "Answer", "text": "Every deal is priced individually based on structure, timeline, and risk - starting at a minimum fee quoted in your written terms. The calculator&#39;s fee fields are editable estimates, and it shows you whether the spread supports the deal before you ever submit."}}, {"@type": "Question", "name": "Do you pull my credit?", "acceptedAnswer": {"@type": "Answer", "text": "No - like all our transactional funding, Echo is underwritten on the deal, not your W-2 or credit score."}}]}</script>
<div class="faqi"><h3>Who actually repays RealQuick Funds?</h3><p>The deal does. Title wires our repayment out of the wholesaler's spread on the same settlement where we funded. Nobody writes us a check afterward.</p></div>
<div class="faqi"><h3>Is this a loan to the end buyer?</h3><p>It's transactional funding into the closing - not a recorded second mortgage, not gap debt that sits on the property.</p></div>
<div class="faqi"><h3>Echo vs. Double Close funding: what's the difference?</h3><p>Double Close funding pays for the A-B purchase and is repaid when the B-C closes. Echo funds the down payment <i>on</i> the B-C itself and is repaid on that same settlement. Nine out of ten Echos ride on a double close - we often fund both legs.</p></div>
<div class="faqi"><h3>Echo vs. a gap lender?</h3><p>A gap lender records a note and lives in the deal for months. Echo is in and out of one closing - no lien on the flip, no second payment eating the rehab budget.</p></div>
<div class="faqi"><h3>Does the B-C price have to appraise?</h3><p>Yes. The appraisal sizes the primary loan, and the primary loan is what makes the spread real. No appraisal support, no Echo.</p></div>
<div class="faqi"><h3>How fast does it move?</h3><p>Written terms typically same day; money out typically in a day or two. Repayment happens the moment the closing records.</p></div>
<div class="faqi"><h3>What does it cost?</h3><p>Every deal is priced individually based on structure, timeline, and risk - starting at a minimum fee quoted in your written terms. The calculator's fee fields are editable estimates, and it shows you whether the spread supports the deal before you ever submit.</p></div>
<div class="faqi"><h3>Do you pull my credit?</h3><p>No - like all our transactional funding, Echo is underwritten on the deal, not your W-2 or credit score.</p></div>'''),
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
 'emd': dict(kicker='Transactional Funding', name='EMD Funding', cta='emd', req='Start an EMD request', title='EMD Funding | RealQuick Funds',
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
 'hard-money': dict(kicker='Leverage', name='Hard Money Loans', cta='hml', req='Start a Hard Money request', title='Hard Money Loans | RealQuick Funds',
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
<p>There's no single "DSCR rate." Pricing starts with a market index - most lenders price off the <b>5-year U.S. Treasury</b> - then add a risk premium built from your file. The index moves daily. Ten things move that premium: four you decide when you set up the loan, and six the deal already carries the day you apply. Learn all ten and you can price a rental in your head before it ever reaches an underwriter.</p>
<h3 style="font-family:var(--disp);font-size:20px;font-weight:800;margin-top:34px">What you decide on this loan</h3>
<p style="margin-top:4px">The knobs you turn at the closing table:</p>
''' + ul(['<b>Down payment.</b> Every extra 5% down buys the rate down a notch. 20% gets you in the door; 25% or more gets rewarded.','<b>Prepay term.</b> DSCR loans carry a stepdown penalty - 3% year one, 2% year two, 1% year three. Accept a longer one and the rate drops; buy it off and it rises. Matters most if you plan to refinance soon.','<b>Cash-out or not.</b> Pulling cash out prices higher than a straight purchase or a rate-and-term refinance. Take only the cash you actually need.','<b>Interest-only.</b> An interest-only payment lowers the monthly and can rescue a thin deal - but it nudges the rate up. A lever, not a freebie.']) + '''
<h3 style="font-family:var(--disp);font-size:20px;font-weight:800;margin-top:34px">What you bring to this loan</h3>
<p style="margin-top:4px">Already set the day you apply - so screen for these before you buy:</p>
''' + ul(['<b>Rent coverage (your DSCR).</b> The big one. Stronger coverage, lower rate - 1.25 unlocks the best tier, below 1.0 adds a real premium. A bigger down payment lifts it.','<b>Credit score.</b> Pulled to price the loan, not to check your income. Mid-600s can qualify; the best pricing starts in the 720s. The one factor here worth improving before your next file.','<b>Loan size.</b> Very small loans price worse; larger loans price best.','<b>Property type.</b> A clean single-family rental prices best. Condos - especially non-warrantable ones - cost more.','<b>Number of units.</b> One unit is cheapest; a 2-4 unit adds a premium.','<b>Location.</b> Your state sets the baseline (foreclosure and landlord laws move it), and rural or low-liquidity areas price higher than suburban - a lender wants to know it can resell the property fast.']) + '''
<p style="margin-top:18px"><b>The first four are yours to move today. The last six are the deal telling you what it is</b> - read them, and you will spot a fundable rental the moment you see it.</p>
<div class="faqi" style="border:2px solid var(--orange);max-width:760px"><h3>Estimated current market rates</h3>
<p style="font-family:var(--mono);font-size:16px;margin-top:10px">5-yr Treasury <b id="mk_t5">&mdash;</b> <span id="mk_asof" style="color:#9a978d;font-size:12px"></span> &nbsp;+&nbsp; risk premium &nbsp;=&nbsp; <b id="mk_lo">&mdash;</b> to <b id="mk_hi">&mdash;</b></p>
<p style="font-size:13px;color:#9a978d;margin-top:8px">Updated each business day from the U.S. Treasury's published par yield curve. Estimates only - your exact rate comes with your written terms, and it can fall outside this range in either direction.</p></div>
<h2>What lenders typically expect</h2>
''' + ul(['Down payment of 20-25% - more for sub-1.0 ratios','Credit floors starting in the low 600s; best pricing in the 720s and up','A few months of payments in liquid reserves','Minimum loan sizes around $100K - smaller properties are hard to place','An appraisal with a market-rent schedule. Notice what is missing from this list: your income.']) + '''
<h2>Short-term rentals</h2>
<p>Airbnb income can qualify, but lenders count it conservatively - the appraiser's estimate, a 12-month revenue history, or market data, usually with a haircut. Verify your city allows STRs before you tie up the property; underwriters check.</p>
<h2>Where DSCR fits in a creative deal</h2>
<p>In most <a href="/stack/">Stack Method</a> structures, the DSCR loan is the primary lender - the base of the stack that the seller carry and transactional funding build on. It also serves as the end loan in an <a href="/echo/">Echo Method</a> structure. Run the whole structure in the <a href="/calculators/stack/">Stack Method Calculator</a> and check the rent coverage in the <a href="/calculators/dscr/">DSCR Calculator</a>. When both pencil, you have a deal.</p>
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
LEGAL = '<p style="margin-top:48px;font-size:16px;color:#9a978d;font-style:italic">Nothing on this website is legal advice. It reflects our opinions and our experience. For legal questions, consult your own counsel.</p>\n'
def meta_desc(s, n=155):
    if len(s) <= n: return s
    return s[:n].rsplit(' ', 1)[0].rstrip(' -,;:') + '…'
for slug,d in DEALS.items():
    page(slug, d.get('title', "%s Funding | RealQuick Funds" % d['name']), meta_desc(d.get('desc', d['sub'])),
         d['kicker'], d['name'], d['sub'], d['body'], cta_type=d['cta'],
         cta_label=d.get('req', "Start a %s request" % d['name']), cta2=d.get('calc'), foot=LEGAL)

CALC_BODY = '''
<h2>The deal tool library.</h2>
<p>Built by the funder - not a blog. Run your structure, adjust the estimates for your market, and know whether the deal works before you talk to anyone. Every calculator feeds straight into a two-minute funding request.</p>
<div class="toolgrid">
  <a class="tool" href="/calculators/stack/"><div class="ic">&#9672;</div><h3>Stack Method Calculator</h3><span class="tag">Purchase + cash flow analysis</span><p>Can you close the stack - and should you keep it? Carry-coverage math plus a full rental P&amp;L with DSCR and balloon planning.</p><div class="go">Open calculator &rarr;</div></a>
  <a class="tool" href="/calculators/echo/"><div class="ic">&#9678;</div><h3>Echo Calculator</h3><span class="tag">The only one on the internet</span><p>Does the spread cover the Echo? Run both legs and see what's left for the wholesaler after funding is repaid on the same settlement.</p><div class="go">Open calculator &rarr;</div></a>
  <a class="tool" href="/calculators/dscr/"><div class="ic">&#8962;</div><h3>DSCR Calculator</h3><span class="tag">The way lenders underwrite</span><p>Gross rent &divide; PITIA &mdash; with interest-only compare, the max loan your rent supports, and a full rental cash-flow P&amp;L with cash-on-cash.</p><div class="go">Open calculator &rarr;</div></a>
  <a class="tool" href="/calculators/hard-money/"><div class="ic">&#9874;</div><h3>Hard Money Calculator</h3><span class="tag">Flip profit + max offer</span><p>Loan sizing that names your binding constraint, the true cost of capital over your hold, your flip P&amp;L - and the most you can pay for the house.</p><div class="go">Open calculator &rarr;</div></a>
  <div class="tool soon"><div class="ic">&#8644;</div><h3>More tools on the way</h3><span class="tag">Coming soon</span><p>A Double Close calculator is in the workshop. Got a request? Tell us in the community.</p><div class="go" style="color:#9a978d">In the workshop</div></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:20px">Estimates only. Exact figures arrive with your written terms, typically the same day.</p>'''
MS_BODY = '''
<div class="calcwrap">
  <div class="calc"><div style="font-family:var(--disp);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--mut);margin-bottom:10px">Stack Method</div>
    <div class="ctabs" id="mtabs"><button class="on" onclick="ctab2('pa',this)">Purchase analysis</button><button onclick="ctab2('cf',this)">Cash flow analysis</button></div>
    <div id="pane_pa">
    <div class="purpose">Will you bring cash to close - or walk away with some?</div>
    <div class="cgrid">
      <div class="fld"><label>Purchase price</label><div class="inwrap"><span>$</span><input id="s_pp" value="500,000" oninput="fmt(this);stack()"></div></div>
      <div class="fld"><label>Seller carry <span class="hint" id="s_sc_d"></span></label><div class="inwrap"><input class="pctin" id="s_scp" value="30.0" oninput="fmtp(this);stack()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Primary lender <span class="hint" id="s_pl_d"></span></label><div class="inwrap"><input class="pctin" id="s_plp" value="75.0" oninput="fmtp(this);stack()"><span class="sfx">%</span></div></div>
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
    <div class="mkline" style="display:none;font-size:11px;line-height:1.4;color:#8a5a00;background:#fff2df;border-radius:8px;padding:5px 10px;margin:0 0 10px"></div>
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
<p>The Stack Method - also called the Morby Method - combines a seller-carried note with a primary lender so the capital stack covers the purchase. The purchase analysis tab answers the question that decides the deal: can you close this structure? It checks that the seller carry can repay the transactional funding and fees, caps the funding accordingly, and shows exactly what lands on you at the closing table - cash to bring, or cash back.</p>
<p>Then flip to the cash flow analysis tab: a full monthly rental P&amp;L on the same numbers - vacancy, taxes, insurance, maintenance, CapEx, property management, both loan payments, the carry balloon, and your DSCR. Whether you can close it and whether you should keep it, on one card.</p>
<h2>How to use it</h2>
<ul><li>Enter the purchase price, the seller carry, and the primary lender's percentage - the dollar equivalents show beside each field.</li><li>The fee fields are pre-filled estimates and every one of them is editable - exact figures come with your written terms.</li><li>Watch the result flip between cash to close and cash back as you adjust the structure.</li><li>Flip to cash flow analysis to see the property as a rental - payments, balloon, and DSCR included.</li></ul>
<p>Want the full mechanics? Read the <a href="/stack/">Stack Method deep dive</a> or ask in <a href="https://www.skool.com/fundinghub">the community</a>. When the numbers work, hit Submit - the funding request pre-fills from your calculator inputs.</p>
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
<p>New to the structure? Read the <a href="/echo/">Echo Method deep dive</a> or ask in <a href="https://www.skool.com/fundinghub">the community</a>. When the spread covers it, hit Submit - the funding request pre-fills the funded amount.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
page('calculators','Deal Calculators for Creative Finance | RealQuick Funds',
 'Free deal calculators built by a transactional funder - Stack Method purchase and rental cash flow analysis, Echo spread coverage, and more tools on the way.',
 'Deal Tools','Run your numbers.','The deal tool library - free calculators built by the funder. Know whether the deal works before you talk to anyone.',CALC_BODY)
page('calculators/stack','Stack Method Calculator (Morby Method) - Free | RealQuick Funds',
 'Free Stack Method (Morby Method) calculator: carry-coverage purchase analysis plus a full rental cash flow P&L with DSCR and balloon planning. Built by the funder.',
 'Deal Tools','Stack Method Calculator','Can you close it - and should you keep it? Purchase analysis with carry-coverage math, plus a full rental cash flow P&L.',MS_BODY, cta_type='morby', cta_label='Start a Stack request', cta2=('What is the Stack Method?','/stack/'))
page('calculators/echo','Echo Method Calculator - Free | RealQuick Funds',
 "The only Echo calculator on the internet: see whether the deal's spread covers the funding on the B-C close. Built by RealQuick Funds.",
 'Deal Tools','Echo Calculator','Does the spread cover the Echo? Run both legs and know in thirty seconds.',ECHO_CALC_BODY, cta_type='echo', cta_label='Start an Echo request', cta2=('What is the Echo Method?','/echo/'))
DSCR_TOOL_BODY = '''
<div class="calcwrap">
  <div class="calc"><div style="font-family:var(--disp);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--mut);margin-bottom:10px">DSCR Calculator</div>
    <div class="ctabs" id="dtabs"><button class="on" onclick="dtab('dq',this)">DSCR check</button><button onclick="dtab('dcf',this)">Cash flow analysis</button></div>
    <div id="pane_dq">
    <div class="mkline" style="display:none;font-size:11px;line-height:1.4;color:#8a5a00;background:#fff2df;border-radius:8px;padding:5px 10px;margin:0 0 10px"></div>
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
    <div class="cgrid">
      <div class="fld"><label>HOA /mo</label><div class="inwrap"><span>$</span><input id="d_hoa" value="0" oninput="fmt(this);dscr()"></div></div>
      <div class="fld"><label>Interest-only?</label><div class="inwrap" style="padding-left:6px"><select id="d_io" onchange="dscr()" style="width:100%;border:none;background:transparent;font-family:Inter;font-size:14.5px;padding:10px 8px;outline:none;color:var(--ink)"><option>No</option><option>Yes</option></select></div></div>
    </div>
    <div class="pnl">
      <div class="prow"><span>Principal &amp; interest</span><b id="ds_pi"></b></div>
      <div class="prow"><span>Taxes + insurance</span><b id="ds_ti"></b></div>
      <div class="prow"><span>HOA</span><b id="ds_hoa"></b></div>
      <div class="prow tot"><span>PITIA - what lenders divide by</span><b id="ds_tot"></b></div>
    </div>
    <div class="result back" id="ds_res" style="margin-top:10px"><div class="rl" id="ds_rl">DSCR</div><div class="rv" id="ds_rv">-</div><div class="rsub" id="ds_sub"></div></div>
    <div class="solves">
      <div class="solve"><div class="sl" id="ds_mll">Max loan at DSCR 1.0</div><div class="sv" id="ds_ml">-</div></div>
      <div class="solve"><div class="sl" id="ds_rnl">Rent to break even (1.0)</div><div class="sv" id="ds_rn">-</div></div>
    </div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('dscr',true)">Submit this deal</button>
    </div>
    <div id="pane_dcf" style="display:none">
    <div class="purpose">Keep it as a rental? Full monthly P&amp;L - uses the price, loan, rent, taxes and insurance from your DSCR check tab.</div>
    <div class="note" style="text-align:left;margin:0 0 12px" id="dc_ctx"></div>
    <div class="cgrid3">
      <div class="fld"><label>Vacancy</label><div class="inwrap"><input class="pctin" id="dc_vac" value="5.0" oninput="fmtp(this);dscrcf()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Maintenance</label><div class="inwrap"><input class="pctin" id="dc_mnt" value="5.0" oninput="fmtp(this);dscrcf()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>CapEx</label><div class="inwrap"><input class="pctin" id="dc_cap" value="5.0" oninput="fmtp(this);dscrcf()"><span class="sfx">%</span></div></div>
    </div>
    <div class="cgrid">
      <div class="fld"><label>Prop Mgmt</label><div class="inwrap"><input class="pctin" id="dc_mgm" value="10.0" oninput="fmtp(this);dscrcf()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Est. closing costs <span class="hint" id="dc_cc_d"></span></label><div class="inwrap"><input class="pctin" id="dc_cc" value="3.0" oninput="fmtp(this);dscrcf()"><span class="sfx">%</span></div></div>
    </div>
    <div class="pnl">
      <div class="prow"><span>Gross rent</span><b id="dc_gr"></b></div>
      <div class="prow"><span>Vacancy</span><b id="dc_vc"></b></div>
      <div class="prow tot"><span>Effective income</span><b id="dc_eg"></b></div>
      <div class="prow"><span>Taxes + insurance + HOA</span><b id="dc_ti"></b></div>
      <div class="prow"><span>Maintenance + CapEx</span><b id="dc_mc"></b></div>
      <div class="prow"><span>Property management</span><b id="dc_mg"></b></div>
      <div class="prow tot"><span>Net operating income</span><b id="dc_noi"></b></div>
      <div class="prow"><span>DSCR loan payment</span><b id="dc_pi"></b></div>
      <div class="prow tot"><span>Cash invested (down + closing)</span><b id="dc_cin"></b></div>
      <div class="prow"><span>Cash-on-cash return</span><b id="dc_coc"></b></div>
    </div>
    <div class="result bring" id="dc_res"><div class="rl" id="dc_rl">Estimated monthly cash flow</div><div class="rv" id="dc_rv">$0</div></div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('dscr',true)">Submit this deal</button>
    </div></div>
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
<ul><li>Enter the purchase price, expected rent, and your down payment - the loan amount and monthly payment show beside the fields.</li><li>The rate is an editable estimate - exact terms come with your written quote.</li><li>Flip Interest-only to Yes to see how an IO period changes your ratio - it can rescue a marginal deal.</li><li>The two boxes under the result answer the questions that matter: the biggest loan this rent supports at DSCR 1.0, and the rent you'd need to break even.</li></ul>
<p>Running a Stack Method deal? The DSCR loan is usually the primary lender in the stack - check the whole structure in the <a href="/calculators/stack/">Stack Method Calculator</a>, or read the <a href="/dscr/">DSCR loan deep dive</a>. Questions? Ask in <a href="https://www.skool.com/fundinghub">the community</a>.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
page('calculators/dscr','DSCR Calculator - Rental Property Loan Qualifier | RealQuick Funds',
 'Free DSCR calculator that computes it the way lenders actually underwrite - gross rent divided by PITIA. Plus a full rental cash flow P&L with cash-on-cash on your down payment.',
 'Deal Tools','DSCR Calculator','If it rents, it funds. Run the rent against PITIA - then flip to the cash flow tab to see what the rental actually puts in your pocket each month.',DSCR_TOOL_BODY, cta_type='dscr', cta_label='Start a DSCR request', cta2=('What is DSCR?','/dscr/'))

HML_TOOL_BODY = '''
<div class="calcwrap">
  <div class="calc"><div style="font-family:var(--disp);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--mut);margin-bottom:10px">Hard Money Calculator</div>
    <div class="purpose">Does the flip pencil - and what's the most you can pay?</div>
    <div class="cgrid">
      <div class="fld"><label>Purchase price</label><div class="inwrap"><span>$</span><input id="h_pp" value="300,000" oninput="fmt(this);hml()"></div></div>
      <div class="fld"><label>Rehab budget</label><div class="inwrap"><span>$</span><input id="h_rb" value="60,000" oninput="fmt(this);hml()"></div></div>
      <div class="fld"><label>After-repair value (ARV)</label><div class="inwrap"><span>$</span><input id="h_arv" value="425,000" oninput="fmt(this);hml()"></div></div>
      <div class="fld"><label>Months held</label><div class="inwrap"><input class="pctin" id="h_mo" value="6" oninput="fmtp(this);hml()"><span class="sfx">mo</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Purchase financed</label><div class="inwrap"><input class="pctin" id="h_pf" value="80.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Rehab financed</label><div class="inwrap"><input class="pctin" id="h_rf" value="100.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>ARV cap <span class="hint" id="h_ac_d"></span></label><div class="inwrap"><input class="pctin" id="h_ac" value="70.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
    </div>
    <div class="cgrid3">
      <div class="fld"><label>Rate (interest-only)</label><div class="inwrap"><input class="pctin" id="h_rt" value="13.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Points <span class="hint" id="h_pts_d"></span></label><div class="inwrap"><input class="pctin" id="h_pts" value="2.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
      <div class="fld"><label>Selling costs <span class="hint" id="h_sc_d"></span></label><div class="inwrap"><input class="pctin" id="h_sc" value="8.0" oninput="fmtp(this);hml()"><span class="sfx">%</span></div></div>
    </div>
    <div class="pnl">
      <div class="prow"><span>Your loan</span><b id="hm_loan"></b></div>
      <div class="prow"><span>Cash to the deal</span><b id="hm_cash"></b></div>
      <div class="prow"><span>Monthly payment (interest-only)</span><b id="hm_pi"></b></div>
      <div class="prow tot"><span>True cost of capital - points + interest</span><b id="hm_coc"></b></div>
    </div>
    <p id="hm_bind" style="font-size:12px;color:#8a5a00;background:#fff2df;border-radius:10px;padding:8px 12px;margin-top:10px"></p>
    <div class="result out" id="hm_res" style="margin-top:10px"><div class="rl" id="hm_rl">Estimated net profit</div><div class="rv" id="hm_rv">-</div><div class="rsub" id="hm_sub"></div></div>
    <div class="solves">
      <div class="solve"><div class="sl">Max offer inside your financing</div><div class="sv" id="hm_mao">-</div></div>
      <div class="solve"><div class="sl">Breakeven purchase price</div><div class="sv" id="hm_be">-</div></div>
    </div>
    <button class="btn" style="width:100%;justify-content:center;margin-top:12px;border-radius:12px" onclick="openModal('hml',true)">Submit this deal</button></div>
</div>
<p style="font-size:12.5px;color:#9a978d;margin-top:14px">Estimates only - rates and terms vary by scenario and market. Exact figures arrive with your written terms.</p>
<h2>How hard money loans are sized</h2>
<p>Two numbers compete, and the smaller one wins. The cost-based number is your purchase price times the financed percentage, plus the funded rehab. The value-based number is the ARV cap - a percentage of what the property will be worth finished. Your loan is the lesser of the two, and this calculator tells you which one is limiting you. When the ARV cap is the ceiling, a better purchase price doesn't buy you a bigger loan - it buys you a smaller gap to cover in cash.</p>
<h2>What it really costs</h2>
<p>The rate is the headline; the hold is the story. Hard money cost is points up front plus interest-only payments for every month you own it - so a two-month delay on your rehab or resale costs real money even when nothing goes wrong. That's why the calculator prices the whole hold, not the annual rate, and why the fastest way to raise your profit is usually to shorten the timeline, not to shop half a point of rate.</p>
<h2>The number to memorize</h2>
<p>The max-offer box is the classic 70% rule computed with your actual numbers instead of folklore: the ARV cap minus your rehab is the most you can pay and still finance the deal your way. The breakeven box is your absolute ceiling - the purchase price where profit hits zero. Between those two numbers is your negotiating room.</p>
<h2>Where it fits</h2>
<p>Hard money is the workhorse of creative finance: it's the primary lender on most <a href="/echo/">Echo Method</a> B-C closings and plenty of <a href="/calculators/stack/">Stack Method</a> structures. New to the product? Read the <a href="/hard-money/">hard money deep dive</a>. Questions? Ask in <a href="https://www.skool.com/fundinghub">the community</a>.</p>
<p style="margin-top:18px"><a href="/calculators/" style="color:var(--orange-d);font-weight:700">&larr; All deal calculators</a></p>'''
page('calculators/hard-money','Hard Money Loan Calculator - Flip Profit and Max Offer | RealQuick Funds',
 'Free hard money calculator: loan sizing with the binding constraint named, true cost of capital over your hold, flip profit and ROI, plus the max offer your financing supports.',
 'Deal Tools','Hard Money Calculator','Loan sizing, true cost of capital, and your flip P&L - plus the max-offer answer no other calculator gives you.',HML_TOOL_BODY, cta_type='hml', cta_label='Start a Hard Money request', cta2=('What is hard money?','/hard-money/'))


AFF_BODY = '''
<h2>What an affiliate is here</h2>
<p>An affiliate is anyone who brings us deals - a member of our <a href="https://www.skool.com/fundinghub">Funding Hub</a> community, or a non-member sending deals straight through this site. We prefer you come into the community first and learn how we do things, so your deals arrive in the right format with the right understanding - but it's not a requirement. Inside the community we call affiliates our acquisition team members. Same people, same pay.</p>
<h2>Why the math is different here</h2>
<p>On escrow-secured funding - EMD, Double Close, Stack Method, and Echo - we're the <b>direct lender</b>, not a broker. It's our capital, so there's no middleman taking a cut ahead of you: when a deal you bring funds, we split <b>actual profits 50/50</b>. You earn dollar for dollar alongside us. On the business we refer out - hard money and DSCR - we've negotiated a strong referral rate with our lending network, and <b>the majority of it goes to you</b>.</p>
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
   <li>The complete education - full Stack Method and Echo playbooks, step-by-step deal SOPs, and every call replay</li>
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
 ("Do you run a credit check?","No credit checks on transactional funding (double close, EMD, Stack, Echo). We underwrite the transaction. Longer-term products like DSCR loans qualify on property cash flow and involve standard lending verification."),
 ("What does it cost?","Every deal is priced individually based on structure, timeline, and risk. Submit your deal and you'll have exact written terms - same day on most submissions, and never more than one business day. No obligation."),
 ("What states do you fund in?","All 50 states."),
 ("Do you fund 100% of a double close?","Yes - we fund 100% of the A-to-B purchase. Your B-to-C sale repays us through escrow the same day."),
 ("What is the Stack Method?","A creative-finance structure - also called the Morby Method - stacking seller carry with a primary lender so you close with little or no cash - sometimes with cash back. Stack Method and Morby Method are the same thing. See the full guide on our Stack Method page, and run your numbers in the calculator."),
 ("How does repayment work?","Repayment flows through licensed title/escrow at closing - funds never pass through personal accounts. Every transaction is escrow-secured and title-verified."),
 ("How do I become an affiliate?","Just bring a deal. Affiliates are Funding Hub community members - or non-members submitting straight through realquickfunds.com - who send us deals. We recommend joining the community first to learn how we fund, but it isn't required. Because we lend our own capital on escrow-secured funding, affiliates split actual profits 50/50 on deals we fund directly, and earn the majority of the referral on hard money and DSCR placed through our lending network. VIP adds the full playbooks and a white-label funding site - details and pricing inside the community."),
]
faq_html = ''.join('<div class="faqi"><h3>%s</h3><p>%s</p></div>' % (q,a) for q,a in FAQS)
import json
faq_schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQS]})
FAQ_BODY = '<script type="application/ld+json">%s</script>\n<h2>Frequently asked questions</h2>%s' % (faq_schema, faq_html)
page('faq','FAQ | RealQuick Funds','Answers on speed, credit checks, states, double closes, the Stack Method, repayment, and the affiliate program.',
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
