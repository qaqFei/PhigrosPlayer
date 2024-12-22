from __future__ import annotations

import typing
import math

import cv2

shaderType = typing.Literal[
    "chromatic",
    "circle_blur",
    "fisheye",
    "glitch",
    "grayscale",
    "noise",
    "pixel",
    "radial_blur",
    "shockwave",
    "vignette"
]

class baseVec:
    dimension: int = 0
    
    def __init__(self, *args: float):
        args: list = list(args)
        args.extend([args[-1]] * (self.dimension - len(args)))
        self.values = args
    
    def __getitem__(self, key: int) -> float:
        return self.values[key]
    
    def __setitem__(self, key: int, value: float):
        self.values[key] = value

    def __add__(self, other: baseVec|float) -> baseVec:
        return type(self)(*[self.values[i] + (other.values[i] if isinstance(other, baseVec) else other) for i in range(self.dimension)])

    def __sub__(self, other: baseVec|float) -> baseVec:
        return type(self)(*[self.values[i] - (other.values[i] if isinstance(other, baseVec) else other) for i in range(self.dimension)])

    def __mul__(self, other: baseVec|float) -> baseVec:
        return type(self)(*[self.values[i] * (other.values[i] if isinstance(other, baseVec) else other) for i in range(self.dimension)])

    def __truediv__(self, other: baseVec|float) -> baseVec:
        return type(self)(*[self.values[i] / (other.values[i] if isinstance(other, baseVec) else other) for i in range(self.dimension)])
    
    def __getattribute__(self, name: str):
        nameset = set(name)
        if len(nameset & set("xyzwrgba")) == len(nameset):
            indexmap = {
                "x": 0, "y": 1, "z": 2, "w": 3,
                "r": 0, "g": 1, "b": 2, "a": 3
            }
            if len(name) == 1: return self.values[indexmap[name]]
            else: vs = [self.values[indexmap[n]] for n in name]
            if len(vs) == 2: return vec2(*vs)
            elif len(vs) == 3: return vec3(*vs)
            elif len(vs) == 4: return vec4(*vs)
            else:
                class vecN(baseVec): dimension: int = len(vs)
                return vecN(*vs)
        else:
            return object.__getattribute__(self, name)
    
    def __setattr__(self, name: str, value: typing.Any):
        nameset = set(name)
        if len(nameset & set("xyzwrgba")) == len(nameset):
            indexmap = {
                "x": 0, "y": 1, "z": 2, "w": 3,
                "r": 0, "g": 1, "b": 2, "a": 3
            }
            for i, n in enumerate(name):
                self.values[indexmap[n]] = value[i]
        else:
            return object.__setattr__(self, name, value)

    def __iter__(self):
        return iter(self.values)
    
    def copy(self):
        return type(self)(*self.values)

    def length(self):
        return math.sqrt(dot(self, self))
    
    def max(self, x: float|baseVec):
        if isinstance(x, float): x = type(self)(x)
        return type(self)(*(max(self.values[i], x.values[i]) for i in range(self.dimension)))

    def min(self, x: float|baseVec):
        if isinstance(x, float): x = type(self)(x)
        return type(self)(*(min(self.values[i], x.values[i]) for i in range(self.dimension)))
    
class vec1(baseVec): dimension: int = 1
class vec2(baseVec): dimension: int = 2
class vec3(baseVec): dimension: int = 3
class vec4(baseVec): dimension: int = 4

class sampler2D:
    def __init__(self, frame: cv2.typing.MatLike):
        self.frame = frame
        self.w, self.h = frame.shape[1], frame.shape[0]

def texture2D(sampler: sampler2D, uv: vec2) -> vec4:
    return vec4(*getPixel(sampler.frame, *uv))

def dot(x: baseVec|float, y: baseVec|float) -> float:
    if isinstance(x, float): x = vec1(x)
    if isinstance(y, float): y = vec1(y)
    return sum([x[i] * y[i] for i in range(x.dimension)])

def normalize(vec: baseVec) -> baseVec:
    return vec.copy() / math.sqrt(dot(vec, vec))

def fract(x: float) -> float:
    return x - math.floor(x)

def mix(x: float, y: float, a: float) -> float:
    return x * (1.0 - a) + y * a

def addMathFunctionHook(name: str):
    f = getattr(math, name)
    
    def hook(x: float|baseVec) -> float|baseVec:
        if isinstance(x, float): return f(x)
        return type(x)(*[f(v) for v in x.values])
        
    setattr(math, name, hook)

def bilinearInterpolation(
    p1: tuple, p2: tuple, p3: tuple, p4: tuple,
    x: float, y: float,
    x1: float, x2: float, y1: float, y2: float
):
    return (
        (p1[0] * (x2 - x) + p2[0] * (x - x1)) * (y2 - y) +
        (p3[0] * (x2 - x) + p4[0] * (x - x1)) * (y - y1),
        (p1[1] * (x2 - x) + p2[1] * (x - x1)) * (y2 - y) +
        (p3[1] * (x2 - x) + p4[1] * (x - x1)) * (y - y1),
        (p1[2] * (x2 - x) + p2[2] * (x - x1)) * (y2 - y) +
        (p3[2] * (x2 - x) + p4[2] * (x - x1)) * (y - y1),
        1.0
    )

