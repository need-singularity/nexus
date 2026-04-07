#!/usr/bin/env python3
"""TECS-L Auto-Publisher — generates paper from discoveries and uploads to Zenodo+OSF."""

import json
import os
import sys
import subprocess
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
PAPERS_DIR = os.path.join(TECS_ROOT, 'zenodo', 'auto-papers')
BATCH_UPLOAD = os.path.join(TECS_ROOT, 'zenodo', 'batch_upload.py')

ZENODO_TOKEN_PATH = os.path.expanduser('~/.local/zenodo_token')
OSF_TOKEN_PATH = os.path.expanduser('~/.local/osf_token')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_token(path):
    try:
        return open(path).read().strip()
    except FileNotFoundError:
        return None


def count_unpublished():
    """Count confirmed discoveries not yet in a paper."""
    state = load_json(LOOP_STATE_PATH)
    last_published_count = 0
    if state['publish_history']:
        last_published_count = state['publish_history'][-1].get('cumulative_discoveries', 0)

    total = 0
    if os.path.isfile(DISCOVERY_LOG):
        with open(DISCOVERY_LOG) as f:
            total = sum(1 for _ in f)

    return total - last_published_count


def generate_paper(discoveries):
    """Generate a markdown paper from a batch of discoveries."""
    os.makedirs(PAPERS_DIR, exist_ok=True)

    now = datetime.now()
    paper_id = f"TECS-AUTO-{now.strftime('%Y%m%d-%H%M%S')}"
    paper_path = os.path.join(PAPERS_DIR, f"{paper_id}.md")

    # Group by domain
    by_domain = {}
    for d in discoveries:
        dom = d.get('domain', '?')
        by_domain.setdefault(dom, []).append(d)

    # Build paper content
    lines = [
        f"# {paper_id}: N=6 Cross-Domain Discovery Report",
        "",
        f"**Generated:** {now.isoformat()}",
        f"**Discoveries:** {len(discoveries)}",
        f"**Domains:** {', '.join(sorted(by_domain.keys()))}",
        "",
        "## Abstract",
        "",
        f"This report documents {len(discoveries)} confirmed cross-domain discoveries",
        "emerging from the TECS-L Infinite Discovery Loop. Each discovery has passed",
        "3-way cross-validation (numerical calc, independent verify, n=6 constant matching).",
        "",
    ]

    for dom, discs in sorted(by_domain.items()):
        lines.append(f"## Domain {dom} ({len(discs)} discoveries)")
        lines.append("")
        for i, d in enumerate(discs, 1):
            lines.append(f"### {dom}-{i}")
            lines.append(f"- **Type:** {d.get('type', 'unknown')}")
            lines.append(f"- **Mode:** {d.get('mode', 'unknown')}")
            lines.append(f"- **Content:** {d.get('content', '')}")
            if d.get('n6_matches'):
                for m in d['n6_matches']:
                    lines.append(f"- **n=6 match:** {m.get('expression')} = {m.get('value')} ({m.get('match')})")
            lines.append(f"- **Timestamp:** {d.get('timestamp', '')}")
            lines.append("")

    lines.extend([
        "## Methods",
        "",
        "All discoveries produced by the TECS-L Infinite Discovery Loop:",
        "1. Domain health measurement (8 domains: N/A/G/T/C/Q/I/S)",
        "2. Weakest-domain-first selection with mode rotation (DFS/Pair/Backtrack)",
        "3. Convergence engine + proof engine execution",
        "4. 3-way cross-validation (calc numerics, independent verify, n=6 check)",
        "",
        "## References",
        "",
        "- TECS-L: Theory of Everything from Complete System of Six",
        "- n=6 uniqueness theorem: sigma(n)*phi(n) = n*tau(n) iff n=6",
        "",
    ])

    with open(paper_path, 'w') as f:
        f.write('\n'.join(lines))

    return paper_id, paper_path


