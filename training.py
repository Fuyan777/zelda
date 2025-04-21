import pyxel
import random

class App:
    def __init__(self):
        pyxel.init(160, 120, title="四角形の移動")
        # 四角形の初期位置
        self.x = 60
        self.y = 40
        # 四角形のサイズ
        self.width = 16
        self.height = 16
        # 剣の状態
        self.sword_active = False
        self.sword_timer = 0
        self.sword_duration = 10  # 剣を出している時間（フレーム数）

        # 敵の情報（位置とサイズ）
        self.enemies = []
        for _ in range(3):  # 3匹の敵を生成
            self.enemies.append({
                'x': random.randint(0, pyxel.width - 16),
                'y': random.randint(0, pyxel.height - 16),
                'width': 16,
                'height': 16,
                'alive': True
            })

        pyxel.run(self.update, self.draw)

    # 毎フレーム実行される
    def update(self):
        # 移動処理
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 1
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 1

        # スクリーンの端を超えないようにする
        self.x = max(0, min(self.x, pyxel.width - self.width))
        self.y = max(0, min(self.y, pyxel.height - self.height))
        
        # 剣を出す処理
        if pyxel.btnp(pyxel.KEY_Z) and not self.sword_active:
            self.sword_active = True
            self.sword_timer = self.sword_duration
        
        # 剣のタイマー処理
        if self.sword_active:
            self.sword_timer -= 1
            if self.sword_timer <= 0:
                self.sword_active = False
        
        # 敵との衝突判定
        self.check_enemy_collision()
        
    # 毎フレーム実行される
    def draw(self):
        pyxel.cls(0)
        # 四角形を描画
        pyxel.rect(self.x, self.y, self.width, self.height, 11)  # 11は水色
        
        # 敵を描画
        for enemy in self.enemies:
            if enemy['alive']:
                pyxel.rect(enemy['x'], enemy['y'], enemy['width'], enemy['height'], 8)  # 8は赤色

        # 剣を描画
        if self.sword_active:
            # 常に左向きの剣を表示
            pyxel.rect(self.x - 16, self.y + self.height // 2 - 2, 16, 4, 7)  # 7は白色

    # 敵との衝突判定
    def check_enemy_collision(self):
        # 剣が出ている場合のみ判定
        if self.sword_active:
            sword_x = self.x - 16
            sword_y = self.y + self.height // 2 - 2
            sword_width = 16
            sword_height = 4

            for enemy in self.enemies:
                if enemy['alive']:
                    # 剣と敵の矩形が重なっているか判定
                    if (sword_x < enemy['x'] + enemy['width'] and
                        sword_x + sword_width > enemy['x'] and
                        sword_y < enemy['y'] + enemy['height'] and
                        sword_y + sword_height > enemy['y']):
                        # 敵を倒した
                        enemy['alive'] = False

App()