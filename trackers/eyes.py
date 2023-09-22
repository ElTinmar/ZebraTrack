from dataclasses import dataclass
import cv2
from scipy import ndimage
from scipy.spatial.distance import pdist
import numpy as np
from numpy.typing import NDArray
from typing import Optional, Tuple
from helper.morphology import bwareafilter_props, bwareafilter
from helper.crop import diagonal_crop, rotation_matrix
from helper.geometry import ellipse_direction, angle_between_vectors
from helper.rect import Rect

@dataclass
class EyesTrackerParamTracking:
    pix_per_mm: float = 30.0
    eye_norm: float = 0.2
    eye_gamma: float = 1.0
    eye_dyntresh_res: int = 20
    eye_contrast: float = 1.0
    eye_size_lo_mm: float = 1.0
    eye_size_hi_mm: float = 10.0
    blur_sz_mm: float = 0.05
    median_filter_sz_mm: float = 0.15
    dist_eye_midline_mm: float = 0.1
    crop_dimension_mm: Tuple[float, float]= (1.2, 1.2) 
    crop_offset_mm: float = 0.2

    def mm2px(self, val_mm):
        val_px = int(val_mm * self.pix_per_mm) 
        return val_px

    @property
    def eye_size_lo_px(self):
        return self.mm2px(self.eye_size_lo_mm)
    
    @property
    def eye_size_hi_px(self):
        return self.mm2px(self.eye_size_hi_mm)
    
    @property
    def dist_eye_midline_px(self):
        return self.mm2px(self.dist_eye_midline_mm)
    
    @property
    def blur_sz_px(self):
        return self.mm2px(self.blur_sz_mm)
    
    @property
    def median_filter_sz_px(self):
        return self.mm2px(self.median_filter_sz_mm)
    
    @property
    def crop_dimension_px(self):
        return (
            self.mm2px(self.crop_dimension_mm[0]),
            self.mm2px(self.crop_dimension_mm[1])
        ) 
    
    @property
    def crop_offset_px(self):
        return self.mm2px(self.crop_offset_mm)
    
@dataclass
class EyesTrackerParamOverlay:
    pix_per_mm: float = 30.0
    eye_len_mm: float = 0.4
    color_eye_left: tuple = (255, 255, 128)
    color_eye_right: tuple = (128, 255, 255)
    thickness: int = 2

    def mm2px(self, val_mm):
        val_px = int(val_mm * self.pix_per_mm) 
        return val_px
    
    @property
    def eye_len_px(self):
        return self.mm2px(self.eye_len_mm)

@dataclass
class EyesTracking:
    heading: NDArray
    centroid: NDArray
    left_eye: dict
    right_eye: dict
    mask: NDArray
    image: NDArray
    
    def to_csv(self):
        '''export data as csv'''
        pass

