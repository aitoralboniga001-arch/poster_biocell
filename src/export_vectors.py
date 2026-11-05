"""Export line work the living poster redraws live (actin filaments, SNARE helices) to Living_poster_v3/data/vectors.js."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_poster

OUT = os.path.join(os.path.dirname(HERE), 'Living_poster_v3', 'data', 'vectors.js')


def main():
    doc = build_poster.build(mode='plate')
    fil, nodes = doc._actin_data
    d = {
        'actin': [[round(a[0], 2), round(a[1], 2), round(b[0], 2), round(b[1], 2), round(k, 3)] for a, b, k in fil],
        'arp': [[round(q[0], 2), round(q[1], 2), round(k, 3)] for q, a1, a2, k in nodes],
        'snare': [{'pts': [[round(x, 2), round(y, 2)] for x, y in pz], 'c': c} for pz, c in doc._snare_data],
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('window.VEC = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, len(d['actin']), 'filaments', len(d['snare']), 'helices')


if __name__ == '__main__':
    main()
