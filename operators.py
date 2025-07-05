import bpy, json, math, mathutils, copy, os
import bpy_extras,addon_utils

# ------------------------ 汎用ヘルパ ------------------------

def _write_and_print(file, line):
    print(line)
    file.write(line + '\n')

# ------------------------ ファイル読み込み ------------------------

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
EXT_OK    = (".obj", ".gltf", ".glb")

def _enum_assets(_, __):
    items = []
    for fname in sorted(os.listdir(ASSET_DIR)):
        if fname.lower().endswith(EXT_OK):
            label = os.path.splitext(fname)[0]
            items.append((fname, label, ""))
    return items or [("", "<empty>", "")]

# ------------------------ 基本オペレータ ------------------------

class MYADDON_OT_add_asset(bpy.types.Operator):
    """assets フォルダーからアセットをインポート"""
    bl_idname = 'myaddon.add_asset'
    bl_label = 'FiledObjectを生成'
    bl_options = {'REGISTER', 'UNDO'}

    # ここが選択用プロパティ
    asset_name: bpy.props.EnumProperty(name="Asset",description="インポートする OBJ",items=_enum_assets)

    def execute(self, context):
        # パスを生成
        obj_path = os.path.join(ASSET_DIR, self.asset_name)
        if not os.path.exists(obj_path):
            self.report({'ERROR'}, f"Not found: {obj_path}")
            return {'CANCELLED'}

        ext = os.path.splitext(obj_path)[1].lower()

        # インポートを実行
        if ext == ".obj":
            addon_utils.enable("io_scene_obj", default_set=True, persistent=True)
            bpy.ops.wm.obj_import(
                filepath=obj_path,
                forward_axis='NEGATIVE_Z',
                up_axis='Y')
        elif ext in {".gltf", ".glb"}:
            addon_utils.enable("io_scene_gltf2", default_set=True, persistent=True)
            bpy.ops.import_scene.gltf(filepath=obj_path)
        else:
            self.report({'ERROR'}, f"Unsupported: {ext}")
            return {'CANCELLED'}

        # 回転とカスタムプロパティを初期化
        imported = context.selected_objects
        if imported:
            context.view_layer.objects.active = imported[0]
            bpy.ops.object.transform_apply(rotation=True)
            for obj in imported:
                obj.rotation_mode = 'XYZ'
                obj["tag_name"]  = "FieldObject"
                obj["file_name"] = self.asset_name
                obj['collider'] = obj.get('collider', 'Box')
                obj['collider_center'] = mathutils.Vector((0,0,0))
                obj['collider_size'] = mathutils.Vector((2,2,2))

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
            center = tuple(obj.get('collider_center', (0,0,0)))
            col['center'] = center

            sx, sy, sz = obj.matrix_local.to_scale()
            if col['type'] == 'Sphere':
                r = obj.get('collider_radius', 1.0)
                col['radius'] = r * max(sx, sy, sz)
            else:
                size = tuple(obj.get('collider_size', (2,2,2)))
                size_scaled = tuple(v * 0.5 for v in size)
                size = obj.get('collider_size', (2, 2, 2))
                # Half-extent にして、各軸のスケールを掛ける
                col['size'] = (
                    size[0] * sx * 0.5,
                    size[1] * sy * 0.5,
                    size[2] * sz * 0.5,
                )
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

class MYADDON_OT_refresh_colliders(bpy.types.Operator):
    bl_idname = "myaddon.refresh_colliders"
    bl_label  = "リスト更新"
    bl_options = {'REGISTER','UNDO'}

    def execute(self, ctx):
        col = ctx.scene.coll_list
        col.clear()
        active = ctx.view_layer.objects.active
        if not active:
            self.report({'WARNING'}, "アクティブなオブジェクトがありません")
            return {'CANCELLED'}

        key = active.get("file_name", active.data.name)
        for obj in bpy.data.objects:
            if ('collider' in obj and
                obj.get("file_name", obj.data.name) == key):
                item = col.add()
                item.name = obj.name
        return {'FINISHED'}


class MYADDON_OT_copy_collider_to_same(bpy.types.Operator):
    """編集中インスタンスの collider 値を同アセットの全インスタンスへコピー"""
    bl_idname = "myaddon.copy_collider_to_same"
    bl_label  = "Apply to Same Asset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, ctx):
        col = ctx.scene.coll_list
        if not col or ctx.scene.coll_index < 0:
            self.report({'WARNING'}, "リストが空です")
            return {'CANCELLED'}

        src = bpy.data.objects[col[ctx.scene.coll_index].name]
        key = src.get("file_name", src.data.name)
        for obj in bpy.data.objects:
            if obj is src:
                continue
            if obj.get("file_name", obj.data.name) != key:
                continue
            for k in ('collider', 'collider_center', 'collider_size', 'collider_radius'):
                if k in src:
                    obj[k] = src[k]

            collider_enum_sync(obj)
        return {'FINISHED'}

# ------------------------ Register Helper ------------------------

_classes = (
    MYADDON_OT_export_scene,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_tagname,
    MYADDON_OT_add_collider,
    MYADDON_OT_add_asset,
    MYADDON_OT_refresh_colliders,
    MYADDON_OT_copy_collider_to_same,
)

def register():
    for c in _classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
