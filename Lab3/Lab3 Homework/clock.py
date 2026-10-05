import sys
import os
from time import sleep, localtime

# tm1637.py 放在另一個資料夾，先把那個資料夾加進 Python 的搜尋路徑
LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "7segment_display", "raspberrypi-tm1637")
sys.path.insert(0, LIB_DIR)

from tm1637 import TM1637

CLK = 23    # BCM GPIO23 = 實體腳位 16 (tm1637 函式庫使用 BCM 編號)
DIO = 24    # BCM GPIO24 = 實體腳位 18


class Clock:
    def __init__(self, tm_instance):
        self.tm = tm_instance
        self.show_colon = False

    def run(self):
        while True:
            t = localtime()                          # 取得現在時間
            self.show_colon = not self.show_colon    # 每次迴圈切換：亮 → 暗 → 亮 ...
            self.tm.numbers(t.tm_hour, t.tm_min, self.show_colon)
            sleep(1)                                 # 每 1 秒更新一次


if __name__ == '__main__':
    tm = TM1637(CLK, DIO)
    tm.brightness(1)        # 亮度 0~7

    try:
        Clock(tm).run()
    except KeyboardInterrupt:
        tm.write([0, 0, 0, 0])   # 結束時把顯示器清空
