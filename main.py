import pyxel

Y_ALIGN = 20
MAP_SIZE_X, MAP_SIZE_Y = 15, 11
MAP_LIST = [
    [0, 0], # 初期
    [0, 1],
    [1, 0]  # 洞窟
]
MOVABLE_CHARA = ((0,0),(1,0),
                 (0,28)) # CAVE_CHARA
CAVE_CHARA = ((0,28),)
MP_NONE, MP_OBST = 0, 1
TILE_MAP = 0
TILE_UNIT = 16
WALL_TILE_Y = 30
DOWN, UP, LEFT, RIGHT = 0, 1, 2, 3 # Direction
MP_NONE = 0
RET_NONE, RET_KILLED, RET_ATTACK, RET_CAVEIN, RET_MOVED, RET_CAVEOUT, RET_GETITEM = 0, 1, 2, 3, 4, 5, 6
SC_OPENING, SC_GAMEOVER, SC_RETRYMENU, SC_SCROLL, SC_CAVEIN, SC_CAVEOUT, SC_CAVE_GETITEM, SC_OVERWORLD = 1,2,3,4,5,6,7,8
ST_NONE, ST_INIT, ST_UPROCK, ST_LEFTROCK, ST_RIGHTROCK, ST_END = 0,1,2,3,4,5
FIRST_MAP, CAVE_GETITEM_MAP = 0, 1
CENTER_X, CENTER_Y = 16*7, 16*5
# Object
O_FLAME, O_OLDMAN1, O_OLDMAN2, O_OLDWOMAN, O_MOBLIN, O_MERCHANT = 801,802,803,804,805,806
PERSON_X, PERSON_Y = 7, 4
I_NONE, W_SWORD = 0,1
NEWITEM_X1, NEWITEM_X2, NEWITEM_X3, NEWITEM_Y = 16*5, 16*7, 16*9, 16*6
M_TREASURE, M__SEACRET = 100, 101

