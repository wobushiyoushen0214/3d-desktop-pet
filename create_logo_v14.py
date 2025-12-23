import bpy
import math
import os

# --- 配置 ---
BLEND_SAVE_PATH = os.path.abspath("logo_model_v13.blend")
GLB_EXPORT_PATH = os.path.abspath("public/logo_animated.glb")

# --- 清理场景 ---
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 清理未使用的 data blocks
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)
for block in bpy.data.curves:
    if block.users == 0:
        bpy.data.curves.remove(block)
for block in bpy.data.actions:
    if block.users == 0:
        bpy.data.actions.remove(block)
for block in bpy.data.armatures:
    if block.users == 0:
        bpy.data.armatures.remove(block)

# --- 材质 ---
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.4
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

blue_mat = create_material("BlueMat", (0.0, 0.4, 1.0, 1.0))
green_mat = create_material("GreenMat", (0.6, 0.8, 0.0, 1.0))
face_mat = create_material("FaceMat", (0.1, 0.1, 0.1, 1.0))

# --- 创建矩形截面曲线 ---
def create_rect_profile(name, width, height):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '2D'
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    spline = curve_data.splines.new(type='POLY')
    w = width / 2
    h = height / 2
    spline.points.add(3)
    spline.points[0].co = (w, h, 0, 1)
    spline.points[1].co = (-w, h, 0, 1)
    spline.points[2].co = (-w, -h, 0, 1)
    spline.points[3].co = (w, -h, 0, 1)
    spline.use_cyclic_u = True
    
    curve_obj.hide_viewport = True
    curve_obj.hide_render = True
    return curve_obj

profile_obj = create_rect_profile("RectProfile", 0.5, 0.15)

# --- 创建波浪函数 ---
def create_wave(name, z_offset, points_coords):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = profile_obj
    
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(len(points_coords) - 1)
    
    for i, coord in enumerate(points_coords):
        bp = spline.bezier_points[i]
        bp.co = (coord[0], coord[1], coord[2] + z_offset)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        bp.radius = 1.0
    
    curve_obj.data.materials.append(blue_mat)
    return curve_obj

wave_points = [
    (-1.6, 0, -0.2), 
    (-0.3, 0, 0.6),  
    (0.6, 0, 0.1)
]

wave1 = create_wave("Wave1", 0.0, wave_points)
wave2 = create_wave("Wave2", -0.45, wave_points)

# 转换为 Mesh
for obj in [wave1, wave2]:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')

# --- 创建圆球 (头部) ---
head_loc = (-0.3, 0, -0.9) 
HEAD_RADIUS = 0.38
bpy.ops.mesh.primitive_uv_sphere_add(radius=HEAD_RADIUS, location=head_loc)
head = bpy.context.active_object
head.name = "Head"
head.data.materials.append(green_mat)
bpy.ops.object.shade_smooth()

# --- 辅助函数：获取球体表面 Y 坐标 (局部) ---
def get_surface_y(x_local, z_local, radius):
    val = radius**2 - x_local**2 - z_local**2
    if val < 0: return 0
    return -math.sqrt(val)

# --- 创建五官 (使用局部坐标) ---
def create_eye(name, x_local, z_local):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0,0,0))
    eye = bpy.context.active_object
    eye.name = name
    eye.data.materials.append(face_mat)
    
    eye.parent = head
    eye.matrix_parent_inverse = head.matrix_world.inverted() 
    eye.location = (0, 0, 0)
    eye.rotation_euler = (0, 0, 0)
    eye.scale = (1, 1, 1)
    
    y_surface = get_surface_y(x_local, z_local, HEAD_RADIUS)
    eye.location = (x_local, y_surface + 0.02, z_local) 
    return eye

# 眼睛
create_eye("EyeL", -0.12, 0.05)
create_eye("EyeR", 0.12, 0.05)

# 嘴巴
bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.01, location=(0,0,0), rotation=(math.radians(90), 0, 0))
mouth = bpy.context.active_object
mouth.name = "Mouth"
mouth.data.materials.append(face_mat)

mouth.parent = head
mouth.location = (0, 0, 0)
mouth_z_local = -0.1
mouth_y_surface = get_surface_y(0, mouth_z_local, HEAD_RADIUS)
mouth.location = (0, mouth_y_surface + 0.005, mouth_z_local)
mouth.rotation_euler = (math.radians(90), 0, 0)

# --- 创建四肢 (使用局部坐标) ---
def create_limb(name, x_local, y_local, z_local):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0,0,0))
    limb = bpy.context.active_object
    limb.name = name
    limb.data.materials.append(green_mat)
    
    limb.parent = head
    limb.location = (x_local, y_local, z_local)
    return limb

