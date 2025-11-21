"""
Face tracking with IOU-based tracking
"""
import logging
from typing import List, Tuple, Optional, Dict
import numpy as np
from .config import DEEPSORT_ENABLED

logger = logging.getLogger(__name__)


class SimpleTracker:
    """Simple IOU-based tracker"""
    
    def __init__(self, max_age=30, iou_threshold=0.3):
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self.tracks = {}  # track_id -> {bbox, age, hits}
        self.next_id = 1
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Convert to x1, y1, x2, y2 format
        box1_area = w1 * h1
        box2_area = w2 * h2
        
        x1_inter = max(x1, x2)
        y1_inter = max(y1, y2)
        x2_inter = min(x1 + w1, x2 + w2)
        y2_inter = min(y1 + h1, y2 + h2)
        
        if x2_inter < x1_inter or y2_inter < y1_inter:
            return 0.0
        
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
        union_area = box1_area + box2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def update(self, detections: List[Tuple[int, int, int, int, float]]):
        """Update tracks with new detections"""
        # Age all tracks
        for track_id in list(self.tracks.keys()):
            self.tracks[track_id]['age'] += 1
            if self.tracks[track_id]['age'] > self.max_age:
                del self.tracks[track_id]
        
        # Match detections to existing tracks
        matched = set()
        results = []
        
        for detection in detections:
            x, y, w, h, conf = detection
            best_iou = 0
            best_track_id = None
            
            # Find best matching track
            for track_id, track in self.tracks.items():
                if track_id in matched:
                    continue
                
                iou = self._calculate_iou((x, y, w, h), track['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id:
                # Update existing track
                self.tracks[best_track_id]['bbox'] = (x, y, w, h)
                self.tracks[best_track_id]['age'] = 0
                self.tracks[best_track_id]['hits'] += 1
                matched.add(best_track_id)
                results.append((x, y, w, h, best_track_id, conf))
            else:
                # Create new track
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = {
                    'bbox': (x, y, w, h),
                    'age': 0,
                    'hits': 1
                }
                results.append((x, y, w, h, track_id, conf))
        
        return results


class Tracker:
    """Face tracker wrapper"""
    
    def __init__(self):
        self.tracker = None
        self._init_tracker()
    
    def _init_tracker(self):
        """Initialize tracker"""
        if not DEEPSORT_ENABLED:
            logger.info("DeepSORT disabled, using IOU-based tracking")
            self.tracker = SimpleTracker()
            return
        
        try:
            # Try to import deepsort
            try:
                from deep_sort_realtime.deepsort_tracker import DeepSort
                self.tracker = DeepSort(max_age=50, n_init=3)
                logger.info("DeepSORT tracker initialized")
                
                # Test the tracker with dummy data to ensure it works
                import numpy as np
                test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
                test_detections = [[10, 10, 20, 20, 0.9]]
                self.tracker.update_tracks(test_detections, frame=test_frame)
                logger.info("DeepSORT tracker test successful")
                
            except ImportError:
                logger.warning("deep_sort_realtime not installed, using IOU-based tracking")
                self.tracker = SimpleTracker()
            except Exception as e:
                logger.warning(f"DeepSORT initialization failed ({e}), using IOU-based tracking")
                self.tracker = SimpleTracker()
        except Exception as e:
            logger.error(f"Error initializing tracker: {e}")
            self.tracker = SimpleTracker()
    
    def update(
        self,
        detections: List[Tuple[int, int, int, int, float]],
        frame: np.ndarray
    ) -> List[Tuple[int, int, int, int, int, float]]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of (x, y, w, h, confidence) tuples
            frame: Current frame (for feature extraction if needed)
            
        Returns:
            List of (x, y, w, h, track_id, confidence) tuples
        """
        if self.tracker is None:
            return [(x, y, w, h, idx, conf) for idx, (x, y, w, h, conf) in enumerate(detections)]
        
        try:
            # Check if it's SimpleTracker
            if isinstance(self.tracker, SimpleTracker):
                return self.tracker.update(detections)
            
            # DeepSORT tracker
            # Convert detections to DeepSORT format: [[x1, y1, x2, y2, confidence], ...]
            detections_formatted = []
            for x, y, w, h, conf in detections:
                # Convert numpy types to Python native types to prevent type errors
                try:
                    x = int(x.item()) if hasattr(x, 'item') else int(x)
                    y = int(y.item()) if hasattr(y, 'item') else int(y)
                    w = int(w.item()) if hasattr(w, 'item') else int(w)
                    h = int(h.item()) if hasattr(h, 'item') else int(h)
                    conf = float(conf.item()) if hasattr(conf, 'item') else float(conf)
                    detections_formatted.append([x, y, x + w, y + h, conf])
                except Exception as e:
                    logger.warning(f"Error converting detection data: {e}, falling back to simple tracker")
                    if not hasattr(self, 'fallback_tracker'):
                        self.fallback_tracker = SimpleTracker()
                    return self.fallback_tracker.update(detections)
            
            if not detections_formatted:
                tracks = self.tracker.update_tracks([], frame=frame)
            else:
                # DeepSORT expects detections as list of lists
                tracks = self.tracker.update_tracks(detections_formatted, frame=frame)
            
            # Convert tracks back to our format
            results = []
            for track in tracks:
                if track.is_confirmed():
                    x1, y1, x2, y2 = track.to_tlbr()
                    track_id = track.track_id
                    confidence = track.get_det_conf() if hasattr(track, 'get_det_conf') else 1.0
                    results.append((int(x1), int(y1), int(x2 - x1), int(y2 - y1), track_id, float(confidence)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error updating tracker: {e}")
            logger.info("Falling back to simple tracking")
            # Fallback to simple tracking
            if not hasattr(self, 'fallback_tracker'):
                self.fallback_tracker = SimpleTracker()
            return [(x, y, w, h, idx, conf) for idx, (x, y, w, h, conf) in enumerate(detections)]