class Player:
    dmg_x, dmg_y, dmg_w, dmg_h, dmg_dir, atk_posture_cnt = 0, 0, 0, 0, DOWN, 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.direction = DOWN
        self.speed = 2
        self.hp = 3
        self.damage_count = 0
        self.move_pattern = 0
        self.walk_count = 0
        self.cavein_count = 0
        self.caveout_count = 0
        self.getitem_count = 0
        self.weapon = I_NONE  # Add weapon attribute

    def update(self):
        ret = RET_NONE

        if Player.atk_posture_cnt:  # 攻撃中
            Player.atk_posture_cnt -= 1

        if Player.atk_posture_cnt:  # 攻撃中
            pass
        elif self.getitem_count:  # アイテム取得中
            self.getitem_count -= 1
            if self.getitem_count == 1:
                self.weapon = W_SWORD  # Set weapon when getting sword
        else:
            if pyxel.btn(pyxel.KEY_DOWN):
                self.direction = DOWN
                ret, self.x, self.y = self.playermove(self.x, self.y, DOWN)
            elif pyxel.btn(pyxel.KEY_UP):
                self.direction = UP
                ret, self.x, self.y = self.playermove(self.x, self.y, UP)
            elif pyxel.btn(pyxel.KEY_LEFT):
                self.direction = LEFT
                ret, self.x, self.y = self.playermove(self.x, self.y, LEFT)
            elif pyxel.btn(pyxel.KEY_RIGHT):
                self.direction = RIGHT
                ret, self.x, self.y = self.playermove(self.x, self.y, RIGHT)

            if ret==RET_MOVED:
                self.walk_count += 1

            if self.damage_count:  # 攻撃を受けている
                self.damage_count -= 1
            
            if self.x==Map.cave_x*16 and self.y==Map.cave_y*16:
                ret = RET_CAVEIN
                self.cavein_count = 16
            elif Map.now_map==CAVE_GETITEM_MAP:
                finproc = False
                if Map.thismap_item==W_SWORD:
                    if self.x==NEWITEM_X2 and self.y==NEWITEM_Y:
                        finproc = True

                if finproc:
                    ret = RET_GETITEM
                    Map.thismap_item = 0
                    self.getitem_count = 50

        self.set_dmg_range(self.x, self.y)
        return ret

    def playermove(self, x, y, dirc, dmg=False, dst=2):
        ix, iy = x, y
        if dirc == UP:
            if y - dst >= 0 and Map.zmap[x // 16][(y - dst) // 16] == MP_NONE:
                y -= dst
                return RET_MOVED, x, y
        elif dirc == DOWN:
            if y + dst >= (MAP_SIZE_Y-1) * 16:
                if Map.now_map in (CAVE_GETITEM_MAP,):
                    Map.caveout()
                    self.caveout_count = 16
                    return RET_CAVEOUT, Map.cave_x * 16, Map.cave_y * 16 + 16

            if y + dst < (MAP_SIZE_Y - 1) * 16 and Map.zmap[x // 16][(y + 16 + dst) // 16] == MP_NONE:
                y += dst
                return RET_MOVED, x, y
        elif dirc == LEFT:
            if x - dst >= 0 and Map.zmap[(x - dst) // 16][y // 16] == MP_NONE:
                x -= dst
                return RET_MOVED, x, y
        elif dirc == RIGHT:
            if x + dst <= (MAP_SIZE_X - 1) * 16 and Map.zmap[(x + 8 + dst) // 16][y // 16] == MP_NONE:
                x += dst
                return RET_MOVED, x, y
        return RET_NONE, ix, iy

    def draw(self):
        if self.damage_count // 2 % 2:
            pass
        elif self.cavein_count:
            Draw.player(self.x, self.y+(16-self.cavein_count), self.direction, self.cavein_count//2%2, h=16-(16-self.cavein_count)-1)
        elif self.caveout_count:
            Draw.player(self.x, self.y-self.caveout_count, DOWN, self.caveout_count//2%2)
        elif self.getitem_count:
            Draw.item(self.x, self.y-16, W_SWORD)
            Draw.player(self.x, self.y, self.direction, item=True)
        else:
            self.move_pattern = self.walk_count % 2
            Draw.player(self.x, self.y, self.direction, self.move_pattern, swd=Player.atk_posture_cnt)

    # ルピーとの当たり判定を確認
    def is_collision_with_rupee(self, rupee):
        if abs(self.x - rupee.x) < self.width and abs(self.y - rupee.y) < self.height:
            return True
        return False

    @classmethod
    def hit(cls, x, y, w, h):
        return Player.dmg_x-w<x<Player.dmg_x+Player.dmg_w and Player.dmg_y-h<y<Player.dmg_y+Player.dmg_h

    def set_dmg_range(self, x, y):
        Player.dmg_x, Player.dmg_y, Player.dmg_w, Player.dmg_h = x+2, y+2, 12, 12
    
    def updown_hp(self, pt):
        self.hp += pt

        return True

    def cavein(self):
        self.cavein_count -= 1

        if self.cavein_count == 0:
            Map.cavein()
            self.x, self.y = CENTER_X, (MAP_SIZE_Y-1)*16
            return True
        
        return False

    def caveout(self):
        self.caveout_count -= 1
        if self.caveout_count == 0:
            return True

        return False

class Sword:
    atk_x, atk_y, atk_w, atk_h, atk_dir, atk_dmg = 0, 0, 7, 16, 0, 0

    def __init__(self, x, y, dirc):
        self.x, self.y = x, y
        self.dirc = dirc
        Sword.atk_dmg = 1
        self.cnt = 8
        Player.atk_posture_cnt = 8
        self.set_attack_range()

    @classmethod
    def hit(cls, x, y, w, h):
        if Sword.atk_x-w<x<Sword.atk_x+Sword.atk_w and Sword.atk_y-h<y<Sword.atk_y+Sword.atk_h:
            return True
        return False

    def set_attack_range(self, x=0, y=0, w=0, h=0, dirc=0):
        Sword.atk_x, Sword.atk_y, Sword.atk_w, Sword.atk_h, Sword.atk_dir = x, y, w, h, dirc

    def update(self):
        self.cnt -= 1

        if self.cnt < 0:
            return False

        if self.cnt==0:
            self.set_attack_range()

        if self.dirc==UP:
            self.set_attack_range(self.x+3, self.y-12, 7, 12, self.dirc)
        elif self.dirc==DOWN:
            self.set_attack_range(self.x+5, self.y+16, 7, 12, self.dirc)
        elif self.dirc==LEFT:
            self.set_attack_range(self.x-12, self.y+6, 12, 7, self.dirc)
        elif self.dirc==RIGHT:
            self.set_attack_range(self.x+16, self.y+6, 12, 7, self.dirc)

        return True

    def draw(self, player_x, player_y, player_dirc):
        Draw.sword(player_x, player_y, player_dirc)

class Map:
    scroll_dir = None
    scroll_count = 0
    scroll_from = None
    scroll_to = None
    
    @classmethod
    def setmap(cls, init=False):
        if init:
            cls.now_map = FIRST_MAP
        cls.thismap_item = 0

        cls.cave_x, cls.cave_y = -1, -1
        Map.zmap = [[MP_NONE]*MAP_SIZE_Y for i in range(MAP_SIZE_X)]

        # 洞窟の位置や障害物の設定
        for x in range(MAP_SIZE_X):
            for y in range(MAP_SIZE_Y):
                tile_map = pyxel.tilemaps[TILE_MAP].pget(MAP_LIST[cls.now_map][0]*32+x*2, MAP_LIST[cls.now_map][1]*24+y*2)

                if tile_map in MOVABLE_CHARA:
                    # 洞窟の入り口
                    if tile_map in CAVE_CHARA:
                        cls.cave_x, cls.cave_y = x, y
                else:
                    # 障害物の設定
                    Map.zmap[x][y] = MP_OBST

    @classmethod
    def setscroll(cls, direction, from_map, to_map):
        cls.scroll_dir = direction
        cls.scroll_count = 16 * 16  # Full screen scroll
        cls.scroll_from = from_map
        cls.scroll_to = to_map
    
    @classmethod
    def scrolling(cls):
        cls.scroll_count -= 8  # Scroll speed
        
        if cls.scroll_count <= 0:
            cls.now_map = cls.scroll_to
            cls.setmap()
            cls.scroll_dir = None
            return True
        
        return False

    @classmethod
    def draw(cls):
        pyxel.bltm(0, Y_ALIGN, 0, MAP_LIST[cls.now_map][0]*16*16, MAP_LIST[cls.now_map][1]*12*16, 16*16, 11*16)
    
    @classmethod
    def draw_scroll(cls):
        if cls.scroll_dir == RIGHT:
            # Current map scrolling left
            pyxel.bltm(-cls.scroll_count, Y_ALIGN, 0, 
                       MAP_LIST[cls.scroll_from][0]*16*16, 
                       MAP_LIST[cls.scroll_from][1]*12*16, 
                       16*16, 11*16)
            # Next map scrolling in from right
            pyxel.bltm(16*16 - cls.scroll_count, Y_ALIGN, 0, 
                      MAP_LIST[cls.scroll_to][0]*16*16, 
                      MAP_LIST[cls.scroll_to][1]*12*16, 
                      16*16, 11*16)
        elif cls.scroll_dir == LEFT:
            # Current map scrolling right
            pyxel.bltm(-cls.scroll_count, Y_ALIGN, 0, 
                        MAP_LIST[cls.scroll_from][0]*16*16, 
                        MAP_LIST[cls.scroll_from][1]*12*16, 
                        16*16, 11*16)
            # Next map scrolling in from left (移動方向を修正)
            pyxel.bltm(16*16 -cls.scroll_count, Y_ALIGN, 0, 
                        MAP_LIST[cls.scroll_to][0]*16*16, 
                        MAP_LIST[cls.scroll_to][1]*12*16, 
                        16*16, 11*16)
        elif cls.scroll_dir == UP:
            # Current map scrolling down
            pyxel.bltm(0, Y_ALIGN + cls.scroll_count, 0, 
                       MAP_LIST[cls.scroll_from][0]*16*16, 
                       MAP_LIST[cls.scroll_from][1]*12*16, 
                       16*16, 11*16)
            # Next map scrolling in from top
            pyxel.bltm(0, Y_ALIGN + cls.scroll_count - 11*16, 0, 
                      MAP_LIST[cls.scroll_to][0]*16*16, 
                      MAP_LIST[cls.scroll_to][1]*12*16, 
                      16*16, 11*16)
        elif cls.scroll_dir == DOWN:
            # Current map scrolling up
            pyxel.bltm(0, Y_ALIGN - cls.scroll_count, 0, 
                       MAP_LIST[cls.scroll_from][0]*16*16, 
                       MAP_LIST[cls.scroll_from][1]*12*16, 
                       16*16, 11*16)
            # Next map scrolling in from bottom
            pyxel.bltm(0, Y_ALIGN - cls.scroll_count + 11*16, 0, 
                      MAP_LIST[cls.scroll_to][0]*16*16, 
                      MAP_LIST[cls.scroll_to][1]*12*16, 
                      16*16, 11*16)
    
    @classmethod
    def get_tile(self, x, y):
        return pyxel.tilemaps[TILE_MAP].pget(x, y)

    @classmethod
    def cavein(cls):
        cls.now_map = CAVE_GETITEM_MAP
        cls.setmap()
    
    @classmethod
    def caveout(cls):
        cls.now_map = FIRST_MAP
        cls.setmap()

class Rupee:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.count = 160

    def update(self):
        self.count -= 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, TILE_UNIT + 8*(self.count//4%2), TILE_UNIT*3, 8, 16, 0)

class Object:
    def __init__(self, x, y, hp, obj):
        self.x = x
        self.y = y
        self.hp = hp
        self.obj = obj
        self.count = 0
    
    def update(self):
        self.count += 1

    def draw(self):
        if self.obj == O_FLAME:
            Draw.flame(self.x, self.y, self.count//4%2)
        elif self.obj == O_OLDMAN1:
            Draw.oldman1(self.x, self.y)

class EnemyDamage:
    def damage(self, x, y, w, h):
        if Sword.hit(x, y, w, h):
            return 1

class BaseEnemy(EnemyDamage):
    def __init__(self, x, y, hp=1):
        self.x, self.y = x, y
        self.hp = hp
        self.direction = pyxel.rndi(UP,RIGHT)
        self.walk_count = 0
        self.damage_count = 0

    def update(self):
        self.walk_count += 1

        if self.damage_count:
            self.damage_count -= 1

            if self.damage_count==0 and self.hp<=0:
                return RET_KILLED

            return RET_NONE

        dmg_point = self.damage(self.x, self.y, 16, 16)
        if dmg_point:
            self.damage_count = 16
            self.hp -= dmg_point
            return RET_NONE

        if Player.hit(self.x, self.y, 16, 16):
            return RET_ATTACK

        return RET_NONE

    def draw(self):
        if self.damage_count and self.hp<=0:
            Draw.flash(self.x, self.y, self.damage_count)
        else:
            self.draw_enemy(self.x, self.y, self.direction, self.walk_count//4%2)

class Octorok(BaseEnemy):
    def draw_enemy(self, x, y, direction, move_pattern):
        Draw.octorok(x, y, direction, move_pattern)

class Draw:
    @classmethod
    def octorok(cls, x, y, dirc, ptn):
        if dirc==UP:
            pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*2, 16, 16, 0)
        elif dirc==DOWN:
            pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*2, 16, 16, 0)
        elif dirc==LEFT:
            pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*2, 16, 16, 0)
        elif dirc==RIGHT:
            pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*2, 16, 16, 0)

    @classmethod
    def flash(cls, x, y, count):
        if count > 12:
            pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT, TILE_UNIT*0, 16, 16, 0)
        elif count > 8:
            pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*2, TILE_UNIT*0, 16, 16, 0)
        elif count > 2:
            pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*3, TILE_UNIT*0, 16, 16, 0)

    @classmethod
    def sword(cls, x, y, direction):
        if direction == UP:
            pyxel.blt(x + 5, y - 12 + Y_ALIGN, 0, TILE_UNIT*1, TILE_UNIT*4, 7, 16, 0)
        elif direction == DOWN:
            pyxel.blt(x + 5, y + 12 + Y_ALIGN, 0, TILE_UNIT*1, TILE_UNIT*4, 7, -16, 0)
        elif direction == LEFT:
            pyxel.blt(x - 11, y + 6 + Y_ALIGN, 0, TILE_UNIT*0, TILE_UNIT*4, -16, 7, 0)
        elif direction == RIGHT:
            pyxel.blt(x + 10, y + 6 + Y_ALIGN, 0, TILE_UNIT*0, TILE_UNIT*4, 16, 7, 0)

    @classmethod
    def player(cls, x, y, direction, move_pattern=0, swd=0, h=16, item=False):
        if item:
            pyxel.blt(x, y+Y_ALIGN, 0, 16*8, 16, 16, 16, 0)
            return

        if direction == UP:
            if swd:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*7, TILE_UNIT, 16, TILE_UNIT, 0)
            else:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*4, TILE_UNIT, 16 if move_pattern else -16, h, 0)
        elif direction == DOWN:
            if swd:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*5, TILE_UNIT, 16, TILE_UNIT, 0)
            else:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*move_pattern, TILE_UNIT, TILE_UNIT, h, 0)
        elif direction == LEFT:
            if swd:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*6, TILE_UNIT, -16, TILE_UNIT, 0)
            else:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*2+TILE_UNIT*move_pattern, TILE_UNIT, -16, TILE_UNIT, 0)
        elif direction == RIGHT:
            if swd:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*6, TILE_UNIT, 16, TILE_UNIT, 0)
            else:
                pyxel.blt(x, y+Y_ALIGN, 0, TILE_UNIT*2+TILE_UNIT*move_pattern, TILE_UNIT, 16, h, 0)

    @classmethod
    def flame(cls, x, y, ptn):
        pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*5, 16 if ptn else -16, 16, 0)
    
    @classmethod
    def oldman1(cls, x, y):
        pyxel.blt(x, y+Y_ALIGN, 0, 0, TILE_UNIT*6, 16, 16, 1)
    
    @classmethod
    def item(cls, x, y, item):
        if item == W_SWORD:
            pyxel.blt(x, y+Y_ALIGN, 0, 16, TILE_UNIT*4, 8, 16, 1)
    
    @classmethod
    def ownheart(cls, hp):
        for i in range(hp):
            pyxel.blt(i * 8, 0, 0, 0, TILE_UNIT * 3 + 8, 8, 8, 0)
    
    @classmethod
    def ownweapon(cls, weapon):
        if weapon == W_SWORD:
            pyxel.blt(32, 1, 0, 16, TILE_UNIT*4, 8, 16, 1, 0, 0.9)

