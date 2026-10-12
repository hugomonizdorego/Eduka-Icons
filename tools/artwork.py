"""Eduka shape library and compatibility catalog. GPL-3.0."""
import hashlib
import math
import re

PALETTE = {'sky':'#258fec','cobalt':'#4b61ef','coral':'#f65c57',
           'honey':'#f4b647','lavender':'#9662e7','teal':'#26b9af',
           'peach':'#f49766','cream':'#ece4d6','mint':'#45bd8a'}

def mix(a,b,t):
    a,b=a.lstrip('#'),b.lstrip('#')
    return '#'+''.join(f'{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02x}' for i in (0,2,4))

def color_for(name):
    return list(PALETTE)[int(hashlib.sha256(name.encode()).hexdigest()[:8],16)%len(PALETTE)]

def fill(c):return c if c=='none' or c.startswith('#') else f'url(#{c})'
def attrs(kw):return ' '.join(f'{k.replace("_","-")}="{v}"' for k,v in kw.items())
def path(d,c='ivory',**kw):return f'<path d="{d}" fill="{fill(c)}" {attrs(kw)}/>'
def rect(x,y,w,h,r=5,c='ivory',**kw):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill(c)}" {attrs(kw)}/>'
def circle(x,y,r,c='ivory',**kw):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill(c)}" {attrs(kw)}/>'
def line(d,c='#fff3dd',width=4,**kw):return path(d,'none',stroke=c,stroke_width=width,stroke_linecap='round',stroke_linejoin='round',**kw)
def book():
    return (path('M29 28H83Q97 28 97 41V98H38Q29 98 29 89Z','coral')+
            rect(27,26,59,70,8,'coral')+rect(31,28,7,64,3,'gold')+
            path('M39 94H94V100H39Q31 100 31 95Q31 90 39 90H94V94Z','paper')+
            rect(74,29,8,61,1,'sky')+line('M77 31V86','#b5efff',1.6)+
            line('M44 43H67M44 50H67M44 57H61','#922e32',3)+
            path('M48 68L53 75L65 62','none',stroke='#ffe1a5',stroke_width=4,stroke_linecap='round',stroke_linejoin='round')+
            line('M32 31V84','#ffb5a0',1.2))

def badge(kind):
    if kind=='home':return path('M50 78L64 67L78 78V94H69V83H59V94H50Z','paper')+line('M48 78L64 65L80 78','#ffd278',2.7)
    if kind=='download':return path('M59 67H69V81H78L64 94L50 81H59Z','paper')
    if kind=='music':return path('M57 73L76 69V87Q76 94 68 93Q62 89 69 86H72V75L61 78V91Q61 98 52 96Q48 90 57 88Z','paper')
    if kind=='pictures':return rect(48,70,32,24,3,'paper')+path('M51 91L60 78L66 85L71 81L78 91Z','sky')+circle(72,76,3,'honey')
    if kind=='video':return rect(48,70,32,24,4,'paper')+path('M60 75L71 82L60 89Z','coral')
    if kind=='share':return line('M57 81L73 73M57 81L73 91','#fff6e6',3)+circle(54,81,5,'paper')+circle(75,72,4,'honey')+circle(75,92,4,'honey')
    if kind=='lock':return path('M57 79V75C57 65 71 65 71 75V79','none',stroke='#fff1db',stroke_width=3)+rect(53,77,22,18,4,'honey')+circle(64,85,2,'ink')
    if kind=='templates':return rect(52,70,24,24,3,'paper')+line('M58 76H70M58 82H70M58 88H66','#6489c0',2)
    if kind=='git':return line('M57 70V91M57 82Q73 82 73 72','#fff2da',3)+circle(57,71,4,'paper')+circle(57,91,4,'paper')+circle(73,72,4,'honey')
    if kind=='cloud':return path('M54 93C41 93 42 79 53 79C54 67 70 65 75 79C87 77 88 93 77 93Z','paper')
    if kind=='desktop':return rect(49,69,30,21,3,'paper')+rect(53,73,22,13,2,'sky')+rect(60,90,8,4,1,'paper')
    if kind=='text':return rect(53,67,24,29,3,'paper')+line('M58 76H72M58 82H72M58 88H69','#7296c4',2.2)
    return ''

def folder(kind='plain',small=False):
    body=(path('M23 38Q23 31 31 31H50Q54 31 58 37L63 43H98Q106 43 106 51V91Q106 100 97 100H31Q23 100 23 91Z','cobalt')+
          path('M28 40H53L59 46H100V87H28Z','sky')+
          rect(33,42,61,44,4,'ivory',transform='rotate(-5 64 64)')+
          rect(35,47,60,39,3,'paper')+
          line('M43 52H84M43 58H80','#e4d1ab',2)+
          path('M23 58Q24 53 31 53H99Q109 53 108 63L102 95Q101 101 94 101H29Q22 101 21 94L18 63Q17 58 23 58Z','blue')+
          path('M22 59H100Q104 59 104 63','none',stroke='#a9e5ff',stroke_width=1.8,stroke_linecap='round')+
          line('M29 98H94','#1254ae',1.7))
    if not small:body+=badge(kind)
    elif kind!='plain':body+=f'<g transform="translate(-6 -7) scale(1.1)">{badge(kind)}</g>'
    return body

def doc(kind='text'):
    accent={'sheet':'mint','slides':'coral','pdf':'coral','zip':'honey','text':'sky'}[kind]
    s=path('M35 25H75L96 46V98Q96 104 89 104H35Q29 104 29 97V31Q29 25 35 25Z','ivory')
    s+=path('M76 26V42Q76 47 82 47H94Z',accent)+line('M35 28H71','#fffdf2',1.5)
    if kind=='sheet':
        s+=rect(38,55,46,35,4,accent)+line('M38 67H84M38 78H84M53 55V90M68 55V90','#e5ffe9',2)
    elif kind=='slides':s+=rect(38,55,47,35,5,accent)+path('M54 62L72 73L54 83Z','paper')
    elif kind=='pdf':s+=line('M43 88Q73 76 66 55Q53 63 79 88Q84 78 43 88','#e8544d',4)
    elif kind=='zip':
        s+=rect(59,43,10,42,2,'gold')+''.join(rect(58+(i%2)*7,46+i*6,7,4,1,'ink') for i in range(6))+rect(57,82,14,12,3,'ink')+rect(61,85,6,5,1,'honey')
    else:s+=rect(38,54,8,36,2,'sky')+line('M53 59H84M53 70H84M53 81H75','#6486ab',3)
    return s

def gear():
    pts=[]
    for i in range(64):
        a=2*math.pi*i/64;r=39 if i%8<4 else 32
        pts.append(f'{64+math.sin(a)*r:.2f},{64+math.cos(a)*r:.2f}')
    return path('M'+'L'.join(pts)+'Z','metal')+circle(64,64,28,'ivory')+circle(64,64,22,'ink')+circle(64,64,16,'sky')+circle(64,64,9,'ivory')+circle(61,59,3,'paper',opacity='.6')

def flower():
    s=''
    for i,c in enumerate(['honey','mint','teal','sky','lavender','coral','peach','gold']):
        s+=f'<ellipse cx="64" cy="44" rx="13" ry="25" transform="rotate({i*45} 64 64)" fill="{fill(c)}" opacity=".93"/>'
    return s+circle(64,64,5,'paper')

