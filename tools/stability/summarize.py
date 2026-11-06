"""Summarise a soak.mjs run: per scene and round, the frame rate, how many frames ran long, the worst frame, and any
blank (flat) screenshots.  usage: python summarize.py out/soak_<label> [out/soak_<other> ...]"""
import json, sys, collections
from PIL import Image, ImageStat


def summarize(d):
    S = json.load(open(d + '/samples.json'))
    rows = collections.OrderedDict()
    flats = []
    for s in S:
        key = (s['tag'], s['sc'])
        r = rows.setdefault(key, {'secs': 0, 'frames': 0, 'l45': 0, 'l100': 0, 'l250': 0, 'max': 0, 'worst': []})
        r['secs'] += 2.1
        r['frames'] += s['frames']
        for l in s['long']:
            if 'd' not in l:
                continue
            r['l45'] += 1
            r['l100'] += l['d'] > 100
            r['l250'] += l['d'] > 250
            r['worst'].append((l['d'], l['T']))
        r['max'] = max(r['max'], s['max'])
        try:
            st = ImageStat.Stat(Image.open(f"{d}/{s['shot']}").convert('L'))
            if st.stddev[0] < 12:
                flats.append((s['t'], s['tag'], s['sc'], s['T']))
        except Exception:
            pass
    print(f'== {d}')
    print(f"{'round':7} {'scene':6} {'fps':>5} {'>45ms':>6} {'>100':>5} {'>250':>5} {'max':>5}  worst (ms @ T)")
    tot = collections.Counter()
    for (tag, sc), r in rows.items():
        fps = r['frames'] / max(r['secs'], 0.1)
        w = ', '.join(f'{d}@{t}' for d, t in sorted(r['worst'], reverse=True)[:4])
        print(f"{tag:7} {sc:6} {fps:5.0f} {r['l45']:6} {r['l100']:5} {r['l250']:5} {r['max']:5}  {w}")
        for k in ('l45', 'l100', 'l250'):
            tot[k] += r[k]
    print(f"TOTAL long frames: >45 ms {tot['l45']}, >100 ms {tot['l100']}, >250 ms {tot['l250']}; blank screenshots: {len(flats)} {flats[:5]}")


for d in sys.argv[1:]:
    summarize(d)
