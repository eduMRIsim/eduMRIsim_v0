from enum import Enum, auto

from PyQt5.QtCore import QPointF

from events import EventEnum
import numpy as np

from events import EventEnum
from utils.logger import log


class ImageGeometry:
    """This class represents the geometry of a 2D acquired image. The axisX_LPS and axisY_LPS parameters define the orientation of the image plane in LPS coordinates. The extentX_mm and extentY_mm parameters define the extent of the image in the X and Y directions in millimeters. The resX_mm and resY_mm parameters define the resolution of the image in the X and Y directions in millimeters. The origin_LPS parameter defines the origin of the image in LPS coordinates."""

    def __init__(self, geometry_parameters: dict):
        self.axisX_LPS = geometry_parameters["axisX_LPS"]
        self.axisY_LPS = geometry_parameters["axisY_LPS"]
        self.extentX_mm = geometry_parameters["extentX_mm"]
        self.extentY_mm = geometry_parameters["extentY_mm"]
        self.resX_mm = geometry_parameters["resX_mm"]
        self.resY_mm = geometry_parameters["resY_mm"]
        self.origin_LPS = geometry_parameters["origin_LPS"]
        self.plane = geometry_parameters["plane"]

    @property
    def axisZ_LPS(self):
        # The Z axis is the cross product of the X and Y axes, i.e., the vector that is perpendicular to the 2D image plane
        return np.cross(self.axisX_LPS, self.axisY_LPS)

    def image_mm_coords_to_pixmap_coords(self, image_mm_coords: tuple) -> tuple:
        """Convert image coordinates to pixmap coordinates. The image coordinates are in millimeters, and the pixmap coordinates are in pixels. The origin of the pixmap coordinate system is at the top left corner of the image. The image coordinate origin is at the center of the image."""
        x, y, z = image_mm_coords
        x_pixmap = (x + (self.extentX_mm / 2)) / self.resX_mm
        y_pixmap = (y + (self.extentY_mm / 2)) / self.resY_mm
        return (x_pixmap, y_pixmap)

    def pixmap_coords_to_image_mm_coords(self, pixmap_coords: tuple) -> tuple:
        """Convert pixmap coordinates to image coordinates. The pixmap coordinates are in pixels, and the image coordinates are in millimeters. The origin of the pixmap coordinate system is at the top left corner of the image. The image coordinate origin is at the center of the image."""
        x, y = pixmap_coords
        x_image_mm = (x * self.resX_mm) - (self.extentX_mm / 2)
        y_image_mm = (y * self.resY_mm) - (self.extentY_mm / 2)
        z_image_mm = 0

        return (x_image_mm, y_image_mm, z_image_mm)

    def image_mm_coords_to_LPS_coords(self, image_mm_coords: tuple) -> tuple:
        """Convert image coordinates to LPS coordinates. The image coordinates are in millimeters, and the LPS coordinates are in millimeters."""

        x, y, z = image_mm_coords

        L, P, S, one = np.dot(self.conversion_matrix, np.array([x, y, z, 1]))

        return (L, P, S)

    def LPS_coords_to_image_mm_coords(self, LPS_coords: tuple) -> tuple:
        """Convert LPS coordinates to image coordinates. The LPS coordinates are in millimeters, and the image coordinates are in millimeters."""

        L, P, S = LPS_coords

        x, y, z, one = np.dot(
            np.linalg.inv(self.conversion_matrix), np.array([L, P, S, 1])
        )

        return (x, y, z)

    def LPS_coords_to_pixmap_coords(self, LPS_coords: tuple) -> tuple:
        """Convert LPS coordinates to pixmap coordinates. The LPS coordinates are in millimeters, and the pixmap coordinates are in pixels."""
        x, y, z = self.LPS_coords_to_image_mm_coords(LPS_coords)
        return self.image_mm_coords_to_pixmap_coords((x, y, z))

    def pixmap_coords_to_LPS_coords(self, pixmap_coords: tuple) -> tuple:
        """Convert pixmap coordinates to LPS coordinates. The pixmap coordinates are in pixels, and the LPS coordinates are in millimeters."""
        x, y = pixmap_coords
        x, y, z = self.pixmap_coords_to_image_mm_coords((x, y))
        return self.image_mm_coords_to_LPS_coords((x, y, z))

    @property
    def conversion_matrix(self) -> np.ndarray:
        """Affine transformation matrix"""
        return np.array(
            [
                [
                    self.axisX_LPS[0],
                    self.axisY_LPS[0],
                    self.axisZ_LPS[0],
                    self.origin_LPS[0],
                ],
                [
                    self.axisX_LPS[1],
                    self.axisY_LPS[1],
                    self.axisZ_LPS[1],
                    self.origin_LPS[1],
                ],
                [
                    self.axisX_LPS[2],
                    self.axisY_LPS[2],
                    self.axisZ_LPS[2],
                    self.origin_LPS[2],
                ],
                [0, 0, 0, 1],
            ]
        )


