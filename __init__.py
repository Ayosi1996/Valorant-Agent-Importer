bl_info = {
    "name" : "Valorant Agents Importer",
    "author" : "sqrt9",
    "description" : "",
    "blender" : (3, 6, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy
import importlib
from . import bone_map
from . import valorant_agents_importer
from . import importer_panel

# When main is already in local, we know this is not the initial import...
if "valorant_agents_importer" in locals():    
    importlib.reload(valorant_agents_importer)

if "importer_panel" in locals():
    importlib.reload(importer_panel)

if "bone_map" in locals():
    importlib.reload(bone_map)

from . valorant_agents_importer import   (
                        SETUP_CONFIG,
                        SETUP_SOURCE_MODEL, 
                        SETUP_METARIG,
                        FIX_FP_BONE,
                        FIX_TP_BONE,
                        SETUP_RIGIFY,
                        COPY_RIGIFY_TO_SRC,
                        )

from . importer_panel import (OHI_PT_Panel, QueryProps)

from . bone_map import *

valorant_agents_importer.init(bone_map.src_bone_to_rigify_fp, bone_map.metarig_to_src_bone_fp, bone_map.src_bone_to_rigify_tp, bone_map.metarig_to_src_bone_tp)

classes = (SETUP_CONFIG,
            SETUP_SOURCE_MODEL,
            SETUP_METARIG,

            FIX_FP_BONE,
            FIX_TP_BONE,
            SETUP_RIGIFY,
            COPY_RIGIFY_TO_SRC,

            OHI_PT_Panel,
            QueryProps)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.QueryProps = bpy.props.PointerProperty(type=QueryProps)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del(bpy.types.Scene.QueryProps)