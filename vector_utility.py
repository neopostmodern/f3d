__author__ = 'mrssheep'

def intersect(ray_origin, ray_direction, plane_origin, plane_normal_vector, allow_negative=False):

    # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection#Algebraic_form
    distance_factor = ((plane_origin - ray_origin).dot(plane_normal_vector)) \
                     / (ray_direction.dot(plane_normal_vector))

    if distance_factor <= 0 or allow_negative:
        return None

    return ray_origin + ray_direction * distance_factor