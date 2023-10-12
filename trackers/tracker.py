from .body import BodyTracker
from .eyes import EyesTracker
from .tail import TailTracker
from .animal import AnimalTracker
import numpy as np
import cv2
from typing import Protocol, Optional
from image.imcontrast import imcontrast
from image.crop import imrotate, rotation_matrix
from geometry.rect import Rect

class Accumulator(Protocol):
    def update(self):
        ...

class Assignment(Protocol):
    def update(self):
        ...
    
    def get_ID(self):
        ...

class Tracker:
    def __init__(
            self, 
            assignment: Assignment,
            accumulator: Accumulator,
            animal_tracker: AnimalTracker,
            body_tracker: Optional[BodyTracker], 
            eyes_tracker: Optional[EyesTracker], 
            tail_tracker: Optional[TailTracker]
        ):
        self.assignment = assignment
        self.accumulator = accumulator
        self.animal_tracker = animal_tracker
        self.body_tracker = body_tracker
        self.eyes_tracker = eyes_tracker
        self.tail_tracker = tail_tracker
        
    def track(self, image):

        # restrain image between 0 and 1
        image = imcontrast(image)

        # get animal centroids (only crude location is necessary)
        animals = self.animal_tracker.track(image)
        centroids = animals.centroids

        # if nothing was detected at that stage, stop here
        if centroids.size == 0:
            return
        
        # assign identities to animals 
        self.assignment.update(centroids)
        identities = self.assignment.get_ID()
        to_keep = self.assignment.get_kept_centroids()        
        data = np.hstack(
            (identities[np.newaxis].T, 
             animals.bb_centroids[to_keep,:], 
             animals.bounding_boxes[to_keep,:])
        ) 

        # loop over animals
        body = {}
        eyes = {}
        tail = {}
        for (id, bb_x, bb_y, left, bottom, right, top) in data.astype(np.int64): 
            eyes[id] = None
            tail[id] = None
            body[id] = None

            # crop each animal's bounding box
            image_cropped = image[bottom:top, left:right] 
            offset = np.array([bb_x, bb_y])
            if self.body_tracker is not None:

                # get more precise centroid and orientation of the animals
                body[id] = self.body_tracker.track(image_cropped, offset)
                if body[id] is not None:
                    
                    # rotate the animal so that it's vertical head up
                    image_rot, centroid_rot = imrotate(
                        image_cropped, 
                        body[id].centroid[0], body[id].centroid[1], 
                        np.rad2deg(body[id].angle_rad)
                    )

                    # track eyes 
                    if self.eyes_tracker is not None:
                        eyes[id] = self.eyes_tracker.track(image_rot, centroid_rot)

                    # track tail
                    if self.tail_tracker is not None:
                        tail[id] = self.tail_tracker.track(image_rot, centroid_rot)

                # compute additional features based on tracking
                if self.accumulator is not None:
                    self.accumulator.update(id,body[id],eyes[id],tail[id])

        # save tracking results in a dict and return
        res = {
            'identities': identities, 
            'indices': to_keep,
            'animals': animals,
            'body': body,
            'eyes': eyes,
            'tail': tail,
            'image': (255*image).astype(np.uint8)
        }
        return res 
 
    def overlay(self, image, tracking):
        if tracking is None:
            return None
        
        image = self.animal_tracker.overlay(image, tracking['animals'])

        # loop over animals
        for idx, id in zip(tracking['indices'], tracking['identities']):
            if self.body_tracker is not None:
                # translate according to animal position 
                translation = tracking['animals'].bounding_boxes[idx,:2]

                # rotate according to animal orientation 
                angle = tracking['body'][id].angle_rad
                rotation = rotation_matrix(np.rad2deg(angle))[:2,:2]
                
                image = self.body_tracker.overlay(image, tracking['body'][id], translation)
                if self.eyes_tracker is not None:
                    w, h = np.array(self.eyes_tracker.tracking_param.crop_dimension_px) / self.eyes_tracker.tracking_param.resize
                    offset_eye_ROI = tracking['body'][id].centroid - w//2 * tracking['body'][id].heading[:,1] + (-h//2 + self.eyes_tracker.tracking_param.crop_offset_px / self.eyes_tracker.tracking_param.resize) * tracking['body'][id].heading[:,0] 
                    image = self.eyes_tracker.overlay(image, tracking['eyes'][id], translation+offset_eye_ROI, rotation)
                if self.tail_tracker is not None:
                    w, h = np.array(self.tail_tracker.tracking_param.crop_dimension_px) / self.tail_tracker.tracking_param.resize
                    offset_tail_ROI = tracking['body'][id].centroid - w//2 * tracking['body'][id].heading[:,1] + (-h//2 + self.tail_tracker.tracking_param.crop_offset_tail_px / self.tail_tracker.tracking_param.resize) * tracking['body'][id].heading[:,0] 
                    image = self.tail_tracker.overlay(image, tracking['tail'][id], translation+offset_tail_ROI, rotation)

            # show ID
            cv2.putText(image, str(id), translation.astype(int), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2, cv2.LINE_AA)
        return image
    
    def overlay_local(self, tracking):
        if tracking is None:
            return None
        
        image = tracking['image'].copy()
        image = np.dstack((image,image,image))
        for idx, id in zip(tracking['indices'], tracking['identities']):
            if self.body_tracker is not None:
                # translate according to animal position 
                translation = tracking['animals'].bounding_boxes[idx,:2]

                # rotate according to animal orientation 
                angle = tracking['body'][id].angle_rad
                rotation = rotation_matrix(np.rad2deg(angle))[:2,:2]

                image = self.body_tracker.overlay(image, tracking['body'][id], translation)
                if self.eyes_tracker is not None:
                    w, h = np.array(self.eyes_tracker.tracking_param.crop_dimension_px) / self.eyes_tracker.tracking_param.resize
                    offset_eye_ROI = tracking['body'][id].centroid - w//2 * tracking['body'][id].heading[:,1] + (-h//2 + self.eyes_tracker.tracking_param.crop_offset_px / self.eyes_tracker.tracking_param.resize) * tracking['body'][id].heading[:,0] 
                    image = self.eyes_tracker.overlay(image, tracking['eyes'][id], translation+offset_eye_ROI, rotation)
                if self.tail_tracker is not None:
                    w, h = np.array(self.tail_tracker.tracking_param.crop_dimension_px) / self.tail_tracker.tracking_param.resize
                    offset_tail_ROI = tracking['body'][id].centroid - w//2 * tracking['body'][id].heading[:,1] + (-h//2 + self.tail_tracker.tracking_param.crop_offset_tail_px / self.tail_tracker.tracking_param.resize) * tracking['body'][id].heading[:,0] 
                    image = self.tail_tracker.overlay(image, tracking['tail'][id], translation+offset_tail_ROI, rotation)

            # show ID
            cv2.putText(image, str(id), translation.astype(int), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2, cv2.LINE_AA)
        return image
    
