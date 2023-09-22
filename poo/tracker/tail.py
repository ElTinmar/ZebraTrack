from dataclasses import dataclass
import math
from scipy.interpolate import splprep, splev
import cv2
import numpy as np
from numpy.typing import NDArray
from typing import Optional
from .helper.crop import diagonal_crop, rotation_matrix
from .helper.rect import Rect

@dataclass
class TailTrackerParamTracking:
    pix_per_mm: float = 30.0
    arc_angle_deg: float = 120.0
    n_tail_points: int = 12
    n_pts_arc: int = 20
    n_pts_interp: int = 40
    tail_length_mm: float = 2.5
    dist_swim_bladder_mm: float = 0.4
    blur_sz_mm: float = 0.10
    
    def mm2px(self, val_mm):
        val_px = int(val_mm * self.pix_per_mm) 
        return val_px
   
    @property
    def tail_length_px(self):
        return self.mm2px(self.tail_length_mm)
    
    @property
    def dist_swim_bladder_px(self):
        return self.mm2px(self.dist_swim_bladder_mm)

    @property
    def blur_sz_px(self):
        return self.mm2px(self.blur_sz_mm) 

@dataclass
class TailTrackerParamOverlay:
    color_tail: tuple = (255, 128, 128)
    thickness: int = 2

@dataclass
class TailTracking:
    heading: NDArray
    centroid: NDArray
    skeleton: NDArray
    skeleton_interp: NDArray
    image: NDArray

    def to_csv(self):
        '''export data as csv'''
        pass

class TailTracker:
    def __init__(
            self, 
            tracking_param: TailTrackerParamTracking, 
            overlay_param: TailTrackerParamOverlay
        ) -> None:
        self.tracking_param = tracking_param
        self.overlay_param = overlay_param

    def track(self, image: NDArray, heading: NDArray, centroid: NDArray):

        angle = np.arctan2(heading[1,1],heading[0,1]) 
        w, h = (int(1.5*self.tracking_param.tail_length_px), int(1.5*self.tracking_param.tail_length_px))
        corner = centroid - w//2 * heading[:,1]
        image_crop = diagonal_crop(
            image, 
            Rect(corner[0],corner[1],w,h),
            np.rad2deg(angle)
        )

        arc_rad = math.radians(self.tracking_param.arc_angle_deg)/2
        frame_blurred = cv2.boxFilter(image_crop, -1, (self.tracking_param.blur_sz_px, self.tracking_param.blur_sz_px))
        spacing = float(self.tracking_param.tail_length_px) / self.tracking_param.n_tail_points
        start_angle = -np.pi/2
        arc = np.linspace(-arc_rad, arc_rad, self.tracking_param.n_pts_arc) + start_angle
        x = w//2 
        y = self.tracking_param.dist_swim_bladder_px
        points = [[x, y]]
        for j in range(self.tracking_param.n_tail_points):
            try:
                # Find the x and y values of the arc centred around current x and y
                xs = x + spacing * np.cos(arc)
                ys = y - spacing * np.sin(arc)
                # Convert them to integer, because of definite pixels
                xs, ys = xs.astype(int), ys.astype(int)
                # Find the index of the minimum or maximum pixel intensity along arc
                idx = np.argmax(frame_blurred[ys, xs])
                # Update new x, y points
                x = xs[idx]
                y = ys[idx]
                # Create a new 180 arc centered around current angle
                arc = np.linspace(arc[idx] - arc_rad, arc[idx] + arc_rad, self.tracking_param.n_pts_arc)
                # Add point to list
                points.append([x, y])
            except IndexError:
                points.append(points[-1])

        # interpolate
        skeleton = np.array(points).astype('float')
        try:
            tck, _ = splprep(skeleton.T)
            new_points = splev(np.linspace(0,1,self.tracking_param.n_pts_interp), tck)
            skeleton_interp = np.array([new_points[0],new_points[1]])
            skeleton_interp = skeleton_interp.T
        except ValueError:
            skeleton_interp = None

        res = TailTracking(
            heading = heading,
            centroid = centroid,
            skeleton = skeleton,
            skeleton_interp = skeleton_interp,
            image = frame_blurred
        )    

        return res
    
    def overlay(self, image: NDArray, tracking: TailTracking, offset: Optional[NDArray]):
        # TODO check if using polyline is faster

        if tracking is not None:
            angle = np.arctan2(tracking.heading[1,1],tracking.heading[0,1]) 
            R = rotation_matrix(np.rad2deg(angle))
            w = int(1.5*self.tracking_param.tail_length_px)
            corner = tracking.centroid - w//2 * tracking.heading[:,1]

            if tracking.skeleton_interp is not None:
                transformed_coord = (R @ tracking.skeleton_interp.T).T + corner
                if offset is not None:
                    transformed_coord += offset
                tail_segments = zip(transformed_coord[:-1,], transformed_coord[1:,])
                for pt1, pt2 in tail_segments:
                    image = cv2.line(
                        image,
                        pt1.astype(np.int32),
                        pt2.astype(np.int32),
                        self.overlay_param.color_tail,
                        self.overlay_param.thickness
                    )
            
        return image