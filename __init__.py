import importlib

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
for m in modules:
    importlib.reload(m)

def register():
    for m in modules:
        m.register()
    print("レベルエディタ (分割版) が有効化されました。")

def unregister():
    for m in reversed(modules):
        m.unregister()
    print("レベルエディタ (分割版) が無効化されました。")

if __name__ == '__main__':
    register()
