from enum import Enum, auto
from events import EventEnum
import numpy as np

class Scanlist:
    def __init__(self):
        self.scanlist_elements = []
        self._active_idx = None
        self.observers = []

    @property
    def active_idx(self):
        return self._active_idx
    
    @active_idx.setter
    def active_idx(self, idx):
        self._active_idx = idx
        print("Active scanlist element index set to", idx)
        self.notify_observers(EventEnum.SCANLIST_ACTIVE_SCANLIST_ELEMENT_CHANGED)

    def add_scanlist_element(self, name, scan_parameters):
        new_scanlist_element = ScanlistElement(name, scan_parameters)
        self.scanlist_elements.append(new_scanlist_element)
        self.notify_observers(EventEnum.SCANLIST_ITEM_ADDED)
        if self.active_idx is None:
            self.active_idx = 0        
    
    def duplicate_scanlist_element(self, index):
        self.add_scanlist_element(self.scanlist_elements[index].name, self.scanlist_elements[index].scan_item.scan_parameters)
        # change active index to the newly added scanlist element
        self.active_idx = len(self.scanlist_elements) - 1

    def remove_scanlist_element(self, index):
        del self.scanlist_elements[index]
        print("Scanlist element removed at index", index, "active index is", self.active_idx)
        if index == self.active_idx:
            print("index removed", index, "is equal to active index", self.active_idx)
            if len(self.scanlist_elements) == 0:
                self.active_idx = None # if the removed scanlist element was the only one in the list, the active index should be set to None
            #else:
                # if index == len(self.scanlist_elements):
                #     self.active_idx -= 1 # if the removed scanlist element was at the end of the list, the active index should be decremented by 1 
            elif index == 0:
                    self.active_idx = 0
            else:
                    self.active_idx -= 1
        else:
            if index < self.active_idx:
                self.active_idx -= 1 # if the removed scanlist element was before the active index, the active index should be decremented by 1
            else:
                self.notify_observers(EventEnum.SCANLIST_ACTIVE_SCANLIST_ELEMENT_CHANGED) # if the removed scanlist element was after the active index, the active index should not change, however, a different scanlist element becomes active, so the observers should be notified
        self.notify_observers(EventEnum.SCANLIST_ITEM_REMOVED)


    @property
    def active_scanlist_element(self):
        return self.scanlist_elements[self.active_idx]
    
    @property
    def active_scan_item(self):
        return self.scanlist_elements[self.active_idx].scan_item

    def get_progress(self):
        # divide the number of completed scans by the total number of scans
        completed = 0
        for scanlist_element in self.scanlist_elements:
            if scanlist_element.scan_item.status == ScanItemStatusEnum.COMPLETE:
                completed += 1
        if len(self.scanlist_elements) == 0:
            return 0
        else:        
            return completed / len(self.scanlist_elements)

    def rename_scanlist_element(self, index, name):
        self.scanlist_elements[index].scan_item.name = name
        self.scanlist_elements[index].name = name

    def add_observer(self, observer):
        self.observers.append(observer)
        print("Observer", observer, "added to", self)

    def notify_observers(self, event: EventEnum):
        for observer in self.observers:
            print("Subject", self, "is updating observer", observer, "with event", event)
            observer.update(event)
            
    def remove_observer(self, observer):
        self.observers.remove(observer)
        print("Observer", observer, "removed from", self)

    @property
    def active_scanlist_element(self):
        return self.scanlist_elements[self.active_idx]
        

class ScanItemStatusEnum(Enum):
    READY_TO_SCAN = auto() # Scan parameters are valid and the scan item can be applied to "scan" the anatomical model
    BEING_MODIFIED = auto() # Scan parameters are being modified by the user on the UI
    INVALID = auto() # Scan parameters are invalid and the scan item cannot be applied to "scan" the anatomical model
    COMPLETE = auto() # The scan item has been applied to "scan" the anatomical model. The acquired data is available.

class ScanlistElement:
    def __init__(self, name, scan_parameters):
        self.scan_item = ScanItem(name, scan_parameters)
        self.acquired_data = None
        self._name = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self.scan_item.name = name

