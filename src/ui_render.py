from __future__ import annotations

import typing
from xml.etree.ElementTree import parse as xml_parse
from io import StringIO
from dataclasses import dataclass, field

import webcv

class LoadUIException(Exception): ...
class RenderUIException(Exception): ...

easings: dict[str, typing.Callable[[float], float]] = {
    "linear": lambda x: x
}

@dataclass
class UIPage:
    layers: list[UILayer] = field(default_factory=list)
    
    def append_layer(self, layer: UILayer):
        self.layers.append(layer)
    
    def render(self, root: webcv.WebCanvas, valuemap: dict[str, object]):
        w, h = valuemap["w"], valuemap["h"]
        
        for layer in self.layers:
            for widget in layer.widgets:
                if isinstance(widget, UIWidget_ColorRect):
                    pass
                elif isinstance(widget, UIWidget_Image):
                    pass
                elif isinstance(widget, UIWidget_Text):
                    pass
                elif isinstance(widget, UIWidget_DiagonalRect):
                    pass
                elif isinstance(widget, UIWidget_DiagonalImage):
                    pass
                else:
                    raise RenderUIException(f"Unknown UIWidget type: {type(widget)}")

@dataclass
class UILayer:
    alpha: float = 1.0
    alpha_easing: typing.Callable[[float], float] = easings["linear"]
    
    widgets: list[UIWidget] = field(default_factory=list)

    def append_widget(self, widget: UIWidget):
        self.widgets.append(widget)

@dataclass
class UIWidget:
    pass

@dataclass
class UIWidget_ColorRect(UIWidget):
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0
    
    r_easing: typing.Callable[[float], float] = easings["linear"]
    g_easing: typing.Callable[[float], float] = easings["linear"]
    b_easing: typing.Callable[[float], float] = easings["linear"]
    a_easing: typing.Callable[[float], float] = easings["linear"]

@dataclass
class UIWidget_Image(UIWidget):
    imname: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    a: float = 1.0
    
    x_easing: typing.Callable[[float], float] = easings["linear"]
    y_easing: typing.Callable[[float], float] = easings["linear"]
    width_easing: typing.Callable[[float], float] = easings["linear"]
    height_easing: typing.Callable[[float], float] = easings["linear"]
    a_easing: typing.Callable[[float], float] = easings["linear"]

@dataclass
class UIWidget_Text(UIWidget):
    text: str = ""
    x: float = 0.0
    y: float = 0.0
    fontsize: float = 0.0
    fontsize_method: typing.Literal["w", "h", "all"] = "all"
    
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0
    
    x_easing: typing.Callable[[float], float] = easings["linear"]
    y_easing: typing.Callable[[float], float] = easings["linear"]
    fontsize_easing: typing.Callable[[float], float] = easings["linear"]
    r_easing: typing.Callable[[float], float] = easings["linear"]
    g_easing: typing.Callable[[float], float] = easings["linear"]
    b_easing: typing.Callable[[float], float] = easings["linear"]
    a_easing: typing.Callable[[float], float] = easings["linear"]

@dataclass
class UIWidget_DiagonalRect(UIWidget_ColorRect):
    deg: float = 0.0
    
    deg_easing: typing.Callable[[float], float] = easings["linear"]

@dataclass
class UIWidget_DiagonalImage(UIWidget_Image):
    deg: float = 0.0
    
    deg_easing: typing.Callable[[float], float] = easings["linear"]

def putAttr(
    obj: object, attr: str,
    vtype: type, attrmap: dict[str, object], default: object,
    hook: typing.Callable[[object], object] = lambda x: x
):
    try:
        setattr(obj, attr, hook(vtype(attrmap.get(attr, default))))
    except ValueError as e:
        raise LoadUIException(f"Invalid {attr} value") from e