# 手
hand_x = HEAD_RADIUS + 0.02
hand_l = create_limb("HandL", -hand_x, 0, -0.1)
hand_r = create_limb("HandR", hand_x, 0, -0.1)

# 脚
create_limb("FootL", -0.15, -0.3, -0.4)
create_limb("FootR", 0.15, -0.3, -0.4)


# --- 骨骼绑定 ---
bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0,0,0))
armature = bpy.context.object
armature.name = "Armature"
amt = armature.data

root_bone = amt.edit_bones.new('Root')
root_bone.head = (0, 0, 0)
root_bone.tail = (0, 0, 1)

body_bone = amt.edit_bones.new('Body')
body_bone.head = head_loc
body_bone.tail = (head_loc[0], head_loc[1], head_loc[2] + 0.5)
body_bone.parent = root_bone

wave1_bone = amt.edit_bones.new('Wave1')
wave1_bone.head = (-0.3, 0, 0.6)
wave1_bone.tail = (-0.3, 0, 1.0)
wave1_bone.parent = root_bone

wave2_bone = amt.edit_bones.new('Wave2')
wave2_bone.head = (-0.3, 0, 0.15)
wave2_bone.tail = (-0.3, 0, 0.55)
wave2_bone.parent = root_bone

# 为四肢创建骨骼 (为了 Greet 动画)
# 这里我们只需要给右手建一个骨骼来控制挥手，其他的跟随 Body
hand_r_bone = amt.edit_bones.new('HandR')
hand_r_bone.head = (head_loc[0] + hand_x, head_loc[1], head_loc[2] - 0.1)
hand_r_bone.tail = (head_loc[0] + hand_x + 0.2, head_loc[1], head_loc[2] - 0.1)
hand_r_bone.parent = body_bone

bpy.ops.object.mode_set(mode='OBJECT')

# 绑定 Mesh
for obj in [wave1, wave2]:
    obj.parent = armature
    mod = obj.modifiers.new(type='ARMATURE', name="Armature")
    mod.object = armature
    vg = obj.vertex_groups.new(name=obj.name) 
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')

head.parent = armature
mod = head.modifiers.new(type='ARMATURE', name="Armature")
mod.object = armature
vg = head.vertex_groups.new(name="Body")
vg.add([v.index for v in head.data.vertices], 1.0, 'REPLACE')

# 右手绑定到 HandR 骨骼
# 首先确保 HandR 对象只受 HandR 骨骼影响
hand_r.parent = armature
mod = hand_r.modifiers.new(type='ARMATURE', name="Armature")
mod.object = armature
vg = hand_r.vertex_groups.new(name="HandR")
vg.add([v.index for v in hand_r.data.vertices], 1.0, 'REPLACE')

# 其他肢体跟随 Body (通过 parent 继承)
# 修正：将所有四肢也绑定到骨骼上。

# 获取所有四肢对象
hand_l = bpy.data.objects.get("HandL")
foot_l = bpy.data.objects.get("FootL")
foot_r = bpy.data.objects.get("FootR")

for obj in [hand_l, foot_l, foot_r]:
    if obj:
        # 解除之前的 parent (head)，改为 armature
        obj.parent = armature
        # 添加修改器
        mod = obj.modifiers.new(type='ARMATURE', name="Armature")
        mod.object = armature
        # 添加顶点组，绑定到 Body 骨骼
        vg = obj.vertex_groups.new(name="Body")
        vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')

