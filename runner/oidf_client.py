"""Synchronous orchestration adapter over the pinned official OIDF Python library."""
import asyncio
import base64
import io
import json
import time
import zipfile
from pathlib import Path
from urllib.parse import quote
import requests
from vendor.oidf.conformance import Conformance

TERMINAL = {'FINISHED', 'FAILED', 'INTERRUPTED', 'CANCELLED'}

class OIDFClient:
    def __init__(self, base_url='https://localhost:8443', token=None, timeout=30, verify_ssl=True):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._loop = None
        self._upstream = None
        # Optional GitHub secrets exist as empty strings when unset. The pinned
        # official client distinguishes None from '', and would send 'Bearer '.
        self.token = token.strip() or None if token is not None else None
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({'Accept': 'application/json'})
        if self.token:
            self.session.headers['Authorization'] = f'Bearer {self.token}'

    def _official(self, method, *args):
        # One event loop/client per runner instance; no cross-thread async client.
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            self._upstream = Conformance(self.base_url, self.token, self.session.verify)
        return self._loop.run_until_complete(asyncio.wait_for(
            getattr(self._upstream, method)(*args), timeout=self.timeout))

    def close(self):
        try:
            if self._loop is not None:
                self._loop.run_until_complete(self._upstream.close_client())
                self._loop.close()
                self._loop = None
                self._upstream = None
        finally:
            self.session.close()

    def request(self, method, path, **kwargs):
        response = self.session.request(method, self.base_url + path, timeout=self.timeout, **kwargs)
        if not response.ok:
            try:
                error = response.json()
                detail = '; '.join(str(error[key])[:500] for key in ['error', 'message', 'error_description']
                                   if isinstance(error, dict) and key in error)
            except ValueError:
                detail = ''
            if detail:
                raise requests.HTTPError(f'{response.status_code} {path}: {detail}', response=response)
        response.raise_for_status()
        return response

    def check_health(self):
        try:
            return isinstance(self.request('GET', '/api/runner/available').json(), list)
        except (requests.RequestException, ValueError):
            return False

    def wait_for_ready(self, max_wait_sec=60, interval_sec=2):
        deadline = time.monotonic() + max_wait_sec
        while time.monotonic() < deadline:
            if self.check_health():
                return True
            time.sleep(min(interval_sec, max(0, deadline - time.monotonic())))
        return False

    def create_test_plan(self, plan_name, config, variant=None):
        return self._official('create_test_plan', plan_name, json.dumps(config), variant or {})

    def get_test_plan(self, plan_id):
        return self.request('GET', f'/api/plan/{quote(plan_id, safe="")}').json()

    def create_test_from_plan(self, plan_id, test_name, variant=None):
        return self._official('create_test_from_plan_with_variant', plan_id, test_name, variant)

    def start_test(self, test_id):
        return self._official('start_test', quote(test_id, safe=''))

    def get_test_status(self, test_id):
        return self._official('get_module_info', quote(test_id, safe=''))

    def get_test_runtime(self, test_id):
        return self.request('GET', f'/api/runner/{quote(test_id, safe="")}').json()

    def poll_test_completion(self, test_id, poll_interval_sec=1, max_timeout_sec=300, on_waiting=None):
        deadline = time.monotonic() + max_timeout_sec
        started = False
        handled = set()
        last = {}
        while time.monotonic() < deadline:
            last = self.get_test_status(test_id)
            state = str(last.get('status', '')).upper()
            if state in TERMINAL:
                return last
            if state == 'CONFIGURED' and not started:
                self.start_test(test_id)
                started = True
                continue
            if state == 'WAITING' and on_waiting:
                runtime = self.get_test_runtime(test_id)
                # The suite may finish between the info and runtime requests.
                latest = self.get_test_status(test_id)
                if str(latest.get('status', '')).upper() in TERMINAL:
                    return latest
                interaction = {**last, **runtime}
                interaction['urls'] = runtime.get('exposed', runtime.get('urls', {}))
                marker = json.dumps({'urls': interaction.get('urls', {}),
                                     'browser': runtime.get('browser', {})}, sort_keys=True)
                if marker not in handled:
                    if on_waiting(interaction, max(1, deadline - time.monotonic())) is not False:
                        handled.add(marker)
            time.sleep(min(poll_interval_sec, max(0, deadline - time.monotonic())))
        return {**last, 'last_observed_status': last.get('status'),
                'last_observed_result': last.get('result'), 'status': 'TIMEOUT', 'result': 'TIMEOUT'}

    def get_test_log(self, test_id):
        return self._official('get_test_log', quote(test_id, safe=''))

    def get_test_images(self, test_id):
        return self.request('GET', f'/api/log/{quote(test_id, safe="")}/images').json()

    def upload_test_image(self, test_id, placeholder, path):
        path = Path(path)
        data = path.read_bytes()
        if len(data) > 500 * 1024:
            raise ValueError('Screenshot exceeds the official suite upload limit')
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif data.startswith(b'\xff\xd8\xff'):
            mime = 'image/jpeg'
        else:
            raise ValueError('Screenshot must be an actual PNG or JPEG')
        encoded = 'data:' + mime + ';base64,' + base64.b64encode(data).decode()
        response = self.request('POST',
            f'/api/log/{quote(test_id, safe="")}/images/{quote(placeholder, safe="")}',
            data=encoded,
            headers={'Content-Type': 'text/plain'}).json()
        if not response or response.get('img') != encoded:
            raise ValueError('Official suite did not fill the screenshot placeholder')
        return {'placeholder': placeholder, 'log_entry_id': response.get('_id')}

    def export_plan_results(self, plan_id, save_to_dir='reports'):
        data = self.request('GET', f'/api/plan/export/{quote(plan_id, safe="")}',
                            headers={'Accept': 'application/zip'}).content
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if not any(not entry.is_dir() and entry.file_size for entry in archive.infolist()):
                raise ValueError('Official export contains no result artifacts')
            bad = archive.testzip()
            if bad:
                raise ValueError(f'Corrupt export member: {bad}')
        directory = Path(save_to_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f'plan-{quote(plan_id, safe="")}-export.zip'
        path.write_bytes(data)
        return {'export_file': str(path)}
