import math


def compute_distance(pos_a, pos_b=(0, 0)):
    return math.sqrt(
        (pos_a[0] - pos_b[0]) ** 2 +
        (pos_a[1] - pos_b[1]) ** 2
    )


def compute_bearing(rel_x, rel_y):
    angle = math.degrees(math.atan2(rel_y, rel_x))
    return angle % 360


def is_in_front(rel_x, rel_y, fov_degrees=90):
    bearing = compute_bearing(rel_x, rel_y)
    half = fov_degrees / 2
    return bearing <= half or bearing >= (360 - half)


def is_behind(rel_x, rel_y, fov_degrees=90):
    bearing = compute_bearing(rel_x, rel_y)
    return 180 - fov_degrees / 2 <= bearing <= 180 + fov_degrees / 2


def is_left(rel_x, rel_y):
    bearing = compute_bearing(rel_x, rel_y)
    return 90 <= bearing < 270


def is_right(rel_x, rel_y):
    return not is_left(rel_x, rel_y)


def classify_relation(rel_x, rel_y, distance, thresholds=None):
    if thresholds is None:
        thresholds = {
            'critical': 5,
            'near':     15,
            'far':      30,
        }

    if distance > thresholds['far']:
        return None

    if distance <= thresholds['critical']:
        zone = 'critical'
    elif distance <= thresholds['near']:
        zone = 'near'
    else:
        zone = 'far'

    if is_in_front(rel_x, rel_y):
        direction = 'front'
    elif is_behind(rel_x, rel_y):
        direction = 'behind'
    elif is_left(rel_x, rel_y):
        direction = 'left'
    else:
        direction = 'right'

    return {
        'zone':      zone,
        'direction': direction,
        'distance':  round(distance, 2),
    }