class AcquiredImage:
    # An acquired image is a 2D image that is acquired during a scan. It consists of image data and image geometry.
    def __init__(self, image_data: np.ndarray, image_geometry: ImageGeometry):
        self.image_data = image_data
        self.image_geometry = image_geometry


class AcquiredSeries:
    """A series of acquired images. The acquired images are 2D."""

    def __init__(
        self, series_name, scan_plane, list_acquired_images: list[AcquiredImage]
    ):
        self.series_name = series_name
        self.scan_plane = scan_plane
        self.list_acquired_images = list_acquired_images


class Scanlist:
    def __init__(self):
        self.scanlist_elements = []
        self._active_idx = None
        self.observers = []

    def add_scanlist_element(self, name, scan_parameters):
        new_scanlist_element = ScanlistElement(name, scan_parameters)
        self.scanlist_elements.append(new_scanlist_element)
        self.notify_observers(EventEnum.SCANLIST_ITEM_ADDED)
        if self.active_idx is None:
            self.active_idx = 0

    @property
    def active_idx(self):
        return self._active_idx

    @active_idx.setter
    def active_idx(self, idx):
        self._active_idx = idx
        self.notify_observers(EventEnum.SCANLIST_ACTIVE_INDEX_CHANGED)

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

    def add_observer(self, observer):
        self.observers.append(observer)
        log.debug(f"Observer {observer} added to {self}")

    def notify_observers(self, event: EventEnum):
        for observer in self.observers:
            log.debug(
                f"Subject {self} is updating observer {observer} with event {event}"
            )
            observer.update(event)

    def remove_observer(self, observer):
        self.observers.remove(observer)
        log.debug(f"Observer {observer}, removed from {self}")


class ScanItemStatusEnum(Enum):
    READY_TO_SCAN = (
        auto()
    )  # Scan parameters are valid and the scan item can be applied to "scan" the anatomical model
    BEING_MODIFIED = auto()  # Scan parameters are being modified by the user on the UI
    INVALID = (
        auto()
    )  # Scan parameters are invalid and the scan item cannot be applied to "scan" the anatomical model
    COMPLETE = (
        auto()
    )  # The scan item has been applied to "scan" the anatomical model. The acquired data is available.


class ScanlistElement:
    def __init__(self, name, scan_parameters):
        self.scan_item = ScanItem(name, scan_parameters)
        self.acquired_data = None
        self.name = name


