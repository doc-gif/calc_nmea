from datetime import datetime
import re
import matplotlib.pyplot as plt
import japanize_matplotlib
import math
import numpy as np
from pyproj import Transformer
from geopy.distance import geodesic
import pandas as pd


def convert_time(t):
    return datetime.strptime(t, '%H%M%S.%f').strftime('%H:%M:%S')


def convert_datetime(t):
    return datetime.strptime(t, '%H%M%S.%f%d%m%Y').isoformat(timespec='milliseconds') + 'Z'


def convert_latitude(t, d):
    degree = float(t[0:2])
    minute = float(t[2:])
    sign = 1 if d == 'N' else -1
    return sign * (degree + minute / 60)


def convert_longitude(t, d):
    degree = float(t[0:3])
    minute = float(t[3:])
    sign = 1 if d == 'E' else -1
    return sign * (degree + minute / 60)


def extract_used_satellites(l):
    result = []
    for s in l:
        if (s != ''):
            result.append(int(s))
    return result


def remove_repetition(iterable):
    result = []
    for item in iterable:
        if item not in result:
            result.append(item)
    return result


def calc_satellites_number(l):
    result = 0
    for i in range(len(l)):
        if i != 0:
            result += l[i][1]
    return result


def int_wrap_nan_data(t):
    if t == '':
        return 0
    else:
        return int(t)


def float_wrap_nan_data(t):
    if t == '':
        return 0
    else:
        return float(t)


def add_left_side_annotation(ax, y1, y2, label, color):
    x1 = 1600
    x2 = 1650

    xs = [x1, x2, x2, x1]
    ys = [y1, y1, y2, y2]
    ax.plot(xs, ys, clip_on=False, color=color)

    center = (y1 + y2) / 2
    ax.text(x2 + 70, center, label, ha="center", va="top")


def add_bottom_side_annotation(ax, x, y_min, y_max, label, color):
    y1 = y_min - 0.0117 * (y_max - y_min)
    y2 = y_min - 0.027 * (y_max - y_min)
    text_y = y_min - 0.028 * (y_max - y_min)

    xs = [x+10, x-10, x, x+10]
    ys = [y2, y2, y1, y2]
    ax.plot(xs, ys, clip_on=False, color=color)

    ax.text(x, text_y, label, ha="left", va="top", fontsize=8, rotation=335)


def add_dashed_vertical_line(ax, x, color):
    ax.axvline(x, linestyle='--', color=color, lw=0.3)


def add_position_annotation(ax, fig, y_min, y_max):
    qz1_color = "y"
    smart_phone_color = "r"
    # QZ1、スマホで誤差が大きかった場所
    add_bottom_side_annotation(ax, 183, y_min, y_max, "桜通×本町通", qz1_color)
    add_dashed_vertical_line(ax, 183, qz1_color)
    add_bottom_side_annotation(ax, 479, y_min, y_max, "大津通×本重町通", qz1_color)
    add_dashed_vertical_line(ax, 479, qz1_color)
    add_bottom_side_annotation(ax, 609, y_min, y_max, "大津通 松坂屋前", qz1_color)
    add_dashed_vertical_line(ax, 609, qz1_color)
    add_bottom_side_annotation(ax, 879, y_min, y_max, "本町通", qz1_color)
    add_dashed_vertical_line(ax, 879, qz1_color)

    # スマホのみ誤差が大きかった場所
    add_bottom_side_annotation(ax, 765, y_min, y_max, "㈱宮田精肉店 本店前", smart_phone_color)
    add_dashed_vertical_line(ax, 765, smart_phone_color)
    add_bottom_side_annotation(ax, 1065, y_min, y_max, "広小路通×本町通", smart_phone_color)
    add_dashed_vertical_line(ax, 1065, smart_phone_color)
    add_bottom_side_annotation(ax, 1222, y_min, y_max, "広小路通×長者町繊維街 入口", smart_phone_color)
    add_dashed_vertical_line(ax, 1222, smart_phone_color)
    add_bottom_side_annotation(ax, 1313, y_min, y_max, "三井住友銀行前", smart_phone_color)
    add_dashed_vertical_line(ax, 1313, smart_phone_color)

    fig.subplots_adjust(left=0.1, right=0.95, bottom=0.17, top=0.9)


def find_nearest_points(t, r):
    distance = remove_repetition([[i, math.sqrt((t[0]-p[0])**2+(t[1]-p[1])**2)] for i, p in enumerate(r)])
    sorted_distance = sorted(distance, key=lambda x: x[1])
    return [r[sorted_distance[0][0]], r[sorted_distance[1][0]]]