def glyph(kind,small=False):
    if kind=='book':return book()
    if kind=='folder' or kind.startswith('folder-'):return folder(kind[7:] if kind.startswith('folder-') else 'plain',small)
    if kind.startswith('doc-'):return doc(kind[4:])
    if kind=='gear':return gear()
    if kind=='flower':return flower()
    if kind=='phone':return circle(64,64,40,'mint')+'<g transform="translate(19 19) scale(.7)">'+path('M31 26Q25 26 23 34Q20 59 44 83Q66 105 89 102Q95 101 99 94L102 84Q103 80 98 77L83 69Q78 67 75 72L69 80Q54 77 46 64Q40 56 40 51L48 46Q52 43 49 38L41 27Q38 24 31 26Z','ivory')+'</g>'
    if kind=='message':return path('M34 29H91Q103 29 103 42V77Q103 89 91 89H59L38 103L40 89H34Q23 89 23 77V42Q23 29 34 29Z','sky')+line('M37 45H89M37 58H78M37 71H66','#fff3dd',5)
    if kind=='chat':return path('M30 40H76Q88 40 88 51V77Q88 88 76 88H53L35 101V88H30Q21 88 21 77V51Q21 40 30 40Z','ivory')+path('M52 25H96Q106 25 106 36V63Q106 74 96 74H87V85L73 74H52Q42 74 42 63V36Q42 25 52 25Z','coral')+line('M54 40H93M54 50H84M54 60H73','#fff0d9',4)+circle(30,94,9,'honey')+line('M26 94H34M30 90V98','#fff8e7',2)
    if kind=='camera':return rect(24,35,80,62,14,'ivory')+rect(40,28,25,13,5,'ivory')+rect(86,42,10,5,2,'ink')+circle(64,66,25,'metal')+circle(64,66,22,'lens')+circle(64,66,17,'glass')+circle(64,66,12,'glass',stroke='#426378',stroke_width='1.2')+circle(58,59,5,'#c8e6ef',opacity='.65')+circle(69,72,3,'sky',opacity='.5')+line('M31 40H42','#fffdf1',1.5)
    if kind=='weather':return circle(84,44,20,'honey')+''.join(line(f'M{84+math.cos(a)*25:.1f} {44+math.sin(a)*25:.1f}L{84+math.cos(a)*31:.1f} {44+math.sin(a)*31:.1f}','#ffc856',3) for a in [i*math.pi/4 for i in range(8)])+path('M34 91C14 91 16 66 35 65C35 39 69 34 79 59C105 55 113 91 89 91Z','paper')+line('M43 97L39 106M63 97L59 106M83 97L79 106','#62ddfa',4)
    if kind=='clock':return circle(64,65,39,'metal')+circle(64,63,37,'ivory')+''.join(line(f'M{64+math.sin(i*math.pi/6)*29:.2f} {63-math.cos(i*math.pi/6)*29:.2f}L{64+math.sin(i*math.pi/6)*25:.2f} {63-math.cos(i*math.pi/6)*25:.2f}','#748197',2) for i in range(12))+line('M64 43V63L83 74','#283a52',5)+line('M64 63L49 83','#f47754',2)+circle(64,63,4,'gold')+rect(32,22,13,10,5,'coral',transform='rotate(-25 38 27)')+rect(83,22,13,10,5,'coral',transform='rotate(25 90 27)')
    if kind=='calculator':return rect(33,24,63,82,12,'ivory')+rect(39,31,51,24,5,'ink')+line('M75 39H83M75 46H83M83 39V46','#93efdd',2)+''.join(rect(x,y,10,9,3,'honey' if x==78 else 'metal') for y in (62,76,90) for x in (40,59,78))+line('M37 27H88','#fffbea',1.3)
    if kind=='music':return rect(25,31,78,68,13,'coral')+circle(64,65,31,'ivory')+circle(64,65,26,'teal')+circle(64,65,22,'paper')+path('M57 54L77 49V76Q77 85 68 84Q62 80 70 75H72V57L62 60V81Q62 89 53 88Q45 83 57 78Z','teal')+circle(32,39,3,'paper')+circle(96,39,3,'sky')
    if kind=='heart':return path('M64 100C52 95 25 76 25 54C25 29 50 27 64 43C78 27 103 29 103 54C103 76 76 95 64 100Z','coral')+path('M32 51Q33 36 47 37','none',stroke='#ffc8af',stroke_width=3,stroke_linecap='round')
    if kind=='browser':return circle(64,64,39,'ivory')+circle(64,64,34,'sky')+path('M40 38L55 30L63 38L58 50L68 54L66 67L77 73L73 91L60 99L52 83L42 77L44 66L34 62Z','teal')+path('M80 35L93 47L97 61L88 65L77 54L79 44Z','honey')+path('M41 29Q24 41 26 60','none',stroke='#ffffff',stroke_width=2,stroke_linecap='round')+line('M88 82L98 91','#baf3ff',2)
    if kind=='terminal':return rect(23,29,82,71,12,'ink')+path('M23 41Q23 29 36 29H92Q105 29 105 41V46H23Z','metal')+circle(34,38,3,'coral')+circle(44,38,3,'honey')+circle(54,38,3,'mint')+line('M38 57L51 68L38 79','#f3efdf',5)+line('M63 83H85','#78edda',5)
    if kind=='code':return rect(23,29,82,72,10,'ink')+rect(23,29,82,17,8,'ivory')+circle(34,37,3,'coral')+circle(44,37,3,'honey')+line('M43 59L32 70L43 81M84 59L95 70L84 81','#bbd3ff',5)+line('M70 55L58 86','#ffc76d',5)
    if kind=='store':return path('M31 43H97L103 98Q104 104 97 104H31Q24 104 25 98Z','ivory')+path('M45 50V36C45 16 83 16 83 36V50','none',stroke='#ffd05f',stroke_width=7)+circle(45,50,3,'gold')+circle(83,50,3,'gold')+rect(47,66,34,23,5,'coral')+line('M64 70V84M57 77H71','#fff0df',4)
    if kind=='update':return circle(64,65,35,'ivory')+path('M40 50C50 30 83 29 94 49L103 41V66H78L86 57C78 42 58 42 49 56Z','sky')+path('M91 82C78 104 48 100 35 81L25 90V65H50L43 73C53 89 73 91 82 76Z','coral')+circle(64,66,7,'honey')
    if kind=='shield':return path('M64 24L99 35V65Q97 90 64 105Q31 90 29 65V35Z','ivory')+path('M64 31L92 41V64Q90 84 64 98Q39 84 36 64V41Z','sky')+line('M48 63L60 75L82 49','#fff8e5',7)+line('M39 43L62 34','#b9efff',1.7)
    if kind=='person':return circle(64,40,15,'peach')+path('M34 103V86Q34 62 64 62Q94 62 94 86V103Z','teal')+path('M51 64L64 80L77 64','ivory')+path('M64 81L59 100H69Z','coral')
    if kind=='rocket':return path('M48 76L27 86L32 62L49 54Z','coral')+path('M65 84L64 105L86 89L82 72Z','coral')+path('M46 80L30 103L52 94Z','honey')+path('M46 74C49 45 73 22 99 25C101 53 84 76 63 87Z','ivory')+circle(77,47,12,'metal')+circle(77,47,8,'sky')+circle(74,44,3,'paper')+path('M44 78L62 92L56 98L39 84Z','gold')
    if kind=='video':return rect(25,35,79,61,14,'ivory')+rect(31,41,67,49,11,'coral')+path('M55 51L80 65L55 80Z','paper')+line('M39 45H85','#ffb1a1',1.4)
    if kind=='headphones':return path('M31 66V56C31 12 97 12 97 56V66','none',stroke='#e5dbca',stroke_width=11)+path('M36 58V54C36 18 92 18 92 54V58','none',stroke='#fff8e7',stroke_width=3)+rect(24,61,22,37,10,'ivory')+rect(83,61,22,37,10,'ivory')+rect(39,67,8,26,4,'coral')+rect(81,67,8,26,4,'coral')
    if kind=='palette':return path('M103 60C101 25 42 21 26 48C11 75 38 103 63 103C82 103 88 91 78 83C67 73 87 72 95 71Q105 70 103 60Z','ivory')+''.join(circle(x,y,7,c) for x,y,c in [(40,49,'coral'),(60,38,'honey'),(82,46,'teal'),(91,62,'sky')])+circle(44,80,9,'ink')+circle(43,78,6,'peach')
    if kind=='flask':return path('M49 25H79V34H74V56L98 92Q104 104 91 104H37Q24 104 31 92L54 56V34H49Z','ivory')+path('M44 73H84L96 93Q100 99 90 99H38Q28 99 33 92Z','teal')+circle(53,82,4,'paper')+circle(72,91,5,'paper')+circle(66,64,4,'sky')+line('M58 37V55','#fffdf0',2)
    if kind=='game':return path('M44 42H83Q98 42 103 65L108 87Q110 103 96 98L81 83H47L32 98Q18 103 21 87L26 64Q31 42 44 42Z','ivory')+line('M34 64H55M44 54V75','#425066',5)+circle(86,56,5,'coral')+circle(96,66,5,'honey')+circle(77,66,5,'sky')+circle(86,77,5,'mint')+circle(56,77,5,'metal')+circle(70,77,5,'metal')
    if kind=='monitor':return rect(22,25,84,62,10,'metal')+rect(27,30,74,49,6,'ink')+rect(31,34,66,41,4,'sky')+path('M32 71L55 50L72 63L96 38V74H32Z','cobalt')+path('M32 35H80L32 64Z','paper',opacity='.13')+rect(56,84,16,12,2,'metal')+rect(43,96,42,8,4,'ivory')+circle(64,83,2,'paper')
    if kind=='laptop':return rect(28,27,72,56,8,'metal')+rect(33,32,62,45,4,'ink')+rect(37,36,54,37,3,'sky')+path('M37 69L57 49L68 57L91 39V73H37Z','cobalt')+path('M28 82H100L112 99Q111 104 103 104H25Q17 104 16 99Z','ivory')+path('M36 88H92L96 94H32Z','metal')+rect(52,95,24,5,2,'ink')
    if kind=='drive':return rect(29,26,70,78,12,'metal')+rect(33,30,62,67,9,'ivory')+circle(64,61,26,'lens')+circle(64,61,22,'metal')+circle(64,61,17,'metal',stroke='#879bab',stroke_width='1')+circle(64,61,7,'ink')+line('M88 83L64 61','#e9f0e8',6)+circle(88,83,4,'gold')+circle(39,92,3,'sky')
    if kind=='usb':return rect(46,23,36,30,4,'metal')+rect(52,28,7,12,1,'ink')+rect(69,28,7,12,1,'ink')+rect(40,48,48,57,14,'sky')+line('M64 85V64M64 73L54 66M64 77L76 69','#eaf8ff',3)+circle(64,88,4,'ivory')+path('M61 64L64 59L67 64Z','ivory')+rect(74,64,5,5,1,'ivory')
    if kind=='printer':return rect(39,24,50,28,4,'paper')+rect(22,45,84,41,12,'metal')+rect(37,69,54,36,5,'paper')+rect(28,62,72,11,4,'ink')+rect(39,70,50,33,4,'paper')+line('M47 81H82M47 90H76','#8197ae',3)+circle(95,55,3,'sky')
    if kind=='battery':return rect(49,23,30,11,3,'metal')+rect(39,31,50,73,11,'ivory')+rect(46,51,36,45,5,'teal')+path('M67 43L54 68H64L61 86L77 61H68Z','honey')+line('M43 36V87','#fffdf3',2)
    if kind=='wifi':return rect(20,22,88,84,26,'sky')+line('M35 56Q64 31 93 56M45 69Q64 53 83 69M55 81Q64 74 73 81','#fff3dd',8)+circle(64,91,6,'honey')
    if kind=='bluetooth':return rect(34,18,60,92,30,'cobalt')+line('M50 48L78 76L64 90V38L78 52L50 80','#fff3dd',7)
    if kind=='home':return path('M33 53L66 27L99 54V97Q99 103 92 103H38Q32 103 32 97Z','gold')+path('M25 57L64 24L105 57L99 64L64 35L31 64Z','honey')+rect(84,29,11,21,2,'gold')+path('M43 63L64 46L86 63V95H43Z','honey')+rect(55,69,19,31,3,'ivory')+rect(59,73,11,24,2,'gold')+circle(69,86,1.5,'paper')+line('M35 63V95H47','#ffd678',2)+line('M38 56L64 34','#ffe3a5',1.6)
    if kind=='trash':return path('M36 46H92L87 96Q86 104 78 104H50Q42 104 41 96Z','metal')+path('M42 48H86L81 98H48Z','ivory')+rect(31,36,66,10,5,'ivory')+rect(50,26,28,11,4,'metal')+line('M53 57L56 88M75 57L72 88','#99aaba',3)
    if kind=='lock':return path('M42 56V42C42 16 86 16 86 42V56','none',stroke='#d1dae0',stroke_width=10)+path('M45 54V42C45 20 83 20 83 42V54','none',stroke='#fff5df',stroke_width=2)+rect(30,52,68,51,12,'honey')+circle(64,72,7,'ink')+rect(61,74,6,14,3,'ink')+line('M37 58H84','#ffe5aa',1.8)
    if kind=='bulb':return path('M45 77C20 53 38 23 64 23C92 23 108 53 83 77L78 90H50Z','honey')+line('M55 84L52 58L64 66L76 58L73 84','#fff8df',3)+rect(49,88,30,7,3,'metal')+rect(51,98,26,5,2,'ink')+rect(57,104,14,4,2,'metal')+path('M42 46Q45 33 57 31','none',stroke='#fff2ba',stroke_width=3,stroke_linecap='round')
    if kind=='mail':return rect(24,35,80,61,11,'ivory')+path('M24 37L64 65L104 37V47L64 76L24 47Z','coral')+path('M24 46L33 52V95H29Q24 95 24 90Z','coral')+path('M95 52L104 46V90Q104 95 99 95H95Z','coral')+line('M35 88L47 77M93 88L81 77','#d8c5b1',2)
    if kind=='calendar':return rect(27,30,74,75,13,'ivory')+path('M27 44Q27 30 40 30H88Q101 30 101 44V52H27Z','coral')+line('M44 25V39M84 25V39','#fff3dc',6)+''.join(rect(x,y,8,7,2,'coral' if (x,y)==(62,76) else 'metal') for x in (36,49,62,75,88) for y in (61,76,91))
    if kind=='search':return circle(56,54,26,'metal')+circle(56,54,20,'glass')+circle(50,47,7,'sky',opacity='.35')+line('M74 74L99 100','#edbc65',13)+line('M80 82L96 98','#ffe2a8',2)+circle(56,54,17,'none',stroke='#acecff',stroke_width='1.5')
    if kind=='warning':return path('M58 29Q64 19 70 29L105 90Q112 103 99 103H29Q16 103 23 90Z','honey')+rect(60,46,8,31,4,'ink')+circle(64,89,4,'ink')+line('M30 88L57 39','#ffe69f',2)
    if kind=='info':return circle(64,64,40,'sky')+circle(64,42,6,'paper')+rect(59,56,10,34,5,'paper')
    if kind=='power':return circle(64,64,40,'coral')+line('M64 38V62','#fff3e3',9)+path('M50 46A24 24 0 1 0 78 46','none',stroke='#fff3e3',stroke_width=9,stroke_linecap='round')
    if kind=='volume':return rect(22,22,84,84,24,'teal')+path('M36 54H48L64 40V88L48 74H36Z','ivory')+path('M74 52Q84 64 74 76M82 42Q100 64 82 86','none',stroke='#fff3dd',stroke_width=6,stroke_linecap='round')
    if kind=='wand':return line('M34 99L86 47','#f5ebd8',12)+line('M34 99L62 71','#689ce4',11)+path('M86 23L91 36L104 41L91 46L86 59L81 46L68 41L81 36Z','honey')+path('M35 28L39 37L48 41L39 45L35 54L31 45L22 41L31 37Z','paper')
    if kind=='network':return rect(44,23,40,29,6,'metal')+rect(49,28,30,17,3,'sky')+line('M64 53V72M33 73H96M33 73V83M96 73V83','#f5f0df',6)+rect(20,82,27,23,5,'ivory')+rect(82,82,27,23,5,'ivory')+rect(24,86,19,12,2,'sky')+rect(86,86,19,12,2,'sky')
    if kind=='keyboard':return rect(18,40,92,54,11,'metal')+rect(22,43,84,47,8,'ivory')+''.join(rect(x,y,8,7,2,'ink') for y in (49,61) for x in (27,40,53,66,79,92))+rect(38,75,52,7,2,'ink')+line('M25 44H98','#fffdf0',1.4)
    if kind=='mouse':return rect(40,23,48,83,24,'ivory')+path('M64 25V60M43 60H85','none',stroke='#a6b4c6',stroke_width=2)+rect(60,33,8,17,4,'sky')+path('M47 45Q48 31 57 29','none',stroke='#fffdf0',stroke_width=2,stroke_linecap='round')
    if kind=='paint':return path('M49 73L89 26Q99 18 103 29L67 83Z','honey')+path('M49 72L68 84L59 97Q54 107 30 105Q45 99 37 92Z','coral')+line('M51 71L70 84','#d2d8da',6)+line('M57 65L93 28','#ffe6ac',2)
    if kind=='bell':return path('M64 24Q87 24 88 52V74L99 89H29L40 74V52Q41 24 64 24Z','honey')+circle(64,22,6,'gold')+circle(64,95,9,'coral')+line('M47 50Q48 36 58 33','#ffeab5',3)
    if kind=='smile':return circle(64,64,40,'honey')+circle(50,56,5,'ink')+circle(78,56,5,'ink')+path('M46 74Q64 92 82 74','none',stroke='#49453e',stroke_width=6,stroke_linecap='round')+circle(42,72,6,'coral',opacity='.55')+circle(86,72,6,'coral',opacity='.55')
    if kind=='help':return circle(64,64,40,'teal')+path('M50 53Q50 37 64 37Q78 37 78 51Q78 60 64 66V73','none',stroke='#fff3dd',stroke_width=9,stroke_linecap='round',stroke_linejoin='round')+circle(64,89,6,'paper')
    if kind=='error':return circle(64,64,40,'coral')+line('M49 49L79 79M79 49L49 79','#fff3dd',9)
    if kind=='check':return circle(64,64,40,'mint')+line('M46 65L59 78L83 51','#fff3dd',9)
    if kind=='key':return circle(44,64,22,'honey')+circle(44,64,8,'ivory')+rect(60,57,48,14,5,'honey')+rect(86,68,8,16,3,'gold')+rect(98,68,8,22,3,'gold')
    if kind=='star':return path('M64 18L77 47L108 50L85 71L92 102L64 86L36 102L43 71L20 50L51 47Z','honey')+line('M57 32L50 48','#ffeab5',3)
    if kind=='globe':return circle(64,64,40,'sky')+path('M40 38L55 30L63 38L58 50L68 54L66 67L77 73L73 91L60 99L52 83L42 77L44 66L34 62Z','mint')+path('M80 35L93 47L97 61L88 65L77 54L79 44Z','honey')+path('M64 24Q82 44 82 64Q82 84 64 104M64 24Q46 44 46 64Q46 84 64 104M25 64H103','none',stroke='#fff3dd',stroke_width=2,opacity='.7')
    if kind=='package':return path('M24 46L64 62V106L24 90Z','gold')+path('M64 62L104 46V90L64 106Z','honey')+path('M24 46L64 30L104 46L64 62Z','ivory')+path('M42 38L82 54V68L90 65V51L50 35Z','coral')
    if kind=='chart':return rect(22,24,84,78,14,'ivory')+rect(36,64,13,26,4,'teal')+rect(57,50,13,40,4,'honey')+rect(78,36,13,54,4,'coral')+line('M33 94H95','#cdbf9f',3)
    if kind=='mic':return rect(47,18,34,56,17,'metal')+line('M54 32H74M54 42H74M54 52H74','#8c8f7c',2.5)+path('M37 58Q37 88 64 88Q91 88 91 58','none',stroke='#e8dcc4',stroke_width=7,stroke_linecap='round')+rect(60,88,8,12,2,'ivory')+rect(44,98,40,9,4,'coral')
    if kind=='font':return rect(22,22,84,84,22,'ivory')+line('M36 90L54 38L72 90M42 74H66','#df7541',9)+circle(86,80,9,'none',stroke='#91b6ae',stroke_width=6)+line('M95 70V90','#91b6ae',6)
    if kind=='cloud':return path('M38 94C16 94 16 62 40 62C42 36 78 32 86 56C108 52 114 94 90 94Z','sky')+line('M34 70Q36 60 46 60','#e6f2ef',3)
    if kind=='download':return rect(24,82,80,22,9,'ivory')+path('M53 22H75V55H90L64 84L38 55H53Z','coral')+circle(88,93,3.5,'mint')
    if kind=='users':return circle(84,40,12,'honey')+path('M64 98V82Q64 60 84 60Q104 60 104 82V98Z','coral')+circle(52,46,15,'peach')+path('M22 106V88Q22 66 52 66Q82 66 82 88V106Z','teal')
    if kind=='puzzle':return path('M28 44H50Q46 24 64 24Q82 24 78 44H100V66Q118 62 118 80Q118 98 100 94V104H28V82Q44 86 44 72Q44 58 28 62Z','mint')+line('M34 50H46','#e5ecd2',2)
    if kind=='disc':return circle(64,64,40,'metal')+circle(64,64,35,'glass')+path('M64 29A35 35 0 0 1 99 64H84A20 20 0 0 0 64 44Z','paper',opacity='.45')+circle(64,64,12,'ivory')+circle(64,64,5,'ink')
    if kind=='image':return rect(22,28,84,72,12,'ivory')+rect(30,36,68,56,7,'sky')+path('M30 84L52 60L68 76L78 68L98 86V92H30Z','mint')+circle(82,52,7,'honey')
    if kind=='moon':return path('M76 24A40 40 0 1 0 104 76A32 32 0 0 1 76 24Z','honey')+path('M92 30L95 37L102 40L95 43L92 50L89 43L82 40L89 37Z','paper')
    if kind=='notes':return rect(26,24,76,80,10,'honey')+rect(26,24,76,16,8,'coral')+line('M38 56H90M38 70H90M38 84H74','#fff6e2',4)
    if kind=='smartphone':return rect(38,16,52,96,14,'ink')+rect(43,24,42,74,8,'sky')+circle(64,104,3.5,'metal')+path('M48 90L60 72L68 82L74 76L80 90Z','mint')
    if kind=='laptop-remote':return rect(28,27,72,56,8,'metal')+rect(33,32,62,45,4,'ink')+rect(37,36,54,37,3,'sky')+path('M28 82H100L112 99Q111 104 103 104H25Q17 104 16 99Z','ivory')+line('M52 55H76M68 47L76 55L68 63','#fff3dd',4)
    if kind=='logout':return rect(30,22,44,84,8,'ivory')+rect(36,28,32,72,5,'honey')+circle(60,66,3.5,'gold')+path('M66 52H86V42L106 64L86 86V76H66Z','coral')
    if kind=='hibernate':return circle(64,64,40,'sky')+path('M74 34A28 28 0 1 0 94 72A22 22 0 0 1 74 34Z','paper')+line('M40 40H50L40 50H50M30 58H37L30 65H37','#fff3dd',3)
    if kind=='clock-settings':return glyph('clock')+'<g transform="translate(66 66) scale(.42)">'+gear()+'</g>'
    raise KeyError(kind)