def load_ui(content: str):
    try:
        root = xml_parse(StringIO(content)).getroot()
    except Exception as e:
        raise LoadUIException("Failed to parse UI XML") from e
    
    if root.tag != "pprui":
        raise LoadUIException(f"Invalid root tag: {root.tag}")
    
    page = UIPage()
    
    for layer in root:
        if layer.tag != "uilayer":
            raise LoadUIException(f"Invalid layer tag: {layer.tag}")
        
        uilayer = UILayer()
        page.append_layer(uilayer)
        
        layer_attrs = layer.attrib
        
        putAttr(uilayer, "alpha", float, layer_attrs, 1.0)
        putAttr(uilayer, "alpha_easing", str, layer_attrs, "linear", easings.get)
        
        for widget in layer:
            widget_attrs = widget.attrib
            
            match widget.tag:
                case "color-rect":
                    widget = UIWidget_ColorRect()
                    putAttr(widget, "r", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "g", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "b", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "a", float, widget_attrs, 1.0, lambda x: max(0.0, min(1.0, x)))
                    putAttr(widget, "r_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "g_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "b_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "a_easing", str, widget_attrs, "linear", easings.get)
                
                case "image":
                    widget = UIWidget_Image()
                    putAttr(widget, "image", str, widget_attrs, "")
                    putAttr(widget, "x", float, widget_attrs, 0.0)
                    putAttr(widget, "y", float, widget_attrs, 0.0)
                    putAttr(widget, "width", float, widget_attrs, 0.0)
                    putAttr(widget, "height", float, widget_attrs, 0.0)
                    putAttr(widget, "a", float, widget_attrs, 1.0, lambda x: max(0.0, min(1.0, x)))
                    putAttr(widget, "x_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "y_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "width_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "height_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "a_easing", str, widget_attrs, "linear", easings.get)
                
                case "text":
                    widget = UIWidget_Text()
                    putAttr(widget, "text", str, widget_attrs, "")
                    putAttr(widget, "x", float, widget_attrs, 0.0)
                    putAttr(widget, "y", float, widget_attrs, 0.0)
                    putAttr(widget, "fontsize", float, widget_attrs, 0.0)
                    putAttr(widget, "fontsize_method", str, widget_attrs, "all")
                    putAttr(widget, "r", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "g", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "b", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "a", float, widget_attrs, 1.0, lambda x: max(0.0, min(1.0, x)))
                    putAttr(widget, "x_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "y_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "fontsize_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "r_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "g_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "b_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "a_easing", str, widget_attrs, "linear", easings.get)
                
                case "diagonal-rect":
                    widget = UIWidget_DiagonalRect()
                    putAttr(widget, "r", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "g", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "b", float, widget_attrs, 0.0, lambda x: max(0.0, min(255.0, x)))
                    putAttr(widget, "a", float, widget_attrs, 1.0, lambda x: max(0.0, min(1.0, x)))
                    putAttr(widget, "deg", float, widget_attrs, 0.0)
                    putAttr(widget, "r_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "g_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "b_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "a_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "deg_easing", str, widget_attrs, "linear", easings.get)
                
                case "diagonal-image":
                    widget = UIWidget_DiagonalImage()
                    putAttr(widget, "image", str, widget_attrs, "")
                    putAttr(widget, "x", float, widget_attrs, 0.0)
                    putAttr(widget, "y", float, widget_attrs, 0.0)
                    putAttr(widget, "width", float, widget_attrs, 0.0)
                    putAttr(widget, "height", float, widget_attrs, 0.0)
                    putAttr(widget, "a", float, widget_attrs, 1.0, lambda x: max(0.0, min(1.0, x)))
                    putAttr(widget, "deg", float, widget_attrs, 0.0)
                    putAttr(widget, "x_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "y_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "width_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "height_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "a_easing", str, widget_attrs, "linear", easings.get)
                    putAttr(widget, "deg_easing", str, widget_attrs, "linear", easings.get)
                
                case _:
                    raise LoadUIException(f"Invalid widget tag: {widget.tag}")
            
            uilayer.append_widget(widget)
    
    return page

if __name__ == "__main__":
    from threading import Thread
    from ctypes import windll
    
    result = load_ui(open("test_ui.xml", "r", encoding="utf-8").read())
    window = webcv.WebCanvas(
        x=400,
        y=300,
        width=800,
        height=600,
        title="Test UI",
        resizable=False
    )
    
    def worker():
        while True:
            result.render(window, {
                "w": 800,
                "h": 600
            })
    
    Thread(target=worker, daemon=True).start()
    window.wait_for_close()
    windll.kernel32.ExitProcess(0)