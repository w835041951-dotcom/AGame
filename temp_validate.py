import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'tools'))
from gen_boss import BOSS_CONFIGS, _row_spans, _choose_face_span, _choose_mouth_span, CELL_PX

ok = True
for name, cfg in BOSS_CONFIGS.items():
    shape = set(cfg['shape'])
    shape_list = list(shape)
    min_y = min(p[1] for p in shape_list)
    face_span = _choose_face_span(shape_list, min_y)
    face_cells = [(x, face_span['y']) for x in range(face_span['start'], face_span['end'] + 1)]
    for fc in face_cells:
        if fc not in shape:
            print(f"FAIL {name}: face cell {fc} NOT in shape!")
            ok = False
    mouth_span = _choose_mouth_span(shape_list, face_span)
    mouth_cells = [(x, mouth_span['y']) for x in range(mouth_span['start'], mouth_span['end'] + 1)]
    for mc in mouth_cells:
        if mc not in shape:
            print(f"FAIL {name}: mouth cell {mc} NOT in shape!")
            ok = False
    fy, fs, fe = face_span['y'], face_span['start'], face_span['end']
    my, ms, me = mouth_span['y'], mouth_span['start'], mouth_span['end']
    print(f"  {name:12s}  face=row{fy}[{fs}-{fe}]  mouth=row{my}[{ms}-{me}]")

# Also validate pack bosses
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'tools'))
from gen_pack_201_300 import BOSSES
print("\n--- Pack 201-300 bosses ---")
for boss in BOSSES:
    shape = set(boss.shape)
    shape_list = list(shape)
    min_y = min(p[1] for p in shape_list)
    face_span = _choose_face_span(shape_list, min_y)
    face_cells = [(x, face_span['y']) for x in range(face_span['start'], face_span['end'] + 1)]
    for fc in face_cells:
        if fc not in shape:
            print(f"FAIL {boss.code}: face cell {fc} NOT in shape!")
            ok = False
    mouth_span = _choose_mouth_span(shape_list, face_span)
    mouth_cells = [(x, mouth_span['y']) for x in range(mouth_span['start'], mouth_span['end'] + 1)]
    for mc in mouth_cells:
        if mc not in shape:
            print(f"FAIL {boss.code}: mouth cell {mc} NOT in shape!")
            ok = False
    fy, fs, fe = face_span['y'], face_span['start'], face_span['end']
    my, ms, me = mouth_span['y'], mouth_span['start'], mouth_span['end']
    print(f"  {boss.code:25s}  face=row{fy}[{fs}-{fe}]  mouth=row{my}[{ms}-{me}]")

print(f"\n{'ALL OK - eyes/mouth strictly inside body' if ok else 'FAILURES FOUND'}")