def folder_kind(name):
    for token,kind in [('desktop','desktop'),('remote','cloud'),('home','home'),('download','download'),('music','music'),('picture','pictures'),('photo','pictures'),('video','video'),('public','share'),('share','share'),('lock','lock'),('private','lock'),('template','templates'),('git','git'),('cloud','cloud'),('document','text'),('text','text')]:
        if token in name.lower():return kind
    return 'plain'

CATALOG = {
 'edukasaun': ('book','mint','apps','edukasaun-os eduka-desktop Eduka-Desktop eduka-menu Eduka-Menu eduka-icons eduka-panel Eduka-Panel start-here distributor-logo-debian'),
 'folder': ('folder','cream','places','folder-green inode-directory folder-open folder-drag-accept folder-visiting folder-new'),
 'user-home': ('home','mint','places','folder-home go-home'),
 'user-trash': ('trash','cream','places','user-trash-full trash-empty trash-full'),
 'folder-documents': ('doc-text','sky','places','folder-documents-green'),
 'folder-download': ('update','mint','places','folder-downloads folder-download-green'),
 'folder-music': ('music','coral','places','folder-music-green'),
 'folder-pictures': ('flower','cream','places','folder-pictures-green'),
 'folder-videos': ('video','lavender','places','folder-video folder-videos-green'),
 'folder-publicshare': ('network','teal','places','folder-public folder-publicshare-green'),
 'folder-templates': ('doc-text','honey','places','folder-templates-green'),
 'network-workgroup': ('network','sky','places','network-server network'),
 'internet-web-browser': ('browser','sky','apps','web-browser epiphany org.gnome.Epiphany'),
 'system-file-manager': ('folder','mint','apps','pcmanfm pcmanfm-qt thunar org.xfce.Thunar system-filemanager org.kde.dolphin dolphin nautilus org.gnome.Nautilus nemo caja'),
 'utilities-terminal': ('terminal','lavender','apps','lxterminal qterminal xterm terminal gnome-terminal org.gnome.Terminal org.kde.konsole konsole xfce4-terminal mate-terminal'),
 'accessories-calculator': ('calculator','cream','apps','galculator gnome-calculator org.gnome.Calculator kcalc mate-calc'),
 'accessories-text-editor': ('doc-text','sky','apps','featherpad org.gnome.TextEditor gedit org.gnome.gedit mousepad pluma kate kwrite'),
 'preferences-system': ('gear','peach','apps','preferences-desktop lxqt-config eduka-menu-settings Eduka-Menu-Settings eduka-settings Eduka-Settings systemsettings gnome-control-center org.gnome.Settings'),
 'eduka-update-system': ('update','mint','apps','eduka-update Eduka-Update-System EUS eduka-update-system-gui system-software-update update-manager'),
 'eduka-konekta': ('chat','sky','apps','Eduka-Konekta eduka-konekta-gui internet-chat'),
 'eduka-block': ('shield','mint','apps','Eduka-Block eduka-block-gui security-high'),
 'edukasaun-welcome': ('wand','honey','apps','eduka-welcome Edukasaun-Welcome welcome-screen eduka-customizer'),
 'eduka-lafa': ('bulb','honey','apps','lafa Lafa-Desktop Lafa-Virtual-Assistant eduka-lafa-desktop'),
 'system-software-install': ('store','cream','apps','gnome-software org.gnome.Software synaptic discover org.kde.discover app-center software-center'),
 'libreoffice-writer': ('doc-text','sky','apps','libreoffice-oasis-text application-vnd.oasis.opendocument.text'),
 'libreoffice-calc': ('doc-sheet','mint','apps','libreoffice-oasis-spreadsheet'),
 'libreoffice-impress': ('doc-slides','coral','apps','libreoffice-oasis-presentation'),
 'libreoffice-draw': ('paint','honey','apps','libreoffice-oasis-drawing'),
 'libreoffice-math': ('flask','lavender','apps','libreoffice-oasis-formula'),
 'libreoffice-startcenter': ('book','cream','apps','libreoffice'),
 'multimedia-photo-manager': ('flower','cream','apps','org.gnome.Photos shotwell digikam gthumb'),
 'camera-photo': ('camera','cream','devices','camera-web webcam'),
 'cheese': ('camera','cream','apps','org.gnome.Cheese guvcview kamoso'),
 'multimedia-video-player': ('video','lavender','apps','vlc org.videolan.VLC mpv celluloid org.gnome.Totem smplayer parole'),
 'multimedia-audio-player': ('music','coral','apps','rhythmbox org.gnome.Rhythmbox audacious clementine elisa org.kde.elisa'),
 'audio-headphones': ('headphones','sky','devices','audio-headset audio-card audio-speakers'),
 'internet-mail': ('mail','cream','apps','thunderbird org.mozilla.Thunderbird evolution org.gnome.Evolution'),
 'accessories-character-map': ('book','lavender','apps','gucharmap'),
 'org.gnome.Weather': ('weather','cream','apps','weather app-weather gnome-weather'),
 'org.gnome.clocks': ('clock','teal','apps','gnome-clocks accessories-clock clock'),
 'x-office-calendar': ('calendar','cream','apps','org.gnome.Calendar gnome-calendar korganizer'),
 'applications-education': ('book','mint','categories','applications-education-school eduka-category-edukasaun'),
 'applications-games': ('game','lavender','categories','applications-games-board'),
 'applications-science': ('flask','teal','categories','applications-science-physics'),
 'applications-graphics': ('palette','peach','categories','eduka-category-graphics'),
 'applications-internet': ('browser','sky','categories','eduka-category-internet'),
 'applications-office': ('doc-text','honey','categories','eduka-category-office'),
 'applications-development': ('code','lavender','categories','applications-programming eduka-category-programming'),
 'applications-multimedia': ('music','coral','categories','eduka-category-sound-video'),
 'applications-system': ('gear','cream','categories','applications-utilities eduka-category-system'),
 'applications-accessories': ('bulb','honey','categories','eduka-category-accessories'),
 'preferences-desktop-accessibility': ('person','sky','categories','applications-accessibility eduka-category-accessibility'),
 'computer': ('monitor','mint','devices','video-display display'),
 'computer-laptop': ('laptop','sky','devices','laptop'),
 'drive-harddisk': ('drive','cream','devices','drive-harddisk-system drive-harddisk-solidstate'),
 'drive-removable-media': ('usb','cream','devices','drive-removable-media-usb drive-removable-media-usb-pendrive media-flash'),
 'printer': ('printer','cream','devices','printer-network'),
 'input-keyboard': ('keyboard','teal','devices','input-keyboard-usb'),
 'input-mouse': ('mouse','mint','devices','input-mouse-usb'),
 'battery': ('battery','mint','devices','battery-ups'),
 'network-wireless': ('wifi','sky','devices','network-wireless-connected'),
 'bluetooth': ('bluetooth','sky','devices','bluetooth-active'),
 'text-x-generic': ('doc-text','cream','mimetypes','text-plain application-x-empty'),
 'application-pdf': ('doc-pdf','coral','mimetypes','application-x-pdf'),
 'application-zip': ('doc-zip','honey','mimetypes','application-x-archive application-x-compressed-tar application-x-7z-compressed application-x-rar'),
 'application-x-deb': ('store','mint','mimetypes','application-vnd.debian.binary-package application-x-rpm'),
 'application-x-executable': ('rocket','lavender','mimetypes','application-x-sharedlib'),
 'image-x-generic': ('flower','cream','mimetypes','image-jpeg image-png image-svg+xml'),
 'audio-x-generic': ('music','coral','mimetypes','audio-mpeg audio-x-wav'),
 'video-x-generic': ('video','lavender','mimetypes','video-mp4 video-x-matroska'),
 'text-x-script': ('code','sky','mimetypes','text-x-python text-x-shellscript text-x-csrc'),
 'system-search': ('search','sky','apps','search org.gnome.SearchTool'),
 'system-lock-screen': ('lock','cream','apps','preferences-system-privacy'),
 'system-shutdown': ('power','coral','apps',''),
 'system-log-out': ('logout','coral','apps','lxqt-logout gnome-logout application-exit xfsm-logout'),
 'dialog-warning': ('warning','cream','status','dialog-important emblem-important'),
 'dialog-information': ('info','sky','status','help-about help-info eduka-about lxqt-about gtk-about'),
 'emblem-favorite': ('heart','cream','emblems','emblem-favorites'),
}

