import webbrowser
from datetime import date

import bpy
import toml

from .register_class import _get_cls

INFO_TOML = "info.toml"


def get_info_toml(force: bool = False):
    """INFO_TOML取得

    :param force: 存在しなければ作成する, defaults to False
    :return: Textオブジェクト
    """
    txt = bpy.data.texts.get(INFO_TOML)
    if not txt:
        txt = bpy.data.texts.new(INFO_TOML)
        txt.write(toml.dumps(dict(url="", date="", author="", tag="")))
        if scr := bpy.data.screens.get("Scripting"):
            if area := next(iter(a for a in scr.areas if a.type == "TEXT_EDITOR"), None):
                area.spaces[0].text = txt
    return txt


class COU_OT_add_url(bpy.types.Operator):
    bl_idname = "object.add_url"
    bl_label = "Add URL"
    bl_description = "Add URL of clipboard."

    def execute(self, context):
        s = bpy.context.window_manager.clipboard
        if not (isinstance(s, str) and s.startswith("http")):
            self.report({"WARNING"}, "You must copy URL.")
            return {"CANCELLED"}
        txt = get_info_toml(True)
        dc = toml.loads(txt.as_string())
        dc["url"] = " ".join(set(dc.get("url", "").split()) | {s})
        dc["date"] = date.today()
        txt.clear()
        txt.write(toml.dumps(dc))
        return {"FINISHED"}


class COU_OT_open_urls(bpy.types.Operator):
    bl_idname = "object.open_urls"
    bl_label = "Open URLs"
    bl_description = "Open the URLs of info.toml."

    def execute(self, context):
        if not (txt := get_info_toml()):
            self.report({"WARNING"}, "No URLs")
            return {"CANCELLED"}
        dc = toml.loads(txt.as_string())
        for url in dc.get("url", "").split():
            webbrowser.open(url)
        return {"FINISHED"}


# 自動的にこのモジュールのクラスを設定
ui_classes = _get_cls(__name__)


def draw_item(self, context):
    """メニューの登録と削除用"""
    for ui_class in ui_classes:
        self.layout.operator(ui_class.bl_idname)


def register():
    """追加登録用（クラス登録は、register_class内で実行）"""
    bpy.types.VIEW3D_MT_object.append(draw_item)


def unregister():
    """追加削除用（クラス削除は、register_class内で実行）"""
    bpy.types.VIEW3D_MT_object.remove(draw_item)
