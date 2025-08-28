from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, validator


class AnimationType(str, Enum):
    CREATE = "create"
    TRANSFORM = "transform"
    MOVE = "move"
    ROTATE = "rotate"
    SCALE = "scale"
    FADE = "fade"
    WAIT = "wait"
    SET_COLOR = "set_color"
    SET_STROKE = "set_stroke"
    SET_FILL = "set_fill"


class AnimationStep(BaseModel):
    type: AnimationType = Field(..., description="Type of animation action")
    target: str = Field(..., description="Name of the target mobject variable")
    duration: float = Field(1.0, ge=0.0)
    parameters: Dict[str, object] = Field(default_factory=dict)
    wait_after: float = Field(0.5, ge=0.0)


class ManimObject(BaseModel):
    name: str = Field(..., description="Variable name to assign the mobject to")
    type: Literal[
        "circle",
        "square",
        "rectangle",
        "ellipse",
        "triangle",
        "text",
        "tex",
        "mathtex",
        "line",
        "dot",
        "axes",
        "number_line",
        "number_plane",
        "graph",
        "polygon",
        "arc",
        "svg",
        "image",
        "brace",
        "surrounding_rectangle",
        "vgroup",
        "parametric_function",
        "table",
        "matrix",
        "code",
    ]
    # Generic properties; compiler will interpret according to type
    props: Dict[str, object] = Field(default_factory=dict)


class ManimScene(BaseModel):
    scene_name: str = Field(..., description="Python class name for the scene")
    background_color: str = Field("#000000")
    resolution: Tuple[int, int] = Field((1280, 720))
    pixel_width: Optional[int] = None
    pixel_height: Optional[int] = None
    default_run_time: float = Field(1.0, ge=0.0)
    default_rate_func: Optional[str] = Field(None, description="Name of Manim rate function, e.g., 'smooth'")
    imports: List[str] = Field(default_factory=lambda: ["from manim import *"])
    objects: List[ManimObject] = Field(default_factory=list)
    animations: List[AnimationStep] = Field(default_factory=list)
    constraints: Dict[str, object] = Field(default_factory=dict, description="Scene-level constraints like layout, no_overlap, keep_on_screen")

    @validator("scene_name")
    def validate_scene_name(cls, value: str) -> str:
        if not value or not value[0].isalpha():
            raise ValueError("scene_name must start with a letter")
        return value


class StructuredGenerationRequest(BaseModel):
    prompt: str
    complexity: Literal["simple", "medium", "complex"] = "medium"
    style: Literal["educational", "artistic", "technical"] = "educational"


