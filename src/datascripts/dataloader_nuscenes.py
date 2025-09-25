import abc
import math
import multiprocessing
import zlib
import os
import sys
map_extent = [-50, 50, -20, 80]
def discard_poses_outside_extent(pose_set, map_extent, ids=None):
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

class TrajectoryDataset(torch_data.Dataset):
    """
    Base class for trajectory datasets.
    """

    def __init__(self, mode: str, data_dir: str):
        """
        Initialize trajectory dataset.
        :param mode: Mode of operation of dataset
        :param data_dir: Directory to store extracted pre-processed data
        """
        if mode not in ['extract_data', 'load_data']:
            raise Exception('Dataset mode needs to be one of {extract_data or load_data}')
        self.mode = mode
        self.data_dir = data_dir
        if mode != 'load_data' and not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Returns size of dataset
        """
        raise NotImplementedError()
    def __getitem__(self, idx: int) -> Union[Dict, int]:
        """
        Get data point, based on mode of operation of dataset.
        param idx: data index
        """
        if self.mode == 'extract_data':
            return self.extract_data(idx)
        else:
            return self.load_data(idx)
    def extract_data(self, idx: int):
        """
        Function to extract data. Bulk of the dataset functionality will be implemented by this method.
        param idx: data index
        """
        data = self.get_mapping(idx)
        return data
    @abc.abstractmethod
    def get_mapping(self, idx: int) -> Dict:
        """
        Extracts model inputs.
        :param idx: data index
        """
        raise NotImplementedError()
    @abc.abstractmethod
    def load_data(self, idx: int) -> Dict:
        """
        Function to load extracted data.
        param idx: data index
        return data: Dictionary with pre-processed data
        """
        raise NotImplementedError()
    @abc.abstractmethod
    def save_data(self, idx: int, data: Dict):
        """
        Function to save extracted pre-processed data.
        :param idx: data index
        :param data: Dictionary with pre-processed data
        """
        raise NotImplementedError()