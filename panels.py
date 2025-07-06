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

class OBJECT_PT_group_name(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_group_name'
    bl_label = 'GroupName'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        if 'group_name' in context.object:
            layout.prop(context.object, '["group_name"]', text='GroupName')
        else:
            layout.operator('myaddon.add_groupname')

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

class VIEW3D_PT_collider_editor(bpy.types.Panel):
    """View3D のサイドバーに配置する一括編集 UI"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_label = 'Collider Editor'

    def draw(self, ctx):
        layout = self.layout
        scn = ctx.scene
        
        row = layout.row()
        row.template_list("MYADDON_UL_collider_objs", "",scn, "coll_list",scn, "coll_index")

        col = row.column(align=True)
        col.operator("myaddon.refresh_colliders", text="", icon='FILE_REFRESH')

        # 詳細編集
        if 0 <= scn.coll_index < len(scn.coll_list):
            obj = bpy.data.objects[scn.coll_list[scn.coll_index].name]
            box = layout.box()
            box.prop(obj, "collider_enum", text="Type")
            box.prop(obj, '["collider_center"]', text="Center")
            if obj.collider_enum == 'Sphere':
                box.prop(obj, '["collider_radius"]', text="Radius")
            else:
                box.prop(obj, '["collider_size"]', text="Size")
            box.operator("myaddon.copy_collider_to_same", icon='CHECKMARK')

class MYADDON_UL_collider_objs(bpy.types.UIList):
    """同一アセットのインスタンスを行ごとに表示"""
    bl_idname = "MYADDON_UL_collider_objs"

    def draw_item(self, ctx, layout, _data, item, _icon, _act, _prop, _idx):
        obj = bpy.data.objects[item.name]
        row = layout.row(align=True)
        row.prop(obj, "name", text="", emboss=False, icon='OBJECT_DATA')
        row.prop(obj, "collider_enum", text="")

_classes = (
    OBJECT_PT_file_name,
    OBJECT_PT_group_name,
    OBJECT_PT_tag_name,
    OBJECT_PT_collider,
    MYADDON_UL_collider_objs,
    VIEW3D_PT_collider_editor,
)

def register():
    for c in _classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
