import cv2,numpy as np,sys
A=cv2.imread('work/lineup_fs060.png'); B=cv2.imread('work/lineup_fs000.png')
d=(np.abs(A.astype(int)-B.astype(int)).max(2)>6).astype(np.uint8)
d=cv2.dilate(d,np.ones((15,15),np.uint8))
n,lab,st,c=cv2.connectedComponentsWithStats(d)
ids=sorted([k for k in range(1,n) if st[k,4]>2000],key=lambda k:st[k,0])
reject={5,7,9}
m=np.zeros(d.shape,np.float32)
for i,k in enumerate(ids):
    if i in reject: m[lab==k]=1
m=cv2.dilate(m,np.ones((31,31),np.uint8)); m=cv2.GaussianBlur(m,(0,0),8)[...,None]
out=(A*(1-m)+B*m).round().astype(np.uint8)
cv2.imwrite('work/lineup_faces_selected.png',out)
print('rejected faces', sorted(reject), 'of', len(ids))
