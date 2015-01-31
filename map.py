#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser
import os,sys,time, csv, operator

scriptpath = os.path.join(os.getcwd(),os.path.dirname(sys.argv[0]));

config = ConfigParser()
config.read(os.path.join(scriptpath,'map.conf'))
path_to_db = os.path.expanduser(config['DEFAULT']['PathToIRPGDB'])
pixel_width = int(config['DEFAULT']['PixelWidth'])
font_path = os.path.join(scriptpath,config['DEFAULT']['Font'])
img_scale = int(config['DEFAULT']['ImageScale'])

csv.register_dialect('irpg', delimiter='\t', quoting=csv.QUOTE_NONE)


class Player:
    
    def __init__(self,data):
        self.name = data["# username"]
        self.history = []
        self.processData(data)

    def processData(self,data):
        assert(self.name== data["# username"])

        true_X = img_scale*int(data["x pos"])
        self.true_X = true_X-img_scale*10 if true_X > img_scale*(500-10) else true_X+5

        true_Y = img_scale*int(data["y pos"])
        self.true_Y = true_Y-img_scale*20 if true_Y > img_scale*(500-20) else true_Y+5

        self.weapon = data["weapon"]
        self.level = data["level"]
        self.online = data["online"] != '0'
        self.history += [(self.true_X,self.true_Y)]

    def pixel(self):
        return (self.true_X-pixel_width,self.true_Y-pixel_width,
                self.true_X+pixel_width,self.true_Y+pixel_width)
        
players = dict()

def read_data(path):

        csvfile = open(path,'r')
        return csv.DictReader(csvfile, dialect='irpg')

def create_image(data):
        global pixel_width

        myim = Image.new("RGB", (500*img_scale,500*img_scale), (255,255,255))
        draw = ImageDraw.Draw(myim)
        font = ImageFont.truetype(font_path, int(config['DEFAULT']['FontSize']))

        for p in data:
            try:
                players[p["# username"]].processData(p)
            except:
                players[p["# username"]] = Player(p)

            player = players[p["# username"]]
            color = (0,0,0)

            if not player.online:
                color = (120,0,0)

            myim.paste(color, player.pixel())
            description = [player.name, "level: " + player.level]
            y = 0

            if config['DEFAULT']['EnableText'] == '1':
                for line in description:
                    draw.text((player.true_X, player.true_Y+y), line, fill=color, font=font)
                    y = y + 12

            color = (0,128,0)
            colorInc = int(255/int(config['DEFAULT']['TailHistory']))
            curPos = (player.true_X,player.true_Y)
            for pos in reversed(player.history):
                if (max(abs(curPos[0]-pos[0]),abs(curPos[1]-pos[1])) > int(config['DEFAULT']['UpdateInterval'])*2):
                    continue
                draw.line([curPos,pos],fill=color,width=2)
                curPos = pos
                color = (color[0]+colorInc,color[1]+int(colorInc/2),color[2]+colorInc)

        #myim.show()
        myim.save(os.path.join(os.path.expanduser(config['DEFAULT']['MapPath']),"map.png"))

while True:
    create_image(read_data(path_to_db))
    time.sleep(int(config['DEFAULT']['UpdateInterval']))