def getPixel(frame: cv2.typing.MatLike, x: float, y: float) -> tuple:
    w, h = frame.shape[1], frame.shape[0]
    x *= w; y *= h
    x = x if x >= 0 else 0; y = y if y >= 0 else 0
    x = x if x <= w else w; y = y if y <= h else h
    if int(x) == x and int(y) == y: return frame[int(y), int(x)]
    
    # bilinear interpolation
    x1, y1 = int(x), int(y)
    x2, y2 = x1 + 1, y1 + 1
    x2 = x2 if x2 >= 0 else 0; y2 = y2 if y2 >= 0 else 0
    x2 = x2 if x2 <= w else w; y2 = y2 if y2 <= h else h
    p1 = frame[max(y1 - 1, 0), max(x1 - 1, 0)]
    p2 = frame[max(y1 - 1, 0), max(x2 - 1, 0)]
    p3 = frame[max(y2 - 1, 0), max(x1 - 1, 0)]
    p4 = frame[max(y2 - 1, 0), max(x2 - 1, 0)]
    return bilinearInterpolation(
        p1, p2, p3, p4,
        x, y,
        x1, x2, y1, y2
    )

def _shaderMethod_chromatic(values: dict[str, float|list[float]]):
    sampleCount = values.get("sampleCount", 3)
    power = values.get("power", 0.01)
    sum = vec3(0.0)
    c = vec3(0.0)
    offset = (uv - vec2(0.5)) * vec2(1, -1)
    sample_count = int(sampleCount)
    for i in range(64):
        if i >= sample_count: break
        t = 2.0 * float(i) / float(sample_count - 1)
        slice = vec3(1.0 - t, 1.0 - abs(t - 1.0), t - 1.0).max(0.0)
        sum += slice
        slice_offset = offset * (t - 1.0) * power
        c += slice * texture2D(screenTexture, uv + slice_offset).rgb
    return c / sum

def _shaderMethod_circle_blur(values: dict[str, float|list[float]]):
    size = values.get("size", 10.0)
    c = texture2D(screenTexture, uv)
    length = dot(c, c)
    pixel_size = 1.0 / screenSize
    x = -size
    while x < size:
        y = -size
        while y < size:
            if x * x + y * y > size * size: continue
            new_c = texture2D(screenTexture, uv + pixel_size * vec2(x, y))
            new_length = dot(new_c, new_c)
            if new_length > length:
                length = new_length
                c = new_c
            y += 1
        x += 1
    return c

def _shaderMethod_fisheye(values: dict[str, float|list[float]]):
    power = values.get("power", -0.1)
    p = vec2(uv.x, uv.y * screenSize.y / screenSize.x)
    aspect = screenSize.x / screenSize.y
    m = vec2(0.5, 0.5 / aspect)
    d = p - m
    r = math.sqrt(dot(d, d))
    new_power = (2.0 * 3.141592 / (2.0 * math.sqrt(dot(m, m)))) * power
    bind = math.sqrt(dot(m, m)) if new_power > 0.0 else (m.x if aspect < 1.0 else m.y)
    if new_power > 0.0:
        nuv = m + normalize(d) * math.tan(r * new_power) * bind / math.tan(bind * new_power)
    else:
        nuv = m + normalize(d) * math.atan(r * -new_power * 10.0) * bind / math.atan(-new_power * bind * 10.0)
    return texture2D(screenTexture, vec2(nuv.x, nuv.y * aspect))

def _glitch_my_trunc(x: float) -> float:
    return -math.floor(-x) if x < 0.0 else math.floor(x)

def _glitch_random(seed: float) -> float:
    return fract(543.2543 * math.sin(dot(vec2(seed, seed), vec2(3525.46, -54.3415))))

def _shaderMethod_glitch(values: dict[str, float|list[float]]):
    power = values.get("power", 0.03)
    rate = values.get("rate", 0.6)
    speed = values.get("speed", 5.0)
    blockCount = values.get("blockCount", 30.5)
    colorRate = values.get("colorRate", 0.01)
    enable_shift = float(_glitch_random(_glitch_my_trunc(time * speed)) < rate)
    fixed_uv = uv
    fixed_uv.x += (_glitch_random((_glitch_my_trunc(uv.y * blockCount) / blockCount) + time) - 0.5) * power * enable_shift
    pixel_color = texture2D(screenTexture, fixed_uv)
    pixel_color.r = mix(
        pixel_color.r,
        texture2D(screenTexture, fixed_uv + vec2(colorRate, 0.0)).r,
        enable_shift
    )
    pixel_color.b = mix(
        pixel_color.b,
        texture2D(screenTexture, fixed_uv + vec2(-colorRate, 0.0)).b,
        enable_shift
    )
    return pixel_color

def _shaderMethod_grayscale(values: dict[str, float|list[float]]):
    factor = values.get("factor", 1.0)
    color = texture2D(screenTexture, uv).xyz
    lum = vec3(0.299, 0.587, 0.114)
    gray = vec3(dot(lum, color))
    return vec4(mix(color, gray, factor), 1.0)

