"""Break a spike.mjs trace down: the long GPU-thread tasks and what is inside them, and every image decode.
usage: python analyze.py out/trace_<label>.json [minMs]"""
import json, sys, collections

ev = json.load(open(sys.argv[1]))
MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 40
thr = {}
for e in ev:
    if e.get('ph') == 'M' and e.get('name') == 'thread_name':
        thr[(e['pid'], e['tid'])] = e['args']['name']
X = [e for e in ev if e.get('ph') == 'X' and e.get('dur')]
by_thread = collections.defaultdict(list)
for e in X:
    by_thread[thr.get((e['pid'], e['tid']), '?')].append(e)
t0 = min(e['ts'] for e in X)

def inside(lst, a, b):
    return [e for e in lst if e['ts'] >= a and e['ts'] + e['dur'] <= b]

for name in ('CrGpuMain', 'CrRendererMain'):
    L = sorted(by_thread.get(name, []), key=lambda e: e['ts'])
    tops = [e for e in L if e['name'] in ('RunTask', 'ThreadControllerImpl::RunTask') and e['dur'] / 1000 > MIN]
    print(f'== {name}: {len(tops)} tasks over {MIN} ms')
    for t in tops[:25]:
        kids = inside(L, t['ts'], t['ts'] + t['dur'])
        agg = collections.Counter()
        for k in kids:
            if k is t:
                continue
            agg[k['name']] = max(agg[k['name']], k['dur'] / 1000)
        top = ', '.join(f'{n} {d:.0f}' for n, d in agg.most_common(7))
        print(f'  @{(t["ts"] - t0) / 1e6:6.2f}s {t["dur"] / 1000:6.0f} ms: {top}')

print('== image decodes (worker threads), longest first')
dec = [e for e in X if e['name'] in ('Decode Image', 'GpuImageDecodeCache::DecodeImage', 'ImageDecodeTask') and e['dur'] / 1000 > 15]
seen = set()
for e in sorted(dec, key=lambda e: -e['dur'])[:30]:
    a = e.get('args', {})
    info = json.dumps(a)[:220]
    key = (e['name'], round(e['ts'] / 1000))
    if key in seen:
        continue
    seen.add(key)
    print(f'  @{(e["ts"] - t0) / 1e6:6.2f}s {e["dur"] / 1000:6.0f} ms {e["name"]} {info}')
