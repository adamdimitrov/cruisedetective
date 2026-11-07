import sys
import urllib.parse
from playwright.sync_api import sync_playwright

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8088'

test_paths = [
    '/',
    '/dinner-cruises-paris',
    '/seine-river-cruises-paris',
    '/canal-cruises-amsterdam',
    '/thames-river-cruises-london',
    '/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison',
    '/fr/meilleurs-diners-croisieres-paris',
    '/fr/meilleures-croisieres-seine-paris',
    '/fr/bateaux-mouches-ou-bateaux-parisiens',
    '/de/besten-bootsfahrten-mit-abendessen-paris',
    '/es/mejores-cruceros-con-cena-paris',
    '/it/migliori-crociere-con-cena-senna-parigi',
    '/ja/' + urllib.parse.quote('パリのベスト-ディナ-クル-ズ'),
    '/nl/beste-boottochten-seine-met-diner-parijs',
    '/pl/najlepsze-rejsy-z-obiadem-paryz',
    '/ro/cele-mai-bune-cina-croaziere-paris'
]

print(f"Starting Automated QC on {len(test_paths)} pages using base: {BASE_URL}...")

total_bugs = 0

with sync_playwright() as p:
    browser = p.chromium.launch()
    for path in test_paths:
        u = f"{BASE_URL}{path}"
        print(f"\n==========================================")
        print(f"AUDITING: {path}")
        print(f"==========================================")
        
        # 1. Desktop Test
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page_errors = []
        page.on('pageerror', lambda err: page_errors.append(str(err)))
        
        try:
            resp = page.goto(u, wait_until='load', timeout=15000)
            page.wait_for_timeout(300)
            status = resp.status if resp else 'None'
            print(f"  Desktop HTTP: {status}")
            
            # Check horizontal overflow
            has_h_scroll = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            if has_h_scroll:
                print(f"  ❌ [BUG: DESKTOP OVERFLOW] Horizontal scroll detected on {path}")
                total_bugs += 1
            else:
                print(f"  ✓ Desktop No Overflow")
                
            # Test filter buttons
            filters = page.query_selector_all('.ltt-tab-btn')
            if filters:
                print(f"  Found {len(filters)} filter buttons")
                for f in filters[:3]:
                    if f.is_visible():
                        f.click()
                        page.wait_for_timeout(80)
                print(f"  ✓ Filter Clicks Handled Cleanly")
                    
            # Test slider buttons
            slider_next = page.query_selector('.bpa-arrow.next')
            if slider_next and slider_next.is_visible():
                slider_next.click()
                page.wait_for_timeout(80)
                print(f"  ✓ Slider Click Handled Cleanly")
                
            # Test TOC jump
            toc_item = page.query_selector('#toc .tocitem')
            if toc_item and toc_item.is_visible():
                toc_item.click()
                print(f"  ✓ TOC Click Handled Cleanly")
                
            if page_errors:
                print(f"  ❌ [BUG: JS ERRORS] {page_errors}")
                total_bugs += len(page_errors)
            else:
                print(f"  ✓ Zero JS Page Errors")
                
        except Exception as e:
            print(f"  ❌ [EXCEPTION] {e}")
            total_bugs += 1
        finally:
            page.close()
            
        # 2. Mobile Test
        mpage = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True)
        m_page_errors = []
        mpage.on('pageerror', lambda err: m_page_errors.append(str(err)))
        try:
            mresp = mpage.goto(u, wait_until='load', timeout=15000)
            mpage.wait_for_timeout(300)
            mstatus = mresp.status if mresp else 'None'
            print(f"  Mobile HTTP: {mstatus}")
            
            has_m_scroll = mpage.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            if has_m_scroll:
                print(f"  ❌ [BUG: MOBILE OVERFLOW] Horizontal scroll detected on mobile for {path}")
                total_bugs += 1
            else:
                print(f"  ✓ Mobile No Overflow")
                
            # Test mobile nav drawer toggle
            nav_toggle = mpage.query_selector('#lttNavToggle')
            drawer = mpage.query_selector('#lttMobileDrawer')
            if nav_toggle and drawer:
                nav_toggle.click()
                mpage.wait_for_timeout(200)
                is_open = drawer.evaluate("el => el.classList.contains('is-open')")
                if not is_open:
                    print(f"  ❌ [BUG: MOBILE NAV] Drawer did not open when hamburger clicked")
                    total_bugs += 1
                else:
                    print(f"  ✓ Mobile Drawer Opens")
                    nav_toggle.click()
                    mpage.wait_for_timeout(200)
                    is_closed = drawer.evaluate("el => !el.classList.contains('is-open')")
                    if not is_closed:
                        print(f"  ❌ [BUG: MOBILE NAV] Drawer did not close when toggle re-clicked")
                        total_bugs += 1
                    else:
                        print(f"  ✓ Mobile Drawer Closes")
                        
            # Scroll down and check sticky bar
            mpage.evaluate("() => window.scrollTo(0, 1200)")
            mpage.wait_for_timeout(300)
            sticky_visible = mpage.evaluate("""() => {
                const bar = document.getElementById('sticky-bar') || document.querySelector('.hybrid-sticky-bar');
                if (!bar) return false;
                const style = window.getComputedStyle(bar);
                return style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0;
            }""")
            
            if any(k in path for k in ['dinner', 'cruises', 'croisieres', 'bateaux', 'bootsfahrten', 'cruceros', 'crociere', 'rejsy', 'boottochten', 'ディナ']):
                if not sticky_visible:
                    print(f"  ❌ [BUG: STICKY BAR] Sticky bar not visible on mobile scroll for {path}")
                    total_bugs += 1
                else:
                    print(f"  ✓ Mobile Sticky Bar Visible On Scroll")
                    
            if m_page_errors:
                print(f"  ❌ [BUG: MOBILE JS ERRORS] {m_page_errors}")
                total_bugs += len(m_page_errors)
            else:
                print(f"  ✓ Zero Mobile JS Errors")
                
        except Exception as e:
            print(f"  ❌ [MOBILE EXCEPTION] {e}")
            total_bugs += 1
        finally:
            mpage.close()

    browser.close()

print(f"\n==========================================")
print(f"AUTOMATED QC COMPLETED. TOTAL BUGS DETECTED: {total_bugs}")
print(f"==========================================")

if total_bugs > 0:
    sys.exit(1)
