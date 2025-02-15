import os.path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import pandas as pd

# 输入:下面knid列表的内容
# 输出:带有国服成绩的等积分表
# --------------------------------------------------------------
#    玩家名称
player = 'CHUNITHM'
#  是否生成高清图 / 1:生成 2:不生成
if_generated = 1

# --------------------------------------------------------------
knid = ['10', '10+', '11', '11+', '12', '12+', '13', '13+', '14', '14+', '15']
difficulty = ['bas', 'adv', 'exp', 'mas', 'ult']


def name_replace(name_str):
    name_str = (
        name_str.replace('[', '［').replace(']', '］')
        .replace('#', '＃').replace('>', '＞').replace('_', ' ')
        .replace('　', ' ')
    )

    name_str = name_str[0].upper() + name_str[1:]
    name_str = (name_str.replace('"', '%22').replace('\\', '%5C')
                .replace('/', '%2F').replace(':', '%3A')
                .replace('*', '%2a').replace('?', '%3F')
                .replace('<', '%3C').replace('>', '%3E')
                .replace('|', '%7C')
                )

    return name_str


def get_songs(srg):
    with open('idinfo.txt', 'r', encoding='utf-8') as p:
        info = eval(p.readlines()[0])
        songs = []
        paint_height = 700 + 150 * 5 + 80 * 4
        a = 10 + srg * 0.5
        b = a + 0.4
        num = [0, 0, 0, 0, 0]
        for name, detail in info.items():

            for di in difficulty:
                if detail[di] != '' and a <= float(detail[di]) <= b:
                    i = 4 - int((float(detail[di]) * 10 - a * 10))
                    num[i] += 1
                    if num[i] > 11 and (num[i] - 1) % 11 == 0:
                        paint_height += 175
                    songs.append((detail['id'], name, di, float(detail[di])))
    return songs, num, paint_height


# input srg
def level_input():
    while 1:
        srg = -1
        level = input()
        for i in range(11):
            if knid[i] == level:
                srg = i
        if srg != -1:
            break
    return srg


srg = level_input()
a = 10 + srg * 0.5
b = a + 0.4
songs, num, height = get_songs(srg)
songs = sorted(songs)

start_y = [400, 0, 0, 0, 0]
start_x = 200
for i in range(1, 5):
    start_y[i] = start_y[i - 1] + 80 + (int((num[i - 1] - 1) / 11) + 1) * 180 - 30


lofk = 'Designed by export60'
player_text = "Player: "+player
df = pd.read_csv('save.csv', encoding='utf-8')
for i in range(10):
    df.drop(i, inplace=True)
df = df[(df['定数'] >= a) & (df['定数'] <= b)]
df.sort_values(by='定数', inplace=True, ascending=False)
df.insert(df.shape[1], 'used', 0)
print(' 成绩读取完成 ')

def draw_leveltittle(img):
    font_size = 70
    setFont = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', font_size)
    draw = ImageDraw.Draw(img)
    for i in range(5):
        levelnow = b - 0.1 * i
        levelnow = int(levelnow * 10) / 10
        x, y = 32, start_y[i] + 20
        draw.text((x, y), str(levelnow), font=setFont, fill='black')
    return img


