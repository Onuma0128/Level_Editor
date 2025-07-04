import bpy

class OBJECT_PT_file_name(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_file_name'
    bl_label = 'FileName'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        if 'file_name' in context.object:
            layout.prop(context.object, '["file_name"]', text='FileName')
        else:
            layout.operator('myaddon.add_filename')

class OBJECT_PT_tag_name(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_tag_name'
    bl_label = 'TagName'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        if 'tag_name' in context.object:
            layout.prop(context.object, '["tag_name"]', text='TagName')
        else:
            layout.operator('myaddon.add_tagname')

class OBJECT_PT_collider(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_collider'
    bl_label = 'Collider'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if 'collider' in obj:
            layout.prop(obj, 'collider_enum', text='Type')
            layout.prop(obj, '["collider_center"]', text='Center')
            if obj.collider_enum == 'Sphere':
                layout.prop(obj, '["collider_radius"]', text='Radius')
            else:
                layout.prop(obj, '["collider_size"]', text='Size')
        else:
            layout.operator('myaddon.add_collider')

_classes = (
    OBJECT_PT_file_name,
    OBJECT_PT_tag_name,
    OBJECT_PT_collider,
)

def register():
    for c in _classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