def make_linear_equation(x1, y1, x2, y2):
    a = y2 - y1
    b = x2 - x1
    c = x2 * y1 - x1 * y2
    return a, b, c


def calc_distance(a, b, c, x, y):
    n = abs(a * x + b * y + c)
    d = math.sqrt(math.pow(a, 2) + math.pow(b, 2))
    return n/d


def calc_latlng_distance(p1, p2):
    return geodesic((p1[0], p1[1]), (p2[0], p2[1])).m


def calc_distance_error(t, ps, transformer):
    # t_x, t_y = transformer.transform(t[0], t[1])
    # p1_x, p1_y = transformer.transform(ps[0][0], ps[0][1])
    # p2_x, p2_y = transformer.transform(ps[1][0], ps[1][1])
    # l_a, l_b, l_c = make_linear_equation(p1_x, p1_y, p2_x, p2_y)
    # result = calc_distance(l_a, l_b, l_c, t_x, t_y)
    # return result
    l_a, l_b, l_c = make_linear_equation(ps[0], ps[1], ps[2], ps[3])
    p_x = (math.pow(l_b, 2)*t[0]-l_a*l_b*t[1]-l_a*l_c)/(pow(l_a, 2) + pow(l_b, 2))
    p_y = (math.pow(l_a, 2)*t[1]-l_a*l_b*t[0]-l_b*l_c)/(pow(l_a, 2) + pow(l_b, 2))
    return calc_latlng_distance(t, [p_x, p_y])


