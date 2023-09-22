from helper.morphology import bwareafilter_props
from sklearn.decomposition import PCA
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
import cv2
from typing import Optional
        
@dataclass
class BodyTrackerParamTracking:
    pix_per_mm: float = 45.0
    body_intensity: float = 0.1
    min_body_size_mm: float = 10.0
    max_body_size_mm: float = 100.0
    min_body_length_mm: float = 2.0
    max_body_length_mm: float = 6.0
    min_body_width_mm: float = 1.0
    max_body_width_mm: float = 3.0

    def mm2px(self, val_mm):
        val_px = int(val_mm * self.pix_per_mm) 
        return val_px

    @property
    def min_body_size_px(self):
        return self.mm2px(self.min_body_size_mm)
    
    @property
    def max_body_size_px(self):
        return self.mm2px(self.max_body_size_mm) 
        
    @property
    def min_body_length_px(self):
        return self.mm2px(self.min_body_length_mm)
    
    @property
    def max_body_length_px(self):
        return self.mm2px(self.max_body_length_mm)

    @property
    def min_body_width_px(self):
        return self.mm2px(self.min_body_width_mm)
    
    @property
    def max_body_width_px(self):
        return self.mm2px(self.max_body_width_mm)

@dataclass
class BodyTrackerParamOverlay:
    pix_per_mm: float = 45.0
    heading_len_mm: float = 1.0
    heading_color: tuple = (0,128,255)
    thickness: int = 2

@dataclass 
class BodyTracking:
    heading: NDArray # 2x2 matrix, column 1 = fish heading, column 2 = fish right direction
    centroid: NDArray # 1x2 vector. (x,y) coordinates of the fish centroid ~ swim bladder location
    mask: NDArray 

    def to_csv(self):
        '''
        export data to csv
        '''
        pass    

class BodyTracker:
    def __init__(
            self, 
            tracking_param: BodyTrackerParamTracking, 
            overlay_param: BodyTrackerParamOverlay
        ) -> None:
        self.tracking_param = tracking_param
        self.overlay_param = overlay_param

    @staticmethod
    def get_orientation(coordinates: NDArray) -> NDArray:
        pca = PCA()
        scores = pca.fit_transform(coordinates)
        # PCs are organized in rows, transform to columns
        principal_components = pca.components_.T
        centroid = pca.mean_

        # correct orientation
        if abs(max(scores[:,0])) > abs(min(scores[:,0])):
            principal_components[:,0] = - principal_components[:,0]
        if np.linalg.det(principal_components) < 0:
            principal_components[:,1] = - principal_components[:,1]
        
        return (principal_components, centroid)

    def track(self, image: NDArray, coord_centroid: Optional[NDArray] = None) -> BodyTracking:
        '''
        coord_centroid: centroid of the fish to track if it's already known.
        Useful when tracking multiple fish to discriminate between nearby blobs
        '''

        mask = (image >= self.tracking_param.body_intensity)
        props = bwareafilter_props(
            mask, 
            min_size = self.tracking_param.min_body_size_px,
            max_size = self.tracking_param.max_body_size_px, 
            min_length = self.tracking_param.min_body_length_px,
            max_length = self.tracking_param.max_body_length_px,
            min_width = self.tracking_param.min_body_width_px,
            max_width = self.tracking_param.max_body_width_px
        )
        
        if props == []:
            return None
        else:
            if coord_centroid is not None:
            # in case of multiple tracking, there may be other blobs
                closest_coords = None
                min_dist = None
                for blob in props:
                    row, col = blob.centroid
                    fish_centroid = np.array([col, row])
                    fish_coords = np.fliplr(blob.coords)
                    dist = np.linalg.norm(fish_centroid - coord_centroid)
                    if (min_dist is None) or (dist < min_dist): 
                        closest_coords = fish_coords
                        min_dist = dist

                (principal_components, centroid) = self.get_orientation(closest_coords)
            else:
                fish_coords = np.fliplr(props[0].coords)
                (principal_components, centroid) = self.get_orientation(fish_coords)

            res = BodyTracking(
                heading = principal_components,
                centroid = centroid,
                mask = (255*mask).astype(np.uint8)
            )
            return res

    def overlay(self, image: NDArray, tracking: BodyTracking, offset: Optional[NDArray] = None) -> NDArray:
        '''
        offset: if tracking on cropped image, offset of cropped part in larger image
        '''

        if tracking is not None:
            pt1 = tracking.centroid
            if offset is not None:
                pt1 += offset
            pt2 = pt1 + self.overlay_param.heading_len_px*tracking.heading[:,0]
            self.image_overlay = cv2.line(
                image,
                pt1.astype(np.int32),
                pt2.astype(np.int32),
                self.overlay_param.heading_color,
                self.overlay_param.thickness
            )
            image = cv2.circle(
                image,
                pt2.astype(np.int32),
                2,
                self.overlay_param.heading_color,
                self.overlay_param.thickness
            )
        
        return image