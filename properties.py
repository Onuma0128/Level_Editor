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

def collider_enum_sync(obj):
    """CustomProperty → EnumProperty へ値を写す"""
    if 'collider' in obj:
        try:
            obj.collider_enum = obj['collider']   # 'Box' / 'Sphere'
        except AttributeError:
            pass

# Collider Editorで選択が変わった瞬間に呼ばれる
def _on_coll_index_update(self, context):
    lst = context.scene.coll_list
    idx = self.coll_index
    if 0 <= idx < len(lst):
        obj = bpy.data.objects[lst[idx].name]
        # すべての選択を解除してから
        for o in context.selected_objects:
            o.select_set(False)
        # 行に対応するオブジェクトを選択・アクティブ化
        obj.select_set(True)
        context.view_layer.objects.active = obj

# 双方向で同期させる
def _sync_list_from_selection(_scene):
    ctx = bpy.context
    act = ctx.view_layer.objects.active
    if not act:
        return
    lst = ctx.scene.coll_list
    for i, item in enumerate(lst):
        if item.name == act.name and ctx.scene.coll_index != i:
            ctx.scene.coll_index = i
            break

# Collider Editorのアクティブオブジェクトからリストを組み直す
def _rebuild_coll_list_from_active(context):
    """
    アクティブオブジェクトと同じ ‘asset key’ を持つものだけで
    scene.coll_list を再構築する
    """
    active = context.view_layer.objects.active
    col    = context.scene.coll_list

    # アクティブが無いColliderを持たない時は空リストにする
    if not active or 'collider' not in active:
        col.clear()
        context.scene.coll_index = -1
        return

    key = active.get("file_name", active.data.name)

    # すでに同じkeyで構築済みなら何もしない
    if len(col) and bpy.data.objects[col[0].name].get("file_name", col[0].name) == key:
        return

    # 再構築
    col.clear()
    for obj in bpy.data.objects:
        if obj.get("file_name", obj.data.name) == key and 'collider' in obj:
            item = col.add()
            item.name = obj.name

    # 行選択をアクティブに合わせる
    for i, item in enumerate(col):
        if item.name == active.name:
            context.scene.coll_index = i
            break
    else:
        context.scene.coll_index = -1

# オブジェクトの更新ごとに実行
def _auto_refresh_coll_list(scene):
    ctx = bpy.context
    _rebuild_coll_list_from_active(ctx)

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
    bpy.types.Object.collider_enable = bpy.props.BoolProperty(
        name = 'Enable',
        description = 'Enable collider drawing and export',
        default = True
    )
    bpy.types.Object.enable_from_export = bpy.props.BoolProperty(
        name = 'Enable',
        description='このオブジェクトをエクスポートするか',
        default = True
    )
    bpy.types.Scene.coll_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.coll_index = bpy.props.IntProperty(update=_on_coll_index_update)
    bpy.app.handlers.depsgraph_update_post.append(_sync_list_from_selection)
    bpy.app.handlers.depsgraph_update_post.append(_auto_refresh_coll_list)

def unregister():
    del bpy.types.Object.collider_enum
    del bpy.types.Scene.coll_list
    del bpy.types.Scene.coll_index
    bpy.app.handlers.depsgraph_update_post.remove(_sync_list_from_selection)
    bpy.app.handlers.depsgraph_update_post.remove(_auto_refresh_coll_list)
