"""Generate data/sdsu_graph.json from hand-digitised map coordinates.

Coordinates were digitised on an 819x654 preview of the 1836x1466 map photo
and are scaled to full-resolution pixels here. Lat/lng come from an affine fit
on three public reference points (Wikipedia/latlong.net) and are APPROXIMATE.
"""
import json, math, pathlib
S = 1836 / 819
B = {  # buildings / landmarks (preview px)
 "Viejas Arena": (345,160), "Aztec Recreation Center": (365,100), "Peterson Gym": (330,30),
 "Parking Structure 12": (488,160), "Parking Lot 13": (400,165), "Rec Field 103": (555,100),
 "ENS 700": (322,288), "Music": (378,295), "Dramatic Arts": (447,300), "Smith Recital Hall": (395,335),
 "Scripps Cottage": (440,255), "Adams Humanities": (330,385), "Love Library": (460,390),
 "Open Air Theatre": (395,400), "Hepner Hall": (550,345), "Communication": (575,320),
 "Professional Studies & Fine Arts": (625,320), "Nasatir Hall": (580,210), "Storm Hall": (600,190),
 "Storm Hall West": (560,185), "Arts & Letters": (665,240), "Art South": (680,330),
 "Life Sciences South": (630,385), "Physical Sciences": (600,420), "Physics & Astronomy": (555,420),
 "Engineering": (645,455), "Engineering & Interdisciplinary Sciences": (600,470),
 "Administration": (510,425), "Manchester Hall": (385,450), "Aztec Student Union": (365,495),
 "Student Services West": (420,515), "Education": (450,540), "North Education": (495,535),
 "Geology, Mathematics & Computer Science": (560,520), "Chemical Sciences Laboratory": (575,585),
 "Lamden Hall": (440,605), "SDSU Transit Center (Trolley)": (290,440), "Gateway Center": (205,275),
 "KPBS": (195,320), "Parking Structure 6": (200,190), "Parking Lot 5": (140,330),
 "Speech, Language & Hearing Sciences": (205,385), "South Campus Plaza": (230,465),
 "College Square": (140,510), "Maya Hall": (140,580), "Tenochca Residence Hall": (140,605),
 "Cuicacalli Residence Hall": (250,590), "University Towers": (60,100), "Parking Lot 14": (680,195),
 "Parking Structure 15": (725,115), "Parking Structure 16": (680,590), "SDSU Garage": (650,600),
}
J = {f"J{i}": p for i, p in enumerate([
 (245,355),(290,355),(350,355),(420,355),(480,355),(520,355),(560,370),(610,370),(660,380),
 (290,250),(350,230),(420,230),(480,215),(540,200),(600,240),(660,250),(420,420),(420,470),
 (480,470),(540,460),(600,500),(290,410),(290,470),(360,530),(450,580),(560,560),(240,250),
 (240,450),(240,550),(360,120),(420,110),(300,60),(150,260),(650,560),(150,450),(700,150)], 1)}
JE = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(1,27),(2,10),(10,11),(11,12),(12,13),(13,14),
 (14,15),(15,16),(16,9),(15,8),(12,4),(4,17),(17,18),(18,19),(19,20),(20,7),(20,21),(21,26),(26,34),
 (21,9),(17,5),(19,5),(2,22),(22,23),(23,18),(23,28),(28,1),(28,29),(29,24),(24,18),(24,25),(25,26),
 (10,27),(27,33),(33,35),(35,28),(11,30),(30,31),(31,13),(30,32),(32,27),(16,36),(14,31),(22,3),(35,29)]
REF = [((345,160),(32.773750,-117.074583)),((460,390),(32.775360,-117.070389)),((550,345),(32.775830,-117.071110))]
def solve3(rows, rhs):
    import itertools
    m = [r[:] + [v] for r, v in zip(rows, rhs)]
    for c in range(3):
        p = max(range(c,3), key=lambda r: abs(m[r][c])); m[c], m[p] = m[p], m[c]
        for r in range(3):
            if r != c:
                f = m[r][c]/m[c][c]; m[r] = [a-f*b for a,b in zip(m[r], m[c])]
    return [m[i][3]/m[i][i] for i in range(3)]
rows = [[x,y,1] for (x,y),_ in REF]
LA = solve3(rows, [ll[0] for _,ll in REF]); LO = solve3(rows, [ll[1] for _,ll in REF])
def ll(p): return (round(LA[0]*p[0]+LA[1]*p[1]+LA[2],6), round(LO[0]*p[0]+LO[1]*p[1]+LO[2],6))
def hav(a,b):
    R=6371000; f1,f2=map(math.radians,(a[0],b[0])); dl=math.radians(b[1]-a[1]); df=f2-f1
    return 2*R*math.asin(math.sqrt(math.sin(df/2)**2+math.cos(f1)*math.cos(f2)*math.sin(dl/2)**2))
nodes, edges = [], []
def full(p): return [round(p[0]*S,1), round(p[1]*S,1)]
for i,(n,p) in enumerate(B.items()):
    nodes.append({"id": f"b{i+1}", "name": n, "type": "building", "x": full(p)[0], "y": full(p)[1]})
for k,p in J.items():
    nodes.append({"id": k.lower(), "name": f"Walkway junction {k[1:]}", "type": "junction", "x": full(p)[0], "y": full(p)[1]})
for n in nodes:
    n["lat"], n["lng"] = ll((n["x"]/S, n["y"]/S))
byid = {n["id"]: n for n in nodes}
d = lambda a,b: math.hypot(a["x"]-b["x"], a["y"]-b["y"])
pairs = {tuple(sorted((f"j{a}", f"j{b}"))) for a,b in JE}
juncs = [n for n in nodes if n["type"]=="junction"]
for n in nodes:
    if n["type"]!="building": continue
    near = sorted(juncs, key=lambda j: d(n,j))
    for j in near[:2]:
        if j is near[0] or d(n,j) < 1.6*d(n,near[0]): pairs.add((n["id"], j["id"]))
mpp = sum(hav(ll(a),ll(b))/(math.hypot(a[0]-b[0],a[1]-b[1])*S) for (a,_),(b,_) in [(REF[0],REF[1]),(REF[1],REF[2]),(REF[0],REF[2])])/3
for a,b in sorted(pairs):
    px = d(byid[a],byid[b]); edges.append({"from":a,"to":b,"px":round(px,1),"m":round(px*mpp,1)})
out = {"campus":"sdsu","name":"San Diego State University","image":"sdsu_map.jpg","width":1836,"height":1466,
 "meters_per_pixel":round(mpp,4),"walk_speed_mps":1.35,"weight":"px",
 "notes":"Pixel coords on the map photo (north arrow points bottom-left). Edges are straight-line approximations of walkways. lat/lng are APPROXIMATE (affine fit on 3 reference points: Viejas Arena, Love Library, Hepner Hall).",
 "geo":{"approximate":True,"references":[{"name":n,"lat":l[0],"lng":l[1]} for n,l in zip(["Viejas Arena","Love Library","Hepner Hall"],[r[1] for r in REF])],
   "px_from_latlng":[[c*S for c in solve3([[l[0],l[1],1] for _,l in REF],[p[i] for p,_ in REF])] for i in (0,1)]},
 "nodes":nodes,"edges":edges}
pathlib.Path(__file__).resolve().parents[1].joinpath("data/sdsu_graph.json").write_text(json.dumps(out, indent=1))
print(len(nodes), len(edges), mpp)
