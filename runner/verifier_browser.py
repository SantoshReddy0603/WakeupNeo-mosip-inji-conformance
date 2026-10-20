"""Exercise the unmodified Inji UI and upload only its real transaction screenshot.

The official wallet receives the QR emitted by the actual release SDK. Browser
traffic and protocol validation are not intercepted or rewritten. Uploads require
the suite's actual placeholder and preserve the suite's REVIEW result.
"""
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def drive_verifier_browser(client, info, test_id, ui_url, expected_request, output_dir, remaining):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    import zxingcpp

    endpoint = info.get('urls', {}).get('authorization_endpoint')
    if not endpoint:
        raise ValueError('Suite did not expose a wallet authorization endpoint')
    wallet = urlsplit(endpoint)
    # Route the suite's own advertised endpoint through the configured origin.
    endpoint = client.base_url + wallet.path + ('?' + wallet.query if wallet.query else '')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = {'evidence_uploaded': False, 'source': 'official_inji_verify_ui', 'ui_url': ui_url}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--host-resolver-rules=MAP host.docker.internal 127.0.0.1'
        ] if os.getenv('CONFORMANCE_RESOLVE_LOCAL') == 'true' else [])
        try:
            context = browser.new_context(ignore_https_errors=client.session.verify is False,
                                          viewport={'width': 1440, 'height': 1000}, device_scale_factor=2)
            page = context.new_page()
            page.set_default_timeout(min(30000, max(1000, remaining * 1000)))
            session_results = []
            def observe(response):
                if urlsplit(response.url).path.endswith('/vp-session-results'):
                    body = response.request.post_data_json
                    if body.get('skipStatusChecks') is not False:
                        raise ValueError('UI session result request disabled status checks')
                    session_results.append({'http_status': response.status, 'request': body,
                                            'response': response.json(),
                                            'request_url': response.url,
                                            'request_method': response.request.method,
                                            'observed_at': datetime.now(timezone.utc).isoformat()})
            page.on('response', observe)
            page.goto(ui_url)
            page.locator('#stepper-request-credentials-button').click()
            with page.expect_response(lambda r: urlsplit(r.url).path.endswith('/v2/vp-session-request')) as event:
                page.locator('#verification-generate-qr-code-button').click()
            response = event.value
            if response.status != 201:
                raise ValueError(f'Native UI session creation returned HTTP {response.status}')
            actual = response.json()
            details = actual['authorizationDetails']
            if details['dcqlQuery'] != expected_request['dcqlQuery'] or details['clientId'] != expected_request['clientId']:
                raise ValueError('Actual UI request differs from the configured native conformance request')
            evidence.update(request_id=actual['requestId'], transaction_id=actual['transactionId'])
            # Decode the rendered QR, rather than synthesizing a wallet request.
            qr = page.locator('svg').filter(has=page.locator('path[fill="#000000"]'))
            qr.wait_for(state='visible')
            qr_image = qr.screenshot()
            (output_dir / 'verifier-qr.png').write_bytes(qr_image)
            barcode = zxingcpp.read_barcode(Image.open(io.BytesIO(qr_image)))
            if barcode is None:
                raise ValueError('Cannot decode the actual Verify UI QR')
            query = urlsplit(barcode.text).query
            fields = parse_qs(query, strict_parsing=True)
            if fields.get('state') != [actual['requestId']]:
                raise ValueError('UI QR state does not identify this transaction')
            if any(len(values) != 1 for values in fields.values()):
                raise ValueError('UI QR contains duplicate authorization parameters')
            evidence['authorization_request_sha256'] = hashlib.sha256(barcode.text.encode()).hexdigest()
            wallet_response = client.session.get(endpoint + ('&' if '?' in endpoint else '?') + query,
                                                 timeout=min(30, remaining), allow_redirects=False)
            evidence['wallet_http_status'] = wallet_response.status_code
            # The pinned official suite performs direct_post itself. Follow neither
            # arbitrary redirect locations nor any stand-in evidence HTML page.
            images = client.get_test_images(test_id)
            pending = [image for image in images if image.get('upload') and not image.get('img')]
            if not pending:
                page.screenshot(path=str(output_dir / 'verifier-browser.jpg'), type='jpeg', quality=85)
                evidence['screenshot_file'] = str(output_dir / 'verifier-browser.jpg')
                return evidence
            if len(pending) != 1:
                raise ValueError('Expected exactly one official verification screenshot placeholder')
            try:
                page.locator('#vc-result-display-message').wait_for(state='visible')
            except Exception:
                evidence['evidence_error'] = 'Native UI did not display a credential verification result'
                page.screenshot(path=str(output_dir / 'verifier-browser.jpg'), type='jpeg', quality=85)
                evidence['screenshot_file'] = str(output_dir / 'verifier-browser.jpg')
                (output_dir / 'verifier-session-results.json').write_text(json.dumps(session_results, indent=2))
                return evidence
            evidence['ui_result_text'] = page.locator('#vc-result-display-message').inner_text()
            if not session_results:
                raise ValueError('UI result has no observed native session-result response')
            if session_results[-1]['response'].get('transactionId') != actual['transactionId']:
                raise ValueError('UI result does not identify the created transaction')
            evidence['verification_http_status'] = session_results[-1]['http_status']
            evidence['verification_result'] = session_results[-1]['response']
            (output_dir / 'verifier-session-results.json').write_text(json.dumps(session_results, indent=2))
            screenshot = output_dir / 'verifier-browser.jpg'
            page.screenshot(path=str(screenshot), type='jpeg', quality=85)
            evidence['screenshot_file'] = str(screenshot)
            evidence['screenshot_sha256'] = hashlib.sha256(screenshot.read_bytes()).hexdigest()
            upload = client.upload_test_image(test_id, pending[0]['upload'], screenshot)
            evidence.update(evidence_uploaded=True, **upload)
            return evidence
        finally:
            browser.close()
