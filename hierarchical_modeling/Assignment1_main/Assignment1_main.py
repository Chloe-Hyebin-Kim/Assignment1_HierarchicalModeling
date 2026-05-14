import math
import pyglet

from pyglet.gl import Config
from OpenGL.GL import *

time_value = 0.0

# ------------------------------------------------------------
# Window / OpenGL Context
# ------------------------------------------------------------

try:
    config = Config(
        double_buffer=True,
        depth_size=24,
        major_version=2,
        minor_version=1
    )

    window = pyglet.window.Window(
        width=900,
        height=700,
        caption="Assignment1_HierarchicalModel - 3D Stand Lamp",
        resizable=True,
        config=config
    )

except pyglet.window.NoSuchConfigException:
    window = pyglet.window.Window(
        width=900,
        height=700,
        caption="Assignment1_HierarchicalModel - 3D Stand Lamp",
        resizable=True
    )


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def set_color(color):
    r, g, b = color
    glColor3f(r, g, b)


def perspective(fov_y, aspect, z_near, z_far):
    top = z_near * math.tan(math.radians(fov_y) / 2.0)
    bottom = -top
    right = top * aspect
    left = -right
    glFrustum(left, right, bottom, top, z_near, z_far)


    #local y 축 방향으로 만들어진 기준점을 링크 방향으로 회전
    #local y축을 실제 링크 방향으로 정렬-> 회전축과 회전각을 계산
def align_y_axis_to_vector(dx, dy, dz):
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return

    vx = dx / length
    vy = dy / length
    vz = dz / length

    #(0, 1, 0) == 처음 생성되는 local y축 방향
    # y 외젓 v
    #원기둥의 기본 방향인 y축을 실제 링크 방향으로 맞추기 위한 회전축 계산
    #(0,1,0)과 목표 방향 외적
    axis_x = vz
    axis_y = 0.0
    axis_z = -vx

    axis_length = math.sqrt(axis_x * axis_x + axis_y * axis_y + axis_z * axis_z)

    dot = vy
    dot = max(-1.0, min(1.0, dot))

    angle = math.degrees(math.acos(dot))#라디안 안씀

    # 음수나오면 뒤집어야 함
    if axis_length < 1e-6:
        if dot < 0.0:
            glRotatef(180.0, 1.0, 0.0, 0.0)
        return

    # 최종 회전
    glRotatef(
        angle,
        axis_x / axis_length,
        axis_y / axis_length,
        axis_z / axis_length
    )


def draw_cylinder_y(radius, height, color, segments=40):
    set_color(color)

    #옆
    glBegin(GL_QUADS)
    for i in range(segments):
        a0 = 2.0 * math.pi * i / segments
        a1 = 2.0 * math.pi * (i + 1) / segments

        x0 = math.cos(a0) * radius
        z0 = math.sin(a0) * radius
        x1 = math.cos(a1) * radius
        z1 = math.sin(a1) * radius

        glVertex3f(x0, 0.0, z0)
        glVertex3f(x1, 0.0, z1)
        glVertex3f(x1, height, z1)
        glVertex3f(x0, height, z0)
    glEnd()

#아래
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(a) * radius, 0.0, math.sin(a) * radius)
    glEnd()

#위
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, height, 0.0)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        glVertex3f(math.cos(a) * radius, height, math.sin(a) * radius)
    glEnd()

def draw_box_y(width, height, depth, color):
    set_color(color)

    x = width / 2.0
    z = depth / 2.0

    glBegin(GL_QUADS)

    # front face
    glVertex3f(-x, 0.0, z)
    glVertex3f(x, 0.0, z)
    glVertex3f(x, height, z)
    glVertex3f(-x, height, z)

    # back face
    glVertex3f(x, 0.0, -z)
    glVertex3f(-x, 0.0, -z)
    glVertex3f(-x, height, -z)
    glVertex3f(x, height, -z)

    # left face
    glVertex3f(-x, 0.0, -z)
    glVertex3f(-x, 0.0, z)
    glVertex3f(-x, height, z)
    glVertex3f(-x, height, -z)

    # right face
    glVertex3f(x, 0.0, z)
    glVertex3f(x, 0.0, -z)
    glVertex3f(x, height, -z)
    glVertex3f(x, height, z)

    # bottom face
    glVertex3f(-x, 0.0, -z)
    glVertex3f(x, 0.0, -z)
    glVertex3f(x, 0.0, z)
    glVertex3f(-x, 0.0, z)

    # top face
    glVertex3f(-x, height, z)
    glVertex3f(x, height, z)
    glVertex3f(x, height, -z)
    glVertex3f(-x, height, -z)

    glEnd()

