import bpy
import math

src_bone_to_rigify = None
metarig_to_src_bone = None

src_bone_to_rigify_fp = None
metarig_to_src_bone_fp = None
src_bone_to_rigify_tp = None
metarig_to_src_bone_tp = None

def init(rigify_fp, metarig_fp, rigify_tp, metarig_tp):
    global src_bone_to_rigify_fp
    global metarig_to_src_bone_fp
    global src_bone_to_rigify_tp
    global metarig_to_src_bone_tp

    src_bone_to_rigify_fp = rigify_fp
    metarig_to_src_bone_fp = metarig_fp
    src_bone_to_rigify_tp = rigify_tp
    metarig_to_src_bone_tp = metarig_tp

from bpy.types import Operator

meta_rig = "metarig"
rigify_rig = "rig"
src_skeleton_name = None

def edit_rig(rig_name):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    target_rig = bpy.data.objects[rig_name]
    target_rig.select_set(state=True)
    bpy.context.view_layer.objects.active = target_rig
    bpy.ops.object.mode_set(mode = 'EDIT')

class SETUP_CONFIG(Operator):
    bl_idname = "object.setup_config"
    bl_label = "Setup Config"
    bl_description = "setup bone map by model type."

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global src_skeleton_name
        global src_bone_to_rigify
        global metarig_to_src_bone

        src_skeleton_name = context.scene.QueryProps.skeleton_name
    
        if context.scene.QueryProps.model_type == 'tp' :
            src_bone_to_rigify = src_bone_to_rigify_tp
            metarig_to_src_bone = metarig_to_src_bone_tp
            print('tp')
        elif context.scene.QueryProps.model_type == 'fp':
            src_bone_to_rigify = src_bone_to_rigify_fp
            metarig_to_src_bone = metarig_to_src_bone_fp
            print('fp')

        print("setup config!")
        return {'FINISHED'}

def clean_bone_layer():
    # todo: bone no layers attribute in 4.0.0
    # move unused bone to the last layer
    model_obj = bpy.data.objects[src_skeleton_name]
    model_obj.select_set(state = True)
    bpy.context.view_layer.objects.active = model_obj
    
    for pose_bone in bpy.context.active_object.pose.bones[:]:
        if pose_bone.name not in src_bone_to_rigify.keys():
            pose_bone.bone.layers[0] = False
            pose_bone.bone.layers[31] = True
    bpy.ops.object.mode_set(mode = 'OBJECT')
    print("seperate bone layer done!")

def apply_model_transform(import_args):
    model_obj = bpy.data.objects[src_skeleton_name]
    model_obj.select_set(state = True)
    bpy.context.view_layer.objects.active = model_obj
    bpy.ops.object.mode_set(mode = 'OBJECT')
    if '-r' in import_args:
        bpy.context.object.rotation_euler[2] = math.radians(-90)
    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)

    model_children = model_obj.children
    for child_obj in model_children:
        if child_obj.type == 'MESH':
            mesh_child = bpy.data.objects[child_obj.name]
            mesh_child.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh_child
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)

    print("mesh transform applied")

def fix_bone_for_cascadeur():
    # reparent spine1 to Pelvis
    edit_rig(src_skeleton_name)
    edit_bones = bpy.data.objects[src_skeleton_name].data.edit_bones
    edit_bones['Spine1'].parent = edit_bones['Pelvis']

    offset = 0.05
    # fix head, toe direction
    head_bone = edit_bones['Head']
    head_copy = head_bone.head.copy()
    head_bone.tail[1] = head_copy[1]
    head_bone.tail[2] = head_copy[2] + offset

    toe_bone = edit_bones['L_Toe']
    toe_head_copy = toe_bone.head.copy()
    toe_bone.tail[0] = toe_head_copy[0]
    toe_bone.tail[1] = toe_head_copy[1] - offset

    toe_bone = edit_bones['R_Toe']
    toe_head_copy = toe_bone.head.copy()
    toe_bone.tail[0] = toe_head_copy[0]
    toe_bone.tail[1] = toe_head_copy[1] - offset

