from geopy.distance import geodesic

target_file = 'data/part2/smartphone_position_log_output.txt'
point_lat, point_lng = 35.1656003368182, 136.90730356717975
point = (point_lat, point_lng)

with open(target_file, 'r') as f:
    index = 0
    d = 1000
    for i, line in enumerate(f.read().splitlines()):
        temp = line.split(',')
        lat = float(temp[0])
        lon = float(temp[1])
        dist = geodesic((lat, lon), point).m
        if dist < d:
            d = dist
            index = i

print(index, d)
