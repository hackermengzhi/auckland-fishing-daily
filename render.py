from PIL import Image,ImageDraw,ImageFont
import math,json,os
from pathlib import Path
from datetime import date
data=json.loads(Path("reports/latest.json").read_text())
DAY=date.fromisoformat(data["date"])
S=2;W,H=1080,1550
im=Image.new('RGB',(W*S,H*S),'#FFFFFF');d=ImageDraw.Draw(im)
CN=os.environ.get('FONT_CN','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');EN=os.environ.get('FONT_EN','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
def tx(x,y,s,z=24,c='#203C49',f=CN):d.text((round(x*S),round(y*S)),s,font=ImageFont.truetype(f,round(z*S)),fill=c)
def ln(ps,c,w=2):d.line([(round(x*S),round(y*S)) for x,y in ps],fill=c,width=w*S)
def fish(x,y,s=1,c='#4CE1CF'):
 d.ellipse((x*S,y*S,(x+35*s)*S,(y+18*s)*S),fill=c)
 d.polygon([((x+27*s)*S,(y+9*s)*S),((x+47*s)*S,(y-2*s)*S),((x+47*s)*S,(y+20*s)*S)],fill=c)
 d.ellipse(((x+7*s)*S,(y+5*s)*S,(x+10*s)*S,(y+8*s)*S),fill='#FFFFFF')
tx(50,33,'AUCKLAND  /  FISHING DAILY',19,'#5D92A5',EN)
tx(50,78,'奥克兰每日鱼情',48)
tx(50,143,f'{DAY.year}年{DAY.month}月{DAY.day}日 · 周'+ '一二三四五六日'[DAY.weekday()],23,'#A0B9C7')
ln([(50,194),(1030,194)],'#DCE6EA',1)
tx(50,224,'全天潮汐',28)


L,R,T,B=90,1000,372,780
X=lambda h:L+(R-L)*h/24;Y=lambda v:B-v/(math.ceil(max(v for h,v in data["tides"]))+.3)*(B-T)
# only short axis marks, no grid, shaded rectangles or curve fill
for v in range(math.ceil(max(v for h,v in data["tides"]))+1):
 y=Y(v);tx(50,y-12,str(v),18,'#698FA4',EN);ln([(80,y),(87,y)],'#42697E',1)
tx(48,317,'m',17,'#698FA4',EN)
es=data["tides"]
ps=[]
for i in range(961):
 h=i/40;a,b=next((a,b) for a,b in zip(es,es[1:]) if a[0]<=h<=b[0]);u=(h-a[0])/(b[0]-a[0]);v=a[1]+(b[1]-a[1])*(1-math.cos(math.pi*u))/2;ps.append((X(h),Y(v)))
ln(ps,'#527784',4)
for a,b in data['blue_windows']:
 ln([p for i,p in enumerate(ps) if a<=i/40<=b],'#32A9FF',6)
 for h in [a,b]:
  x,y=ps[min(960,round(h*40))];mins=round(h*60);label=f'{mins//60:02}:{mins%60:02}'
  tx(max(92,min(943,x-25)),y-40 if h==b else y+18,label,17,'#2495DF',EN)
for j,(h,v) in enumerate(es):
 if not 0<=h<24:continue
 high=v>es[j-1][1];mins=round(h*60);tm=f'{mins//60:02}:{mins%60:02}';x,y=X(h),Y(v)
 d.ellipse(((x-5)*S,(y-5)*S,(x+5)*S,(y+5)*S),fill='#F4AE77' if high else '#70DCCA')
 tx(max(90,min(930,x-47)),y-74 if high else y+17,tm,30)
 tx(max(90,min(930,x-29)),y-34 if high else y+56,f'{v:.1f}m',20,'#80A4B6',EN)
for h in [0,6,12,18,24]:tx(X(h)-24,856,f'{h:02}:00',19,'#7F9CAC',EN)
ln([(50,915),(1030,915)],'#DCE6EA',1)
tx(50,943,'鱼类',28);tx(824,950,'AUCKLAND',18,'#5D92A5',EN)
species=[('SNAPPER','鲷鱼'),('KINGFISH','黄条鰤'),('KAHAWAI','卡哈怀'),('TREVALLY','竹荚鲹'),('GURNARD','红鲂鮄'),('JOHN DORY','海鲂')]
for i,(en,cn) in enumerate(species):
 row,col=divmod(i,3);x=50+col*337;y=1002+row*113
 fish(x,y+8,.68,'#4EB9B0');tx(x+49,y,en,21,'#203C49',EN);tx(x+49,y+36,cn,21,'#80A4B6')
ln([(50,1247),(1030,1247)],'#DCE6EA',1)
def fmt(key,unit,places=1):
 a,b=data['ranges'][key];return f'{a:.{places}f}–{b:.{places}f}{unit}'
items=[('海表温度',fmt('sst','℃')),('气温',fmt('air','℃',0)),('风速',fmt('wind','节',0)),('浪高',fmt('wave','m')),('月相',data['moon']),('日出',data['sunrise']),('日落',data['sunset']),('月出 / 月落',data['moonrise']+' / '+data['moonset'])]

for i,(label,value) in enumerate(items):
 row,col=divmod(i,4);x=50+col*255;y=1282+row*112
 tx(x,y,label,19,'#7A929D')
 tx(x,y+35,value,27,'#203C49')
im.resize((W,H),Image.Resampling.LANCZOS).save('reports/latest.png')

Path(f"reports/{DAY}.png").write_bytes(Path("reports/latest.png").read_bytes())
