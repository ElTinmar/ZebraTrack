from image.morphology import bwareafilter_centroids
from image.imcontrast import imcontrast
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
import cv2

@dataclass
class AnimalTrackerParamTracking:
    pix_per_mm: float = 40.0
    target_pix_per_mm: float = 20.0
    body_intensity: float = 0.1
    min_body_size_mm: float = 10.0
    max_body_size_mm: float = 100.0
    min_body_length_mm: float = 2.0
    max_body_length_mm: float = 6.0
    min_body_width_mm: float = 1.0
    max_body_width_mm: float = 3.0
    pad_value_mm: float = 3.0

    def mm2px(self, val_mm):
        val_px = int(val_mm * self.target_pix_per_mm) 
        return val_px

    @property
    def resize(self):
        return self.target_pix_per_mm/self.pix_per_mm
    
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
    
    @property
    def pad_value_px(self):
        return self.mm2px(self.pad_value_mm)

@dataclass
class AnimalTrackerParamOverlay:
    pix_per_mm: float = 40.0
    radius_mm: float = 0.1
    centroid_color: tuple = (255, 128, 128)
    bbox_color:tuple = (255, 255, 255) 
    centroid_thickness: int = -1
    bbox_thickness: int = 2

    def mm2px(self, val_mm):
        return int(val_mm * self.pix_per_mm) 

    @property
    def radius_px(self):
        return self.mm2px(self.radius_mm)

@dataclass
class AnimalTracking:
    centroids: NDArray # nx2 vector. (x,y) coordinates of the n fish centroid ~ swim bladder location
    bounding_boxes: NDArray
    bb_centroids: NDArray
    mask: NDArray
    image: NDArray

    def to_csv(self):
        '''
        export data to csv
        '''
        pass    

class AnimalTracker:
    def __init__(
            self, 
            tracking_param: AnimalTrackerParamTracking, 
            overlay_param: AnimalTrackerParamOverlay
        ) -> None:
        self.tracking_param = tracking_param
        self.overlay_param = overlay_param

    def track(self, image: NDArray) -> AnimalTracking:
        
        if self.tracking_param.resize != 1:
            image = cv2.resize(
                image, 
                None, 
                None,
                self.tracking_param.resize,
                self.tracking_param.resize,
                cv2.INTER_AREA
            )

        # tune image contrast and gamma
        imcontrast(image)

        height, width = image.shape
        mask = (image >= self.tracking_param.body_intensity)
        centroids = bwareafilter_centroids(
            mask, 
            min_size = self.tracking_param.min_body_size_px,
            max_size = self.tracking_param.max_body_size_px, 
            min_length = self.tracking_param.min_body_length_px,
            max_length = self.tracking_param.max_body_length_px,
            min_width = self.tracking_param.min_body_width_px,
            max_width = self.tracking_param.max_body_width_px
        )

        bboxes = np.zeros((centroids.shape[0],4), dtype=int)
        bb_centroids = np.zeros((centroids.shape[0],2), dtype=float)
        for idx, (x,y) in enumerate(centroids):
            left = max(int(x - self.tracking_param.pad_value_px), 0) 
            bottom = max(int(y - self.tracking_param.pad_value_px), 0) 
            right = min(int(x + self.tracking_param.pad_value_px), width)
            top = min(int(y + self.tracking_param.pad_value_px), height)
            bboxes[idx,:] = [left,bottom,right,top]
            bb_centroids[idx,:] = [x-left, y-bottom] 

        res = AnimalTracking(
            centroids = centroids/self.tracking_param.resize,
            bounding_boxes = bboxes/self.tracking_param.resize,
            bb_centroids = bb_centroids/self.tracking_param.resize,
            mask = (255*mask).astype(np.uint8),
            image = (255*image).astype(np.uint8)
        )
        return res

    def overlay(self, image: NDArray, tracking: AnimalTracking) -> NDArray:
        if tracking is not None:
            # draw centroid
            for (x,y) in tracking.centroids:
                image = cv2.circle(
                    image,
                    (int(x),int(y)), 
                    self.overlay_param.radius_px, 
                    self.overlay_param.centroid_color, 
                    self.overlay_param.centroid_thickness
                )

            # draw bounding boxes
            for (left, bottom, right, top) in tracking.bounding_boxes:
                image = cv2.rectangle(
                    image, 
                    (int(left), int(top)),
                    (int(right), int(bottom)), 
                    self.overlay_param.bbox_color, 
                    self.overlay_param.bbox_thickness
                )

        return image
    
    def overlay_local(self, tracking: AnimalTracking):
        if tracking is not None:
            image = tracking.image.copy()

            if self.tracking_param.resize != 1:
                image = cv2.resize(
                    image, 
                    None, 
                    None,
                    self.tracking_param.resize,
                    self.tracking_param.resize,
                    cv2.INTER_AREA
                )

            # draw centroid
            for (x,y) in tracking.centroids:
                image = cv2.circle(
                    image,
                    (int(x),int(y)), 
                    self.overlay_param.radius_px, 
                    self.overlay_param.centroid_color, 
                    self.overlay_param.centroid_thickness
                )

            # draw bounding boxes
            for (left, bottom, right, top) in tracking.bounding_boxes:
                image = cv2.rectangle(
                    image, 
                    (int(left), int(top)),
                    (int(right), int(bottom)), 
                    self.overlay_param.bbox_color, 
                    self.overlay_param.bbox_thickness
                )

        return image
    