class EyesTracker:
    def __init__(
            self, 
            tracking_param: EyesTrackerParamTracking, 
            overlay_param: EyesTrackerParamOverlay
        ) -> None:
        self.tracking_param = tracking_param
        self.overlay_param = overlay_param
    
    @staticmethod
    def get_eye_prop(blob, heading):
        eye_dir = ellipse_direction(blob.inertia_tensor, heading)
        eye_angle = angle_between_vectors(eye_dir, heading)
        # (row,col) to (x,y) coordinates 
        y, x = blob.centroid
        eye_centroid = np.array([x, y],dtype = np.float32)
        return {'direction': eye_dir, 'angle': eye_angle, 'centroid': eye_centroid}
    
    @staticmethod
    def assign_features(blob_centroids):
            """From Duncan, returns indicies of sb, left, right from an array of contour centres"""
            contour_centres = np.array(blob_centroids)
            distances = pdist(blob_centroids)
            sb_idx = 2 - np.argmin(distances)
            eye_idxs = [i for i in range(3) if i != sb_idx]
            eye_vectors = contour_centres[eye_idxs] - contour_centres[sb_idx]
            cross_product = np.cross(*eye_vectors)
            if cross_product < 0:
                eye_idxs = eye_idxs[::-1]
            left_idx, right_idx = eye_idxs
            return sb_idx, left_idx, right_idx
    
    def track(self, image: NDArray, heading: NDArray, centroid: NDArray):

        angle = np.arctan2(heading[1,1],heading[0,1]) 
        w, h = self.tracking_param.crop_dimension_px
        corner = centroid - w//2 * heading[:,1] + (h+self.tracking_param.crop_offset_px) * heading[:,0] 
        image_crop = diagonal_crop(
            image, 
            Rect(corner[0],corner[1],w,h),
            np.rad2deg(angle)
        )
        image_crop = cv2.boxFilter(image_crop, -1, 
            (self.tracking_param.blur_sz_px, self.tracking_param.blur_sz_px)
        )
        image_crop[image_crop<0] = 0
        image_crop = image_crop/self.tracking_param.eye_norm 
        image_crop = ndimage.median_filter(image_crop, size = self.tracking_param.median_filter_sz_px)
        image_crop = self.tracking_param.eye_contrast*image_crop**self.tracking_param.eye_gamma
        image_crop[image_crop>1] = 1

        # sweep threshold to obtain 3 connected component within size range (include SB)
        thresholds = np.linspace(0,1,self.tracking_param.eye_dyntresh_res)
        found_eyes_and_sb = False
        for t in thresholds:
            mask = 1.0*(image_crop >= t)
            props = bwareafilter_props(
                mask, 
                min_size = self.tracking_param.eye_size_lo_px, 
                max_size = self.tracking_param.eye_size_hi_px
            )
            if len(props) == 3:
                found_eyes_and_sb = True
                mask = bwareafilter(
                    mask, 
                    min_size = self.tracking_param.eye_size_lo_px, 
                    max_size = self.tracking_param.eye_size_hi_px
                )
                break

        left_eye = None
        right_eye = None
        new_heading = None
        if found_eyes_and_sb: 
            blob_centroids = np.array([blob.centroid for blob in props])
            sb_idx, left_idx, right_idx = self.assign_features(blob_centroids)
            heading_after_rot = np.array([0, 1], dtype=np.float32)
            left_eye = self.get_eye_prop(props[left_idx], heading_after_rot)
            right_eye = self.get_eye_prop(props[right_idx], heading_after_rot)
            new_heading = (props[left_idx].centroid + props[right_idx].centroid)/2 - props[sb_idx].centroid
            new_heading = new_heading / np.linalg.norm(new_heading)

        res = EyesTracking(
            heading = heading,
            centroid = centroid,
            left_eye = left_eye,
            right_eye = right_eye,
            mask = (255*mask).astype(np.uint8),
            image = (255*image_crop).astype(np.uint8)
        )
        
        return res
       
    def overlay(self, image: NDArray, tracking: EyesTracking, offset: Optional[NDArray] = None):

        def process_eye(
                image: NDArray, 
                eye: dict, 
                R: NDArray, 
                corner: NDArray, 
                offset: Optional[NDArray], 
                color: tuple, 
                eye_len_px: float, 
                thickness: int
            ) -> NDArray:

            eye_centroid = R @ eye['centroid'] + corner
            if offset is not None:
                eye_centroid += offset
            eye_direction = R @ eye['direction']

            pt1 = eye_centroid
            pt2 = pt1 + eye_len_px * eye_direction
            image = cv2.line(
                image,
                pt1.astype(np.int32),
                pt2.astype(np.int32),
                color,
                thickness
            )
            pt2 = pt1 - eye_len_px * eye_direction
            image = cv2.line(
                image,
                pt1.astype(np.int32),
                pt2.astype(np.int32),
                color,
                thickness
            )
            image = cv2.circle(
                image,
                pt2.astype(np.int32),
                2,
                color,
                thickness
            )
            return image
        
        if tracking is not None:
            angle = np.arctan2(tracking.heading[1,1],tracking.heading[0,1]) 
            w, h = self.tracking_param.crop_dimension_px
            corner = tracking.centroid - w//2 * tracking.heading[:,1] + (h+self.tracking_param.crop_offset_px) * tracking.heading[:,0] 
            R = rotation_matrix(np.rad2deg(angle))

            image = process_eye(
                image, 
                tracking.left_eye, 
                R, 
                corner, 
                offset, 
                self.overlay_param.color_eye_left, 
                self.overlay_param.eye_len_px, 
                self.overlay_param.thickness
            )
            image = process_eye(
                image, 
                tracking.right_eye, 
                R, 
                corner, 
                offset, 
                self.overlay_param.color_eye_right, 
                self.overlay_param.eye_len_px, 
                self.overlay_param.thickness
            )
        
        return image
    