if __name__ == "__main__":
    target1_filepath = 'data/part2/20240718_124104_QZ1-005.nmea'
    # 全情報(Excel表示用)
    all_data_filepath = 'all_data.txt'
    # マップ表示用の緯度・経度のファイル
    lat_lon_filepath = 'data/part2/lat_lon.txt'
    # 実走行経路のファイル
    actual_route_filepath = 'data/part2/actual_route.txt'
    # スマートフォンで測位したデータファイル
    smart_phone_result_filepath = 'data/part2/position_log_output.txt'

    # Message IDの正規表現
    GxGGA_pat = '\$G[A-Z]GGA'
    GxGLL_pat = '\$G[A-Z]GLL'
    GxGSA_pat = '\$G[A-Z]GSA'
    GxGSV_pat = '\$G[A-Z]GSV'
    GxRMC_pat = '\$G[A-Z]RMC'
    GxVTG_pat = '\$G[A-Z]VTG'
    GxZDA_pat = '\$G[A-Z]ZDA'

    # nmeaファイルに書かれている測位情報をnp.arrayに格納する
    # 3次元配列となる（後に二次元配列を挿入）
    positioning_data = []

    # nmeaファイル解析
    with open(target1_filepath) as target:
        # 読み取ったメッセージを一つずつ格納していく
        temp = []
        for row in target.readlines():
            # GxGGA, GxGLL, GxGSA, GxGSV, GxRMC, GxVTG, GxZDAのいずれかを見つけたときにtempに格納
            row = ''.join(row.splitlines())
            GxGGA_result = re.search(GxGGA_pat, row)
            if GxGGA_result:
                temp.append(row.split(','))
                continue
            GxGLL_result = re.search(GxGLL_pat, row)
            if GxGLL_result:
                temp.append(row.split(','))
                continue
            GxGSA_result = re.search(GxGSA_pat, row)
            if GxGSA_result:
                temp.append(row.split(','))
                continue
            GxGSVP_result = re.search(GxGSV_pat, row)
            if GxGSVP_result:
                temp.append(row.split(','))
                continue
            GxRMC_result = re.search(GxRMC_pat, row)
            if GxRMC_result:
                temp.append(row.split(','))
                continue
            GxVTG_result = re.search(GxVTG_pat, row)
            if GxVTG_result:
                temp.append(row.split(','))
                continue
            GxZDA_result = re.search(GxZDA_pat, row)
            if GxZDA_result:
                temp.append(row.split(','))
                continue
            if temp:
                positioning_data.append(temp.copy())
                temp.clear()

    # 抽出したデータを格納するための配列
    all_data = []  # 2次元配列 [[a,b,c,d,e,f,g,h], ...] a=時刻(UTC),b=緯度,c=経度,d=測位ステータス,e=測位に使用した衛星数,f=測位モード,g=PDOP,h=HDOP,i=VDOP,j=可視衛星数,k=移動方向,l=対地速度,m=日付(ISO8601)
    lat_lon = []  # 2次元配列 [[x,y,z], ...] x=時刻(UTC),y=緯度,z=経度
    positioning_status = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=測位ステータス
    used_satellite_number = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=測位に使用した衛星数
    used_positioning_status = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=測位モード
    used_satellite_list = []  # 2次元配列 [[x,y,z, ...], ...] x=時刻(UTC),y=測位に使用した衛星番号1,z=測位に使用した衛星番号2, ...
    pdop = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=PDOP
    hdop = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=HDOP
    vdop = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=VDOP
    visible_satellite_number = []  # 3次元配列 [[x,[xx,xy], ..., n], ...] x=時刻(UTC),xx=衛星の種類(Gx),xy=その衛星の数,n=総衛星数
    visible_satellite_list = []  # 3次元配列 [[x,[xx,xy,xz,xw], ...], ...] x=時刻(UTC),xx=衛星番号,xy=仰角,xz=方位角,xw=C/N比
    direction_with_truth_direction = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=移動方向(真方位)
    direction_with_magnetic_direction = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=移動方向(地磁方位)
    speed = []  # 2次元配列 [[x,y], ...] x=時刻(UTC),y=対地速度(km/h)
    date = []  # 1次元配列 [x, ...] x=日付(ISO8601)

    for collection in positioning_data:
        time = ""
        temp_visible_satellite_number = []
        temp_visible_satellite_list = []
        for data in collection:
            match data[0][3:6]:
                case 'GGA':
                    time = convert_time(data[1])
                    latitude = convert_latitude(data[2], data[3])
                    longitude = convert_longitude(data[4], data[5])
                    lat_lon.append([time, latitude, longitude])
                    positioning_status.append([time, int(data[6])])
                    used_satellite_number.append([time, int(data[7])])
                    continue
                case 'GLL':
                    continue
                case 'GSA':
                    used_positioning_status.append([time, int(data[2])])
                    used_satellite_list.append([time, extract_used_satellites(data[3:15])])
                    pdop.append([time, float(data[15])])
                    hdop.append([time, float(data[16])])
                    vdop.append([time, float(data[17][0:3])])
                    continue
                case 'GSV':
                    if not temp_visible_satellite_number:
                        temp_visible_satellite_number.append(time)
                    temp_visible_satellite_number.append([data[0][1:3], int(data[3])])
                    if not temp_visible_satellite_list:
                        temp_visible_satellite_list.append(time)
                    try:
                        if data[4] != '':
                            temp_visible_satellite_list.append([
                                int(data[4]),
                                int_wrap_nan_data(data[5]),
                                int_wrap_nan_data(data[6]),
                                int_wrap_nan_data(data[7])
                            ])
                        if data[8] != '':
                            temp_visible_satellite_list.append([
                                int(data[8]),
                                int_wrap_nan_data(data[9]),
                                int_wrap_nan_data(data[10]),
                                int_wrap_nan_data(data[11])
                            ])
                        if data[12] != '':
                            temp_visible_satellite_list.append([
                                int(data[12]),
                                int_wrap_nan_data(data[13]),
                                int_wrap_nan_data(data[14]),
                                int_wrap_nan_data(data[15])
                            ])
                        if data[16] != '':
                            temp_visible_satellite_list.append([
                                int(data[16]),
                                int_wrap_nan_data(data[17]),
                                int_wrap_nan_data(data[18]),
                                int_wrap_nan_data(data[19][:-3])
                            ])
                    finally:
                        continue
                case 'RMC':
                    continue
                case 'VTG':
                    direction_with_truth_direction.append([time, float(data[1])])
                    direction_with_magnetic_direction.append([time, float(data[3])])
                    speed.append([time, float_wrap_nan_data(data[7])])
                    continue
                case 'ZDA':
                    date.append(convert_datetime(''.join(data[1:5])))
                    # visible_satellite_numberへの処理
                    if temp_visible_satellite_number:
                        # 重複削除
                        temp_visible_satellite_number = remove_repetition(temp_visible_satellite_number)
                        # 確認可能な衛星数を追加（総数）
                        temp_visible_satellite_number.append(calc_satellites_number(temp_visible_satellite_number))
                        visible_satellite_number.append(temp_visible_satellite_number.copy())
                        temp_visible_satellite_number.clear()
                    # visible_satellite_listへの処理
                    if temp_visible_satellite_list:
                        # 重複削除
                        temp_visible_satellite_list = remove_repetition(temp_visible_satellite_list)
                        visible_satellite_list.append(temp_visible_satellite_list.copy())
                        temp_visible_satellite_list.clear()
                    continue

    # マップ表示用の緯度・経度を記述したファイル作成
    with open(lat_lon_filepath, "w") as t:
        result = ''
        for data in lat_lon:
            result += '[' + str(data[1]) + ', ' + str(data[2]) + '],\n'
        result = result[:-2]
        t.write(result)

    actual_route = []
    # 実走行距離のデータを配列に格納
    with open(actual_route_filepath, "r") as t:
        for line in t.readlines():
            line = line[0:-1].replace(' ', '')
            temp = line.split(',')
            actual_route.append([float(temp[0]), float(temp[1])])

    smart_phone_route = []
    # スマートフォンで測位したデータを配列に格納
    with open(smart_phone_result_filepath, 'r') as t:
        for line in t.readlines():
            temp = line.split(',')
            smart_phone_route.append([float(temp[0]), float(temp[1])])

    # 誤差距離の計算
    # 直交座標系に直すとうまくいかなかった。オーバーフロー？
    # epsg4326_to_epsg6675 = Transformer.from_crs("epsg:4326", "epsg:6675")
    # qz1_position_error = [calc_distance_error(target[1:], find_nearest_points(target[1:], actual_route), epsg4326_to_epsg6675) for target in lat_lon]
    qz1_position_error = [calc_latlng_distance(target[1:], find_nearest_points(target[1:], actual_route)[0]) for target in lat_lon]
    smart_phone_position_error = [calc_latlng_distance(position, find_nearest_points(position, actual_route)[0]) for position in smart_phone_route]
    # それぞれの平均
    average_of_qz1_position_error = sum(qz1_position_error) / len(qz1_position_error)
    average_of_smart_phone_position_error = sum(smart_phone_position_error) / len(smart_phone_position_error)
    print("距離誤差平均（QZ1）：" + str(average_of_qz1_position_error))
    print("距離誤差平均（スマホ）：" + str(average_of_smart_phone_position_error))
    time_x = [item[0] for item in lat_lon]
    # スマホ、QZ1の距離誤差のグラフ表示
    # QZ1のみ
    fig1, ax1 = plt.subplots()
    ax1.plot(time_x, qz1_position_error, label="QZ1(みちびきSLAS)")
    ax1.set_xticks([])
    ax1.set_ylabel('誤差(m)')
    ax1.set_ylim(0, 80)
    ax1.set_title('QZ1の距離誤差')
    ax1.axhline(y=average_of_qz1_position_error, color='#d3381c', linestyle='--', label="距離誤差平均(QZ1)")
    ax1.grid(which='major', linewidth=0.8)
    ax1.grid(which='minor', linestyle=':', linewidth=0.5)
    ax1.minorticks_on()
    ax1.legend()
    add_position_annotation(ax1, fig1, 0, 80)
    plt.savefig('qz1_distance_error.png', dpi=600)
    plt.show()
    # スマホのみ
    fig2, ax2 = plt.subplots()
    ax2.plot(range(len(smart_phone_position_error)), smart_phone_position_error, label="スマートフォン", color="#ff7f00")
    ax2.set_xticks([])
    ax2.set_ylabel('誤差(m)')
    ax2.set_ylim(0, 80)
    ax2.set_title('スマートフォンの距離誤差')
    ax2.axhline(y=average_of_smart_phone_position_error, color='#00a381', linestyle='--', label="距離誤差平均(スマートフォン)")
    ax2.grid(which='major', linewidth=0.8)
    ax2.grid(which='minor', linestyle=':', linewidth=0.5)
    ax2.minorticks_on()
    ax2.legend()
    add_position_annotation(ax2, fig2, 0, 80)
    plt.savefig('smartphone_distance_error.png', dpi=600)
    plt.show()
    # QZ1、スマホ
    fig3, ax3 = plt.subplots()
    ax3.plot(time_x, qz1_position_error, label="QZ1(みちびきSLAS)")
    ax3.plot(range(len(smart_phone_position_error)), smart_phone_position_error, label="スマートフォン")
    ax3.set_xticks([])
    ax3.set_ylabel('誤差(m)')
    ax3.set_ylim(0, 80)
    ax3.set_title('QZ1、スマートフォンの距離誤差')
    ax3.axhline(y=average_of_qz1_position_error, color='#d3381c', linestyle='--', label="距離誤差平均(QZ1)")
    ax3.axhline(y=average_of_smart_phone_position_error, color='#00a381', linestyle='--', label="距離誤差平均(スマートフォン)")
    ax3.grid(which='major', linewidth=0.8)
    ax3.grid(which='minor', linestyle=':', linewidth=0.5)
    ax3.minorticks_on()
    ax3.legend()
    add_position_annotation(ax3, fig3, 0, 80)
    plt.savefig('qz1_and_smartphone_distance_error.png', dpi=600)
    plt.show()

    # 可視衛星数のグラフ表示
    fig4, ax4 = plt.subplots()
    time_x = [item[0] for item in visible_satellite_number]
    number_of_visible_satellite_y = [item[-1] for item in visible_satellite_number]
    average_of_number_of_visible_satellite = sum(number_of_visible_satellite_y) / len(number_of_visible_satellite_y)
    print("可視衛星数平均：" + str(average_of_number_of_visible_satellite))
    ax4.plot(time_x, number_of_visible_satellite_y)
    ax4.set_xticks([])
    ax4.set_ylim(0, 20)
    ax4.set_yticks(np.arange(0, 20, 5))
    ax4.set_ylabel('衛星数')
    ax4.set_title('観測可能な衛星数')
    ax4.axhline(y=average_of_number_of_visible_satellite, color='r')
    ax4.grid(which='major', linewidth=0.8)
    ax4.grid(which='minor', linestyle=':', linewidth=0.5)
    ax4.minorticks_on()
    add_position_annotation(ax4, fig4, 0, 20)
    plt.savefig('qz1_number_of_visible_satellite.png', dpi=600)
    plt.show()
    # 使用衛星数のグラフ表示
    fig5, ax5 = plt.subplots()
    time_x = [item[0] for item in used_satellite_number]
    number_of_used_satellite_y = [item[1] for item in used_satellite_number]
    average_of_number_of_used_satellite = sum(number_of_used_satellite_y) / len(number_of_used_satellite_y)
    print("使用衛星数平均：" + str(average_of_number_of_used_satellite))
    ax5.plot(time_x, number_of_used_satellite_y)
    ax5.set_xticks([])
    ax5.set_ylim(0, 13)
    ax5.set_yticks(np.arange(0, 13, 5))
    ax5.set_ylabel('衛星数')
    ax5.set_title('測位に使用した衛星数')
    ax5.axhline(y=average_of_number_of_used_satellite, color='r')
    ax5.grid(which='major', linewidth=0.8)
    ax5.grid(which='minor', linestyle=':', linewidth=0.5)
    ax5.minorticks_on()
    add_position_annotation(ax5, fig5, 0, 13)
    plt.savefig('qz1_number_of_used_satellite.png', dpi=600)
    plt.show()
    # HDOPのグラフ表示
    fig6, ax6 = plt.subplots()
    time_x = [item[0] for item in hdop]
    hdop_y = [item[1] for item in hdop]
    average_of_hdop = sum(hdop_y) / len(hdop_y)
    print("HDOP値平均：" + str(average_of_hdop))
    ax6.plot(time_x, hdop_y)
    ax6.set_xticks([])
    ax6.set_xlim(0, 1570)
    ax6.set_ylabel('hdop')
    ax6.set_ylim(0.7, 5.2)
    ax6.set_title('hdop値（水平測位精度の劣化度）')
    ax6.grid(which='major', linewidth=0.8)
    ax6.grid(which='minor', linestyle=':', linewidth=0.5)
    ax6.minorticks_on()
    ax6.axhline(y=1, color="b", linestyle="--")  # Ideal
    ax6.axhline(y=2, color="g", linestyle="--")  # Excellent
    ax6.axhline(y=5, color="y", linestyle="--")  # Good
    ax6.axhline(y=average_of_hdop, color="r")
    add_left_side_annotation(ax6, 0.7, 0.95, '理想', 'b')
    add_left_side_annotation(ax6, 1.05, 1.95, '優良', 'g')
    add_left_side_annotation(ax6, 2.05, 4.95, '良', 'y')
    add_position_annotation(ax6, fig6, 0.7, 5.2)
    fig6.subplots_adjust(left=0.125, right=0.9)
    plt.savefig('qz1_hdop.png', dpi=600)
    plt.show()

    # 測位ステータスのグラフ表示
    fig7, ax7 = plt.subplots()
    positioning_status_y = [item[1] for item in positioning_status]
    ax7.plot(range(len(positioning_status_y)), positioning_status_y)
    ax7.set_xticks([])
    ax7.set_xlim(0, 1570)
    ax7.set_ylim(-0.2, 2.2)
    ax7.set_yticks(np.arange(0, 2.2, 1))
    ax7.set_ylabel('ステータス')
    ax7.set_title('測位ステータス')
    ax7.grid(which='major', linewidth=0.8)
    ax7.plot([1600, 1650], [0, 0], clip_on=False, color="r")
    ax7.text(1600, -0.1, "測位不能")
    ax7.plot([1600, 1650], [1, 1], clip_on=False, color="y")
    ax7.text(1600, 0.9, "単独測位")
    ax7.plot([1600, 1650], [2, 2], clip_on=False, color="g")
    ax7.text(1600, 1.9, "DGPS")
    add_position_annotation(ax7, fig7, -0.2, 2.2)
    fig7.subplots_adjust(left=0.125, right=0.9)
    plt.savefig('qz1_positioning_satus.png', dpi=600)
    plt.show()

    # 位置情報誤差の分布
    # QZ1
    df_qz1_position_error = pd.Series(qz1_position_error, name='df_qz1_position_error')
    qz1_bins = np.linspace(0, 100, 26)
    qz1_freq = df_qz1_position_error.value_counts(bins=qz1_bins, sort=False)
    qz1_class_value = (qz1_bins[:-1] + qz1_bins[1:]) / 2  # 階級値
    qz1_rel_freq = qz1_freq / df_qz1_position_error.count()  # 相対度数
    qz1_cum_freq = qz1_freq.cumsum()  # 累積度数
    qz1_rel_cum_freq = qz1_rel_freq.cumsum()  # 相対累積度数
    qz1_dist = pd.DataFrame(
        {
            "階級値": qz1_class_value,
            "度数": qz1_freq,
            "相対度数": qz1_rel_freq,
            "累積度数": qz1_cum_freq,
            "相対累積度数": qz1_rel_cum_freq,
        },
        index=qz1_freq.index
    )
    fig8, ax8 = plt.subplots()
    qz1_dist.plot.bar(x="階級値", y="度数", ax=ax8, width=1, ec="k", lw=2)
    ax8.set_ylim(0, 850)
    ax9 = ax8.twinx()
    ax9.plot(np.arange(len(qz1_dist)), qz1_dist["相対累積度数"], "--o", color="k")
    ax9.set_ylabel("累積相対度数")
    ax9.set_ylim(0, )
    plt.savefig('qz1_distance_error_frequency.png', dpi=600)
    plt.show()
    # スマホ
    df_smart_phone_position_error = pd.Series(smart_phone_position_error, name='df_smart_phone_position_error')
    smart_phone_bins = np.linspace(0, 100, 26)
    smart_phone_freq = df_smart_phone_position_error.value_counts(bins=smart_phone_bins, sort=False)
    smart_phone_class_value = (smart_phone_bins[:-1] + smart_phone_bins[1:]) / 2  # 階級値
    smart_phone_rel_freq = smart_phone_freq / df_smart_phone_position_error.count()  # 相対度数
    smart_phone_cum_freq = smart_phone_freq.cumsum()  # 累積度数
    smart_phone_rel_cum_freq = smart_phone_rel_freq.cumsum()  # 相対累積度数
    smart_phone_dist = pd.DataFrame(
        {
            "階級値": smart_phone_class_value,
            "度数": smart_phone_freq,
            "相対度数": smart_phone_rel_freq,
            "累積度数": smart_phone_cum_freq,
            "相対累積度数": smart_phone_rel_cum_freq,
        },
        index=smart_phone_freq.index
    )
    print(smart_phone_dist)
    fig10, ax10 = plt.subplots()
    smart_phone_dist.plot.bar(x="階級値", y="度数", ax=ax10, width=1, ec="k", lw=2)
    ax10.set_ylim(0, 850)
    ax11 = ax10.twinx()
    ax11.plot(np.arange(len(smart_phone_dist)), smart_phone_dist["相対累積度数"], "--o", color="k")
    ax11.set_ylabel("累積相対度数")
    ax11.set_ylim(0, )
    plt.savefig('smartphone_distance_error_frequency.png', dpi=600)
    plt.show()