class ScanItem: 
    def __init__(self, name, scan_parameters):
        self.name = name
        self._scan_parameters = {}
        for key, value in scan_parameters.items():
            self._scan_parameters[key] = value
        # self.scan_volume = ScanVolume()
        # self.scan_volume.add_observer(self) # Scan item adds itself to scan volume as an observer so that it can receive notifications that the scan volume has changed. It receives notifications when changes are caused by user interactions with the scan volume display on viewing windows on the UI. 
        self.observers = []
        self.scan_parameters = scan_parameters
        self._scan_parameters_original = {}
        for key, value in scan_parameters.items():
            self._scan_parameters_original[key] = value
        self.messages = {}
        self.valid = True
        self._status = ScanItemStatusEnum.READY_TO_SCAN

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status):
        self._status = status
        self.notify_observers(EventEnum.SCAN_ITEM_STATUS_CHANGED)

    @property
    def scan_parameters(self):
        return self._scan_parameters
    
    @scan_parameters.setter
    def scan_parameters(self, scan_parameters):
        for key, value in scan_parameters.items():
            try: 
                self._scan_parameters[key] = float(value) 
            except: 
                self._scan_parameters[key] = value
        self.notify_observers(EventEnum.SCAN_ITEM_PARAMETERS_CHANGED)

    @property
    def scan_parameters_original(self):
        return self._scan_parameters_original
    
    @scan_parameters_original.setter
    def scan_parameters_original(self, scan_parameters):
        for key, value in scan_parameters.items():
            try: self._scan_parameters_original[key] = float(value)   
            except: self._scan_parameters_original[key] = value       
    
    def cancel_changes(self):
        if self.valid == True:
            self.status = ScanItemStatusEnum.READY_TO_SCAN
        else:
            self.status = ScanItemStatusEnum.INVALID

    def reset_parameters(self):      
        self.scan_parameters = self.scan_parameters_original
        self.valid = True
        self.messages = {}
        self.status = ScanItemStatusEnum.READY_TO_SCAN    

    def validate_scan_parameters(self, scan_parameters):
        '''This whole function will need to be deleted or changed. For now I am pretending that the scan parameters are valid.'''
        self.valid = True
        self.messages = {}
        
        try: scan_parameters["TE_ms"] = float(scan_parameters["TE_ms"])

        except: 
            self.valid = False
            self.messages["TE_ms"] = "TE must be a number."

        if isinstance(scan_parameters["TE_ms"], float):
            if scan_parameters["TE_ms"] < 0:
                self.valid = False
                self.messages["TE_ms"] = "TE cannot be a negative number."

        try: scan_parameters["TR_ms"] = float(scan_parameters["TR_ms"])
        except: 
            self.valid = False
            self.messages["TR_ms"] = "TR must be a number."
        
        if isinstance(scan_parameters["TR_ms"], float):
            if scan_parameters["TR_ms"] < 0:
                self.valid = False
                self.messages["TR_ms"] = "TR cannot be a negative number."

        try: scan_parameters["TI_ms"] = float(scan_parameters["TI_ms"])
        except: 
            self.valid = False
            self.messages["TI_ms"] = "TI must be a number."

        if isinstance(scan_parameters["TI_ms"], float):
            if scan_parameters["TI_ms"] < 0:
                self.valid = False
                self.messages["TI_ms"] = "TI cannot be a negative number."

        try: scan_parameters["FA_deg"] = float(scan_parameters["FA_deg"])
        except: 
            self.valid = False
            self.messages["FA_deg"] = "FA must be a number."

        if isinstance(scan_parameters["FA_deg"], float):
            if scan_parameters["FA_deg"] < 0:
                self.valid = False
                self.messages["FA_deg"] = "FA cannot be a negative number."

        self.scan_parameters = scan_parameters
  

        if self.valid == True:
            self.status = ScanItemStatusEnum.READY_TO_SCAN
            
        else:
            self.status = ScanItemStatusEnum.INVALID

    # def update(self, event):
    #         if event == EventEnum.SCAN_VOLUME_CHANGED:
    #             parameters = self.scan_volume.get_parameters()
    #             self.scan_parameters = parameters 

    def add_observer(self, observer):
        self.observers.append(observer)
        print("Observer", observer, "added to", self)

    def notify_observers(self, event: EventEnum):
        for observer in self.observers:
            print("Subject", self, "is updating observer", observer, "with event", event)
            observer.update(event)
            
    def remove_observer(self, observer):
        self.observers.remove(observer)
        print("Observer", observer, "removed from", self)
           
