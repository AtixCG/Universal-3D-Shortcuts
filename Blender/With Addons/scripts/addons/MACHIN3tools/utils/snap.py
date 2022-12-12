import bpy
import bmesh
from . raycast import cast_scene_ray_from_mouse








class Snap:
    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    debug = False

    depsgraph = None
    cache = None

    exclude = []
    exclude_wire = False
    alternative = []

    hit = None
    hitobj = None
    hitindex = None
    hitlocation = None
    hitnormal = None
    hitmx = None

    hitface = None

    _edit_mesh_objs = []
    _modifiers = []

    def __init__(self, context, include=None, exclude=None, exclude_wire=False, alternative=None, debug=False):
        self.debug = debug

        self.log("\nInitialize Snapping")

        self._init_edit_mode(context)

        self._init_exclude(context, include, exclude, exclude_wire)

        self._init_alternatives(context, alternative)

        self.depsgraph = context.evaluated_depsgraph_get()
        self.cache = SnapCache(debug=debug)

        self.hitface = None

        self.log()

    def finish(self):
        self.log("\nFinish Snapping")

        if self._modifiers:
            self._enable_modifiers()

        self._remove_alternatives()

        self.cache.clear()

    def get_hit(self, mousepos):

        self.hit, self.hitobj, self.hitindex, self.hitlocation, self.hitnormal, self.hitmx = cast_scene_ray_from_mouse(mousepos, self.depsgraph, exclude=self.exclude, exclude_wire=self.exclude_wire, unhide=self.alternative, debug=self.debug)

        if self.hit:
            name = self.hitobj.name


            if name not in self.cache.objects:


                self.cache.objects[name] = self.hitobj



                mesh = bpy.data.meshes.new_from_object(self.hitobj.evaluated_get(self.depsgraph), depsgraph=self.depsgraph)
                self.cache.meshes[name] = mesh



                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.verts.ensure_lookup_table()
                bm.faces.ensure_lookup_table()
                self.cache.bmeshes[name] = bm



                self.cache.loop_triangles[name] = bm.calc_loop_triangles()
                self.cache.tri_coords[name] = {}






            if not self.hitface or (self.hitface and self.hitface.index != self.hitindex):
                self.log("Hitface changed to", self.hitindex)

                self.hitface = self.cache.bmeshes[name].faces[self.hitindex]



            if self.hitindex not in self.cache.tri_coords[name]:
                self.log("Adding tri coords for face index", self.hitindex)

                loop_triangles = self.cache.loop_triangles[name]

                tri_coords = [self.hitmx @ l.vert.co for tri in loop_triangles if tri[0].face == self.hitface for l in tri]
                self.cache.tri_coords[name][self.hitindex] = tri_coords

    def _init_edit_mode(self, context):

        if context.mode == 'EDIT_MESH':
            self._update_meshes(context)
            self._disable_modifiers()

    def _init_exclude(self, context, include, exclude, exclude_wire):
        if include:
            self.exclude = [obj for obj in context.visible_objects if obj not in include]

        elif exclude:
            self.exclude = exclude

        else:
            self.exclude = []

        view = context.space_data

        if view.local_view:
            hidden = [obj for obj in context.view_layer.objects if not obj.visible_get()]
            self.exclude += hidden

        self.exclude_wire = exclude_wire

    def _init_alternatives(self, context, alternative):

        self.alternative = []

        if alternative:
            for obj in alternative:
                if obj not in self.exclude:
                    self.exclude.append(obj)

                dup = obj.copy()
                dup.data = obj.data.copy()
                context.scene.collection.objects.link(dup)
                dup.hide_set(True)

                self.alternative.append(dup)

                self.log(f" Created alternative object {dup.name} for {obj.name}")

    def _remove_alternatives(self):
        for obj in self.alternative:
            self.log(f" Removing alternave object {obj.name}")
            bpy.data.meshes.remove(obj.data, do_unlink=True)

    def _update_meshes(self, context):

        self._edit_mesh_objs = [obj for obj in context.visible_objects if obj.mode == 'EDIT']

        for obj in self._edit_mesh_objs:
            obj.update_from_editmode()

    def _disable_modifiers(self):

        self._modifiers = [(obj, mod) for obj in self._edit_mesh_objs for mod in obj.modifiers if mod.show_viewport]

        for obj, mod in self._modifiers:
            self.log(f" Disabling {obj.name}'s {mod.name}")

            mod.show_viewport = False

    def _enable_modifiers(self):

        for obj, mod in self._modifiers:
            self.log(f" Re-enabling {obj.name}'s {mod.name}")

            mod.show_viewport = True


class SnapCache:
    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    debug = False

    objects = {}
    meshes = {}

    bmeshes = {}

    loop_triangles = {}
    tri_coords = {}

    def __init__(self, debug=False):
        self.debug = debug
        self.log(" Initialize SnappingCache")

    def clear(self):
        for name, mesh in self.meshes.items():
            self.log(f" Removing {name}'s temporary snapping mesh {mesh.name} with {len(mesh.polygons)} faces and {len(mesh.vertices)} verts")
            bpy.data.meshes.remove(mesh, do_unlink=True)

        for name, bm in self.bmeshes.items():
            self.log(f" Freeing {name}'s temporary snapping bmesh")
            bm.free()

        self.objects.clear()
        self.meshes.clear()

        self.bmeshes.clear()

        self.loop_triangles.clear()
        self.tri_coords.clear()
