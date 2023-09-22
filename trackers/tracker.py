from body import BodyTracker
from eyes import EyesTracker
from tail import TailTracker
from multi_animal import MultiAnimalTracker
import numpy as np
import cv2
from typing import Protocol

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
            multi_animal: MultiAnimalTracker,
            body_tracker: BodyTracker, 
            eyes_tracker: EyesTracker, 
            tail_tracker: TailTracker
        ):
        self.assignment = assignment
        self.accumulator = accumulator
        self.multi_animal_tracker = multi_animal
        self.body_tracker = body_tracker
        self.eyes_tracker = eyes_tracker
        self.tail_tracker = tail_tracker
        
    def track(self, image):
        animals = self.multi_animal_tracker.track(image)
        self.assignment.update(animals.centroids)
        identities = self.assignment.get_ID()
        data = zip(identities, animals.bb_centroids, animals.bounding_boxes)
        body = {}
        eyes = {}
        tail = {}
        for (id, bb_x, bb_y, left, bottom, right, top) in data:
            image_cropped = image[bottom:top, left:right]
            offset = np.array([bb_x, bb_y])
            body[id] = self.body_tracker.track(image_cropped, offset)
            if body is not None:
                eyes[id] = self.eyes_tracker.track(image, body.heading, body.centroid)
                tail[id] = self.tail_tracker.track(image, body.heading, body.centroid)
            self.accumulator.update(id,body[id],eyes[id],tail[id])

        res = {
            'identities': identities, 
            'animals': animals,
            'body': body,
            'eyes': eyes,
            'tail': tail
        }

        return res 
 
    def overlay(self, image, tracking):
        image = self.multi_animal_tracker.overlay(image, tracking['animals'])
        for idx, id in enumerate(tracking['identities']):
            offset = tracking['animals'].bounding_boxes[idx,:2]
            image = self.body_tracker.overlay(image,tracking['body'][id], offset)
            image = self.eyes_tracker.overlay(image, tracking['eyes'][id], offset)
            image = self.tail_tracker.overlay(image, tracking['tail'][id], offset)
            cv2.putText(image, str(id), offset.astype(int), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2, cv2.LINE_AA)
        return image
    