def _noise_random(pos: vec2):
    return fract(math.sin(vec2(dot(pos, vec2(12.9898,78.233)), dot(pos, vec2(-148.998,-65.233)))) * 43758.5453)

def _shaderMethod_noise(values: dict[str, float|list[float]]):
    seed = values.get("seed", 81.0)
    power = values.get("power", 0.03)
    new_uv = uv + (_noise_random(uv + vec2(seed, 0.0)) - vec2(0.5, 0.5)) * power
    return texture2D(screenTexture, new_uv)

def _shaderMethod_pixel(values: dict[str, float|list[float]]):
    size = values.get("size", 10.0)
    factor = screenSize / size
    x = math.floor(uv.x * factor.x + 0.5) / factor.x
    y = math.floor(uv.y * factor.y + 0.5) / factor.y
    return texture2D(screenTexture, vec2(x, y))

def _shaderMethod_radial_blur(values: dict[str, float|list[float]]):
    centerX = values.get("centerX", 0.5)
    centerY = values.get("centerY", 0.5)
    power = values.get("power", 0.01)
    sampleCount = values.get("sampleCount", 6)
    direction = uv - vec2(centerX, centerY)
    c = vec3(0.0)
    f = 1.0 / sampleCount
    for i in range(64):
        if i >= sampleCount: break
        c += texture2D(screenTexture, uv - direction * power * i).rgb * f
    return c

def _shaderMethod_shockwave(values: dict[str, float|list[float]]):
    progress = values.get("progress", 0.2)
    centerX = values.get("centerX", 0.5)
    centerY = values.get("centerY", 0.5)
    width = values.get("width", 0.1)
    distortion = values.get("distortion", 0.8)
    expand = values.get("expand", 10.0)
    aspect = screenSize.y / screenSize.x
    center = vec2(centerX, centerY)
    center.y = (center.y - 0.5) * aspect + 0.5
    tex_coord = uv
    tex_coord.y = (tex_coord.y - 0.5) * aspect + 0.5
    dist = math.dist(tex_coord, center)
    if (progress - width <= dist) or (dist <= progress + width):
        diff = dist - progress
        scale_diff = 1.0 - pow(abs(diff * expand), distortion)
        dt = diff * scale_diff
        dir = normalize(tex_coord - center)
        tex_coord += ((dir * dt) / (progress * dist * 40.0))
        gl_FragColor = texture2D(screenTexture, vec2(tex_coord.x, (tex_coord.y - 0.5) / aspect + 0.5))
        gl_FragColor += (gl_FragColor * scale_diff) / (progress * dist * 40.0)
        return gl_FragColor
    else:
        return texture2D(screenTexture, vec2(tex_coord.x, (tex_coord.y - 0.5) / aspect + 0.5))

def _shaderMethod_vignette(values: dict[str, float|list[float]]):
    color = values.get("color", vec4(0.0, 0.0, 0.0, 1.0))
    extend = values.get("extend", 0.25)
    radius = values.get("radius", 15.0)
    new_uv = uv * (uv.yx * -1 + 1.0)
    vig = new_uv.x * new_uv.y * radius
    vig = pow(vig, extend)
    return mix(color, texture2D(screenTexture, uv), vig)

# has many bugs, use it as much as possible, and create a issue, and fix it
shaderMethodMap: dict[str, typing.Callable[[float, float, dict[str, float|list[float]]], tuple]] = {
    "chromatic": _shaderMethod_chromatic,
    "circle_blur": _shaderMethod_circle_blur,
    "fisheye": _shaderMethod_fisheye,
    "glitch": _shaderMethod_glitch,
    "grayscale": _shaderMethod_grayscale,
    "noise": _shaderMethod_noise,
    "pixel": _shaderMethod_pixel,
    "radial_blur": _shaderMethod_radial_blur,
    "shockwave": _shaderMethod_shockwave,
    "vignette": _shaderMethod_vignette,
    
    "circleBlur": _shaderMethod_circle_blur,
    "radialBlur": _shaderMethod_radial_blur,
    
    "default": lambda sv: texture2D(screenTexture, uv)
}

def processFrame(frame: cv2.typing.MatLike, shaders: list[tuple[shaderType, dict[str, float|list[float]]]]) -> cv2.typing.MatLike:
    global uv, screenTexture
    
    screenTexture = sampler2D(frame)
    newFrame = frame.copy()
    
    for sn, sv in shaders:
        if sn in shaderMethodMap:
            for y in range(frame.shape[0]):
                print(y)
                for x in range(frame.shape[1]):
                    uv = vec2(x, y) / screenSize
                    newFrame[y, x] = tuple(shaderMethodMap[sn](sv).rgb.values)
        else:
            raise NotImplementedError(f"Shader {sn} is not implemented")
    
    return newFrame

for hname in (
    "sqrt", "floor",
    "tan", "atan", "sin",
    "dist"
):
    addMathFunctionHook(hname)

time: float = 0.0 # chart play time
screenSize: vec2 # screen size
screenTexture: sampler2D # screen texture
