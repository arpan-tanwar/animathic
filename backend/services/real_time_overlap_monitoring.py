"""
Real-time Overlap Detection During Generation for Animathic
Monitors overlaps during animation generation and provides real-time feedback and correction
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class OverlapSeverity(Enum):
    """Overlap severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OverlapEvent:
    """Represents a detected overlap event"""
    object1_id: str
    object2_id: str
    object1_type: str
    object2_type: str
    overlap_area: float
    severity: OverlapSeverity
    timestamp: float
    position1: List[float]
    position2: List[float]
    size1: float
    size2: float
    distance: float
    suggested_action: str
    auto_corrected: bool = False
    correction_applied: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Configuration for real-time overlap monitoring"""
    check_interval: float = 0.1  # Check every 0.1 seconds
    overlap_threshold: float = 0.1  # Minimum overlap to trigger action
    auto_correct: bool = True  # Automatically correct overlaps
    logging: bool = True  # Log overlap events
    real_time_feedback: bool = True  # Provide real-time feedback
    correction_strategies: List[str] = field(default_factory=lambda: [
        'reposition', 'fade_out', 'scale_adjust', 'timing_adjust'
    ])
    max_concurrent_corrections: int = 3
    correction_timeout: float = 5.0  # Timeout for correction operations


class RealTimeOverlapMonitor:
    """Real-time overlap detection and monitoring system"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize the real-time overlap monitor"""
        self.config = config or MonitoringConfig()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_corrections)
        
        # Monitoring state
        self.current_objects: Dict[str, Dict[str, Any]] = {}
        self.overlap_history: List[OverlapEvent] = []
        self.active_corrections: Dict[str, Dict[str, Any]] = {}
        self.monitoring_stats = {
            'total_checks': 0,
            'overlaps_detected': 0,
            'corrections_applied': 0,
            'failed_corrections': 0,
            'last_check_time': 0.0
        }
        
        # Callbacks for real-time feedback
        self.overlap_callbacks: List[Callable[[OverlapEvent], None]] = []
        self.correction_callbacks: List[Callable[[str, bool], None]] = []
        
        logger.info("RealTimeOverlapMonitor initialized")
    
    def start_monitoring(self, objects: Dict[str, Dict[str, Any]]) -> bool:
        """Start real-time overlap monitoring"""
        try:
            if self.monitoring_active:
                logger.warning("Monitoring already active")
                return False
            
            self.current_objects = objects.copy()
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            logger.info("Real-time overlap monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop real-time overlap monitoring"""
        try:
            if not self.monitoring_active:
                return True
            
            self.monitoring_active = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2.0)
            
            # Cancel any pending corrections
            for correction_id in list(self.active_corrections.keys()):
                self._cancel_correction(correction_id)
            
            logger.info("Real-time overlap monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def update_objects(self, objects: Dict[str, Dict[str, Any]]) -> None:
        """Update the current object set being monitored"""
        try:
            self.current_objects = objects.copy()
            logger.debug(f"Updated monitoring objects: {len(objects)} objects")
        except Exception as e:
            logger.error(f"Failed to update objects: {e}")
    
    def add_object(self, obj_id: str, obj_data: Dict[str, Any]) -> None:
        """Add a new object to monitoring"""
        try:
            self.current_objects[obj_id] = obj_data
            logger.debug(f"Added object to monitoring: {obj_id}")
        except Exception as e:
            logger.error(f"Failed to add object {obj_id}: {e}")
    
    def remove_object(self, obj_id: str) -> None:
        """Remove an object from monitoring"""
        try:
            if obj_id in self.current_objects:
                del self.current_objects[obj_id]
                logger.debug(f"Removed object from monitoring: {obj_id}")
        except Exception as e:
            logger.error(f"Failed to remove object {obj_id}: {e}")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                start_time = time.time()
                
                # Check for overlaps
                overlaps = self._check_current_overlaps()
                
                # Process detected overlaps
                for overlap in overlaps:
                    self._process_overlap(overlap)
                
                # Update monitoring stats
                self.monitoring_stats['total_checks'] += 1
                self.monitoring_stats['last_check_time'] = start_time
                
                # Wait for next check interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.check_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.monitoring_active = False
    
    def _check_current_overlaps(self) -> List[OverlapEvent]:
        """Check for current overlaps in the scene"""
        overlaps = []
        
        try:
            object_items = list(self.current_objects.items())
            
            for i, (obj_id1, obj1) in enumerate(object_items):
                pos1 = obj1.get('properties', {}).get('position', [0, 0, 0])
                size1 = obj1.get('properties', {}).get('size', 1.0)
                type1 = obj1.get('type', 'unknown')
                
                if len(pos1) < 2:
                    continue
                
                for j, (obj_id2, obj2) in enumerate(object_items[i+1:], i+1):
                    pos2 = obj2.get('properties', {}).get('position', [0, 0, 0])
                    size2 = obj2.get('properties', {}).get('size', 1.0)
                    type2 = obj2.get('type', 'unknown')
                    
                    if len(pos2) < 2:
                        continue
                    
                    # Calculate distance and overlap
                    distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    combined_size = (size1 + size2) / 2
                    
                    # Check for overlap
                    if distance < combined_size:
                        overlap_area = self._calculate_overlap_area(pos1, size1, pos2, size2)
                        
                        if overlap_area > self.config.overlap_threshold:
                            # Determine severity
                            severity = self._determine_overlap_severity(overlap_area, distance, combined_size)
                            
                            # Create overlap event
                            overlap_event = OverlapEvent(
                                object1_id=obj_id1,
                                object2_id=obj_id2,
                                object1_type=type1,
                                object2_type=type2,
                                overlap_area=overlap_area,
                                severity=severity,
                                timestamp=time.time(),
                                position1=pos1,
                                position2=pos2,
                                size1=size1,
                                size2=size2,
                                distance=distance,
                                suggested_action=self._suggest_correction_action(severity, type1, type2)
                            )
                            
                            overlaps.append(overlap_event)
            
            return overlaps
            
        except Exception as e:
            logger.error(f"Error checking overlaps: {e}")
            return []
    
    def _calculate_overlap_area(self, pos1: List[float], size1: float, pos2: List[float], size2: float) -> float:
        """Calculate the overlap area between two objects"""
        try:
            # Simple circular overlap calculation
            distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
            
            if distance >= size1 + size2:
                return 0.0  # No overlap
            
            if distance <= abs(size1 - size2):
                # One object is completely inside the other
                return min(size1, size2) ** 2 * math.pi
            
            # Partial overlap - calculate intersection area
            r1, r2 = size1, size2
            d = distance
            
            # Using the formula for circular segment intersection
            cos_theta1 = (d**2 + r1**2 - r2**2) / (2 * d * r1)
            cos_theta2 = (d**2 + r2**2 - r1**2) / (2 * d * r2)
            
            theta1 = math.acos(max(-1, min(1, cos_theta1)))
            theta2 = math.acos(max(-1, min(1, cos_theta2)))
            
            area1 = r1**2 * theta1 - 0.5 * r1**2 * math.sin(2 * theta1)
            area2 = r2**2 * theta2 - 0.5 * r2**2 * math.sin(2 * theta2)
            
            return area1 + area2
            
        except Exception as e:
            logger.error(f"Error calculating overlap area: {e}")
            return 0.0
    
    def _determine_overlap_severity(self, overlap_area: float, distance: float, combined_size: float) -> OverlapSeverity:
        """Determine the severity of an overlap"""
        try:
            overlap_ratio = overlap_area / (combined_size ** 2 * math.pi)
            
            if overlap_ratio > 0.8:
                return OverlapSeverity.CRITICAL
            elif overlap_ratio > 0.5:
                return OverlapSeverity.HIGH
            elif overlap_ratio > 0.2:
                return OverlapSeverity.MEDIUM
            else:
                return OverlapSeverity.LOW
                
        except Exception as e:
            logger.error(f"Error determining overlap severity: {e}")
            return OverlapSeverity.MEDIUM
    
    def _suggest_correction_action(self, severity: OverlapSeverity, type1: str, type2: str) -> str:
        """Suggest a correction action based on overlap severity and object types"""
        try:
            # ULTRA CONSERVATIVE: Only use fade-out for critical overlaps
            # Prefer repositioning and timing adjustments over fade-outs
            
            if severity == OverlapSeverity.CRITICAL:
                # Only for truly critical overlaps
                return "immediate_fade_out"
            elif severity == OverlapSeverity.HIGH:
                if type1 in ['text', 'label'] or type2 in ['text', 'label']:
                    return "reposition_text"
                else:
                    # For high severity, try timing adjustment first, not fade-out
                    return "timing_adjust"
            elif severity == OverlapSeverity.MEDIUM:
                return "timing_adjust"
            else:
                return "monitor"
                
        except Exception as e:
            logger.error(f"Error suggesting correction action: {e}")
            return "monitor"
    
    def _process_overlap(self, overlap: OverlapEvent) -> None:
        """Process a detected overlap event"""
        try:
            # Log overlap event
            if self.config.logging:
                logger.warning(f"Overlap detected: {overlap.object1_id} ({overlap.object1_type}) and {overlap.object2_id} ({overlap.object2_type}) - Severity: {overlap.severity.value}")
            
            # Add to overlap history
            self.overlap_history.append(overlap)
            self.monitoring_stats['overlaps_detected'] += 1
            
            # Trigger overlap callbacks
            for callback in self.overlap_callbacks:
                try:
                    callback(overlap)
                except Exception as e:
                    logger.error(f"Error in overlap callback: {e}")
            
            # ULTRA CONSERVATIVE: Only auto-correct for critical overlaps
            # Avoid unnecessary fade-outs for mathematical content
            if self.config.auto_correct and overlap.severity == OverlapSeverity.CRITICAL:
                # Only for truly critical overlaps
                self._schedule_correction(overlap)
            elif self.config.auto_correct and overlap.severity == OverlapSeverity.HIGH and overlap.object1_type in ['text', 'label'] or overlap.object2_type in ['text', 'label']:
                # Only auto-correct high severity text overlaps
                self._schedule_correction(overlap)
            
        except Exception as e:
            logger.error(f"Error processing overlap: {e}")
    
    def _schedule_correction(self, overlap: OverlapEvent) -> None:
        """Schedule an overlap correction"""
        try:
            correction_id = f"correction_{overlap.object1_id}_{overlap.object2_id}_{int(time.time())}"
            
            # Check if we can handle more corrections
            if len(self.active_corrections) >= self.config.max_concurrent_corrections:
                logger.warning(f"Maximum concurrent corrections reached, skipping correction for {correction_id}")
                return
            
            # Schedule correction
            future = self.executor.submit(self._apply_correction, overlap, correction_id)
            
            self.active_corrections[correction_id] = {
                'overlap': overlap,
                'future': future,
                'start_time': time.time(),
                'status': 'pending'
            }
            
            logger.info(f"Scheduled correction {correction_id} for overlap between {overlap.object1_id} and {overlap.object2_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling correction: {e}")
    
    def _apply_correction(self, overlap: OverlapEvent, correction_id: str) -> bool:
        """Apply a correction for an overlap"""
        try:
            logger.info(f"Applying correction {correction_id} for overlap between {overlap.object1_id} and {overlap.object2_id}")
            
            # Update correction status
            self.active_corrections[correction_id]['status'] = 'applying'
            
            # Apply correction based on suggested action
            success = False
            correction_applied = None
            
            if overlap.suggested_action == "immediate_fade_out":
                success, correction_applied = self._apply_immediate_fade_out(overlap)
            elif overlap.suggested_action == "reposition_text":
                success, correction_applied = self._apply_text_reposition(overlap)
            elif overlap.suggested_action == "fade_out_previous":
                success, correction_applied = self._apply_fade_out_previous(overlap)
            elif overlap.suggested_action == "timing_adjust":
                success, correction_applied = self._apply_timing_adjustment(overlap)
            else:
                success, correction_applied = self._apply_monitoring_only(overlap)
            
            # Update overlap event
            overlap.auto_corrected = True
            overlap.correction_applied = correction_applied
            
            # Update correction status
            self.active_corrections[correction_id]['status'] = 'completed' if success else 'failed'
            
            # Update monitoring stats
            if success:
                self.monitoring_stats['corrections_applied'] += 1
            else:
                self.monitoring_stats['failed_corrections'] += 1
            
            # Trigger correction callbacks
            for callback in self.correction_callbacks:
                try:
                    callback(correction_id, success)
                except Exception as e:
                    logger.error(f"Error in correction callback: {e}")
            
            logger.info(f"Correction {correction_id} {'completed successfully' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Error applying correction {correction_id}: {e}")
            self.active_corrections[correction_id]['status'] = 'failed'
            self.monitoring_stats['failed_corrections'] += 1
            return False
    
    def _apply_immediate_fade_out(self, overlap: OverlapEvent) -> Tuple[bool, str]:
        """Apply immediate fade-out correction"""
        try:
            # Determine which object to fade out (usually the newer one)
            obj1_timestamp = self.current_objects.get(overlap.object1_id, {}).get('created_at', 0)
            obj2_timestamp = self.current_objects.get(overlap.object2_id, {}).get('created_at', 0)
            
            target_obj_id = overlap.object2_id if obj2_timestamp > obj1_timestamp else overlap.object1_id
            
            # Add fade-out animation
            if target_obj_id in self.current_objects:
                obj = self.current_objects[target_obj_id]
                if 'animations' not in obj:
                    obj['animations'] = []
                
                fade_out_anim = {
                    'type': 'fade_out',
                    'duration': 0.3,
                    'start_time': 'immediate',
                    'reason': 'overlap_correction'
                }
                
                obj['animations'].append(fade_out_anim)
                
                return True, f"immediate_fade_out_{target_obj_id}"
            
            return False, "object_not_found"
            
        except Exception as e:
            logger.error(f"Error applying immediate fade-out: {e}")
            return False, f"error: {str(e)}"
    
    def _apply_text_reposition(self, overlap: OverlapEvent) -> Tuple[bool, str]:
        """Apply text repositioning correction"""
        try:
            # Identify which object is text
            text_obj_id = None
            other_obj_id = None
            
            if overlap.object1_type in ['text', 'label']:
                text_obj_id = overlap.object1_id
                other_obj_id = overlap.object2_id
            elif overlap.object2_type in ['text', 'label']:
                text_obj_id = overlap.object2_id
                other_obj_id = overlap.object1_id
            
            if text_obj_id and other_obj_id:
                # Calculate new position for text (above and to the right)
                other_pos = self.current_objects[other_obj_id]['properties']['position']
                text_size = self.current_objects[text_obj_id]['properties'].get('size', 0.5)
                
                new_pos = [
                    other_pos[0] + text_size * 1.5,
                    other_pos[1] + text_size * 1.5,
                    other_pos[2] if len(other_pos) > 2 else 0
                ]
                
                # Update text position
                self.current_objects[text_obj_id]['properties']['position'] = new_pos
                
                return True, f"text_reposition_{text_obj_id}"
            
            return False, "no_text_object_found"
            
        except Exception as e:
            logger.error(f"Error applying text reposition: {e}")
            return False, f"error: {str(e)}"
    
    def _apply_fade_out_previous(self, overlap: OverlapEvent) -> Tuple[bool, str]:
        """Apply fade-out previous object correction"""
        try:
            # Determine which object to fade out (usually the older one)
            obj1_timestamp = self.current_objects.get(overlap.object1_id, {}).get('created_at', 0)
            obj2_timestamp = self.current_objects.get(overlap.object2_id, {}).get('created_at', 0)
            
            target_obj_id = overlap.object1_id if obj1_timestamp < obj2_timestamp else overlap.object2_id
            
            # Add fade-out animation
            if target_obj_id in self.current_objects:
                obj = self.current_objects[target_obj_id]
                if 'animations' not in obj:
                    obj['animations'] = []
                
                fade_out_anim = {
                    'type': 'fade_out',
                    'duration': 0.3,
                    'start_time': 'after_persistent_display',
                    'reason': 'overlap_correction'
                }
                
                obj['animations'].append(fade_out_anim)
                
                return True, f"fade_out_previous_{target_obj_id}"
            
            return False, "object_not_found"
            
        except Exception as e:
            logger.error(f"Error applying fade-out previous: {e}")
            return False, f"error: {str(e)}"
    
    def _apply_timing_adjustment(self, overlap: OverlapEvent) -> Tuple[bool, str]:
        """Apply timing adjustment correction"""
        try:
            # Add a small delay to prevent overlap
            target_obj_id = overlap.object2_id  # Usually the newer object
            
            if target_obj_id in self.current_objects:
                obj = self.current_objects[target_obj_id]
                if 'animations' not in obj:
                    obj['animations'] = []
                
                # Add wait animation at the beginning
                wait_anim = {
                    'type': 'wait',
                    'duration': 0.2,
                    'start_time': 'immediate',
                    'reason': 'overlap_prevention'
                }
                
                obj['animations'].insert(0, wait_anim)
                
                return True, f"timing_adjustment_{target_obj_id}"
            
            return False, "object_not_found"
            
        except Exception as e:
            logger.error(f"Error applying timing adjustment: {e}")
            return False, f"error: {str(e)}"
    
    def _apply_monitoring_only(self, overlap: OverlapEvent) -> Tuple[bool, str]:
        """Apply monitoring-only correction (no action taken)"""
        return True, "monitoring_only"
    
    def _cancel_correction(self, correction_id: str) -> bool:
        """Cancel a pending correction"""
        try:
            if correction_id in self.active_corrections:
                correction = self.active_corrections[correction_id]
                if correction['status'] == 'pending':
                    correction['future'].cancel()
                
                del self.active_corrections[correction_id]
                logger.info(f"Cancelled correction {correction_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling correction {correction_id}: {e}")
            return False
    
    def add_overlap_callback(self, callback: Callable[[OverlapEvent], None]) -> None:
        """Add a callback for overlap events"""
        self.overlap_callbacks.append(callback)
    
    def add_correction_callback(self, callback: Callable[[str, bool], None]) -> None:
        """Add a callback for correction events"""
        self.correction_callbacks.append(callback)
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'monitoring_active': self.monitoring_active,
            'objects_being_monitored': len(self.current_objects),
            'active_corrections': len(self.active_corrections),
            'overlap_history_count': len(self.overlap_history),
            'monitoring_stats': self.monitoring_stats.copy(),
            'config': {
                'check_interval': self.config.check_interval,
                'overlap_threshold': self.config.overlap_threshold,
                'auto_correct': self.config.auto_correct,
                'logging': self.config.logging,
                'real_time_feedback': self.config.real_time_feedback
            }
        }
    
    def get_overlap_summary(self) -> Dict[str, Any]:
        """Get a summary of detected overlaps"""
        try:
            if not self.overlap_history:
                return {'overlaps_detected': 0, 'summary': 'No overlaps detected'}
            
            # Group by severity
            severity_counts = {}
            type_overlaps = {}
            
            for overlap in self.overlap_history:
                severity = overlap.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                type_key = f"{overlap.object1_type}_{overlap.object2_type}"
                type_overlaps[type_key] = type_overlaps.get(type_key, 0) + 1
            
            # Calculate correction success rate
            total_corrections = sum(1 for o in self.overlap_history if o.auto_corrected)
            successful_corrections = sum(1 for o in self.overlap_history if o.auto_corrected and o.correction_applied)
            correction_success_rate = (successful_corrections / total_corrections * 100) if total_corrections > 0 else 0
            
            return {
                'overlaps_detected': len(self.overlap_history),
                'severity_distribution': severity_counts,
                'type_distribution': type_overlaps,
                'correction_stats': {
                    'total_corrections': total_corrections,
                    'successful_corrections': successful_corrections,
                    'success_rate': correction_success_rate
                },
                'recent_overlaps': [
                    {
                        'object1': f"{o.object1_id} ({o.object1_type})",
                        'object2': f"{o.object2_id} ({o.object2_type})",
                        'severity': o.severity.value,
                        'timestamp': o.timestamp,
                        'corrected': o.auto_corrected,
                        'correction': o.correction_applied
                    }
                    for o in self.overlap_history[-10:]  # Last 10 overlaps
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating overlap summary: {e}")
            return {'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.stop_monitoring()
            if self.executor:
                self.executor.shutdown(wait=True)
            logger.info("RealTimeOverlapMonitor cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global instance
real_time_overlap_monitor = RealTimeOverlapMonitor()