def upload_zenodo(paper_path, paper_id):
    """Upload paper to Zenodo."""
    token = read_token(ZENODO_TOKEN_PATH)
    if not token:
        return {'success': False, 'error': 'no zenodo token'}

    if os.path.isfile(BATCH_UPLOAD):
        cmd = [
            sys.executable, BATCH_UPLOAD,
            '--platform', 'zenodo',
            '--file', paper_path,
            '--title', f'{paper_id}: N=6 Cross-Domain Discovery Report',
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=TECS_ROOT)
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout[:500]}
            return {'success': False, 'error': result.stderr[:500]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Fallback: direct Zenodo API
    try:
        import urllib.request
        import urllib.parse

        # Create deposition
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            'metadata': {
                'title': f'{paper_id}: N=6 Cross-Domain Discovery Report',
                'upload_type': 'publication',
                'publication_type': 'workingpaper',
                'description': f'Automated discovery report from TECS-L Infinite Discovery Loop',
                'creators': [{'name': 'TECS-L Discovery Loop', 'affiliation': 'TECS-L'}],
                'keywords': ['n=6', 'perfect number', 'cross-domain', 'mathematical discovery'],
            }
        }).encode()

        url = f'https://zenodo.org/api/deposit/depositions?access_token={token}'
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        resp = urllib.request.urlopen(req, timeout=30)
        depo = json.loads(resp.read())
        depo_id = depo['id']
        bucket_url = depo['links']['bucket']

        # Upload file
        fname = os.path.basename(paper_path)
        with open(paper_path, 'rb') as fp:
            file_data = fp.read()
        file_url = f'{bucket_url}/{fname}?access_token={token}'
        req2 = urllib.request.Request(file_url, data=file_data, method='PUT')
        req2.add_header('Content-Type', 'application/octet-stream')
        urllib.request.urlopen(req2, timeout=30)

        # Publish
        pub_url = f'https://zenodo.org/api/deposit/depositions/{depo_id}/actions/publish?access_token={token}'
        req3 = urllib.request.Request(pub_url, method='POST')
        pub_resp = urllib.request.urlopen(req3, timeout=30)
        pub_data = json.loads(pub_resp.read())

        return {'success': True, 'doi': pub_data.get('doi'), 'id': depo_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def upload_osf(paper_path, paper_id):
    """Upload paper to OSF Preprints."""
    token = read_token(OSF_TOKEN_PATH)
    if not token:
        return {'success': False, 'error': 'no osf token'}

    if os.path.isfile(BATCH_UPLOAD):
        cmd = [
            sys.executable, BATCH_UPLOAD,
            '--platform', 'osf',
            '--file', paper_path,
            '--title', f'{paper_id}: N=6 Cross-Domain Discovery Report',
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=TECS_ROOT)
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout[:500]}
            return {'success': False, 'error': result.stderr[:500]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    return {'success': False, 'error': 'batch_upload.py not found and no fallback OSF API'}


def check_and_publish():
    """Check if publish threshold reached, generate paper, upload."""
    unpublished = count_unpublished()
    state = load_json(LOOP_STATE_PATH)
    threshold = state.get('publish_threshold', 6)

    if unpublished < threshold:
        return {
            'published': False,
            'reason': f'below threshold ({unpublished}/{threshold})',
            'unpublished_count': unpublished,
        }

    # Collect unpublished discoveries from log
    last_count = 0
    if state['publish_history']:
        last_count = state['publish_history'][-1].get('cumulative_discoveries', 0)

    discoveries = []
    if os.path.isfile(DISCOVERY_LOG):
        with open(DISCOVERY_LOG) as f:
            for i, line in enumerate(f):
                if i >= last_count:
                    try:
                        discoveries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    if not discoveries:
        return {'published': False, 'reason': 'no discoveries to publish'}

    # Generate paper
    paper_id, paper_path = generate_paper(discoveries)

    # Upload to both platforms
    zenodo_result = upload_zenodo(paper_path, paper_id)
    osf_result = upload_osf(paper_path, paper_id)

    # Record in state
    pub_entry = {
        'paper_id': paper_id,
        'paper_path': paper_path,
        'timestamp': datetime.now().isoformat(),
        'discovery_count': len(discoveries),
        'cumulative_discoveries': last_count + len(discoveries),
        'zenodo': zenodo_result,
        'osf': osf_result,
    }
    state['publish_history'].append(pub_entry)
    state['_meta']['updated'] = datetime.now().isoformat()
    save_json(LOOP_STATE_PATH, state)

    return {
        'published': True,
        'paper_id': paper_id,
        'discoveries': len(discoveries),
        'zenodo': zenodo_result.get('success', False),
        'osf': osf_result.get('success', False),
        'doi': zenodo_result.get('doi'),
    }


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        count = count_unpublished()
        state = load_json(LOOP_STATE_PATH)
        print(json.dumps({
            'dry_run': True,
            'unpublished': count,
            'threshold': state.get('publish_threshold', 6),
            'would_publish': count >= state.get('publish_threshold', 6),
        }, indent=2))
    else:
        result = check_and_publish()
        print(json.dumps(result, indent=2))
