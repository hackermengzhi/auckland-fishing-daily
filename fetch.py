import csv,io,json,math,os
from datetime import datetime,date,time,timedelta,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import requests
from astral import Observer
from astral.sun import sun
from astral.moon import phase,moonrise,moonset
TZ=ZoneInfo('Pacific/Auckland');DAY=date.fromisoformat(os.environ.get('REPORT_DATE',datetime.now(TZ).date().isoformat()))
OUT=Path('reports');OUT.mkdir(exist_ok=True)
def get(url):
 r=requests.get(url,timeout=45);r.raise_for_status();return r
es=[]
for year in sorted({(DAY+timedelta(days=d)).year for d in [-1,0,1]}):
 url=f'https://static.charts.linz.govt.nz/tide-tables/maj-ports/csv/Auckland%20{year}.csv'
 for row in csv.reader(io.StringIO(get(url).content.decode('utf-8-sig'))):
  try:dt=date(int(row[3]),int(row[2]),int(row[0]))
  except (ValueError,IndexError):continue
  if abs((dt-DAY).days)>1:continue
  for i in range(4,len(row)-1,2):
   if not row[i]:continue
   h,m=map(int,row[i].split(':'));es.append(((dt-DAY).days*24+h+m/60,float(row[i+1])))
es.sort();assert len(es)>=8,'Missing surrounding tide predictions'
# Half-cosine interpolation. Blue = absolute interpolated water-level change >=0.5 m/hour.
def height_speed(h):
 a,b=next((a,b) for a,b in zip(es,es[1:]) if a[0]<=h<=b[0]);u=(h-a[0])/(b[0]-a[0]);return a[1]+(b[1]-a[1])*(1-math.cos(math.pi*u))/2,(b[1]-a[1])*math.pi*math.sin(math.pi*u)/(2*(b[0]-a[0]))
active=[];start=None
for minute in range(1441):
 on=abs(height_speed(minute/60)[1])>=.5
 if on and start is None:start=minute/60
 if start is not None and (not on or minute==1440):active.append((start,minute/60));start=None
weather=get('https://solotapi.com/v1/forecast/getweatherall/rckq2fs7b').json()
def range_for(section,key,convert):
 d=weather[section]['dataset'];vals=[]
 for i,stamp in enumerate(d['ftime']):
  dt=datetime.fromisoformat(stamp.replace('Z','+00:00'))
  if dt.tzinfo is None:dt=dt.replace(tzinfo=timezone.utc)
  if dt.astimezone(TZ).date()==DAY and d[key][i] is not None:vals.append(convert(d[key][i]))
 if not vals:raise ValueError(f'No {DAY} values for {section}/{key}')
 return min(vals),max(vals)
ranges={k:range_for(*v) for k,v in {'sst':('sst','tmp',lambda x:x-273.15),'air':('atmos','tmp',lambda x:x-273.15),'wind':('atmos','wind',lambda x:x*1.943844),'wave':('wave','htsgw',lambda x:x)}.items()}
obs=Observer(-36.8556,174.7653);solar=sun(obs,date=DAY,tzinfo=TZ)
def lunar(fn):
 try:return fn(obs,date=DAY,tzinfo=TZ).strftime('%H:%M')
 except ValueError:return '—'
p=phase(DAY);names=['新月','峨眉月','上弦月','盈凸月','满月','亏凸月','下弦月','残月'];moon=names[int((p+1.75)//3.5)%8]
data={'date':DAY.isoformat(),'tides':es,'blue_windows':active,'ranges':ranges,'sunrise':solar['sunrise'].strftime('%H:%M'),'sunset':solar['sunset'].strftime('%H:%M'),'moon':moon,'moonrise':lunar(moonrise),'moonset':lunar(moonset),'generated_at':datetime.now(TZ).isoformat(),'weather_updates':{k:v.get('updateTime') for k,v in weather.items()},'blue_method':'reference estimate: |half-cosine interpolated tide height derivative| >= 0.5 m/hour; NOT Global Tide fish activity','time_assumption':'Solot timezone-naive ftime interpreted as UTC; not yet validated against App','species_type':'static Auckland species list, not live fish detections','tide_source':'LINZ Auckland port, chart datum; not screenshot coordinate model'}
(OUT/'latest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print('Fetched report data for',DAY)
