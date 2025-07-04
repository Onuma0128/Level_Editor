import bpy
from .operators import (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene
)

class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = 'TOPBAR_MT_my_menu'
    bl_label = 'MyMenu'

    def draw(self, context):
        layout = self.layout
        layout.operator('wm.url_open_preset', text='Manual', icon='HELP')
        layout.operator(MYADDON_OT_stretch_vertex.bl_idname, text=MYADDON_OT_stretch_vertex.bl_label)
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text=MYADDON_OT_create_ico_sphere.bl_label)
        layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)

    @classmethod
    def poll(cls, _context):
        return True

def draw_in_topbar(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

def register():
    bpy.utils.register_class(TOPBAR_MT_my_menu)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_in_topbar)

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_in_topbar)
    bpy.utils.unregister_class(TOPBAR_MT_my_menu)
