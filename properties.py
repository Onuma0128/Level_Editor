import bpy
import mathutils

def _ensure_size_or_radius(obj):
    if obj.collider_enum == 'Sphere':
        obj['collider_radius'] = obj.get('collider_radius', 1.0)
        obj.pop('collider_size', None)
    else:
        obj['collider_size'] = obj.get('collider_size', mathutils.Vector((2,2,2)))
        obj.pop('collider_radius', None)

def _collider_enum_update(self, _ctx):
    self['collider'] = self.collider_enum
    _ensure_size_or_radius(self)

def register():
    bpy.types.Object.collider_enum = bpy.props.EnumProperty(
        name='Collider',
        description='Choose collider shape',
        items=[
            ('Box', 'Box', 'Axis‑aligned box'),
            ('Sphere', 'Sphere', 'Bounding sphere'),
        ],
        default='Box',
        update=_collider_enum_update
    )

def unregister():
    del bpy.types.Object.collider_enum