class SETUP_SOURCE_MODEL(Operator):
    bl_idname = "object.setup_source_model"
    bl_label = "Setup Source Model"
    bl_description = "1.clean bone layer \n2.apply bone transform \n3.fix bone tail pos for cascadeur"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        import_args = context.scene.QueryProps.import_args
        # clean_bone_layer()
        apply_model_transform(import_args)
        fix_bone_for_cascadeur()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
        return {'FINISHED'}

def create_metarig():
    bpy.ops.object.armature_human_metarig_add()
    bpy.ops.pose.rigify_upgrade_face()
    print("meta-rig created!")

def copy_src_bone_to_metarig():
    src_bone_data = {}
    meta_bone_data = {}
    edit_rig(src_skeleton_name)
    # save source model bone data
    for bone in bpy.data.objects[src_skeleton_name].data.edit_bones:
        if bone.name not in metarig_to_src_bone.values():
            continue

        # save a copy of source bone data
        src_bone_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)

    edit_rig(meta_rig)
    for bone in bpy.data.objects[meta_rig].data.edit_bones:
        if bone.name == 'spine.004':
            bone.use_connect = True

        # save a copy of metarig bone data
        meta_bone_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)

    edit_rig(meta_rig)
    for bone in bpy.data.objects[meta_rig].data.edit_bones:
        if bone.name not in metarig_to_src_bone.keys():
            continue

        bone.head, bone.tail, bone.roll = src_bone_data[metarig_to_src_bone[bone.name]]

    # handle rest bone
    edit_rig(meta_rig)
    all_bones = bpy.data.objects[meta_rig].data.edit_bones
    for bone in all_bones:
        if (bone is not None) and (bone.name not in metarig_to_src_bone.keys()) and (bone.parent is not None):
            target_parent = bone.parent
            while target_parent is not None and (target_parent.name not in metarig_to_src_bone.keys()):
                target_parent = target_parent.parent

            if target_parent is None:
                continue

            ori_head_offset = meta_bone_data[bone.name][0] - meta_bone_data[target_parent.name][0]
            ori_tail_offset = meta_bone_data[bone.name][1] - meta_bone_data[target_parent.name][0]

            bone.head = all_bones[target_parent.name].head.copy() + ori_head_offset
            bone.tail = all_bones[target_parent.name].head.copy() + ori_tail_offset

    edit_rig(meta_rig)
    for b in bpy.data.objects[meta_rig].data.edit_bones:        
        if b.name == 'spine.004':
            b.use_connect = False
            break

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
    bpy.context.object.show_in_front = True

    print("source bone data copy to meta rig, you can generate rigify now!")

class SETUP_METARIG(Operator):
    bl_idname = "object.setup_metarig"
    bl_label = "Setup Metarig"
    bl_description = "create meta rig and copy valorant rest pose to meta rig."

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        create_metarig()
        copy_src_bone_to_metarig()
        return {'FINISHED'}

def fix_fp_bones(dir, all_bones):
    palm_01 = all_bones['palm.01.' + dir]
    palm_02 = all_bones['palm.02.' + dir]
    palm_03 = all_bones['palm.03.' + dir]
    palm_04 = all_bones['palm.04.' + dir]

    hand = all_bones['hand.' + dir]
    hand.tail = (palm_01.tail.copy() + palm_02.tail.copy() + palm_03.tail.copy() + palm_04.tail.copy() + hand.head.copy()) / 5

class FIX_FP_BONE(Operator):
    bl_idname = "object.fix_fp_bone"
    bl_label = "Fix FP Bone"
    bl_description = "Just click, it's ok."

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.scene.QueryProps.model_type == 'tp' :
            return

        edit_rig(meta_rig)
        all_bones = bpy.data.objects[meta_rig].data.edit_bones

        fix_fp_bones('L', all_bones)
        fix_fp_bones('R', all_bones)

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
        return {'FINISHED'}