# Semantic folder mapping. Clay artwork is selected by tools/clay.py.
for name,(kind,c,ctx,aliases) in list(CATALOG.items()):
    if name.startswith('folder'):
        kind='folder-'+folder_kind(name);c='cream'
    elif name=='system-file-manager':kind='folder';c='cream'
    elif name=='user-home':c='cream'
    elif kind in ('book','shield'):c='sky'
    elif kind in ('camera','mail','calculator'):c='coral' if kind=='camera' else 'lavender'
    elif kind=='gear':c='cobalt'
    elif kind in ('terminal','code'):c='lavender'
    elif kind in ('music','video'):c='teal' if kind=='music' else 'coral'
    elif kind=='flower':c='cream'
    elif kind in ('monitor','drive','printer','mouse','keyboard'):c='cobalt'
    elif kind in ('update','store','battery'):c='sky'
    CATALOG[name]=(kind,c,ctx,aliases)
CATALOG['call-start']=('phone','teal','apps','internet-telephony org.gnome.Calls call-outgoing')
CATALOG['mail-unread']=('message','teal','status','mail-message-new')

# Application aliases use original functional artwork rather than brand logos.
k,c,context,names=CATALOG['internet-web-browser']
CATALOG['internet-web-browser']=(k,c,context,names+' firefox firefox-esr org.mozilla.firefox chromium chromium-browser org.chromium.Chromium google-chrome com.google.Chrome brave-browser vivaldi opera')