def draw_cylinder_between(start, end, radius, color, segments=40):
    sx, sy, sz = start
    ex, ey, ez = end

    dx = ex - sx
    dy = ey - sy
    dz = ez - sz

    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    glPushMatrix()
    glTranslatef(sx, sy, sz) #시작점 이동
    align_y_axis_to_vector(dx, dy, dz) # 실제 link 방향으로 회전
    draw_cylinder_y(radius, length, color, segments)
    glPopMatrix()


def draw_frustum_y(radius_bottom, radius_top, height, color, segments=40):
    set_color(color)
    glBegin(GL_QUADS)
    for i in range(segments):
        a0 = 2.0 * math.pi * i / segments
        a1 = 2.0 * math.pi * (i + 1) / segments

        bx0 = math.cos(a0) * radius_bottom
        bz0 = math.sin(a0) * radius_bottom
        bx1 = math.cos(a1) * radius_bottom
        bz1 = math.sin(a1) * radius_bottom

        tx0 = math.cos(a0) * radius_top
        tz0 = math.sin(a0) * radius_top
        tx1 = math.cos(a1) * radius_top
        tz1 = math.sin(a1) * radius_top

        glVertex3f(bx0, 0.0, bz0)
        glVertex3f(bx1, 0.0, bz1)
        glVertex3f(tx1, height, tz1)
        glVertex3f(tx0, height, tz0)
    glEnd()

    set_color((0.95, 0.75, 0.20))
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        glVertex3f(
            math.cos(a) * radius_bottom,
            0.0,
            math.sin(a) * radius_bottom
        )
    glEnd()
    glLineWidth(1.0)


def draw_frustum_between(start, end, radius_start, radius_end, color, segments=40):
    sx, sy, sz = start
    ex, ey, ez = end

    dx = ex - sx
    dy = ey - sy
    dz = ez - sz

    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    glPushMatrix()
    glTranslatef(sx, sy, sz)
    align_y_axis_to_vector(dx, dy, dz)
    draw_frustum_y(radius_start, radius_end, length, color, segments)
    glPopMatrix()


def draw_sphere(center, radius, color, slices=24, stacks=12):
    cx, cy, cz = center
    set_color(color)

    for stack in range(stacks):
        phi0 = math.pi * stack / stacks
        phi1 = math.pi * (stack + 1) / stacks

        y0 = math.cos(phi0) * radius
        r0 = math.sin(phi0) * radius

        y1 = math.cos(phi1) * radius
        r1 = math.sin(phi1) * radius

        glBegin(GL_QUAD_STRIP)
        for slice_index in range(slices + 1):
            theta = 2.0 * math.pi * slice_index / slices

            x0 = math.cos(theta) * r0
            z0 = math.sin(theta) * r0

            x1 = math.cos(theta) * r1
            z1 = math.sin(theta) * r1

            glVertex3f(cx + x0, cy + y0, cz + z0)
            glVertex3f(cx + x1, cy + y1, cz + z1)
        glEnd()


def draw_floor_grid():
    set_color((0.35, 0.35, 0.35))
    glLineWidth(1.0)

    glBegin(GL_LINES)

    grid_size = 5
    step = 0.5

    for i in range(-grid_size * 2, grid_size * 2 + 1):
        p = i * step

        glVertex3f(-grid_size, 0.0, p)
        glVertex3f(grid_size, 0.0, p)

        glVertex3f(p, 0.0, -grid_size)
        glVertex3f(p, 0.0, grid_size)

    glEnd()

