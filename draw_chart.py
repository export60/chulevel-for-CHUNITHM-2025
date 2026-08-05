import json
import os.path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import pandas as pd

# 输入:下面levels列表的内容
# 输出:带有国服成绩的等级分表
# 数据格式：水鱼: df_score.csv 落雪: lx_score.csv
# --------------------------------------------------------------
#    玩家名称
player = ''
#  是否生成高清图 / 1:生成 2:不生成
if_generated = 1
#  分数来源（查分器）/ 1:水鱼 diving-fish 2:落雪 lxns
source = 2

# --------------------------------------------------------------
levels = ['10', '10+', '11', '11+', '12', '12+', '13', '13+', '14', '14+', '15', '15+']
difficulty = ['bas', 'adv', 'exp', 'mas', 'ult']


def get_songs(srg):
    with open('index/data.json', 'r', encoding='utf-8') as p:
        data = json.load(p)
        paint_height = 700 + 150 * 5 + 80 * 4
        a = 10 + srg * 0.5
        b = a + 0.4
        songs = []
        num = [0, 0, 0, 0, 0]
        for song in data:
            for i_ds in range(len(song['ds'])):
                if  a <= float(song['ds'][i_ds]) <= b:
                    i = 4 - int((float(song['ds'][i_ds]) * 10 - a * 10))
                    num[i] += 1
                    if num[i] > 11 and (num[i] - 1) % 11 == 0:
                        paint_height += 175
                    songs.append((i,song['id'],song['title'], difficulty[i_ds], float(song['ds'][i_ds])))
    return songs, num, paint_height


# input srg
def level_input():
    while 1:
        srg = -1
        level = input("[10, 10+, 11, 11+, 12, 12+, 13, 13+, 14, 14+, 15, 15+]\n输入你想要查询的等级区间: ")
        for i in range(12):
            if levels[i] == level:
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
if source == 1:
    df = pd.read_csv('df_score.csv', encoding='utf-8')
    df = df[(df['定数'] >= a) & (df['定数'] <= b)]
    df.sort_values(by='定数', inplace=True, ascending=False)

elif source == 2:
    df = pd.read_csv('lx_score.csv', encoding='utf-8')
    df = df[(df['level'] == levels[srg])]
    df.sort_values(by='score', inplace=True, ascending=False)
    df = df.drop_duplicates(subset=['id','level_index'])

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
        # song (i, id, name, difficulty, level)
        for song in songs:
            if song[3] == di:
                # 水鱼 df (排名, 乐曲名, 难度, 定数, 分数, Rating, used)
                if source == 1:
                    for df_row in df.itertuples():
                        if getattr(df_row, 'used') == 1:
                            continue

                            level = float(getattr(df_row, '定数'))
                            title = getattr(df_row, '乐曲名')
                            score = getattr(df_row, '分数')
                        else:
                            level = song[4]
                            title = getattr(df_row, 'song_name')
                            score = getattr(df_row, 'score')

                        if song[2] == title:

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
                            song_img = Image.open('./img/songs/' + str(song[1]) + '.png').convert('RGBA')
                            song_img = song_img.resize((150, 150))
                            if di != 'mas':
                                x -= 8
                                y -= 8
                                song_img = ImageOps.expand(song_img, border=(8, 8, 8, 8), fill=color)

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
                else:
                    # song (i, id, name, difficulty, level)
                    # 落雪 df (id,song_name,level,level_index,score,rating,
                    #       over_power,clear,full_combo,full_chain,rank,upload_time,play_time， used)
                    id = song[1]
                    if not os.path.isfile('./img/songs/'+str(id)+'.png'):
                        # 歌被删了
                        continue
                    level = song[4]
                    title = song[2]
                    score = 0
                    for df_row in df.itertuples():
                        if getattr(df_row, 'song_name') == title and difficulty[getattr(df_row, 'level_index')] == song[3]:
                            score = getattr(df_row, 'score')
                            break
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
                    song_img = Image.open('./img/songs/' + str(song[1]) + '.png').convert('RGBA')
                    song_img = song_img.resize((150, 150))
                    if di != 'mas':
                        x -= 8
                        y -= 8
                        song_img = ImageOps.expand(song_img, border=(8, 8, 8, 8), fill=color)

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


    return img


img = Image.open('./img/bg.png').convert('RGBA').resize((2200, height))
img = draw_leveltittle(img)
logo = Image.open('./img/chusan2026.png')
font_size = 60
setFont5 = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', 120)
setFont6 = ImageFont.truetype('C:/windows/fonts/SimHei.ttf', font_size)
if source == 1:
    text1 = 'Data is from Diving-fish'
else :
    text1 = 'Data is from lxns.net'
ImageDraw.Draw(img).text((1400, height - 170), text1, font=setFont6, fill=(195, 33, 54), stroke_fill='white',
                         stroke_width=2)
ImageDraw.Draw(img).text((1520, height - 100), lofk, font=setFont6, fill=(195, 33, 54), stroke_fill='white',
                         stroke_width=2)
ImageDraw.Draw(img).text((200, 140), player_text, font=setFont5, fill=(197, 83, 98), stroke_fill='white',
                         stroke_width=6)
img.paste(logo, (1700, 0), mask=logo)

print(' 正在绘制图标')

img = draw_chart(img)
if os.path.exists('./output') is False:
    os.makedirs('./output')
if if_generated:
    img.save('./output/chulevel_chart_' + levels[srg] + '.png')

compress_rate = 0.38

w, h = img.size
img = img.resize((int(w * compress_rate), int(h * compress_rate)))
img.save('./output/chulevel_chart_' + levels[srg] + '_compressed.png')

print(' 已输出至 output/chulevel_chart_' + levels[srg] + '')
print(' 绘制完成，感谢使用~')
