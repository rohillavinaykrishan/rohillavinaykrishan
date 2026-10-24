import cv2,json,numpy as np
a={f['frame']:f for f in json.load(open('../../layout/v001/anchor.json'))['frames']}
tiles=[]
for i in range(25,52,2):
  p=cv2.imread('plate/plate.%04d.png'%i); x0,y0,x1,y1=map(int,a[i]['bbox'])
  cv2.rectangle(p,(x0,y0),(x1,y1),(255,0,255),3)
  p=cv2.resize(p,(480,201)); cv2.putText(p,'s%d'%i,(5,22),0,0.7,(0,255,255),2); tiles.append(p)
while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite('review/monument_bbox_vs_blade_heli.png',np.vstack([np.hstack(tiles[r:r+4]) for r in range(0,len(tiles),4)]))