def _extend(name, extra):
    kind, c, context, names = CATALOG[name]
    CATALOG[name] = (kind, c, context, names + ' ' + extra)

# Desktop environments, Eduka-Desktop and common Debian applications.
EXTENSIONS = {
 'edukasaun': 'edukasaun-desktop edukasaun-desktop-menu-open eduka-menu-daemon eduka-desktop-session edukasaun-logo distributor-logo start-here-debian applications-boot',
 'internet-web-browser': 'microsoft-edge librewolf io.gitlab.librewolf-community waterfox falkon org.kde.falkon midori qutebrowser konqueror org.kde.konqueror palemoon torbrowser tor-browser seamonkey floorp zen-browser text-html application-xhtml+xml',
 'system-file-manager': 'org.xfce.thunar spacefm doublecmd krusader org.kde.krusader pcmanfm-qt-desktop file-manager',
 'utilities-terminal': 'alacritty Alacritty kitty foot tilix com.gexperts.Tilix terminator guake yakuake sakura urxvt rxvt-unicode uxterm cool-retro-term org.gnome.Console kgx lxqt-sudo root-terminal',
 'accessories-calculator': 'qalculate qalculate-gtk qalculate-qt speedcrunch org.kde.kcalc applications-mathematics tuxmath geogebra org.geogebra.GeoGebra kbruch org.kde.kbruch kig org.kde.kig kmplot org.kde.kmplot',
 'accessories-text-editor': 'gnome-text-editor org.kde.kate xed notepadqq juffed leafpad l3afpad text-editor',
 'preferences-system': 'lxqt-config-session lxqt-config-globalkeyshortcuts lxqt-config-file-associations dconf-editor ca.desrt.dconf-editor preferences-other preferences-desktop-default-applications xfce4-settings-manager org.xfce.settings.manager mate-control-center systemsettings5 kcmshell5 cinnamon-settings budgie-control-center applications-system-settings lxqt-panel',
 'eduka-update-system': 'software-update-available software-properties software-properties-gtk software-properties-qt mintupdate org.gnome.Software-update package-update-indicator system-upgrade',
 'eduka-konekta': 'internet-chat-app telegram telegram-desktop org.telegram.desktop signal-desktop org.signal.Signal whatsapp-linux-app whatsapp-desktop com.github.eneshecan.WhatsAppForLinux zapzap discord com.discordapp.Discord element-desktop im.riot.Riot pidgin hexchat io.github.Hexchat konversation org.kde.konversation polari org.gnome.Polari skype slack com.slack.Slack zoom us.zoom.Zoom teams-for-linux jitsi-meet applications-chat',
 'eduka-block': 'gufw firewall-config firewalld security-high eduka-parental malcontent-control org.freedesktop.MalcontentControl preferences-system-parental-controls clamtk',
 'system-software-install': 'muon packagekit gnome-packagekit pamac pamac-manager flatpak flathub mintinstall plasma-discover org.kde.discover.app lxqt-archiver-store snap-store io.snapcraft.Store',
 'libreoffice-writer': 'abiword org.gnome.AbiWord x-office-document application-msword application-vnd.openxmlformats-officedocument.wordprocessingml.document application-rtf text-richtext',
 'libreoffice-calc': 'gnumeric org.gnome.Gnumeric x-office-spreadsheet application-vnd.ms-excel application-vnd.openxmlformats-officedocument.spreadsheetml.sheet application-vnd.oasis.opendocument.spreadsheet text-csv',
 'libreoffice-impress': 'x-office-presentation application-vnd.ms-powerpoint application-vnd.openxmlformats-officedocument.presentationml.presentation application-vnd.oasis.opendocument.presentation',
 'libreoffice-draw': 'x-office-drawing application-vnd.oasis.opendocument.graphics image-x-xcf',
 'libreoffice-startcenter': 'onlyoffice-desktopeditors org.onlyoffice.desktopeditors wps-office wps-office2019-kprometheus calligra applications-office-suite',
 'multimedia-photo-manager': 'lximage-qt eog org.gnome.eog gpicview ristretto org.xfce.ristretto gwenview org.kde.gwenview nomacs org.nomacs.ImageLounge feh loupe org.gnome.Loupe image-viewer accessories-image-viewer applications-photography eom org.mate.eom xviewer',
 'multimedia-video-player': 'io.mpv.Mpv haruna org.kde.haruna dragonplayer org.kde.dragonplayer kaffeine xplayer smplayer-mpv gnome-mpv io.github.celluloid_player.Celluloid totem showtime org.gnome.Showtime kodi tv.kodi.Kodi applications-video',
 'multimedia-audio-player': 'strawberry org.strawberrymusicplayer.strawberry lollypop org.gnome.Lollypop spotify com.spotify.Client deadbeef qmmp amarok juk sayonara quodlibet io.github.quodlibet.QuodLibet cantata gnome-music org.gnome.Music shortwave de.haeckerfelix.Shortwave multimedia-player',
 'audio-headphones': 'audacity org.audacityteam.Audacity ardour lmms io.lmms.LMMS hydrogen musescore mscore soundconverter easytag kid3 multimedia-audio-editor applications-audio',
 'internet-mail': 'geary org.gnome.Geary kmail org.kde.kmail2 claws-mail sylpheed mailspring betterbird eu.betterbird.Betterbird mail-client',
 'accessories-character-map': 'org.gnome.Characters gnome-characters kcharselect org.kde.kcharselect',
 'x-office-calendar': 'office-calendar evolution-calendar orage appointment-soon appointment-new text-calendar text-x-vcalendar',
 'applications-education': 'gcompris gcompris-qt org.kde.gcompris scratch scratch-desktop edu.mit.Scratch blinken org.kde.blinken applications-school',
 'applications-science': 'kalzium org.kde.kalzium avogadro chemtool step org.kde.step gnuplot octave org.octave.Octave scilab rstudio jupyter jupyterlab spyder',
 'applications-games': 'gnome-mines org.gnome.Mines gnome-mahjongg aisleriot sol gnome-chess org.gnome.Chess kpat kmines ksudoku supertux supertuxkart 0ad minetest net.minetest.Minetest steam com.valvesoftware.Steam lutris retroarch input-gaming',
 'applications-development': 'geany org.geany.Geany vscode com.visualstudio.code code codium com.vscodium.codium sublime-text thonny org.thonny.Thonny bluefish idle idle3 qtcreator org.qt-project.qtcreator kdevelop org.kde.kdevelop codeblocks lazarus arduino arduino-ide cc.arduino.IDE2 eclipse netbeans pycharm-community android-studio gitg org.gnome.gitg git-cola meld org.gnome.Meld ghex org.gnome.GHex okteta applications-engineering',
 'computer': 'hardinfo hardinfo2 cpu-x kinfocenter org.kde.kinfocenter preferences-desktop-display lxqt-config-monitor arandr display-settings xfce-display-settings preferences-desktop-screensaver',
 'computer-laptop': 'virtualbox VirtualBox virt-manager gnome-boxes org.gnome.Boxes qemu remmina org.remmina.Remmina krdc org.kde.krdc rustdesk anydesk teamviewer x2goclient vmplayer',
 'drive-harddisk': 'org.gnome.DiskUtility gnome-disks gparted partitionmanager org.kde.partitionmanager baobab org.gnome.baobab filelight qdirstat deja-dup org.gnome.DejaDup timeshift backintime drive-multidisk',
 'printer': 'system-config-printer printer-settings print-manager cups simple-scan org.gnome.SimpleScan skanlite xsane scanner',
 'input-keyboard': 'preferences-desktop-keyboard preferences-desktop-keyboard-shortcuts klavaro ktouch org.kde.ktouch tuxtype',
 'input-mouse': 'preferences-desktop-peripherals preferences-desktop-mouse lxqt-config-input input-touchpad',
 'battery': 'preferences-system-power-management preferences-system-power lxqt-config-powermanagement xfce4-power-manager-settings org.xfce.powermanager gnome-power-manager org.gnome.PowerStats power-statistics',
 'network-wireless': 'nm-applet network-manager',
 'network-workgroup': 'preferences-system-network nm-connection-editor preferences-system-network-proxy lxqt-config-network org.gnome.Settings-network',
 'bluetooth': 'preferences-system-bluetooth blueman blueman-manager blueman-adapters blueman-sendto blueman-services bluedevil gnome-bluetooth',
 'org.gnome.clocks': 'time-admin',
 'camera-photo': 'applets-screenshooter accessories-screenshot screengrab flameshot org.flameshot.Flameshot gnome-screenshot org.gnome.Screenshot spectacle org.kde.spectacle xfce4-screenshooter',
 'preferences-desktop-accessibility': 'orca accessibility preferences-desktop-accessibility-zoom',
 'applications-multimedia': 'applications-music',
 'text-x-generic': 'text-markdown text-x-readme text-x-log text-x-changelog text-x-copying',
 'application-pdf': 'document-viewer accessories-document-viewer evince org.gnome.Evince qpdfview okular org.kde.okular atril xreader zathura mupdf papers org.gnome.Papers application-postscript image-vnd.djvu',
 'application-zip': 'archive-manager file-roller org.gnome.FileRoller lxqt-archiver xarchiver ark org.kde.ark engrampa p7zip squeeze utilities-file-archiver application-x-bzip application-x-xz application-x-tar application-gzip application-x-gzip application-x-zstd-compressed-tar application-x-xz-compressed-tar application-x-bzip-compressed-tar application-vnd.rar application-x-7z application-x-lzma',
 'application-x-deb': 'gdebi gdebi-kde qapt-deb-installer application-vnd.flatpak.ref application-vnd.snap',
 'application-x-executable': 'application-x-ms-dos-executable application-x-msdownload application-x-msi application-x-appimage application-vnd.appimage wine winecfg application-x-desktop application-default-icon',
 'image-x-generic': 'image-gif image-bmp image-webp image-tiff image-x-icon image-heic image-avif',
 'audio-x-generic': 'audio-flac audio-ogg audio-x-vorbis+ogg audio-mp4 audio-aac audio-midi audio-x-mpegurl',
 'video-x-generic': 'video-webm video-x-msvideo video-quicktime video-mpeg video-ogg',
 'text-x-script': 'application-x-shellscript text-x-java text-x-c++src text-x-chdr application-javascript text-javascript application-json text-x-makefile text-css application-x-python-bytecode',
 'system-search': 'catfish org.gnome.Nautilus-search kfind fsearch',
 'system-lock-screen': 'lxqt-lockscreen xscreensaver light-locker',
 'system-shutdown': 'lxqt-leave lxqt-shutdown gnome-session-halt xfsm-shutdown system-shutdown-panel',
 'eduka-lafa': 'applications-other',
}
for _name, _extra in EXTENSIONS.items():
    _extend(_name, _extra)