def fix_tp_bones(dir, all_bones):
    palm_01 = all_bones['palm.01.' + dir]
    palm_02 = all_bones['palm.02.' + dir]
    palm_03 = all_bones['palm.03.' + dir]
    palm_04 = all_bones['palm.04.' + dir]

    index_01 = all_bones['f_index.01.' + dir]
    middle_01 = all_bones['f_middle.01.' + dir]
    ring_01 = all_bones['f_ring.01.' + dir]
    pinky_01 = all_bones['f_pinky.01.' + dir]

    hand = all_bones['hand.' + dir]

    hand.tail = (index_01.head.copy() + middle_01.head.copy() + ring_01.head.copy() + pinky_01.head.copy() + hand.head.copy()) / 5
    palm_01.tail = index_01.head.copy()
    palm_02.tail = middle_01.head.copy()
    palm_03.tail = ring_01.head.copy()
    palm_04.tail = pinky_01.head.copy()

    palm_01.head = hand.tail
    palm_02.head = hand.tail
    palm_03.head = hand.tail
    palm_04.head = hand.tail

class FIX_TP_BONE(Operator):
    bl_idname = "object.fix_tp_bone"
    bl_label = "Fix TP Bone"
    bl_description = "Just click, it's ok."

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.scene.QueryProps.model_type == 'fp' :
            return
        
        edit_rig(meta_rig)
        all_bones = bpy.data.objects[meta_rig].data.edit_bones

        fix_tp_bones('L', all_bones)
        fix_tp_bones('R', all_bones)

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
        return {'FINISHED'}

############### generate rigify manually ###############

def copy_rigify_to_src_bone():
    rigify_bone_data = {}
    edit_rig(rigify_rig)
    for bone in bpy.data.objects[rigify_rig].data.edit_bones:
        if bone.name not in src_bone_to_rigify.values():
            continue
        rigify_bone_data[bone.name] = (bone.head.copy(), bone.tail.copy(), bone.roll)

    edit_rig(src_skeleton_name)
    for bone in bpy.data.objects[src_skeleton_name].data.edit_bones:
        if bone.name not in src_bone_to_rigify.keys():
            continue
        bone.head, bone.tail, bone.roll = rigify_bone_data[src_bone_to_rigify[bone.name]]

    bpy.ops.object.mode_set(mode = 'OBJECT')
    print("copy from rigify to source bone done!")
    return {'FINISHED'}

def src_bone_add_constraints():
    bpy.context.view_layer.objects.active = bpy.data.objects[src_skeleton_name]
    bpy.ops.object.mode_set(mode = 'POSE')
    bpy.ops.pose.select_all(action = 'SELECT')
    all_select_bones = bpy.context.selected_pose_bones
    scene = bpy.context.scene
    target_rig = scene.objects.get(rigify_rig)

    for bone in all_select_bones:
        if bone.name not in src_bone_to_rigify.keys():
            continue
        trans_cons = bone.constraints.new('COPY_TRANSFORMS')
        trans_cons.target = target_rig
        trans_cons.subtarget = src_bone_to_rigify[bone.name]

    bpy.ops.object.mode_set(mode = 'OBJECT')
    print("source bone add constraints done!")

class SETUP_RIGIFY(Operator):
    bl_idname = "object.setup_rigify"
    bl_label = "Setup Rigify"
    bl_description = "bind source bone to rigify bone"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        copy_rigify_to_src_bone()
        src_bone_add_constraints()
        return {'FINISHED'}

class COPY_RIGIFY_TO_SRC(Operator):
    bl_idname = "object.copy_rigify_to_src"
    bl_label = "Copy Rigify To Src"
    bl_description = bl_label

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        copy_rigify_to_src_bone()
        return {'FINISHED'}