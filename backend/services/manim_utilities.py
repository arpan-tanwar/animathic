"""
Manim Utility Functions for Animathic
Contains helper functions and utilities for Manim operations
"""

import logging

logger = logging.getLogger(__name__)


def _mobj_bbox(m):
    """Get bounding box of a Manim object"""
    try:
        bb = m.get_bounding_box()
        w = max(1e-6, bb[1][0] - bb[0][0])
        h = max(1e-6, bb[1][1] - bb[0][1])
        return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]), w, h)
    except Exception:
        return None


def get_bbox(ids, get_group_func):
    """Get bounding box for a group of objects"""
    try:
        g = get_group_func(ids)
        if len(g) == 0:
            return None
        bb = g.get_bounding_box()
        return ((bb[0][0], bb[0][1]), (bb[1][0], bb[1][1]))
    except Exception:
        return None


def get_group(ids, id_to_mobject, get_object_by_id_func):
    """Get group of objects by IDs"""
    try:
        mobjects = []
        for obj_id in ids:
            obj_info = get_object_by_id_func(obj_id)
            if obj_info and obj_info['mobject']:
                mobjects.append(obj_info['mobject'])
        
        if mobjects:
            from manim import VGroup
            return VGroup(*mobjects)
        from manim import VGroup
        return VGroup()
    except Exception:
        from manim import VGroup
        return VGroup()


def bbox_union(bboxes):
    """Union of multiple bounding boxes"""
    try:
        xs = []
        ys = []
        for b in bboxes:
            if not b:
                continue
            (x0, y0), (x1, y1) = b
            xs += [x0, x1]
            ys += [y0, y1]
        if not xs or not ys:
            return None
        return ((min(xs), min(ys)), (max(xs), max(ys)))
    except Exception:
        return None


def fits_in_view(bbox, camera_frame, margin=0.1):
    """Check if bounding box fits in camera view"""
    try:
        if not bbox:
            return True
        (x0, y0), (x1, y1) = bbox
        bw = max(1e-6, x1 - x0)
        bh = max(1e-6, y1 - y0)
        fw = float(camera_frame.get_width())
        fh = float(camera_frame.get_height())
        return (bw <= fw * (1.0 - margin)) and (bh <= fh * (1.0 - margin))
    except Exception:
        return True


def safe_play(scene, *args, run_time=1.0):
    """Safe play function with error handling"""
    try:
        scene.play(*args, run_time=run_time)
    except Exception:
        pass


def safe_color(c):
    """Safe color function with fallbacks"""
    try:
        if not isinstance(c, str):
            return "WHITE"
        upper = c.upper()
        if upper in ["BLACK", "#000000", "#000"]:
            return "WHITE"
        return c
    except Exception:
        return "WHITE"


def _is_axes(mobj):
    """Check if object is axes"""
    try:
        return 'Axes' in str(type(mobj))
    except Exception:
        return False


def _priority_for(obj_id, id_to_meta):
    """Get priority for object based on type"""
    try:
        t = id_to_meta.get(obj_id, {}).get('type', '')
        if t in ('text', 'dot'):
            return 0  # secondary/annotation
        if t in ('line',):
            return 1  # ephemeral/helpers
        if t in ('axes', 'plot', 'square', 'circle'):
            return 2  # primary
        return 1
    except Exception:
        return 1


def _safe_eval(expr, x):
    """Safe evaluation of mathematical expressions"""
    try:
        import numpy as np
        allowed = {
            'np': np,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
            'abs': np.abs, 'pi': np.pi, 'e': np.e,
            'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
        }
        allowed_dict = {**allowed, 'x': x}
        return eval(expr, {"__builtins__": {}}, allowed_dict)
    except Exception:
        return 0
