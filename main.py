import datetime
import math
import re


target_filepath = './20240227_152258_QZ1-005.nmea'
GxRMC_filepath = './GxRMC.nmea'
lat_lon_filepath = './lat_lon.txt'

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
    if (data[2] == 'N'): continue
    result = []
    for i in range(len(data)):
        # 時刻 hhmmss.ss 日本時間 +9時間
        if (i == 1):
            hour = int(data[1][0:2])
            minute = int(data[1][2:4])
            second = math.floor(float(data[1][4:8]))
            time = datetime.datetime(year=2024, month=1, day=15, hour=hour, minute=minute, second=second)
            time += datetime.timedelta(hours=9)
            result.append(datetime.time(hour=time.hour, minute=time.minute, second=time.second))
        # 緯度　ddmm.mmmmmmm
        if (i == 3):
            degree = math.floor(float(data[3]) / 100)
            minute1 = float(data[3]) - degree * 100
            minute2 = minute1 / 60
            latitude = degree + minute2
            result.append(latitude)
        # 南北 N=北緯, S=南緯
        if (i == 4):
            if (data[4] == 'S'):
                result[1] *= -1
        # 経度 dddmm.mmmmmmm
        if (i == 5):
            degree = math.floor(float(data[5]) / 100)
            minute1 = float(data[5]) - degree * 100
            minute2 = minute1 / 60
            longitude = degree + minute2
            result.append(longitude)
        # 東西 E=東経, S=西経
        if (i == 6):
            if (data[6] == 'S'):
                result[2] *= -1
        # 速度 [knot]
        if (i == 7):
            if (data[7] != ''):
                result.append(float(data[7]) * 1.852)
            else:
                result.append(0)
        # 真方位 [deg]
        if (i == 8):
            result.append(float(data[8]))
        # 日付 ddmmyy
        if (i == 9):
            year = int(data[9][4:6])+2000
            month = int(data[9][2:4])
            day = int(data[9][0:2])
            date = datetime.datetime(year=year, month=month, day=day)
            result.append(date)
    output.append(result)

with open(lat_lon_filepath, mode='w', encoding='utf-8') as target:
    s = ''
    for i in range(len(output)):
        if i != len(output) - 1:
            s += f'[{output[i][1]}, {output[i][2]}],\n'
        else:
            s += f'[{output[i][1]}, {output[i][2]}]'
    target.write(s)