"""Two-bone inverse kinematics for 2D character animation.

Returns elbow and hand joints that preserve segment lengths; used for actual
articulated sprites. This is NOT a neural video generation or art model.
"""
import math

def solve_two_bone(shoulder, target, upper_length, forearm_length, bend=1):
    sx, sy = map(float, shoulder)
    tx, ty = map(float, target)
    dx, dy = tx-sx, ty-sy
    distance = math.hypot(dx, dy)
    if upper_length <= 0 or forearm_length <= 0:
        raise ValueError("bone lengths must be positive")
    low = abs(upper_length-forearm_length)+1e-7
    high = upper_length+forearm_length-1e-7
    reachable = min(high, max(low, distance))
    theta = math.atan2(dy,dx)
    cosval = (upper_length**2+reachable**2-forearm_length**2)/(2*upper_length*reachable)
    upper_angle = theta+(1 if bend >= 0 else -1)*math.acos(max(-1,min(1,cosval)))
    elbow = (sx+upper_length*math.cos(upper_angle), sy+upper_length*math.sin(upper_angle))
    if distance < 1e-7:
        hand = (sx+reachable,sy)
    else:
        hand=(sx+reachable*dx/distance,sy+reachable*dy/distance)
    return {
        "elbow":elbow, "hand":hand,
        "upper_angle_degrees":math.degrees(upper_angle),
        "forearm_angle_degrees":math.degrees(math.atan2(hand[1]-elbow[1],hand[0]-elbow[0])),
        "distance_error":max(0,distance-high)
    }