class App:
    def __init__(self):
        map_x = TILE_UNIT*MAP_SIZE_X
        map_y = TILE_UNIT*MAP_SIZE_Y + Y_ALIGN
        pyxel.init(map_x, map_y, title="Zelda-like Game")
        pyxel.load("assets/resource.pyxres")

        # ゲームオブジェクトの初期化
        Map.setmap(init=True)
        self.player = Player(80, 60)

        self.scene = SC_OVERWORLD
        self.sword = None
        self.enemies = []  # 敵を管理するリスト
        self.rupees = []  # ルピーを管理するリスト
        self.flame = []
        self.person = []
        self.status = ST_INIT

        self.nowmap_enemy = None

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # シーンの設定
        if self.scene == SC_SCROLL:
            # Handle map scrolling
            if Map.scrolling():
                self.scene = SC_OVERWORLD
            return
        elif self.scene == SC_CAVEIN:
            if self.player.cavein():
                if Map.now_map==CAVE_GETITEM_MAP:
                    self.scene = SC_CAVE_GETITEM
            return
        elif self.scene == SC_CAVEOUT:
            if self.player.caveout():
                self.scene = SC_OVERWORLD
            return
        elif self.scene == SC_CAVE_GETITEM:
            if self.status == ST_INIT:
                self.flame = []  # 炎
                self.flame.append(Object(16*4, 16*4, 100, O_FLAME))
                self.flame.append(Object(16*10, 16*4, 100, O_FLAME))

                self.person = []
                self.person.append(Object(PERSON_X*16, PERSON_Y*16, 100, O_OLDMAN1))
                Map.zmap[PERSON_X][PERSON_Y] = MP_OBST

                Map.thismap_item = W_SWORD

                self.status = ST_NONE
            elif self.status == ST_NONE:
                for i in reversed(range(len(self.flame))):
                    self.flame[i].update()
                for i in reversed(range(len(self.person))):
                    self.person[i].update()

        elif self.scene == SC_OVERWORLD:
            # Check for map edge transitions
            if self.player.x <= 0:  # Left edge
                print(self.player.x, "test")
                next_map = self.get_adjacent_map(LEFT)
                if next_map is not None:
                    Map.setscroll(LEFT, Map.now_map, next_map)
                    self.player.x = (MAP_SIZE_X - 1) * 16  # Move to right edge of new map
                    self.scene = SC_SCROLL
                    return
            elif self.player.x >= (MAP_SIZE_X - 1) * 16:  # Right edge
                next_map = self.get_adjacent_map(RIGHT)
                if next_map is not None:
                    Map.setscroll(RIGHT, Map.now_map, next_map)
                    self.player.x = 0  # Move to left edge of new map
                    self.scene = SC_SCROLL
                    return
            elif self.player.y <= 0:  # Top edge
                next_map = self.get_adjacent_map(UP)
                if next_map is not None:
                    Map.setscroll(UP, Map.now_map, next_map)
                    self.player.y = (MAP_SIZE_Y - 2) * 16  # Move to bottom edge of new map
                    self.scene = SC_SCROLL
                    return
            elif self.player.y >= (MAP_SIZE_Y - 1) * 16:  # Bottom edge
                next_map = self.get_adjacent_map(DOWN)
                if next_map is not None:
                    Map.setscroll(DOWN, Map.now_map, next_map)
                    self.player.y = 0  # Move to top edge of new map
                    self.scene = SC_SCROLL
                    return

        # プレイヤーの更新
        ret = self.player.update()

        if ret==RET_CAVEIN:
            self.scene = SC_CAVEIN
            return
        elif ret==RET_CAVEOUT:
            self.scene = SC_CAVEOUT
            return
        elif ret==RET_GETITEM:
            self.bgm(M_TREASURE)
            return

        for i in reversed(range(len(self.enemies))): # 敵
            ret = self.enemies[i].update()

            if ret == RET_KILLED:
                self.rupees.append(Rupee(self.enemies[i].x, self.enemies[i].y))

                del self.enemies[i]
            elif ret == RET_ATTACK and self.player.damage_count == 0:
                self.player_damaged()

        # ルピーの更新
        for rupee in self.rupees:
            rupee.update()

        # プレイヤーとルピーの当たり判定を確認
        for rupees in self.rupees:
            if self.player.is_collision_with_rupee(rupees):
                self.rupees.remove(rupees)

        self.handle_command()

        if self.sword is not None:
            ret = self.sword.update()

            if not ret:
                self.sword = None
    
    def get_adjacent_map(self, direction):
        # マップ接続情報の定義: [現在のマップID, 方向] -> 接続先マップID
        map_connections = {
            (FIRST_MAP, LEFT): 1,
            (FIRST_MAP, RIGHT): 1,    # 右にマップID 1を接続
            (FIRST_MAP, UP): None,    # 上には接続なし
            (FIRST_MAP, DOWN): None,  # 下には接続なし
            
            (1, LEFT): 1,     # 左にはマップID 0 (FIRST_MAP)を接続
            (1, RIGHT): None,         # 右には接続なし
            (1, UP): None,            # 上には接続なし
            (1, DOWN): None,          # 下には接続なし
        }
        
        # 現在のマップと方向の組み合わせから接続先を取得
        connection_key = (Map.now_map, direction)
        if connection_key in map_connections:
            return map_connections[connection_key]
        
        return None

    def handle_command(self):
        if pyxel.btn(pyxel.KEY_Z):
            if self.sword is None:
                self.sword = Sword(self.player.x, self.player.y, self.player.direction)
    
    def player_damaged(self, pt=1):
        self.player.damage_count = 80
        self.player.updown_hp(-pt)

    def draw(self):
        pyxel.cls(0)

        # マップの描画
        if self.scene == SC_SCROLL:
            Map.draw_scroll()
        else:
            Map.draw()

        # HPの表示
        Draw.ownheart(self.player.hp)

        pyxel.rectb(28, 0, 15, 18, 1)
        pyxel.text(27, 7, "Z", 7)
        if self.player.weapon != I_NONE:
            Draw.ownweapon(self.player.weapon)

        if self.sword is not None:
            self.sword.draw(self.player.x, self.player.y, self.player.direction)  # ソード

        if self.scene == SC_CAVE_GETITEM:
            for i in reversed(range(len(self.flame))):
                self.flame[i].draw()
            for i in reversed(range(len(self.person))):
                self.person[i].draw()

            if Map.thismap_item == W_SWORD:
                Draw.item(NEWITEM_X2+4, NEWITEM_Y, W_SWORD)

        for e in self.enemies:
            e.draw()

        # ルピーの描画
        for rupee in self.rupees:
            rupee.draw()
    
        # プレイヤーの描画
        self.player.draw()
    
    def bgm(self, scene=0):
        if scene == M_TREASURE:
            pyxel.playm(1, loop=False)
        elif scene == M__SEACRET:
            pyxel.playm(2, loop=False)
        else:
            pyxel.stop()

App()