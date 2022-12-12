from math import cos, sin, pi
from mathutils import Vector


def calculate_thread(segments=12, loops=2, radius=1, depth=0.1, h1=0.2, h2=0.0, h3=0.2, h4=0.0, fade=0.15):

    height = h1 + h2 + h3 + h4

    falloff = segments * fade

    profile = [Vector((radius, 0, 0))]
    profile.append(Vector((radius + depth, 0, h1)))

    if h2 > 0:
        profile.append(Vector((radius + depth, 0, h1 + h2)))

    profile.append(Vector((radius, 0, h1 + h2 + h3)))

    if h4 > 0:
        profile.append(Vector((radius, 0, h1 + h2 + h3 + h4)))

    pcount = len(profile)

    coords = []
    indices = []

    bottom_coords = []
    bottom_indices = []

    top_coords = []
    top_indices = []

    for loop in range(loops):
        for segment in range(segments + 1):
            angle = segment * 2 * pi / segments

            for pidx, co in enumerate(profile):

                if loop == 0 and segment <= falloff and pidx in ([1, 2] if h2 else [1]):
                    r = radius + depth * segment / falloff
                elif loop == loops - 1 and segments - segment <= falloff and pidx in ([1, 2] if h2 else [1]):
                    r = radius + depth * (segments - segment) / falloff
                else:
                    r = co.x

                z = co.z + (segment / segments) * height + (height * loop)

                coords.append(Vector((r * cos(angle), r * sin(angle), z)))

                if loop == 0 and pidx == 0:

                    if segment == segments:
                        bottom_coords.extend([Vector((radius, 0, co.z)) for co in profile])

                    else:
                        bottom_coords.extend([Vector((r * cos(angle), r * sin(angle), 0)), Vector((r * cos(angle), r * sin(angle), z))])

                elif loop == loops - 1 and pidx == len(profile) - 1:

                    if segment == 0:
                        top_coords.extend([Vector((radius, 0, co.z + height + height * loop)) for co in profile])

                    else:
                        top_coords.extend([Vector((r * cos(angle), r * sin(angle), z)), Vector((r * cos(angle), r * sin(angle), 2 * height + height * loop))])


            if segment > 0:

                for p in range(pcount - 1):
                    indices.append([len(coords) + i + p for i in [-pcount * 2, -pcount, -pcount + 1, -pcount * 2 + 1]])

                if loop == 0:
                    if segment < segments:
                        bottom_indices.append([len(bottom_coords) + i for i in [-4, -2, -1, -3]])

                    else:
                        bottom_indices.append([len(bottom_coords) + i for i in [-1 - pcount, -2 - pcount] + [i - pcount for i in range(pcount)]])

                if loop == loops - 1:
                    if segment == 1:
                        top_indices.append([len(top_coords) + i for i in [-2, -1] + [-3 - i for i in range(pcount)]])
                    else:
                        top_indices.append([len(top_coords) + i for i in [-4, -2, -1, -3]])

    return (coords, indices), (bottom_coords, bottom_indices), (top_coords, top_indices), height + height * loops
