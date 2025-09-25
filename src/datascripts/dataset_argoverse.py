import math
import multiprocessing
import os, sys
import pickle
import zlib
import random
from multiprocessing import Process

TIMESTAMP = 0
TRACK_ID = 1
OBJECT_TYPE = 2
X = 3
Y = 4
CITY_NAME = 5

type2index = {}
type2index["OTHERS"] = 0
type2index["AGENT"] = 1
type2index["AV"] = 2

max_vector_num = 0

VECTOR_PRE_X = 0
VECTOR_PRE_Y = 1
VECTOR_X = 2
VECTOR_Y = 3
map_extent = [-50, 50, -20, 60]

def discard_poses_outside_extent(pose_set, map_extent, ids= None):
    """
    Discards lane or agent poses outside predefined extent in target agent's frame of reference.
    :param pose_set: agent or lane polyline poses
    :param ids: annotation record tokens for pose_set. Only applies to lanes.
    :return: Updated pose set
    """
    updated_pose_set = []
    updated_ids = []

    for m, poses in enumerate(pose_set):
        flag = False
        for n, pose in enumerate(poses):
            if map_extent[0] <= pose[0] <= map_extent[1] and \
                    map_extent[2] <= pose[1] <= map_extent[3]:
                flag = True

        if flag:
            updated_pose_set.append(poses)
            if ids is not None:
                updated_ids.append(ids[m])
        else:
            pass
            # print("discard_poses_outside_extent", poses)

    if ids is not None:
        return updated_pose_set, updated_ids
    else:
        return updated_pose_set

def discard_poses_outside_extent_agent(id2info, map_extent):
    """
    Discards agent poses outside predefined extent in target agent's frame of reference.
    :param id2info: agent dictionary
    :param map_extent: extent of map
    :return: Updated pose set
    """
    id2delete = []
    for id in id2info:
        if id == "AGENT" or id == "AV":
            continue
        flag = False
        info = id2info[id]
        for line in info:
            if map_extent[0] <= line[X] <= map_extent[1] and \
                    map_extent[2] <= line[Y] <= map_extent[3]:
                flag = True
        if flag:
            pass
        else:
            id2delete.append(id)
    print("discard_poses_outside_extent_agent", len(id2delete))
    print("id3info", len(id2info))
    for id in id2delete:
        del id2info[id]
    return id2info


def get_sub_map(args: config.Args, x, y, city_name, vectors=[], polyline_spans=[], mapping=None):