# 眼睛嘴巴也是一样，需要绑定到 Body
for obj_name in ["EyeL", "EyeR", "Mouth"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.parent = armature
        mod = obj.modifiers.new(type='ARMATURE', name="Armature")
        mod.object = armature
        vg = obj.vertex_groups.new(name="Body")
        vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')


# --- 动画 ---
bpy.ops.object.mode_set(mode='POSE')
armature.animation_data_create()

# 获取骨骼 Pose
p_body = armature.pose.bones["Body"]
p_wave1 = armature.pose.bones["Wave1"]
p_wave2 = armature.pose.bones["Wave2"]
p_hand_r = armature.pose.bones["HandR"]

# 1. Idle (待机：呼吸 + 波浪轻微摆动)
action_idle = bpy.data.actions.new(name="Idle")
armature.animation_data.action = action_idle

# Frame 1
p_body.location.z = 0
p_body.scale = (1, 1, 1)
p_wave1.rotation_euler = (0, 0, 0)
p_wave2.rotation_euler = (0, 0, 0)
p_hand_r.rotation_euler = (0, 0, 0)

for b in [p_body, p_wave1, p_wave2, p_hand_r]:
    b.keyframe_insert("location", frame=1)
    b.keyframe_insert("scale", frame=1)
    b.keyframe_insert("rotation_euler", frame=1)

# Frame 30
p_body.location.z = 0.05
p_body.scale = (1.02, 1.02, 0.98) # 压扁一点点 (呼吸)
p_wave1.rotation_euler = (0, math.radians(5), 0) # 波浪摇摆
p_wave2.rotation_euler = (0, math.radians(-5), 0) # 反向摇摆

for b in [p_body, p_wave1, p_wave2]:
    b.keyframe_insert("location", frame=30)
    b.keyframe_insert("scale", frame=30)
    b.keyframe_insert("rotation_euler", frame=30)

# Frame 60
p_body.location.z = 0
p_body.scale = (1, 1, 1)
p_wave1.rotation_euler = (0, 0, 0)
p_wave2.rotation_euler = (0, 0, 0)

for b in [p_body, p_wave1, p_wave2]:
    b.keyframe_insert("location", frame=60)
    b.keyframe_insert("scale", frame=60)
    b.keyframe_insert("rotation_euler", frame=60)

track_idle = armature.animation_data.nla_tracks.new()
track_idle.name = "IdleTrack"
strip_idle = track_idle.strips.new(name="Idle", start=1, action=action_idle)

# 2. Jump (跳跃：360旋转 + 强挤压)
action_jump = bpy.data.actions.new(name="Jump")
armature.animation_data.action = action_jump

# Frame 1: 预备
p_body.location.z = 0
p_body.scale = (1.1, 1.1, 0.8) # 压扁蓄力
p_body.rotation_euler = (0, 0, 0)
p_body.keyframe_insert("location", frame=1)
p_body.keyframe_insert("scale", frame=1)
p_body.keyframe_insert("rotation_euler", frame=1)

# Frame 10: 起跳 & 旋转开始
p_body.location.z = 1.2
p_body.scale = (0.8, 0.8, 1.2) # 拉伸
p_body.rotation_euler = (0, 0, math.radians(180)) # 转一半
p_body.keyframe_insert("location", frame=10)
p_body.keyframe_insert("scale", frame=10)
p_body.keyframe_insert("rotation_euler", frame=10)

# Frame 20: 落地 & 旋转结束
p_body.location.z = 0
p_body.scale = (1.1, 1.1, 0.8) # 落地压扁
p_body.rotation_euler = (0, 0, math.radians(360)) # 转一圈
p_body.keyframe_insert("location", frame=20)
p_body.keyframe_insert("scale", frame=20)
p_body.keyframe_insert("rotation_euler", frame=20)

# Frame 30: 恢复
p_body.location.z = 0
p_body.scale = (1, 1, 1)
p_body.rotation_euler = (0, 0, 0) # 归零
p_body.keyframe_insert("location", frame=30)
p_body.keyframe_insert("scale", frame=30)
# p_body.keyframe_insert("rotation_euler", frame=30)

track_jump = armature.animation_data.nla_tracks.new()
track_jump.name = "JumpTrack"
strip_jump = track_jump.strips.new(name="Jump", start=1, action=action_jump)

# 3. Greet (打招呼：挥手)
action_greet = bpy.data.actions.new(name="Greet")
armature.animation_data.action = action_greet

# Frame 1
p_hand_r.rotation_euler = (0, 0, 0)
p_hand_r.keyframe_insert("rotation_euler", frame=1)

# Frame 10: 举手
p_hand_r.rotation_euler = (0, math.radians(30), 0)
p_hand_r.keyframe_insert("rotation_euler", frame=10)

# Frame 15: 摆过去
p_hand_r.rotation_euler = (0, math.radians(-30), 0)
p_hand_r.keyframe_insert("rotation_euler", frame=15)

# Frame 20: 摆回来
p_hand_r.rotation_euler = (0, math.radians(30), 0)
p_hand_r.keyframe_insert("rotation_euler", frame=20)

# Frame 30: 放下
p_hand_r.rotation_euler = (0, 0, 0)
p_hand_r.keyframe_insert("rotation_euler", frame=30)

track_greet = armature.animation_data.nla_tracks.new()
track_greet.name = "GreetTrack"
strip_greet = track_greet.strips.new(name="Greet", start=1, action=action_greet)


# --- 导出 ---
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_as_mainfile(filepath=BLEND_SAVE_PATH)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=GLB_EXPORT_PATH,
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_nla_strips=True
)