def draw_chart(img):
    font_size = 40
    setFont = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', font_size)
    now, row = [0] * 5, [0] * 5
    alpha = 0
    for di in reversed(difficulty):
        if a >= 11 and di == 'bas':
            continue
        elif a >= 13 and di == 'adv':
            continue
        # song (id, name, difficulty, level)
        for song in songs:
            if song[2] == di:
                # df (排行, 乐曲名, 难度, 定数, 分数, Rating, used)
                for df_row in df.itertuples():
                    if getattr(df_row, 'used') == 1:
                        continue
                    name2 = name_replace(getattr(df_row, '乐曲名'))
                    level = float(getattr(df_row, '定数'))
                    if song[1] == name2 and a <= level <= a + 0.4:

                        # 定位细分难度
                        i = 4 - int((level * 10 - a * 10))

                        # 定位像素点
                        x = start_x + now[i] * 175
                        y = start_y[i] + row[i] * 180

                        # 放贴图
                        if di == 'ult':
                            color = 'black'
                        elif di == 'exp':
                            color = 'red'
                        elif di == 'adv':
                            color = 'orange'
                        elif di == 'bas':
                            color = 'green'
                        song_img = Image.open('./img/' + name2 + '.png').convert('RGBA')
                        if di != 'mas':
                            x -= 8
                            y -= 8
                            song_img = ImageOps.expand(song_img, border=(8, 8, 8, 8), fill=color)
                        score = getattr(df_row, '分数')
                        # 没打过的歌,调透明度
                        if int(score) == 0:
                            fx, fy = song_img.size
                            for ix in range(fx):
                                for iy in range(fy):
                                    colori = song_img.getpixel((ix, iy))
                                    colori = colori[:-1] + (180,)
                                    # song_img.putpixel((ix, iy), colori)
                            # 降低亮度
                            song_img = ImageEnhance.Brightness(song_img).enhance(0.5)
                        img.paste(song_img, (x, y))

                        # 放分数
                        if int(score) > 0:
                            l, t, r, b = setFont.getbbox(str(score))
                            w, h = r - l, b - t
                            text_x = x + (150 - w) / 2 + 8
                            text_y = y + 141
                            if di == 'mas':
                                text_y -= 8
                                text_x -= 8
                            draw = ImageDraw.Draw(img)
                            draw.text((text_x, text_y), str(score), font=setFont, fill='black', stroke_width=4,
                                      stroke_fill='white')

                        # 放Rank
                        if int(score) > 0:
                            rank = None
                            if int(score) >= 1009000:  # sss+
                                rank = Image.open('./img/sssp.png')
                            elif int(score) >= 1007500:  # sss
                                rank = Image.open('./img/sss.png')
                            elif int(score) >= 1005000:  # ss+
                                rank = Image.open('./img/ssp.png')
                            elif int(score) >= 1000000:  # ss
                                rank = Image.open('./img/ss.png')
                            elif int(score) >= 990000:  # s+
                                rank = Image.open('./img/sp.png')
                            elif int(score) >= 975000:  # s
                                rank = Image.open('./img/s.png')
                            if rank is not None:
                                rank = rank.convert('RGBA')
                                rank_x, rank_y = x + 12, y - 8
                                if di != 'mas':
                                    rank_x += 8
                                    rank_y += 8
                                img.paste(rank, (rank_x, rank_y))

                        now[i] += 1
                        if now[i] >= 11:
                            now[i] = 0
                            row[i] += 1
                        df.at[df_row.Index, 'used'] = 1
                        break

    return img


img = Image.open('./img/bg.png').convert('RGBA').resize((2200, height))
img = draw_leveltittle(img)
logo = Image.open('./img/chusan2025.png')
font_size = 60
setFont5 = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', 120)
setFont6 = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', font_size)
text1 = 'Data is from Diving-fish'
ImageDraw.Draw(img).text((1400, height - 170), text1, font=setFont6, fill=(195, 33, 54), stroke_fill='white',
                         stroke_width=2)
ImageDraw.Draw(img).text((1520, height - 100), lofk, font=setFont6, fill=(195, 33, 54), stroke_fill='white',
                         stroke_width=2)
ImageDraw.Draw(img).text((200, 140), player_text, font=setFont5, fill=(68, 206, 246), stroke_fill='white',
                         stroke_width=6)
img.paste(logo, (1700, 0), mask=logo)

print(' 正在绘制图标')

img = draw_chart(img)
if os.path.exists('./output') is False:
    os.makedirs('./output')
if if_generated:
    img.save('./output/chulevel_chart_' + knid[srg] + '.png')

compress_rate = 0.38

w, h = img.size
img = img.resize((int(w * compress_rate), int(h * compress_rate)))
img.save('./output/chulevel_chart_' + knid[srg] + '_compressed.png')

print(' 已输出至 output/chulevel_chart_' + knid[srg] + '')
print(' 绘制完成，感谢使用~')
