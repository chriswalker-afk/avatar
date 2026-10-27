#!/usr/bin/env python3
"""Real Chromium smoke/a11y/responsiveness checks, without external services."""
import http.server
import pathlib
import threading
import os
from contextlib import contextmanager
from xml.etree import ElementTree
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[1]
@contextmanager
def site():
    handler=lambda *args,**kw:http.server.SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kw)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}/index.html'
    finally:server.shutdown();server.server_close();thread.join(timeout=5)

def browser_launch(p):
    binary='/usr/bin/chromium'
    return p.chromium.launch(headless=True, executable_path=binary if os.path.exists(binary) else None, args=['--no-sandbox'])

def ready(page,url):
    page.goto(url,wait_until='domcontentloaded')
    page.locator('#creator-controls').wait_for(state='visible',timeout=15000)
    assert page.locator('#loading-error').is_hidden()
    assert page.locator('#critter-picture svg').count()==3
    assert page.locator('#head-options button').count()==8
    assert page.locator('#body-options button').count()==6
    assert page.locator('#legs-options button').count()==6
    for layer in ('head','body','legs'):
        assert page.locator(f'#{layer}-colours button').count()==7
        assert page.locator(f'#{layer}-options button[aria-pressed="true"]').count()==1
        assert page.locator(f'#{layer}-colours button[aria-pressed="true"]').count()==1

def desktop(browser,url):
    context=browser.new_context(viewport={'width':1440,'height':960},accept_downloads=True)
    page=context.new_page()
    errors=[];external=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:external.append(r.url) if not r.url.startswith(url.split('/index.html')[0]) else None)
    ready(page,url)
    assert page.locator('#critter-name').inner_text()=='Foxy Waddler'
    assert page.locator('#save-message').inner_text()=='Saved on this device'
    assert page.locator('#critter-picture').get_attribute('aria-label')=='Fox head, Penguin body and Frog legs'
    page.get_by_role('button',name='Owl head').click()
    page.get_by_role('button',name='Bear body').click()
    page.get_by_role('button',name='Rabbit legs').click()
    assert page.locator('#critter-name').inner_text()=='Owly Hugger'
    assert page.locator('#critter-description').inner_text()=='Owl head · Bear body · Rabbit legs'
    assert page.locator('#critter-picture svg').count()==3
    page.get_by_role('button',name='Grape purple head colour').click()
    page.get_by_role('button',name='Ocean teal body colour').click()
    page.get_by_role('button',name='Sunset orange legs colour').click()
    saved=page.evaluate("JSON.parse(localStorage.getItem('critter-lab.avatar.v1'))")
    assert saved=={'version':1,'head':'owl','body':'bear','legs':'rabbit','colours':{'head':'grape-purple','body':'ocean-teal','legs':'sunset-orange'}}
    # At least one recolour token is applied to each of the three rendered layers.
    assert page.locator('svg[data-layer="head"] [fill="#a785d5"]').count()>0
    assert page.locator('svg[data-layer="body"] [fill="#47b4c6"]').count()>0
    assert page.locator('svg[data-layer="legs"] [fill="#fb8156"]').count()>0
    with page.expect_download() as download_info:page.get_by_role('button',name='Save artwork').click()
    dl=download_info.value
    assert dl.suggested_filename=='critter-owl-bear-rabbit.svg'
    xml=dl.path().read_text(encoding='utf-8')
    root=ElementTree.fromstring(xml)
    assert root.attrib['viewBox']=='0 0 320 360'
    assert len(root.findall('{http://www.w3.org/2000/svg}g'))==3
    assert '<script' not in xml.lower() and 'https://' not in xml.lower()
    page.reload()
    ready(page,url)
    assert page.locator('#critter-name').inner_text()=='Owly Hugger'
    assert page.get_by_role('button',name='Grape purple head colour').get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='Surprise me!').click()
    assert page.locator('#critter-picture svg').count()==3
    assert page.locator('#announcer').inner_text().startswith('Surprise!')
    page.get_by_role('button',name='Start again').click()
    assert page.locator('#critter-name').inner_text()=='Foxy Waddler'
    assert page.get_by_role('button',name='Original head colour').get_attribute('aria-pressed')=='true'
    page.screenshot(path=str(ROOT/'tests'/'desktop-preview.png'),full_page=True)
    assert not errors,f'JS errors: {errors}'
    assert not external,f'Unexpected external requests: {external}'
    context.close()

def mobile(browser,url,width,height):
    context=browser.new_context(viewport={'width':width,'height':height},is_mobile=True,has_touch=True,device_scale_factor=1)
    page=context.new_page()
    ready(page,url)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'Horizontal overflow at {width}px'
    assert page.locator('#critter-picture').is_visible()
    page.get_by_role('button',name='Frog head').tap()
    page.get_by_role('button',name='Dino body').tap()
    page.get_by_role('button',name='Duck legs').tap()
    assert page.locator('#critter-description').inner_text()=='Frog head · Dino body · Duck legs'
    page.get_by_role('button',name='Leaf green head colour').tap()
    assert page.get_by_role('button',name='Leaf green head colour').get_attribute('aria-pressed')=='true'
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'Overflow after changes at {width}px'
    page.screenshot(path=str(ROOT/'tests'/f'mobile-{width}.png'),full_page=True)
    context.close()

def extras(browser,url):
    ctx=browser.new_context(viewport={'width':1024,'height':768},reduced_motion='reduce')
    page=ctx.new_page()
    ready(page,url)
    assert page.locator('#critter-picture').evaluate('(el)=>getComputedStyle(el).animationName')=='none'
    owl=page.get_by_role('button',name='Owl head')
    owl.focus()
    page.keyboard.press('Enter')
    assert owl.get_attribute('aria-pressed')=='true'
    assert page.locator('#announcer').inner_text().startswith('Owl head selected')
    ctx.close()
    bad=browser.new_context()
    bad.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Denied','SecurityError')}})")
    page=bad.new_page()
    ready(page,url)
    assert 'Storage unavailable' in page.locator('#save-message').inner_text()
    page.get_by_role('button',name='Cat head').click()
    assert page.locator('#critter-name').inner_text()=='Whiskers Waddler'
    bad.close()
    offline=browser.new_context()
    page=offline.new_page()
    page.route('**/manifest.json',lambda route:route.abort())
    page.goto(url)
    page.locator('#loading-error').wait_for(state='visible',timeout=12000)
    assert page.get_by_role('button',name='Surprise me!').is_disabled()
    page.unroute('**/manifest.json')
    page.get_by_role('button',name='Try again').click()
    page.locator('#creator-controls').wait_for(state='visible',timeout=15000)
    assert page.locator('#critter-picture svg').count()==3
    offline.close()

if __name__=='__main__':
    with site() as url:
        with sync_playwright() as p:
            browser=browser_launch(p)
            try:
                desktop(browser,url)
                for w,h in [(320,720),(390,844),(768,1024),(1280,720)]:mobile(browser,url,w,h)
                extras(browser,url)
                print('PASS: desktop save/reload, colour independence, export, random/reset, phone/tablet, a11y, network/storage/reduced-motion')
            finally:browser.close()