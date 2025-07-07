import importlib,bpy

# Blender アドオン情報
bl_info = {
    "name": "レベルエディタ (分割版)",
    "author": "Taro Kamata",
    "version": (1, 1),
    "blender": (3, 3, 1),
    "description": "レベルエディタをモジュール毎に分割したサンプル",
    "category": "Object",
}

# サブモジュールを読み込み
from . import properties, operators, panels, draw_collider, menu

# 再読み込み時にキャッシュをクリア
modules = [properties, operators, panels, draw_collider, menu]
def _reload_modules():
    global modules
    # いったん全部 reload して、リストも最新のモジュール参照に差し替える
    modules = [importlib.reload(m) for m in modules]

def register():
    _reload_modules()
    for m in modules:
        m.register()
    print("レベルエディタ (分割版) が有効化されました。")


def unregister():
    for m in reversed(modules):
        m.unregister()
    print("レベルエディタ (分割版) が無効化されました。")

if __name__ == '__main__':
    register()
