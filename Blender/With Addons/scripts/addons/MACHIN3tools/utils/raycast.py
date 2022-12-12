import bpy
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
import bmesh
from mathutils.bvhtree import BVHTree as BVH
import sys



def cast_bvh_ray_from_mouse(mousepos, candidates=None, bmeshes={}, bvhs={}, debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    objects = [(obj, None) for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    cache = {'bmesh': {},
             'bvh': {}}

    for obj, src in objects:
        mx = obj.matrix_world
        mxi = mx.inverted_safe()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        if obj.name in bmeshes:
            bm = bmeshes[obj.name]
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            cache['bmesh'][obj.name] = bm

        if obj.name in bvhs:
            bvh = bvhs[obj.name]
        else:
            bvh = BVH.FromBMesh(bm)
            cache['bvh'][obj.name] = bvh

        location, normal, index, distance = bvh.ray_cast(ray_origin, ray_direction)

        if distance:
            distance = (mx @ location - origin_3d).length

        if debug:
            print("candidate:", obj.name, location, normal, index, distance)

        if distance and distance < hitdistance:
            hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance


    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        return hitobj, hitlocation, hitnormal, hitindex, hitdistance, cache

    return None, None, None, None, None, cache



def cast_obj_ray_from_mouse(mousepos, depsgraph=None, candidates=None, debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    if not candidates:
        candidates = bpy.context.visible_objects

    objects = [obj for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitobj_eval = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj in objects:
        mx = obj.matrix_world
        mxi = mx.inverted_safe()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        success, location, normal, index = obj.ray_cast(origin=ray_origin, direction=ray_direction, depsgraph=depsgraph)
        distance = (mx @ location - origin_3d).length

        if debug:
            print("candidate:", success, obj.name, location, normal, index, distance)

        if success and distance < hitdistance:
            hitobj, hitobj_eval, hitlocation, hitnormal, hitindex, hitdistance = obj, obj.evaluated_get(depsgraph) if depsgraph else None, mx @ location, mx.to_3x3() @ normal, index, distance

    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        return hitobj, hitobj_eval, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None, None



def get_closest(origin, candidates=[], depsgraph=None, debug=False):
    nearestobj = None
    nearestlocation = None
    nearestnormal = None
    nearestindex = None
    nearestdistance = sys.maxsize

    if not candidates:
        candidates = bpy.context.visible_objects

    objects = [obj for obj in candidates if obj.type == 'MESH']

    for obj in objects:
        mx = obj.matrix_world

        origin_local = mx.inverted_safe() @ origin

        obj_eval = obj.evaluated_get(depsgraph)

        if obj_eval.data.polygons:
            success, location, normal, index = obj.closest_point_on_mesh(origin_local, depsgraph=depsgraph)


            distance = (mx @ location - origin).length if success else sys.maxsize

            if debug:
                print("candidate:", success, obj, location, normal, index, distance)

            if distance is not None and distance < nearestdistance:
                nearestobj, nearestlocation, nearestnormal, nearestindex, nearestdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance

        elif debug:
                print("candidate:", "%s's evaluated mesh contains no faces" % (obj))


    if debug:
        print("best hit:", nearestobj, nearestlocation, nearestnormal, nearestindex, nearestdistance)

    if nearestobj:
        return nearestobj, nearestobj.evaluated_get(depsgraph), nearestlocation, nearestnormal, nearestindex, nearestdistance

    return None, None, None, None, None, None



def cast_scene_ray_from_mouse(mousepos, depsgraph, exclude=[], exclude_wire=False, unhide=[], debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    view_origin = region_2d_to_origin_3d(region, region_data, mousepos)
    view_dir = region_2d_to_vector_3d(region, region_data, mousepos)

    scene = bpy.context.scene

    for ob in unhide:
        ob.hide_set(False)

    hit, location, normal, index, obj, mx = scene.ray_cast(depsgraph=depsgraph, origin=view_origin, direction=view_dir)


    hidden = []

    if hit:
        if obj in exclude or (exclude_wire and obj.display_type == 'WIRE'):
            ignore = True

            while ignore:
                if debug:
                    print(" Ignoring object", obj.name)

                obj.hide_set(True)
                hidden.append(obj)

                hit, location, normal, index, obj, mx = scene.ray_cast(depsgraph=depsgraph, origin=view_origin, direction=view_dir)

                if hit:
                    ignore = obj in exclude or (exclude_wire and obj.display_type == 'WIRE')
                else:
                    break

    for ob in unhide:
        ob.hide_set(True)

    for ob in hidden:
        ob.hide_set(False)

    if hit:
        if debug:
            print(obj.name, index, location, normal)

        return hit, obj, index, location, normal, mx

    else:
        if debug:
            print(None)

        return None, None, None, None, None, None
