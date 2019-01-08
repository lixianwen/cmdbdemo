# !/usr/bin/env python
# coding:utf8

import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

class VeifyCode(object):
    def __init__(self):
        self.drawline = True                                  #默认加入干扰线
        self.fontpath = '/usr/share/fonts/lyx/arial.ttf'        #字体位置，不同版本的系统可能路径有所不同
        self.number = 4                                       #生成多少位的验证码
        self.size = (100, 30)                                  #生成验证码图片的高度和宽度
        self.bgcolor = (255, 255, 255)                        #背景颜色，默认白色
        self.linenumber = 20                                  #加入干扰线的条数

# 用来随机生成一个字符串
    def getText(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, self.number))

#随机生成颜色
    def getRandomColor(self):
        return random.randint(0, 245), random.randint(0, 245), random.randint(0, 245),

# 用来绘制干扰线
    def drawInterferentLine(self, draw, width, height):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill=self.getRandomColor(), width=1)

# 生成验证码
    def getImage(self):
        width, height = self.size
        image = Image.new('RGBA', (width, height), self.bgcolor)  # 创建图片
        font = ImageFont.truetype(self.fontpath, 25)         # 验证码的字体
        draw = ImageDraw.Draw(image)                         # 创建画笔
        text = self.getText()                                # 生成字符串
        font_width, font_height = font.getsize(text)
        draw.text(((width - font_width) / self.number, (height - font_height) / self.number), text, font=font,
                  fill=self.getRandomColor())                            # 填充字符串
        if self.drawline:
            for i in range(self.linenumber):
                self.drawInterferentLine(draw, width, height)

        # 创建扭曲
        # image = image.transform((width + 20, height + 10), Image.AFFINE, (1, -0.3, 0, -0.1, 1, 0), Image.BILINEAR)
        # 滤镜，边境加强
        # image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        # image.save('verifycode.png')  # 保存验证码图片
        buf = BytesIO()
        image.save(buf, 'png', quality=70)
        buf_str = buf.getvalue()
        buf.close()
        return text.lower(), buf_str
