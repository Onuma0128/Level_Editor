import bpy, math, mathutils, copy, gpu
from gpu_extras.batch import batch_for_shader

class DrawCollider:
    handle = None

    @staticmethod
    def draw_collider():
        vertices = {'pos': []}
        indices = []

        offsets = [
            (-.5,-.5,-.5), (.5,-.5,-.5), (-.5,.5,-.5), (.5,.5,-.5),
            (-.5,-.5,.5), (.5,-.5,.5), (-.5,.5,.5), (.5,.5,.5),
        ]

        for obj in bpy.context.scene.objects:
            if 'collider' not in obj:
                continue
            center = mathutils.Vector(obj['collider_center'])

            if obj['collider'] == 'Box':
                size = mathutils.Vector(obj['collider_size'])
                start = len(vertices['pos'])
                for off in offsets:
                    p = center + mathutils.Vector((
                        off[0]*size[0], off[1]*size[1], off[2]*size[2]))
                    loc, rot, _ = obj.matrix_world.decompose()
                    mat = rot.to_matrix().to_4x4()
                    mat.translation = loc
                    p = mat @ p
                    vertices['pos'].append(p)
                # 12 辺
                edges = [
                    (0,1),(2,3),(0,2),(1,3),
                    (4,5),(6,7),(4,6),(5,7),
                    (0,4),(1,5),(2,6),(3,7)
                ]
                for a,b in edges:
                    indices.append((start+a, start+b))

            elif obj['collider'] == 'Sphere':
                RINGS = 24
                r = obj.get('collider_radius',1.0)
                def add_circle(a,b):
                    start = len(vertices['pos'])
                    for i in range(RINGS):
                        t0 = i*2*math.pi/RINGS
                        t1 = (i+1)*2*math.pi/RINGS
                        p0 = center.copy(); p1 = center.copy()
                        p0[a] += math.cos(t0)*r
                        p0[b] += math.sin(t0)*r
                        p1[a] += math.cos(t1)*r
                        p1[b] += math.sin(t1)*r
                        loc, rot, _ = obj.matrix_world.decompose()
                        mat = rot.to_matrix().to_4x4()
                        mat.translation = loc
                        p0 = mat @ p0
                        p1 = mat @ p1
                        vertices['pos'].extend([p0,p1])
                        indices.append((start+2*i, start+2*i+1))
                add_circle(0,1); add_circle(1,2); add_circle(0,2)

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": vertices['pos']}, indices=indices)
        shader.bind()
        shader.uniform_float('color', (0.5,1,1,1))
        gpu.state.depth_test_set('NONE')
        batch.draw(shader)
        gpu.state.depth_test_set('LESS_EQUAL')

def register():
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(
        DrawCollider.draw_collider, (), 'WINDOW', 'POST_VIEW')

def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, 'WINDOW')
