"""Stable 12-point head contours across front, three-quarter and profile.
Separate per-view geometry, interpolated without topology-switching.
"""
from math import pi

FRONT=[(-41,-28),(-44,-8),(-43,12),(-33,39),(-8,58),(27,48),(42,18),(42,-10),(42,-36),(18,-60),(-15,-64),(-33,-51)]
QUARTER=[(-37,-30),(-40,-8),(-40,4),(-30,37),(-5,57),(29,48),(46,21),(54,3),(45,-13),(37,-40),(10,-62),(-17,-63)]
PROFILE=[(-36,-29),(-37,-6),(-34,8),(-17,46),(9,60),(30,46),(44,23),(64,9),(53,-3),(44,-17),(36,-47),(-21,-62)]

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def morph(a,b,t):
    if len(a)!=len(b):
        raise ValueError("Incompatible contours; resample to equal topology")
    return [(x+(u-x)*t,y+(v-y)*t) for (x,y),(u,v) in zip(a,b)]

def head_at(yaw):
    yaw=max(0,min(1,yaw))
    if yaw<=.5: return morph(FRONT,QUARTER,smooth(yaw*2))
    return morph(QUARTER,PROFILE,smooth((yaw-.5)*2))

def far_eye_width(yaw,base=9):
    return max(.4,base*(1-max(0,min(1,yaw))))

if __name__=="__main__":
    for t in (0,.1,.25,.5,.75,.9,1):
        assert len(head_at(t))==12
    print("Contour topology checks passed")
