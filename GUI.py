import sys, pygame

class GUI:

    class GemInfo:
        def __init__(self,name,color,image):
            self.name = name
            self.color = color
            self.image = image
            self.textcolor = pygame.Color("Black" if name !="Onyx" else "White")

        def img(self):
            return pygame.image.load("assets/"+self.image+".png")

    def __init__(self):
        pygame.init()
        self.SIZE = 1500, 800
        self.SCREEN = pygame.display.set_mode(self.SIZE)
        self.CONST = {
            "basicColor" : pygame.Color("Grey"),
            "secondColor" : pygame.Color("Light Grey"),
            "warningColor" : pygame.Color("Red"),
            "arial20" : pygame.font.Font(pygame.font.match_font("arial"),20),
            "arial42" : pygame.font.Font(pygame.font.match_font("arial"),42)
        }
        self.GemsInfo = [
            GUI.GemInfo("Saphir",pygame.Color("Blue"),"sphir"),
            GUI.GemInfo("Emeraude",pygame.Color("Green"),"emeraude"),
            GUI.GemInfo("Rubis",pygame.Color("Red"),"rubis"),
            GUI.GemInfo("Diamant",pygame.Color("White"),"diamant"),
            GUI.GemInfo("Onyx",pygame.Color("Black"),"onyx"),
            GUI.GemInfo("Or",pygame.Color("Yellow"),"or")
        ]

    def drawCard(self,i,v=[0,0,0,0,0], points = 0, rect=pygame.Rect(0,0,160,140), selected=0, where=None):
        if(where==None):
            where=self.SCREEN
        points = 2 #TODO

        gem = self.GemsInfo[i]
        color = gem.color
        pygame.draw.rect(where,color,rect)
        pygame.draw.rect(where,self.CONST["basicColor"] if selected == 0 else self.CONST["warningColor"],rect,2)

        if(points!=0):
            text = self.CONST["arial42"].render(str(points), True, gem.textcolor)
            where.blit(text,(rect.x+8,rect.y+4))

        w = rect.w/6
        h = rect.h/6
        for k in range(0,5):
            gem = self.GemsInfo[k]

            vrect = pygame.Rect(rect.x + (k + 0.5)*w + 2*(k - 2), rect.bottom - h - 4,w,h)
            pygame.draw.rect(where,gem.color,vrect)
            pygame.draw.rect(where,self.CONST["basicColor"],vrect,2)

            text = self.CONST["arial20"].render(str(v[k]), True, gem.textcolor)
            where.blit(text,(vrect.x+4,vrect.y+2))

    def drawCardPack(self,left=0, rect=pygame.Rect(0,0,160,140), where=None):
        if(where==None):
            where=self.SCREEN
        if left==0:
            return

        color = pygame.Color("Dark Grey")
        pygame.draw.rect(where,color,rect)
        pygame.draw.rect(where,self.CONST["basicColor"],rect,2)

        text = self.CONST["arial42"].render(str(left), True, self.CONST["secondColor"])
        where.blit(text,(rect.x + rect.w/2-8,rect.y + rect.h/2 - 21))

    def mineCardPos(x,y):
        return pygame.Rect(1500 - (5-x)*170 , (1+y)*150,160,140)

    def test_draw(self):
        self.SCREEN.fill(self.CONST["secondColor"])

        for x in range(0,5):
            for y in range(0,3):
                if(x<=3):
                    self.drawCard((x+3*y)%5,v=[0,0,0,0,0], points = 0, rect=GUI.mineCardPos(x,y), selected=0)
                else:
                    self.drawCardPack(left=5, rect=GUI.mineCardPos(4,y))

        pygame.display.flip()

    def test(self,t):
        self.SCREEN.fill(self.CONST["secondColor"])
        text = self.CONST["arial42"].render(str(t), True, self.CONST["basicColor"])
        self.SCREEN.blit(text,(0,0))
        pygame.display.flip()

class ConsoleInterpreter:
    '''
    <action> is a dict with two keys :
    - type : a string among <game.POSSIBLE_ACTIONS>
    - params : the parameters of the action. Its format depends on the type.
        - take_3 : list/iterable of three color names : [<color_1>, <color_2>, <color_3>]
        - take_2 : string, color name
        - reserve : origin and coordinate of the card
            - ['from_table', (i, j)]
            - ['from_deck', i]
        - purchase : origin and coordinate of the card
            - ['from_table', (i, j)]
            - ['from_hand', i]
    '''
    def __init__(self):

    def setup(self,state,player):
        self.possible = state.get_possible_actions(player)

    def valid(self,action):
        return (action in self.possible)

    def command_to_action(self,command):
        words = command.split(' ')
        actionType = words[0]
        if(actionType in ("take_3","take3","t3")):
            action = commandT




gui = GUI()
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    gui.test(input("This is a test"))
    #gui.test_draw()



