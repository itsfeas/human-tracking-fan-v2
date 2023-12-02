import math

# Calculates left and right fan angles.
# 
# INPUTS
# w: the distance between both fans and mid
# d: the distance of the target from the center fan
# theta: angle of the center fan (from the perspective of the center fan)
def get_fan_angles(w, d, theta):
    theta_rad = theta*math.pi/180
    theta_opp = math.pi-theta_rad
    a = math.sqrt(d**2+w**2-2*d*w*math.cos(theta_opp))
    l_theta = math.asin(d*math.sin(theta_opp)/a)
    b = math.sqrt(d**2+w**2-2*d*w*math.cos(theta_rad))
    r_theta = math.asin(d*math.sin(theta_rad)/b)
    return (l_theta*180/math.pi, theta, r_theta*180/math.pi)

def get_angles_diff(angles_before, angles_after):
    return (angles_before[0]-angles_after[0], angles_before[1]-angles_after[1], angles_before[2]-angles_after[2])

if __name__ == '__main__':
    # should be (59.28621250006115, 21.445087812765514)
    angles = get_fan_angles(10, 8.9, 134.3)
    print(angles)
    assert angles[0]==59.28621250006115
    assert angles[1]==134.3
    assert angles[2]==21.445087812765514

    print(get_angles_diff((0,0,0), angles))