class ScanItem:
    def __init__(self, name, scan_parameters):
        self.name = name
        self._scan_parameters = {}
        self.scan_volume = ScanVolume()
        self.scan_volume.add_observer(
            self
        )  # Scan item adds itself to scan volume as an observer so that it can receive notifications that the scan volume has changed. It receives notifications when changes are caused by user interactions with the scan volume display on viewing windows on the UI.
        self.observers = []
        self.scan_parameters = scan_parameters
        self._scan_parameters_original = {}
        self.scan_parameters_original = scan_parameters
        self.messages = {}
        self.valid = True
        self._status = ScanItemStatusEnum.READY_TO_SCAN

    @property
    def status(self):
        return self._status

    @property
    def axisZ_LPS(self):
        return self.axisZ_LPS

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
        self.scan_volume.remove_observer(
            self
        )  # Scan item removes itself as an observer of the scan volume so that it does not receive the notification that the scan voulume has changed. This is to avoid an infinite loop. In the future a more sophisticated event system could be implemented to ensure that observers do not respond to events that they themselves initiated.
        self.scan_volume.set_scan_volume_geometry(self.scan_parameters)

        # Update with clamped values
        params = self.scan_volume.get_parameters()

        for key, value in params.items():
            self._scan_parameters[key] = value

        self.scan_volume.add_observer(
            self
        )  # Scan item adds itself to scan volume as an observer so that it can receive notifications that the scan volume has changed.
        self.notify_observers(EventEnum.SCAN_ITEM_PARAMETERS_CHANGED)

    @property
    def scan_parameters_original(self):
        return self._scan_parameters_original

    @scan_parameters_original.setter
    def scan_parameters_original(self, scan_parameters):
        for key, value in scan_parameters.items():
            try:
                self._scan_parameters_original[key] = float(value)
            except:
                self._scan_parameters_original[key] = value

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
        """This whole function will need to be deleted or changed. For now I am pretending that the scan parameters are valid."""
        self.valid = True
        self.messages = {}
        self.scan_parameters = scan_parameters

        if self.valid == True:
            self.status = ScanItemStatusEnum.READY_TO_SCAN

        # old code for validating contrast parameters
        # try: scan_parameters["TE"] = float(scan_parameters["TE"])

        # except:
        #     self.valid = False
        #     self.messages['TE'] = "TE must be a number."

        # if isinstance(scan_parameters["TE"], float):
        #     if scan_parameters["TE"] < 0:
        #         self.valid = False
        #         self.messages['TE'] = "TE cannot be a negative number."

        # try: scan_parameters["TR"] = float(scan_parameters["TR"])
        # except:
        #     self.valid = False
        #     self.messages['TR'] = "TR must be a number."

        # if isinstance(scan_parameters["TR"], float):
        #     if scan_parameters["TR"] < 0:
        #         self.valid = False
        #         self.messages['TR'] = "TR cannot be a negative number."

        # try: scan_parameters["TI"] = float(scan_parameters["TI"])
        # except:
        #     self.valid = False
        #     self.messages["TI"] = "TI must be a number."

        # if isinstance(scan_parameters["TI"], float):
        #     if scan_parameters["TI"] < 0:
        #         self.valid = False
        #         self.messages['TI'] = "TI cannot be a negative number."

        # try: scan_parameters["FA"] = float(scan_parameters["FA"])
        # except:
        #     self.valid = False
        #     self.messages["FA"] = "FA must be a number."

        # if isinstance(scan_parameters["FA"], float):
        #     if scan_parameters["FA"] < 0:
        #         self.valid = False
        #         self.messages['FA'] = "FA cannot be a negative number."

        # self.scan_parameters = scan_parameters

        # if self.valid == True:
        #     self.status = ScanlistElementStatusEnum.READY_TO_SCAN

        # else:
        #     self.status = ScanlistElementStatusEnum.INVALID

    #Rotation check for Plane changing according to rotation. Only gets called when the save button is pressed
    def perform_rotation_check(self, scan_parameters):
        scanPlane = scan_parameters['ScanPlane']
        RLAngle_deg = float(scan_parameters['RLAngle_deg'])
        APAngle_deg = float(scan_parameters['APAngle_deg'])
        FHAngle_deg = float(scan_parameters['FHAngle_deg'])

        THRESHOLD_ANGLE = 45  # degrees. Keep at 45 for expected behaviour

        changed = False  # Flag to indicate if a plane change occurred

        # Check for Axial plane
        if scanPlane == 'Axial':
            if abs(APAngle_deg) > THRESHOLD_ANGLE and abs(RLAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Sagittal plane
                scan_parameters['ScanPlane'] = 'Sagittal'

                # Adjust APAngle_deg
                if APAngle_deg > 0:
                    #FHAngle_deg += 90
                    APAngle_deg -= 90
                else:
                    #FHAngle_deg -= 90
                    APAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

            elif abs(RLAngle_deg) > THRESHOLD_ANGLE and abs(APAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Coronal plane
                scan_parameters['ScanPlane'] = 'Coronal'

                # Adjust RLAngle_deg
                if RLAngle_deg > 0:
                    #FHAngle_deg -= 90
                    RLAngle_deg -= 90
                else:
                    #FHAngle_deg += 90
                    RLAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

        elif scanPlane == 'Sagittal':
            if abs(APAngle_deg) > THRESHOLD_ANGLE and abs(FHAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Axial plane
                scan_parameters['ScanPlane'] = 'Axial'

                # Adjust APAngle_deg
                if APAngle_deg > 0:
                    APAngle_deg -= 90
                    #RLAngle_deg -= 90
                else:
                    APAngle_deg += 90
                    #RLAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

            elif abs(FHAngle_deg) > THRESHOLD_ANGLE and abs(APAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Coronal plane
                scan_parameters['ScanPlane'] = 'Coronal'

                # Adjust FHAngle_deg
                if FHAngle_deg > 0:
                    #APAngle_deg += 90
                    FHAngle_deg -= 90
                else:
                    #APAngle_deg -= 90
                    FHAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

        elif scanPlane == 'Coronal':
            if abs(RLAngle_deg) > THRESHOLD_ANGLE and abs(FHAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Axial plane
                scan_parameters['ScanPlane'] = 'Axial'

                # Adjust RLAngle_deg
                if RLAngle_deg > 0:
                    RLAngle_deg += 90
                    #APAngle_deg -= 90
                else:
                    RLAngle_deg -= 90
                    #APAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

            elif abs(FHAngle_deg) > THRESHOLD_ANGLE and abs(RLAngle_deg) <= THRESHOLD_ANGLE:
                # Change to Sagittal plane
                scan_parameters['ScanPlane'] = 'Sagittal'

                # Adjust FHAngle_deg
                if FHAngle_deg > 0:
                    #RLAngle_deg -= 90
                    FHAngle_deg -= 90
                else:
                    #RLAngle_deg += 90
                    FHAngle_deg += 90

                # Set parameters
                scan_parameters['RLAngle_deg'] = str(RLAngle_deg)
                scan_parameters['APAngle_deg'] = str(APAngle_deg)
                scan_parameters['FHAngle_deg'] = str(FHAngle_deg)
                changed = True

        if changed:
            # Update the scan volume geometry
            self.scan_volume.set_scan_volume_geometry(scan_parameters)
            self.scan_volume.update_axis_vectors()

            # Notify observers
        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def update(self, event):
        if event == EventEnum.SCAN_VOLUME_CHANGED:
            parameters = self.scan_volume.get_parameters()
            self.scan_parameters = parameters

    def add_observer(self, observer):
        self.observers.append(observer)
        log.debug(f"Observer {observer} added to {self}")

    def notify_observers(self, event: EventEnum):
        for observer in self.observers:
            log.debug(
                f"Subject {self} is updating observer {observer} with event {event}"
            )
            observer.update(event)

    def remove_observer(self, observer):
        self.observers.remove(observer)
        log.debug(f"Observer {observer} removed from {self}")


class ScanVolume:
    """The scan volume defines the rectangular volume to be scanned next. Its orientation with respect to the LPS coordinate system is defined by the axisX_LPS, axisY_LPS and axisZ_LPS parameters. The extent of the scan volume in the X, Y and Z directions is defined by the extentX_mm, extentY_mm and extentZ_mm parameters. The position of the center of the volume with respect to the LPS coordinate system is defined by the origin_LPS parameter."""

    def __init__(self):
        self.axisX_LPS = None
        self.axisY_LPS = None
        self.axisZ_LPS = None
        self.extentX_mm = None
        self.extentY_mm = None
        self._extentZ_mm = None  # See property extentZ_mm:  N_slices * slice_thickness_mm + (N_slices - 1) * slice_gap_mm
        self.resX_mm = 1
        self.resY_mm = 1
        # resolution in Z direction is the slice thickness
        self.origin_LPS = None
        self.N_slices = None
        self.slice_thickness_mm = None
        self.slice_gap_mm = None
        self.scanPlane = None

        # Angle radians to be used for rotation
        self.RLAngle_rad = 0.0
        self.APAngle_rad = 0.0
        self.FHAngle_rad = 0.0
        self.Rotation_lock = "None"
        self.scanPlane = "None"
        self.observers = []

        # Default scanner dimensions in mm
        self.scanner_AP_mm = 700.0
        self.scanner_RL_mm = 700.0
        self.scanner_FH_mm = 2000.0

    @property
    def extentZ_mm(self):
        return (
            self.N_slices * self.slice_thickness_mm
            + (self.N_slices - 1) * self.slice_gap_mm
        )

    @property
    def conversion_matrix(self) -> np.ndarray:
        """Affine transformation matrix that converts scan volume coordinates to LPS coordinates"""
        return np.array(
            [
                [
                    self.axisX_LPS[0],
                    self.axisY_LPS[0],
                    self.axisZ_LPS[0],
                    self.origin_LPS[0],
                ],
                [
                    self.axisX_LPS[1],
                    self.axisY_LPS[1],
                    self.axisZ_LPS[1],
                    self.origin_LPS[1],
                ],
                [
                    self.axisX_LPS[2],
                    self.axisY_LPS[2],
                    self.axisZ_LPS[2],
                    self.origin_LPS[2],
                ],
                [0, 0, 0, 1],
            ]
        )

    def set_scan_volume_geometry(self, scan_parameters: dict):
        self.N_slices = int(float(scan_parameters["NSlices"]))
        self.slice_gap_mm = float(scan_parameters["SliceGap_mm"])
        self.slice_thickness_mm = float(scan_parameters["SliceThickness_mm"])
        self.extentX_mm = float(scan_parameters["FOVPE_mm"])
        self.extentY_mm = float(scan_parameters["FOVFE_mm"])
        self.Rotation_lock = scan_parameters.get("Rotation_lock", self.Rotation_lock)
        if scan_parameters["ScanPlane"] == "Axial":
            self.scanPlane = "Axial"
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 1, 0])
            self.axisZ_LPS = np.array([0, 0, 1])
        if scan_parameters["ScanPlane"] == "Sagittal":
            self.scanPlane = "Sagittal"
            self.axisX_LPS = np.array([0, 1, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([-1, 0, 0])
        if scan_parameters["ScanPlane"] == "Coronal":
            self.scanPlane = "Coronal"
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([0, 1, 0])
        self.resXmm = 1
        self.resYmm = 1
        self.RLAngle_rad = np.deg2rad(float(scan_parameters.get("RLAngle_deg", 0)))
        self.APAngle_rad = np.deg2rad(float(scan_parameters.get("APAngle_deg", 0)))
        self.FHAngle_rad = np.deg2rad(float(scan_parameters.get("FHAngle_deg", 0)))
        self.update_axis_vectors()

        self.origin_LPS = np.array(
            [
                float(scan_parameters["OffCenterRL_mm"]),
                float(scan_parameters["OffCenterAP_mm"]),
                float(scan_parameters["OffCenterFH_mm"]),
            ]
        )

        # Commented this out since upadte_axis_vectors() does the same job. Can be deleted if not being used by anywhere else
        # rotate the axes according to the angle parameters

        self.clamp_to_scanner_dimensions()

        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def clamp_to_scanner_dimensions(self):

        # Clamp extent in all planes
        if self.scanPlane == "Axial":
            self.extentX_mm = np.clip(self.extentX_mm, 0, self.scanner_RL_mm)
            self.extentY_mm = np.clip(self.extentY_mm, 0, self.scanner_AP_mm)
        elif self.scanPlane == "Sagittal":
            self.extentX_mm = np.clip(self.extentX_mm, 0, self.scanner_AP_mm)
            self.extentY_mm = np.clip(self.extentY_mm, 0, self.scanner_FH_mm)
        elif self.scanPlane == "Coronal":
            self.extentX_mm = np.clip(self.extentX_mm, 0, self.scanner_RL_mm)
            self.extentY_mm = np.clip(self.extentY_mm, 0, self.scanner_FH_mm)

        half_extentX = self.extentX_mm / 2
        half_extentY = self.extentY_mm / 2
        half_extentZ = self.extentZ_mm / 2

        # Clamp origin and extent in RL direction
        self.origin_LPS[0] = np.clip(
            self.origin_LPS[0],
            -self.scanner_RL_mm / 2 + half_extentX,
            self.scanner_RL_mm / 2 - half_extentX,
        )
        # AP direction
        self.origin_LPS[1] = np.clip(
            self.origin_LPS[1],
            -self.scanner_AP_mm / 2 + half_extentY,
            self.scanner_AP_mm / 2 - half_extentY,
        )
        #  FH direction
        self.origin_LPS[2] = np.clip(
            self.origin_LPS[2],
            -self.scanner_FH_mm / 2 + half_extentZ,
            self.scanner_FH_mm / 2 - half_extentZ,
        )

    def calculate_from_edges_intersection_points_pixamp(
        self, edges: list[tuple], acquired_image: AcquiredImage
    ) -> list[np.array]:
        list_intersection_pts_LPS = []
        acquired_image_geometry = acquired_image.image_geometry
        origin_acq_im = acquired_image_geometry.origin_LPS
        axisX_acq_im = acquired_image_geometry.axisX_LPS
        axisY_acq_im = acquired_image_geometry.axisY_LPS
        for edge in edges:
            start_pt_line_LPS = self.scan_volume_mm_coords_to_LPS_coords(edge[0])
            end_pt_line_LPS = self.scan_volume_mm_coords_to_LPS_coords(edge[1])
            intersection_pts_LPS = self._line_plane_intersection(
                origin_acq_im,
                axisX_acq_im,
                axisY_acq_im,
                start_pt_line_LPS,
                end_pt_line_LPS,
            )
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
        list_intersection_pts_pixmap = sorted(
            list_intersection_pts_pixmap,
            key=lambda pt: np.arctan2(pt[1] - centroid[1], pt[0] - centroid[0]),
        )

        return list_intersection_pts_pixmap

    def compute_intersection_with_acquired_image(
        self, acquired_image: AcquiredImage
    ) -> list[np.array]:
        # compute the intersection of the scan volume with the acquired image and return a list of the corners of the polygon that represents the intersection. The corners are in pixmap coordinates and are ordered in a clockwise manner.
        # list the edges of the scan volume in scan volume coordinates. For each edge, find the intersection points (if any) with the 2D acquired image. Also find middle line of scan and intersection with the acquired image.
        edges, middle_lines, slice_collection = self._list_edges_of_scan_volume()

        intersections_points_slices = []
        for slice_edges in slice_collection:
            intersections_points_slices.append(
                self.calculate_from_edges_intersection_points_pixamp(
                    slice_edges, acquired_image
                )
            )

        return (
            self.calculate_from_edges_intersection_points_pixamp(edges, acquired_image),
            self.calculate_from_edges_intersection_points_pixamp(
                middle_lines, acquired_image
            ),
            intersections_points_slices,
        )

    def _get_geometry_parameters(self) -> dict:
        geometry_parameters = {}
        geometry_parameters["axisX_LPS"] = self.axisX_LPS
        geometry_parameters["axisY_LPS"] = self.axisY_LPS
        geometry_parameters["extentX_mm"] = self.extentX_mm
        geometry_parameters["extentY_mm"] = self.extentY_mm
        geometry_parameters["resX_mm"] = self.resX_mm
        geometry_parameters["resY_mm"] = self.resY_mm
        return geometry_parameters

    def get_image_geometry_of_slice(self, slice_number: int) -> ImageGeometry:
        """This function returns the ImageGeometry of each slice in the scan volume."""
        origin_slice_in_scan_volume_coords = np.array(
            [
                0,
                0,
                -self.extentZ_mm / 2
                + slice_number * (self.slice_thickness_mm + self.slice_gap_mm)
                + self.slice_thickness_mm / 2,
            ]
        )
        origin_slice_in_LPS_coords = self.scan_volume_mm_coords_to_LPS_coords(
            origin_slice_in_scan_volume_coords
        )
        geometry_parameters = self._get_geometry_parameters()
        geometry_parameters["origin_LPS"] = origin_slice_in_LPS_coords
        geometry_parameters["plane"] = self.scanPlane
        return ImageGeometry(geometry_parameters)

    def get_rotations(self) -> dict:
        return {'RLAngle_rad': self.RLAngle_rad, 'APAngle_rad': self.APAngle_rad, 'FHAngle_rad': self.FHAngle_rad}

    def translate_scan_volume(self, translation_vector_LPS: np.ndarray):
        # translate the scan volume by the translation vector (which is in LPS coordinates)
        self.origin_LPS += translation_vector_LPS
        self.clamp_to_scanner_dimensions()
        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def scale_scan_volume(self, scale_factor_x: float, scale_factor_y: float, origin_plane: str, handle_pos: QPointF, center_pos: QPointF):

        # Parameter validation
        valid_planes = ('Axial', 'Sagittal', 'Coronal')
        if origin_plane not in valid_planes:
            raise ValueError(f'Invalid "original" scan plane: {origin_plane}')
        top_down_plane = self.scanPlane
        if top_down_plane not in valid_planes:
            raise ValueError(f'Invalid "current" scan plane: {top_down_plane}')

        # Variable to keep track if the scale factors have been checked
        checked = False
        if self.APAngle_rad == 0 and origin_plane == 'Coronal':
            log.debug('Coronal not roated')
            checked = True
        if self.RLAngle_rad == 0 and origin_plane == 'Sagittal':
            log.debug('Sagittal not roated')
            checked = True
        if self.FHAngle_rad == 0 and origin_plane == 'Axial':
            log.debug('Axial not roated')
            checked = True

        # Logic to determine which axis to scale on it is done through creating quadrants from the middle point of the scan volume, since only one of scale handles are in one at any given moment
        if not checked:
            if origin_plane == 'Sagittal': #around RL axis
                log.debug('Grabbed Sagittal')
                # Rotation to positive direction
                if self.RLAngle_rad * 2 % 2 <= 1 and self.RLAngle_rad * 2 % 2 > 0:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                elif self.RLAngle_rad * 2 % 2 > 1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                # Rotation to negative direction
                elif self.RLAngle_rad * 2 % 2 < 0 and self.RLAngle_rad * 2 % 2 >= -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                elif self.RLAngle_rad * 2 % 2 < -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
            elif origin_plane == 'Coronal': #around AP axis
                log.debug('Grabbed Coronal')
                # Rotation to positive direction
                if self.APAngle_rad * 2 % 2 <= 1 and self.APAngle_rad * 2 % 2 > 0:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                elif self.APAngle_rad * 2 % 2 > 1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                # Rotation to negative direction
                elif self.APAngle_rad * 2 % 2 < 0 and self.APAngle_rad * 2 % 2 >= -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                elif self.APAngle_rad * 2 % 2 < -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
            elif origin_plane == 'Axial': #around FH axis
                log.debug('Grabbed Axial')
                # Rotation to positive direction
                if self.FHAngle_rad * 2 % 2 <= 1 and self.FHAngle_rad * 2 % 2 > 0:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                elif self.FHAngle_rad * 2 % 2 > 1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                # Rotation to negative direction
                elif self.FHAngle_rad * 2 % 2 < 0 and self.FHAngle_rad * 2 % 2 >= -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True
                elif self.FHAngle_rad * 2 % 2 < -1:
                    if handle_pos.x() > center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_x = 1
                        checked = True
                    if handle_pos.x() > center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() > center_pos.y():
                        scale_factor_y = 1
                        checked = True
                    if handle_pos.x() < center_pos.x() and handle_pos.y() < center_pos.y():
                        scale_factor_x = 1
                        checked = True

        # If the scale factors have not been checked, then the scale factors are set to 1 since the decision tree didn't result in changes
        if not checked:
            log.debug('Have not changed any of the scale factors')
            scale_factor_x = 1
            scale_factor_y = 1

        if scale_factor_x != 1 and scale_factor_y != 1:
            log.debug(checked, scale_factor_x, scale_factor_y)

        log.debug('Scale factors:', scale_factor_x, scale_factor_y)

        # Scaling logic
        if top_down_plane == origin_plane:
            self.extentX_mm *= scale_factor_x
            self.extentY_mm *= scale_factor_y
        elif top_down_plane == "Axial":
            if origin_plane == "Sagittal":
                self.extentY_mm *= scale_factor_x
                self.slice_gap_mm *= scale_factor_y
            elif origin_plane == "Coronal":
                self.extentX_mm *= scale_factor_x
                self.slice_gap_mm *= scale_factor_y
        elif top_down_plane == "Sagittal":
            if origin_plane == "Axial":
                self.extentX_mm *= scale_factor_y
                self.slice_gap_mm *= scale_factor_x
            elif origin_plane == "Coronal":
                self.extentY_mm *= scale_factor_y
                self.slice_gap_mm *= scale_factor_x
        elif top_down_plane == "Coronal":
            if origin_plane == "Axial":
                self.extentX_mm *= scale_factor_x
                self.slice_gap_mm *= scale_factor_y
            elif origin_plane == "Sagittal":
                self.extentY_mm *= scale_factor_y
                self.slice_gap_mm *= scale_factor_x

        self.clamp_to_scanner_dimensions()
        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    # Event reciever for rotation using rotation handlers
    def rotate_scan_volume(self, rotation_angle_rad, rotation_axis):
        """This function computes the new angle using rotation angle and axis"""

        def normalize_angle_rad(angle_rad):
            return (angle_rad + np.pi) % (2 * np.pi) - np.pi

        # Update the rotation angle for the specified axis
        if rotation_axis == "RL" and self.Rotation_lock in ("None", "RL"):
            self.RLAngle_rad += rotation_angle_rad
            self.RLAngle_rad = normalize_angle_rad(self.RLAngle_rad)
        elif rotation_axis == "AP" and self.Rotation_lock in ("None", "AP"):
            self.APAngle_rad += rotation_angle_rad
            self.APAngle_rad = normalize_angle_rad(self.APAngle_rad)
        elif rotation_axis == "FH" and self.Rotation_lock in ("None", "FH"):
            self.FHAngle_rad += rotation_angle_rad
            self.FHAngle_rad = normalize_angle_rad(self.FHAngle_rad)
        else:
            if rotation_axis in ("RL", "AP", "FH"):
                log.warning("Attempted rotation locked by Rotation Lock")
                pass
            else:
                log.error(f"Unknown rotation axis: {rotation_axis}")
                raise ValueError(f"Unknown rotation axis: {rotation_axis}")

        # Update the axis vectors based on the new rotation angles
        self.update_axis_vectors()
        self.clamp_to_scanner_dimensions()
        self.notify_observers(EventEnum.SCAN_VOLUME_CHANGED)

    def update_axis_vectors(self):
        """Updates the scan area for rotation purposes"""
        # Reset axes to initial state
        if self.scanPlane == "Axial":
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 1, 0])
            self.axisZ_LPS = np.array([0, 0, 1])
        elif self.scanPlane == "Sagittal":
            self.axisX_LPS = np.array([0, 1, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([-1, 0, 0])
        elif self.scanPlane == "Coronal":
            self.axisX_LPS = np.array([1, 0, 0])
            self.axisY_LPS = np.array([0, 0, -1])
            self.axisZ_LPS = np.array([0, 1, 0])
        else:
            log.error(f"Unknown scanPlane: {self.scanPlane}")
            raise ValueError(f"Unknown scanPlane: {self.scanPlane}")

        # Apply rotations in the order RL, AP, FH
        rotation_matrix_RL = self.get_rotation_matrix("RL", self.RLAngle_rad)
        rotation_matrix_AP = self.get_rotation_matrix("AP", self.APAngle_rad)
        rotation_matrix_FH = self.get_rotation_matrix("FH", self.FHAngle_rad)

        # Combined rotation matrix
        combined_rotation_matrix = np.linalg.multi_dot(
            [rotation_matrix_FH, rotation_matrix_AP, rotation_matrix_RL]
        )

        # Rotate axes
        self.axisX_LPS = np.dot(combined_rotation_matrix, self.axisX_LPS)
        self.axisY_LPS = np.dot(combined_rotation_matrix, self.axisY_LPS)
        self.axisZ_LPS = np.dot(combined_rotation_matrix, self.axisZ_LPS)

    def get_rotation_matrix(self, axis, angle_rad):
        """Returns the rotation matrix for a given axis and angle"""
        if axis == "RL":
            rotation_matrix = np.array(
                [
                    [1, 0, 0],
                    [0, np.cos(angle_rad), -np.sin(angle_rad)],
                    [0, np.sin(angle_rad), np.cos(angle_rad)],
                ]
            )
        elif axis == "AP":
            rotation_matrix = np.array(
                [
                    [np.cos(angle_rad), 0, np.sin(angle_rad)],
                    [0, 1, 0],
                    [-np.sin(angle_rad), 0, np.cos(angle_rad)],
                ]
            )
        elif axis == "FH":
            rotation_matrix = np.array(
                [
                    [np.cos(angle_rad), -np.sin(angle_rad), 0],
                    [np.sin(angle_rad), np.cos(angle_rad), 0],
                    [0, 0, 1],
                ]
            )
        else:
            raise ValueError(f"Unknown rotation axis: {axis}")
        return rotation_matrix

    def scan_volume_mm_coords_to_LPS_coords(
        self, scan_volume_mm_coords: tuple
    ) -> tuple:
        """Convert scan volume coordinates to LPS coordinates. The scan volume coordinates are in millimeters, and the LPS coordinates are in millimeters."""
        x, y, z = scan_volume_mm_coords

        L, P, S, one = np.dot(self.conversion_matrix, np.array([x, y, z, 1]))

        return (L, P, S)

    def LPS_coords_to_scan_volume_mm_coords(self, LPS_coords: tuple) -> tuple:
        """Convert LPS coordinates to scan volume coordinates. The LPS coordinates are in millimeters, and the scan volume coordinates are in millimeters."""

        L, P, S = LPS_coords

        x, y, z, one = np.dot(
            np.linalg.inv(self.conversion_matrix), np.array([L, P, S, 1])
        )

        return (x, y, z)

    def _list_edges_of_scan_volume(self) -> list[tuple]:
        """list the edges of the scan volume in scan volume coordinates"""
        # Define the corners of the FOV in FOV coordinates
        front_top_left = np.array(
            [-self.extentX_mm / 2, -self.extentY_mm / 2, -self.extentZ_mm / 2]
        )
        front_top_right = np.array(
            [self.extentX_mm / 2, -self.extentY_mm / 2, -self.extentZ_mm / 2]
        )
        front_bottom_right = np.array(
            [self.extentX_mm / 2, self.extentY_mm / 2, -self.extentZ_mm / 2]
        )
        front_bottom_left = np.array(
            [-self.extentX_mm / 2, self.extentY_mm / 2, -self.extentZ_mm / 2]
        )
        back_top_left = np.array(
            [-self.extentX_mm / 2, -self.extentY_mm / 2, self.extentZ_mm / 2]
        )
        back_top_right = np.array(
            [self.extentX_mm / 2, -self.extentY_mm / 2, self.extentZ_mm / 2]
        )
        back_bottom_right = np.array(
            [self.extentX_mm / 2, self.extentY_mm / 2, self.extentZ_mm / 2]
        )
        back_bottom_left = np.array(
            [-self.extentX_mm / 2, self.extentY_mm / 2, self.extentZ_mm / 2]
        )

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
            (front_bottom_left, back_bottom_left),
        ]

        top_left = (back_top_left - front_top_left) / 2 + front_top_left
        top_right = (back_top_right - front_top_right) / 2 + front_top_right
        bottom_left = (back_bottom_left - front_bottom_left) / 2 + front_bottom_left
        bottom_right = (back_bottom_right - front_bottom_right) / 2 + front_bottom_right

        # dx = front_top_left - front_bottom_left
        # dy = P2.y - P1.y
        # dz = P2.z - P1.z
        # Len = sqrt(dx*dx+dy*dy+dz*dz)
        # dx /= Len
        # dy /= Len
        # dz /= Len
        v1 = back_top_left - front_top_left
        v2 = back_top_right - front_top_right
        v3 = back_bottom_left - front_bottom_left
        v4 = back_bottom_right - front_bottom_right
        v_hat1 = v1 / (v1**2).sum() ** 0.5
        v_hat2 = v2 / (v2**2).sum() ** 0.5
        v_hat3 = v3 / (v3**2).sum() ** 0.5
        v_hat4 = v4 / (v4**2).sum() ** 0.5

        middle_lines = [
            (top_left, top_right),
            (top_right, bottom_right),
            (bottom_right, bottom_left),
            (bottom_left, top_left),
        ]

        slice_center_distances = []
        for i in range(self.N_slices):
            center = (self.slice_thickness_mm / 2) + i * (
                self.slice_thickness_mm + self.slice_gap_mm
            )
            slice_center_distances.append(center)

        slices_collection = []

        for i in range(len(slice_center_distances)):
            disatance_from_0 = slice_center_distances[i]
            point_1 = front_top_left + disatance_from_0 * v_hat1
            point_2 = front_top_right + disatance_from_0 * v_hat2
            point_3 = front_bottom_left + disatance_from_0 * v_hat3
            point_4 = front_bottom_right + disatance_from_0 * v_hat4

            slices_collection.append(
                (
                    (point_1, point_2),
                    (point_2, point_4),
                    (point_4, point_3),
                    (point_3, point_1),
                )
            )

        return edges, middle_lines, slices_collection

    def _line_plane_intersection(
        self, origin_plane, axisX_plane, axisY_plane, start_pt_line, end_pt_line
    ) -> list[np.array]:

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

        else:
            try:
                t, u, v = np.linalg.solve(mat, vec)
                # Check if the intersection lies within the line segment
                if 0 <= t <= 1:
                    intersection_pts.append(start_pt_line + t * line_dir)
                    return intersection_pts
                else:
                    # The intersection point lies outside the line segment
                    return None
            except np.linalg.LinAlgError:
                log.error("Error: Singular matrix")
                # The line is parallel to the plane
                return None

    def add_observer(self, observer):
        self.observers.append(observer)
        log.debug(f"Observer {observer} added to {self}")

    def notify_observers(self, event: EventEnum):
        for observer in self.observers:
            log.debug(
                f"Subject {self}, is updating observer {observer}, with event, {event}"
            )
            observer.update(event)

    def remove_observer(self, observer):
        self.observers.remove(observer)
        log.debug(f"Observer {observer}, removed from {self}")

    # Added angles and scan plane as parameters. Needed to compute rotation
    def get_parameters(self):
        return {
            "NSlices": self.N_slices,
            "SliceGap_mm": self.slice_gap_mm,
            "SliceThickness_mm": self.slice_thickness_mm,
            "FOVPE_mm": self.extentX_mm,
            "FOVFE_mm": self.extentY_mm,
            "OffCenterRL_mm": self.origin_LPS[0],
            "OffCenterAP_mm": self.origin_LPS[1],
            "OffCenterFH_mm": self.origin_LPS[2],
            "RLAngle_deg": np.degrees(self.RLAngle_rad),
            "APAngle_deg": np.degrees(self.APAngle_rad),
            "FHAngle_deg": np.degrees(self.FHAngle_rad),
            "ScanPlane": self.scanPlane,
            "Rotation_lock": self.Rotation_lock,
        }

    def calculate_slice_positions(self):
        slice_positions = []
        for i in range(self.N_slices):
            z_position = -self.extentZ_mm / 2 + i * (
                self.slice_thickness_mm + self.slice_gap_mm
            )
            slice_positions.append(z_position)
        return slice_positions