""" class ScanVolume:
    ''' The scan volume defines the rectangular volume to be scanned next. Its orientation with respect to the LPS coordinate system is defined by the axisX_LPS, axisY_LPS and axisZ_LPS parameters. The extent of the scan volume in the X, Y and Z directions is defined by the extentX_mm, extentY_mm and extentZ_mm parameters. The position of the center of the volume with respect to the LPS coordinate system is defined by the origin_LPS parameter. '''
    def __init__(self):
        self.axisX_LPS = None
        self.axisY_LPS = None
        self.axisZ_LPS = None
        self.extentX_mm = None
        self.extentY_mm = None
        self._extentZ_mm = None # See property extentZ_mm:  N_slices * slice_thickness_mm + (N_slices - 1) * slice_gap_mm
        self.resX_mm = 1
        self.resY_mm = 1
        # resolution in Z direction is the slice thickness
        self.origin_LPS = None
        self.N_slices = None
        self.slice_thickness_mm = None
        self.slice_gap_mm = None

        self.observers = []

    @property
    def extentZ_mm(self):
        return self.N_slices * self.slice_thickness_mm + (self.N_slices - 1) * self.slice_gap_mm
     
    @property
    def conversion_matrix(self) -> np.ndarray:
        '''Affine transformation matrix that converts scan volume coordinates to LPS coordinates'''
        return np.array([[self.axisX_LPS[0], self.axisY_LPS[0], self.axisZ_LPS[0], self.origin_LPS[0]], [self.axisX_LPS[1], self.axisY_LPS[1], self.axisZ_LPS[1], self.origin_LPS[1]], [self.axisX_LPS[2], self.axisY_LPS[2], self.axisZ_LPS[2], self.origin_LPS[2]], [0, 0, 0, 1]])
   
    def set_scan_volume_geometry(self, scan_parameters: dict):
        self.N_slices = int(float(scan_parameters['NSlices']))
        self.slice_gap_mm = float(scan_parameters['SliceGap_mm'])
        self.slice_thickness_mm = float(scan_parameters['SliceThickness_mm'])
        self.extentX_mm = float(scan_parameters['FOVPE_mm'])
        self.extentY_mm = float(scan_parameters['FOVFE_mm'])
        if scan_parameters['ScanPlane'] == 'Axial':
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 1, 0])
            self.axisZ_LPS = np.array([0, 0, 1])
        if scan_parameters['ScanPlane'] == 'Sagittal':
            self.axisX_LPS = np.array([0, 1, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([-1, 0, 0])
        if scan_parameters['ScanPlane'] == 'Coronal':
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([0, 1, 0])
        self.resXmm = 1
        self.resYmm = 1

        self.origin_LPS = np.array([float(scan_parameters['OffCenterRL_mm']), float(scan_parameters['OffCenterAP_mm']), float(scan_parameters['OffCenterFH_mm'])])

        # rotate the axes according to the angle parameters

        # first rotate around RL axis
        angleRL_deg = scan_parameters.get('RLAngle_deg', 0)
        # make sure angleRL is type float
        angleRL_deg = float(angleRL_deg)
        # rotate the LPS axes by the angleRL
        angleRL_rad = np.deg2rad(angleRL_deg)
        rotation_matrix_RL = np.array([[1, 0, 0], [0, np.cos(angleRL_rad), -np.sin(angleRL_rad)], [0, np.sin(angleRL_rad), np.cos(angleRL_rad)]])
        self.axisX_LPS = np.dot(rotation_matrix_RL, self.axisX_LPS)
        self.axisY_LPS = np.dot(rotation_matrix_RL, self.axisY_LPS)
        self.axisZ_LPS = np.dot(rotation_matrix_RL, self.axisZ_LPS)

        # then rotate around AP axis             
        angleAP_deg = scan_parameters.get('APAngle_deg', 0)
        # make sure angleAP is type float
        angleAP_deg = float(angleAP_deg)
        # rotate the LPS axes by the angleAP
        angleAP_rad = np.deg2rad(angleAP_deg)
        rotation_matrix_AP = np.array([[np.cos(angleAP_rad), 0, np.sin(angleAP_rad)], [0, 1, 0], [-np.sin(angleAP_rad), 0, np.cos(angleAP_rad)]])
        self.axisX_LPS = np.dot(rotation_matrix_AP, self.axisX_LPS)
        self.axisY_LPS = np.dot(rotation_matrix_AP, self.axisY_LPS)
        self.axisZ_LPS = np.dot(rotation_matrix_AP, self.axisZ_LPS)

        # finally rotate around FH axis
        angleFH_deg = scan_parameters.get('FHAngle_deg', 0)
        # make sure angleFH is type float
        angleFH_deg = float(angleFH_deg)
        # rotate the LPS axes by the angleFH
        angleFH_rad = np.deg2rad(angleFH_deg)
        rotation_matrix_FH = np.array([[np.cos(angleFH_rad), -np.sin(angleFH_rad), 0], [np.sin(angleFH_rad), np.cos(angleFH_rad), 0], [0, 0, 1]])
        self.axisX_LPS = np.dot(rotation_matrix_FH, self.axisX_LPS)
        self.axisY_LPS = np.dot(rotation_matrix_FH, self.axisY_LPS)
        self.axisZ_LPS = np.dot(rotation_matrix_FH, self.axisZ_LPS)        

        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def compute_intersection_with_acquired_image(self, acquired_image: AcquiredImage) -> list[np.array]:
        # compute the intersection of the scan volume with the acquired image and return a list of the corners of the polygon that represents the intersection. The corners are in pixmap coordinates and are ordered in a clockwise manner.

        # list the edges of the scan volume in scan volume coordinates. For each edge, find the intersection points (if any) with the 2D acquired image. 
        edges = self._list_edges_of_scan_volume()
        list_intersection_pts_LPS = []
        acquired_image_geometry = acquired_image.image_geometry
        origin_acq_im = acquired_image_geometry.origin_LPS
        axisX_acq_im = acquired_image_geometry.axisX_LPS
        axisY_acq_im = acquired_image_geometry.axisY_LPS
        for edge in edges:
            start_pt_line_LPS = self.scan_volume_mm_coords_to_LPS_coords(edge[0])
            end_pt_line_LPS = self.scan_volume_mm_coords_to_LPS_coords(edge[1])
            intersection_pts_LPS = self._line_plane_intersection(origin_acq_im, axisX_acq_im, axisY_acq_im, start_pt_line_LPS, end_pt_line_LPS)
            if intersection_pts_LPS is not None:
                for pt in intersection_pts_LPS:
                    list_intersection_pts_LPS.append(pt)

        # convert the intersection points from LPS coordinates to pixmap coordinates
        list_intersection_pts_pixmap = []
        for pt_LPS in list_intersection_pts_LPS:
            pt_pixmap = acquired_image_geometry.LPS_coords_to_pixmap_coords(pt_LPS)
            list_intersection_pts_pixmap.append(pt_pixmap)

        # sort the 2D intersection points in a clockwise manner
        # find the centroid of the intersection points
        centroid = np.mean(list_intersection_pts_pixmap, axis=0)
        list_intersection_pts_pixmap = sorted(list_intersection_pts_pixmap, key=lambda pt: np.arctan2(pt[1] - centroid[1], pt[0] - centroid[0]))

        return list_intersection_pts_pixmap

    def _get_geometry_parameters(self) -> dict:
        geometry_parameters = {}
        geometry_parameters['axisX_LPS'] = self.axisX_LPS
        geometry_parameters['axisY_LPS'] = self.axisY_LPS
        geometry_parameters['extentX_mm'] = self.extentX_mm
        geometry_parameters['extentY_mm'] = self.extentY_mm
        geometry_parameters['resX_mm'] = self.resX_mm
        geometry_parameters['resY_mm'] = self.resY_mm
        return geometry_parameters

    def get_image_geometry_of_slice(self, slice_number: int) -> ImageGeometry:
        '''This function returns the ImageGeometry of each slice in the scan volume.'''
        origin_slice_in_scan_volume_coords = np.array([0, 0, -self.extentZ_mm / 2 + slice_number * (self.slice_thickness_mm + self.slice_gap_mm) + self.slice_thickness_mm / 2])
        origin_slice_in_LPS_coords = self.scan_volume_mm_coords_to_LPS_coords(origin_slice_in_scan_volume_coords)
        geometry_parameters = self._get_geometry_parameters()
        geometry_parameters['origin_LPS'] = origin_slice_in_LPS_coords
        return ImageGeometry(geometry_parameters)

    def translate_scan_volume(self, translation_vector_LPS: np.ndarray):
        # translate the scan volume by the translation vector (which is in LPS coordinates)
        self.origin_LPS += translation_vector_LPS
        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def scan_volume_mm_coords_to_LPS_coords(self, scan_volume_mm_coords: tuple) -> tuple:
        '''Convert scan volume coordinates to LPS coordinates. The scan volume coordinates are in millimeters, and the LPS coordinates are in millimeters. '''
        x, y, z = scan_volume_mm_coords

        L, P, S, one = np.dot(self.conversion_matrix, np.array([x, y, z, 1]))

        return (L, P, S)
    
    def LPS_coords_to_scan_volume_mm_coords(self, LPS_coords: tuple) -> tuple:
        '''Convert LPS coordinates to scan volume coordinates. The LPS coordinates are in millimeters, and the scan volume coordinates are in millimeters. '''

        L, P, S = LPS_coords

        x, y, z, one = np.dot(np.linalg.inv(self.conversion_matrix), np.array([L, P, S, 1]))

        return (x, y, z)
    
    def _list_edges_of_scan_volume(self) -> list[tuple]:
        '''list the edges of the scan volume in scan volume coordinates'''
        # Define the corners of the FOV in FOV coordinates
        front_top_left = np.array([-self.extentX_mm / 2, -self.extentY_mm / 2, -self.extentZ_mm / 2])
        front_top_right = np.array([self.extentX_mm / 2, -self.extentY_mm / 2, -self.extentZ_mm / 2])
        front_bottom_right = np.array([self.extentX_mm / 2, self.extentY_mm / 2, -self.extentZ_mm / 2])
        front_bottom_left = np.array([-self.extentX_mm / 2, self.extentY_mm / 2, -self.extentZ_mm / 2])
        back_top_left = np.array([-self.extentX_mm / 2, -self.extentY_mm / 2, self.extentZ_mm / 2])
        back_top_right = np.array([self.extentX_mm / 2, -self.extentY_mm / 2, self.extentZ_mm / 2])
        back_bottom_right = np.array([self.extentX_mm / 2, self.extentY_mm / 2, self.extentZ_mm / 2])
        back_bottom_left = np.array([-self.extentX_mm / 2, self.extentY_mm / 2, self.extentZ_mm / 2]) 

        # List the edges of the scan volume in scan volume coordinates. Each edge is a tuple containing the coordinates of the two endpoints of the edge.
        edges = [
            (front_top_left, front_top_right),
            (front_top_right, front_bottom_right),
            (front_bottom_right, front_bottom_left),
            (front_bottom_left, front_top_left),
            (back_top_left, back_top_right),
            (back_top_right, back_bottom_right),
            (back_bottom_right, back_bottom_left),
            (back_bottom_left, back_top_left),
            (front_top_left, back_top_left),
            (front_top_right, back_top_right),
            (front_bottom_right, back_bottom_right),
            (front_bottom_left, back_bottom_left)
        ]

        return edges 

    def _line_plane_intersection(self, origin_plane, axisX_plane, axisY_plane, start_pt_line, end_pt_line) -> list[np.array]:
        
        # Convert inputs to numpy arrays
        origin_plane = np.array(origin_plane)
        axisX_plane = np.array(axisX_plane)
        axisY_plane = np.array(axisY_plane)
        start_pt_line = np.array(start_pt_line)
        end_pt_line = np.array(end_pt_line)

        # Direction vector of the line
        line_dir = end_pt_line - start_pt_line

        # Matrix and vector to solve for the intersection point
        mat = np.column_stack((line_dir, -axisX_plane, -axisY_plane))
        vec = origin_plane - start_pt_line

        # Create list to store intersection points
        intersection_pts = []

        # Check if the matrix is singular
        if np.linalg.matrix_rank(mat) < 3:
            # The line is parallel to the plane
            mat2 = np.column_stack((-axisX_plane, -axisY_plane, vec)) 
            if np.linalg.matrix_rank(mat2) == 3:
                # The line is parallel to the plane and does not lie on the plane
                return None
            else:
                # The line is parallel to the plane and lies on the plane
                intersection_pts.append(start_pt_line)
                intersection_pts.append(end_pt_line)
                return intersection_pts
        if self.valid == True:
            self.status = ScanItemStatusEnum.READY_TO_SCAN
            
        else:
            self.status = ScanItemStatusEnum.INVALID
             """


        