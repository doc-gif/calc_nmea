import re


target_filepath = './20240227_152258_QZ1-005.nmea'
GxRMC_filepath = './GxRMC.nmea'

GxRMC = []
GxRMC_pat = '\$G[A-Z]RMC'

output = []

with open(target_filepath) as target:
    for row in target.readlines():
        result = re.match(GxRMC_pat, row)
        if (result):
            GxRMC.append(row)

with open(GxRMC_filepath, mode='w') as target:
    str = ''.join(GxRMC)
    target.write(str)

for row in GxRMC:
    row.replace('\n', '')
    data = row.split(',')
    if (data[2]): continue
    result = []
    for i in range(data.len()):
        # 時刻 hhmmss.ss 日本時間 +9時間
        if (i == 1):

        # 緯度　ddmm.mmmmmmm
        if (i == 3):

        # 南北 N=北緯, S=南緯
        if (i == 4):

        # 経度 dddmm.mmmmmmm
        if (i == 5):

        # 東西 E=東経, S=西経
        if (i == 6):

        # 速度 [knot]
        if (i == 7):

        # 真方位 [deg]
        if (i == 8):

        # 日付 ddmmyy
        if (i == 9):