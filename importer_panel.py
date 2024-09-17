import bpy

from bpy.types import Panel

class QueryProps(bpy.types.PropertyGroup):
    skeleton_name: bpy.props.StringProperty(default="", description = "agent bone root name")
    model_type: bpy.props.StringProperty(default="tp", description = "tp/fp. means third person or first person.")
    import_args: bpy.props.StringProperty(default="", description = "-r : rotate skeleton 90 along Y asix before apply transform.")

class OHI_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Valorant agents importer operations"
    bl_category = "VAI"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.QueryProps

        row = layout.row()
        col = layout.column()

        tips1 = "使用前请启用Rigify插件!"
        tips2 = "导入模型前删除所有物体!"
        tips5 = "Mesh需要是Skeleton的子物体"
        tips3 = "下一步之前先Rigify生成!"
        tips4 = "修复Metarig Bones"

        col.label(text = tips1, icon = "ERROR")
        col.label(text = tips2, icon = "ERROR")
        col.label(text = tips5, icon = "ERROR")

        rowsub = col.row(align=True)
        rowsub.prop(props, "skeleton_name", text="Skeleton Name")
        rowsub = col.row(align=True)
        rowsub.prop(props, "model_type", text="Model Type")
        rowsub = col.row(align=True)
        rowsub.prop(props, "import_args", text="Import Args")

        col.separator()
        col.operator("object.setup_config", text = "1. Setup Config")
        col.operator("object.setup_source_model", text = "2. Setup Model")
        col.operator("object.setup_metarig", text = "3. Setup Metarig")

        col.separator()
        col.label(text = tips4, icon = "ERROR")
        col.operator("object.fix_fp_bone", text = "4. Fix FP Metarig")
        col.operator("object.fix_tp_bone", text = "4. Fix TP Metarig")

        col.separator()
        col.label(text = tips3, icon = "ERROR")
        #col.operator("object.copy_rigify_to_src", text = "Copy Rigify To Src")
        col.operator("object.setup_rigify", text = "5. Setup Rigify")