###
# Hierarchical stand lamp
###
def draw_stand_lamp():
    global time_value

    #움직일 각도
    base_yaw_angle = math.sin(time_value * 0.8) * 35.0
    lower_arm_angle = -55.0 + math.sin(time_value * 1.2) * 20.0
    lamp_head_angle = -95.0 + math.sin(time_value * 1.8) * 18.0
    
    neck_length = 0.85
    lower_arm_length = 1.85
    lamp_head_length = 0.75

    # 바닥 위 사각기둥 받침대
    base_width = 1.2
    base_depth = 1.2
    base_height = 0.25

    glPushMatrix()

    draw_box_y(
        width=base_width,
        height=base_height,
        depth=base_depth,
        color=(0.30, 0.30, 0.30)
    )

    # 베이스 상단 연결부
    #base_top = (0.0, base_height, 0.0)
    #glPopMatrix()
    glTranslatef(0.0, base_height, 0.0) 
    draw_sphere(
       #center=base_top,
        center=(0.0, 0.0, 0.0),
        radius=0.10,
        color=(0.85, 0.85, 0.85)
    )

    # Base 회전
    glRotatef(base_yaw_angle, 0.0, 1.0, 0.0)



    # 꺾인 목
    #neck_end = (0.0, 1.10, 0.0)
    #arm_end = (1.85, 2.25, 0.0)

    # 수직 목 부분
    draw_cylinder_y(
        radius=0.07,
        height=neck_length,
        color=(0.20, 0.55, 0.90)
    )
    #draw_cylinder_between(
    #    start=base_top,
    #    end=neck_end,
    #    radius=0.07,
    #    color=(0.20, 0.55, 0.90)
    #)

    # 목 끝 관절로 이동
    glTranslatef(0.0, neck_length, 0.0)


    draw_sphere(
        #center=neck_end,
        center=(0.0, 0.0, 0.0),
        radius=0.12,
        color=(0.85, 0.85, 0.85)
    )

    # Lower Arm 회전
    glRotatef(lower_arm_angle, 0.0, 0.0, 1.0)

    # 꺾인 목
    draw_cylinder_y(
        radius=0.07,
        height=lower_arm_length,
        color=(0.20, 0.55, 0.90)
    )
    #draw_cylinder_between(
    #    start=neck_end,
    #    end=arm_end,
    #    radius=0.07,
    #    color=(0.20, 0.55, 0.90)
    #)
     
    # 팔 끝 관절로 이동
    glTranslatef(0.0, lower_arm_length, 0.0)

    draw_sphere(
        #center=arm_end,
        center=(0.0, 0.0, 0.0),
        radius=0.12,
        color=(0.85, 0.85, 0.85)
    )


    # Lamp Head 회전
    glRotatef(lamp_head_angle, 0.0, 0.0, 1.0)

     # 조명 갓
    draw_frustum_y(
        radius_bottom=0.18,
        radius_top=0.48,
        height=lamp_head_length,
        color=(0.95, 0.80, 0.25)
    )
    # 조명
    #head_end = (2.30, 1.45, 0.0)

    #draw_frustum_between(
    #   start=arm_end,
    #    end=head_end,
    #   radius_start=0.18,
    #    radius_end=0.48,
    #    color=(0.95, 0.80, 0.25)
    #)

    glPopMatrix()



# ------------------------------------------------------------
# Event handlers
# ------------------------------------------------------------

@window.event
def on_resize(width, height):
    if height == 0:
        height = 1

    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspect = width / float(height)
    perspective(
        fov_y=45.0,
        aspect=aspect,
        z_near=0.1,
        z_far=100.0
    )

    glMatrixMode(GL_MODELVIEW)

    return pyglet.event.EVENT_HANDLED


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # 캠뷰
    glTranslatef(0.0, -1.2, -7.0)
    glRotatef(25.0, 1.0, 0.0, 0.0)
    glRotatef(-35.0, 0.0, 1.0, 0.0)

    draw_floor_grid()
    draw_stand_lamp()


# ------------------------------------------------------------
# OpenGL state
# ------------------------------------------------------------


#tick
def update(dt):
    global time_value
    time_value += dt

glClearColor(0.06, 0.07, 0.09, 1.0)
glEnable(GL_DEPTH_TEST)

pyglet.clock.schedule_interval(update, 1 / 60)

pyglet.app.run()