NEW_ENTRIES = {
 'help-browser': ('help','teal','apps','yelp org.gnome.Yelp help-contents system-help khelpcenter org.kde.khelpcenter dialog-question'),
 'dialog-error': ('error','coral','status','emblem-unreadable process-error'),
 'emblem-default': ('check','mint','emblems','emblem-ok emblem-checked task-complete'),
 'emblem-readonly': ('lock','cream','emblems','emblem-locked'),
 'system-reboot': ('update','sky','apps','system-restart lxqt-reboot gnome-session-reboot'),
 'system-suspend': ('moon','honey','apps','lxqt-suspend'),
 'system-hibernate': ('hibernate','sky','apps','lxqt-hibernate system-suspend-hibernate'),
 'preferences-system-time': ('clock-settings','teal','apps','preferences-system-date-time lxqt-admin-time'),
 'system-run': ('rocket','lavender','apps','gnome-run lxqt-runner krunner org.kde.krunner xfce4-appfinder'),
 'system-users': ('users','coral','apps','users lxqt-admin-user user-admin gnome-user-accounts preferences-system-users org.gnome.Settings-users system-switch-user'),
 'preferences-desktop-locale': ('globe','sky','apps','lxqt-config-locale config-language locale org.gnome.Settings-region applications-geography kgeography org.kde.kgeography marble org.kde.marble stellarium celestia org.gnome.Maps gnome-maps applications-astronomy eduka-language-pack-tet'),
 'preferences-desktop-sound': ('volume','teal','apps','pavucontrol pavucontrol-qt org.pulseaudio.pavucontrol multimedia-volume-control audio-volume-control lxqt-config-sound gnome-sound-properties'),
 'preferences-system-notifications': ('bell','honey','apps','lxqt-config-notificationd lxqt-notificationd notification-area preferences-desktop-notification notification'),
 'preferences-desktop-theme': ('palette','peach','apps','lxqt-config-appearance preferences-desktop-appearance preferences-desktop-color gnome-tweaks org.gnome.tweaks lxappearance qt5ct qt6ct kvantum kvantummanager'),
 'preferences-desktop-wallpaper': ('image','sky','apps','preferences-desktop-background nitrogen variety'),
 'preferences-desktop-font': ('font','cream','apps','font-manager org.gnome.font-viewer gnome-font-viewer font-x-generic application-x-font-ttf font-ttf application-x-font-otf'),
 'utilities-system-monitor': ('chart','cream','apps','qps lxqt-qps lxtask gnome-system-monitor org.gnome.SystemMonitor ksysguard plasma-systemmonitor org.kde.plasma-systemmonitor htop btop xfce4-taskmanager mate-system-monitor'),
 'accessories-dictionary': ('book','mint','apps','goldendict artha org.gnome.Dictionary gnome-dictionary anki kwordquiz parley khangman kanagram calibre calibre-gui com.calibre_ebook.calibre foliate com.github.johnfactotum.Foliate accessories-ebook-reader application-epub+zip'),
 'accessories-notes': ('notes','honey','apps','org.gnome.Notes xpad gnote tomboy cherrytree joplin obsidian simplenote standard-notes zim qownnotes knotes org.gnome.Todo gnome-todo planner errands'),
 'dialog-password': ('key','honey','apps','keepassxc org.keepassxc.KeePassXC seahorse org.gnome.seahorse.Application kwalletmanager bitwarden passwords password-manager'),
 'internet-download-manager': ('download','coral','apps','transmission transmission-gtk transmission-qt com.transmissionbt.Transmission qbittorrent org.qbittorrent.qBittorrent deluge ktorrent fragments de.haeckerfelix.Fragments uget motrix persepolis application-x-bittorrent'),
 'face-smile': ('smile','honey','emblems','face-smile-big face-laugh face-happy emoji'),
 'starred': ('star','honey','emblems','rating emblem-favorite-star bookmark-new user-bookmarks'),
 'package-x-generic': ('package','honey','mimetypes','application-x-addon package'),
 'application-x-extension': ('puzzle','mint','mimetypes','preferences-plugins extensions applications-utilities-extra'),
 'media-optical': ('disc','cream','devices','drive-optical media-optical-cd media-optical-dvd application-x-cd-image application-x-iso9660-image brasero k3b xfburn'),
 'audio-input-microphone': ('mic','cream','devices','microphone audio-input-microphone-high'),
 'phone': ('smartphone','sky','devices','smartphone kdeconnect org.kde.kdeconnect.app gsconnect multimedia-player-apple-ipod'),
 'x-office-address-book': ('users','coral','apps','org.gnome.Contacts gnome-contacts kaddressbook contacts text-x-vcard'),
 'graphics-editor': ('paint','honey','apps','gimp org.gimp.GIMP inkscape org.inkscape.Inkscape krita org.kde.krita mypaint org.mypaint.MyPaint pinta com.github.PintaProject.Pinta kolourpaint org.kde.kolourpaint drawing com.github.maoschanz.drawing tuxpaint darktable rawtherapee blender scribus applications-painting'),
 'multimedia-video-editor': ('video','coral','apps','kdenlive org.kde.kdenlive openshot org.openshot.OpenShot shotcut org.shotcut.Shotcut pitivi flowblade obs com.obsproject.Studio simplescreenrecorder vokoscreenNG kazam peek handbrake fr.handbrake.ghb'),
 'folder-desktop': ('folder-desktop','cream','places','user-desktop user-desktop-folder'),
 'folder-git': ('folder-git','cream','places','folder-development folder-code'),
 'folder-remote': ('folder-cloud','cream','places','folder-cloud folder-network network-server-folder folder-remote-ftp'),
 'folder-locked': ('folder-lock','cream','places','folder-lock folder-private'),
 'folder-text': ('folder-text','cream','places','folder-documents-open'),
}
for _name, _entry in NEW_ENTRIES.items():
    if _name in CATALOG: raise ValueError(f'Duplicate catalog entry: {_name}')
    CATALOG[_name] = _entry

def duplicates():
    """Return icon names claimed by more than one catalog entry."""
    owners = {}
    for name, (_, _, _, names) in CATALOG.items():
        for other in {name, *names.split()}:
            owners.setdefault(other, []).append(name)
    return {n: o for n, o in owners.items() if len(o) > 1}
