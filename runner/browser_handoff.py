"""Configurable real issuer login/consent browser automation."""
import os
from urllib.parse import urlsplit


def browser_urls(info, config, visited_urls=()):
    url = info.get('urls', {}).get(config.get('url_key', 'authorization_endpoint'))
    browser = info.get('browser', {})
    visited = set(browser.get('visited', [])) | set(visited_urls)
    candidates = [u for u in browser.get('urls', []) if u not in visited]
    return [candidate for candidate in dict.fromkeys(([url] if url else []) + candidates)
            if candidate not in visited]


def browser_url(info, config, visited_urls=()):
    urls = browser_urls(info, config, visited_urls)
    return urls[0] if urls else None


def drive_browser(info, config, output_dir, verify_ssl, remaining, visited_urls=None):
    from playwright.sync_api import sync_playwright
    visited_urls = visited_urls if visited_urls is not None else set()
    urls = browser_urls(info, config, visited_urls)
    if not urls:
        raise ValueError('Suite did not publish the configured browser URL key')
    allowed = config.get('allowed_hosts', [])
    if any(urlsplit(url).hostname not in allowed for url in urls):
        raise ValueError('Browser URL host is not in allowed_hosts')
    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--host-resolver-rules=MAP host.docker.internal 127.0.0.1'
        ] if os.getenv('CONFORMANCE_RESOLVE_LOCAL') == 'true' else [])
        screenshots = []
        for url in urls:
            context = browser.new_context(ignore_https_errors=verify_ssl is False)
            page = context.new_page()
            page.set_default_timeout(min(remaining * 1000, 30000))
            page.goto(url)
            for step in config['steps']:
                if urlsplit(page.url).hostname not in allowed:
                    raise ValueError('Login redirect host is not in allowed_hosts')
                locator = page.locator(step['selector'])
                action = step['action']
                if action == 'fill':
                    value = os.environ[step['value_env']] if 'value_env' in step else step['value']
                    locator.fill(value)
                elif action == 'click':
                    locator.click()
                elif action == 'wait':
                    locator.wait_for(state='visible')
                else:
                    raise ValueError(f'Unsupported browser action: {action}')
            # The suite callback submits the authorization response asynchronously.
            # Keep the real browser alive until that network activity completes.
            page.wait_for_load_state('networkidle')
            sequence = len(list(output_dir.glob('issuer-browser*.png'))) + 1
            screenshot = output_dir / ('issuer-browser-' + str(sequence) + '.png')
            page.screenshot(path=str(screenshot), full_page=True)
            screenshots.append(str(screenshot))
            visited_urls.add(url)
            context.close()
        browser.close()
    return {'screenshot_file': screenshots[-1], 'screenshot_files': screenshots, 'evidence_uploaded': False}
