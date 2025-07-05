import bpy, json, math, mathutils, copy, os
import bpy_extras,addon_utils

# ------------------------ 汎用ヘルパ ------------------------

def _write_and_print(file, line):
    print(line)
    file.write(line + '\n')

# ------------------------ 基本オペレータ ------------------------
    
def ensure_obj_import_enabled():
    # アドオンが無効なら有効化
    addon_utils.enable("io_scene_obj", default_set=True, persistent=True)

class MYADDON_OT_add_tower_windmill(bpy.types.Operator):
    """TowerWindmill.obj をシーンインポート"""
    bl_idname = 'myaddon.add_tower_windmill'
    bl_label = '風車を生成'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import os
        ensure_obj_import_enabled()
        obj_path = os.path.join(os.path.dirname(__file__), "assets/", "TowerWindmill.obj")

        if not os.path.exists(obj_path):
            self.report({'ERROR'}, f"OBJ not found: {obj_path}")
            return {'CANCELLED'}
        
        before = set(bpy.context.scene.objects)

        # 既定の OBJ インポートオペレータを呼び出す
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(
                filepath=obj_path,
                forward_axis='Z',
                up_axis='Y',
            )

        # 生成した風車のObjectの回転を無くす
        imported = context.selected_objects
        if imported:
            context.view_layer.objects.active = imported[0]
            bpy.ops.object.transform_apply(rotation=True)
            for obj in imported:
                # すでに別の値があれば上書きしない
                obj["tag_name"] = "FieldObject"
                obj["file_name"] = os.path.basename(obj_path)

        return {'FINISHED'}

# ------------------------ シーン Export ------------------------

class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = 'myaddon.export_scene'
    bl_label = 'シーン出力'
    filename_ext = '.json'

    # ------ コア処理 ------

    def execute(self, context):
        self.export_json()
        self.report({'INFO'}, 'シーン情報をExportしました')
        return {'FINISHED'}

    # ------ テキスト形式ダンプ (省略版) ------

    def _export_text(self, file):
        for obj in bpy.context.scene.objects:
            if obj.parent:
                continue
            self._parse_recursive_text(file, obj, 0)

    def _parse_recursive_text(self, file, obj, level):
        indent = '\t' * level
        _write_and_print(file, f'{indent}{obj.type}')
        # ... 以降、省略 ...

    # ------ JSON 出力 ------

    def export_json(self):
        root = {'name': 'scene', 'objects': []}
        for obj in bpy.context.scene.objects:
            if obj.parent:
                continue
            self._parse_recursive_json(root['objects'], obj)

        with open(self.filepath, 'wt', encoding='utf-8') as f:
            json.dump(root, f, ensure_ascii=False, indent=4)

    def _parse_recursive_json(self, parent, obj):
        node = {
            'type': obj.type,
            'name': obj.name,
        }
        parent.append(node)

        trans, rot, scale = obj.matrix_local.decompose()
        rot = rot.to_euler()
        node['transform'] = {
            'translation': (trans.x, trans.y, trans.z),
            'rotation': (math.degrees(rot.x), math.degrees(rot.y), math.degrees(rot.z)),
            'scaling': (scale.x, scale.y, scale.z),
        }

        if 'file_name' in obj:
            node['file_name'] = obj['file_name']
        if 'tag_name' in obj:
            node['tag_name'] = obj['tag_name']

        if 'collider' in obj:
            col = {'type': obj['collider']}
            if col['type'] == 'Sphere':
                col['radius'] = obj.get('collider_radius', 1.0)
                col['center'] = obj.get('collider_center', (0,0,0))
            else:
                col['size'] = obj.get('collider_size', (2,2,2))
                col['center'] = obj.get('collider_center', (0,0,0))
            node['collider'] = col

        if obj.children:
            node['children'] = []
            for ch in obj.children:
                self._parse_recursive_json(node['children'], ch)

# ------------------------ Custom‑Property 追加 ------------------------

class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = 'myaddon.add_filename'
    bl_label = 'FileName 追加'
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        context.object['file_name'] = ''
        return {'FINISHED'}

class MYADDON_OT_add_tagname(bpy.types.Operator):
    bl_idname = 'myaddon.add_tagname'
    bl_label = 'TagName 追加'
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        context.object['tag_name'] = ''
        return {'FINISHED'}

class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = 'myaddon.add_collider'
    bl_label = 'Collider 追加'
    bl_options = {'REGISTER','UNDO'}

    def execute(self, context):
        obj = context.object
        obj['collider'] = obj.get('collider', 'Box')
        obj['collider_center'] = mathutils.Vector((0,0,0))
        if obj['collider'] == 'Sphere':
            obj['collider_radius'] = 1.0
        else:
            obj['collider_size'] = mathutils.Vector((2,2,2))
        return {'FINISHED'}

# ------------------------ Register Helper ------------------------

_classes = (
    MYADDON_OT_export_scene,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_tagname,
    MYADDON_OT_add_collider,
    MYADDON_OT_add_tower_windmill,
)

def register():
    for c in _classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
