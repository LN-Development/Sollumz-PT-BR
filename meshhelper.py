import bpy
import bmesh
from math import cos, sin, degrees, radians, sqrt
from mathutils import Vector, Matrix, Quaternion, Euler
import numpy as np

def bound_sphere(mesh, radius):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=radius)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def bound_cylinder(mesh, radius, length):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=32, diameter1=radius, diameter2=radius, depth=length)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def bound_disc(mesh, radius, length):
    bm = bmesh.new()
    rot_mat = Matrix.Rotation(radians(90.0), 4, 'Y')
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=32, diameter1=radius, diameter2=radius, depth=length, matrix=rot_mat)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def bound_capsule(mesh, radius, length, rings = 9, segments = 16):
    bm = bmesh.new()
    mat_loc = Matrix.Translation((0.0, 0.0, length/2))
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, diameter=radius, matrix=mat_loc)
    mat_loc = Matrix.Translation((0.0, 0.0, -length/2))
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, diameter=radius, matrix=mat_loc)
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=segments, diameter1=radius, diameter2=radius, depth=length)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def add_vector_list(list1, list2):
    x = list1[0] + list2[0]
    y = list1[1] + list2[1]
    z = list1[2] + list2[2]     
    return [x, y, z]

def subtract_vector_list(list1, list2):
    x = list1[0] - list2[0]
    y = list1[1] - list2[1]
    z = list1[2] - list2[2]     
    return [x, y, z]

def multiple_vector_list(list, num):
    x = list[0] * num
    y = list[1] * num
    z = list[2] * num
    return [x, y, z]

def get_vector_list_length(list):
    sx = list[0]**2  
    sy = list[1]**2
    sz = list[2]**2
    length = (sx + sy + sz) ** 0.5
    return length 

# see https://blender.stackexchange.com/questions/223858/how-do-i-get-the-bounding-box-of-all-objects-in-a-scene
"""Multiply 3d coord list by matrix"""
def np_matmul_coords(coords, matrix, space=None):
    M = (space @ matrix @ space.inverted()
         if space else matrix).transposed()
    ones = np.ones((coords.shape[0], 1))
    coords4d = np.hstack((coords, ones))
    
    return np.dot(coords4d, M)[:,:-1]


"""Get min and max bounds for an object and all of its children"""
def get_total_bbs(obj) -> list:
    objects = [obj, *obj.children]
    # get the global coordinates of all object bounding box corners    
    coords = np.vstack(
        tuple(np_matmul_coords(np.array(o.bound_box), o.matrix_world.copy())
            for o in  
                objects
                if o.type == 'MESH'
                )
            )
    # bottom front left (all the mins)
    bb_min = coords.min(axis=0)
    # top back right
    bb_max = coords.max(axis=0)
    return [Vector(bb_min), Vector(bb_max)]

def get_children_recursive(obj): 
    children = [] 
    for child in obj.children:
        children.append(child)
        if len(child.children) > 0: 
            children.append(*get_children_recursive(child))
            
    return children 

def get_bound_center(obj) -> Vector:
    # Get the center of the object's bounds for later use. Credit: https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
    local_bbox_center = 0.125 * sum((Vector(b)
                                     for b in obj.bound_box), Vector())
    center = obj.matrix_world @ local_bbox_center
    return Vector(center)

def get_sphere_bb(objs, bbminmax) -> list:
    allverts = []
    for obj in objs:
        mesh = obj.data
        for vert in mesh.vertices:
            allverts.append(vert)
    bscen = [0, 0, 0]
    bsrad = 0
    
    av = add_vector_list(bbminmax[0], bbminmax[1])
    bscen = multiple_vector_list(av, 0.5)

    for v in allverts:
        bsrad = max(bsrad, get_vector_list_length(subtract_vector_list(v.co, bscen)))

    return [bscen, bsrad]  

def get_bound_box_verts(verts):

    #xs = []
    #zs = []
    #for vert in verts:
    #    xs.append(vert.co[0])
    #    zs.append(vert.co[2])

    #xmax = max(xs)
    #zmax = max(zs)

    #diagonals = []

    #for vert in verts:
    #    if(vert.co[0] == xmax):
    #        diagonals.append(vert.co)
    #    if(vert.co[2] == zmax):
    #        diagonals.append(vert.co) 
 
    #alldiagonals = [diagonals[0], diagonals[1], verts[0], verts[1]]

    #return alldiagonals
    return None
