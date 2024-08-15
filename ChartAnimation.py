import typing

import webcvapis

import Chart_Objects_Phi
import Tool_Functions
import rpe_easing
import Const
import Tool_Functions

def BeginLoadingAnimation(p: float, vals: dict) -> Chart_Objects_Phi.FrameRenderTask:
    root: webcvapis.WebCanvas
    draw_background: typing.Callable[[], None]
    w: int; h: int
    infoframe_x: float; infoframe_y: float
    infoframe_width: float; infoframe_height: float
    infoframe_ltr: float
    chart_name_text: str; chart_name_font_size: float
    chart_artist_text: str; chart_artist_text_font_size: float
    chart_level_number: int; chart_level_number_font_size: float
    chart_level_text: str; chart_level_text_font_size: float
    tip: str; tip_font_size: float
    chart_charter_text: str; chart_charter_text_font_size: float
    chart_illustrator_text: str; chart_illustrator_text_font_size: float
    
    (
        root, draw_background,
        w, h, infoframe_x, infoframe_y,
        infoframe_width, infoframe_height,
        infoframe_ltr,
        chart_name_text, chart_name_font_size,
        chart_artist_text, chart_artist_text_font_size,
        chart_level_number, chart_level_number_font_size,
        chart_level_text, chart_level_text_font_size,
        tip, tip_font_size,
        chart_charter_text, chart_charter_text_font_size,
        chart_illustrator_text, chart_illustrator_text_font_size,
    ) = (
        vals["root"], vals["draw_background"],
        vals["w"], vals["h"], vals["infoframe_x"], vals["infoframe_y"],
        vals["infoframe_width"], vals["infoframe_height"],
        vals["infoframe_ltr"],
        vals["chart_name_text"], vals["chart_name_font_size"],
        vals["chart_artist_text"], vals["chart_artist_text_font_size"],
        vals["chart_level_number"], vals["chart_level_number_font_size"],
        vals["chart_level_text"], vals["chart_level_text_font_size"],
        vals["tip"], vals["tip_font_size"],
        vals["chart_charter_text"], vals["chart_charter_text_font_size"],
        vals["chart_illustrator_text"], vals["chart_illustrator_text_font_size"]
    )
    
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    
    Task(root.clear_canvas, wait_execute = True)
    all_ease_value = Tool_Functions.begin_animation_eases.im_ease(p)
    background_ease_value = Tool_Functions.begin_animation_eases.background_ease(p) * 1.25
    info_data_ease_value = Tool_Functions.begin_animation_eases.info_data_ease((p - 0.2) * 3.25)
    info_data_ease_value_2 = Tool_Functions.begin_animation_eases.info_data_ease((p - 0.275) * 3.25)
    im_size = 1 / 2.5
    
    Task(draw_background)
    
    Task(
        root.create_polygon,
        [
            (-w * 0.1,0),
            (-w * 0.1,h),
            (background_ease_value * w - w * 0.1,h),
            (background_ease_value * w,0),
            (-w * 0.1,0)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = f"rgba(0, 0, 0, {0.75 * (1 - p)})",
        wait_execute = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate({all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(
        root.create_polygon,
        [
            (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height),
            (infoframe_x + infoframe_ltr + infoframe_width,infoframe_y - infoframe_height),
            (infoframe_x + infoframe_width,infoframe_y),
            (infoframe_x,infoframe_y),
            (infoframe_x + infoframe_ltr,infoframe_y - infoframe_height)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "rgba(0, 0, 0, 0.75)",
        wait_execute = True
    )
    
    Task(
        root.create_polygon,
        [
            (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03),
            (infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215,infoframe_y - infoframe_height * 1.03),
            (infoframe_x + w * 0.225 + infoframe_width * 0.215,infoframe_y + infoframe_height * 0.03),
            (infoframe_x + w * 0.225,infoframe_y + infoframe_height * 0.03),
            (infoframe_x + w * 0.225 + infoframe_ltr,infoframe_y - infoframe_height * 1.03)
        ],
        strokeStyle = "rgba(0, 0, 0, 0)",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + infoframe_ltr * 2,
        infoframe_y - infoframe_height * 0.65,
        text = chart_name_text,
        font = f"{(chart_name_font_size)}px PhigrosFont",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + infoframe_ltr * 2,
        infoframe_y - infoframe_height * 0.31,
        text = chart_artist_text,
        font = f"{(chart_artist_text_font_size)}px PhigrosFont",
        textBaseline = "middle",
        fillStyle = "#FFFFFF",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
        infoframe_y - infoframe_height * 1.03 * 0.58,
        text = chart_level_number,
        font = f"{(chart_level_number_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        infoframe_x + w * 0.225 + infoframe_ltr + infoframe_width * 0.215 / 2 - infoframe_ltr / 2,
        infoframe_y - infoframe_height * 1.03 * 0.31,
        text = chart_level_text,
        font = f"{(chart_level_text_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.065,
        h * 0.95,
        text = f"Tip: {tip}",
        font = f"{tip_font_size}px PhigrosFont",
        textBaseline = "bottom",
        fillStyle = f"rgba(255, 255, 255, {Tool_Functions.begin_animation_eases.tip_alpha_ease(p)})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
        h * 0.5225,
        text = "Chart",
        font = f"{w / 98}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1375 + (1 - info_data_ease_value) * -1 * w * 0.075,
        h * 0.5225 + w / 98 * 1.25,
        text = chart_charter_text,
        font = f"{chart_charter_text_font_size}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
        h * 0.565 + w / 98 * 1.25,
        text = "Illustration",
        font = f"{w / 98}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    Task(
        root.create_text,
        w * 0.1235 + (1 - info_data_ease_value_2) * -1 * w * 0.075,
        h * 0.565 + w / 98 * 1.25 + w / 98 * 1.25,
        text = chart_illustrator_text,
        font = f"{chart_illustrator_text_font_size}px PhigrosFont",
        textBaseline = "top",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    Task(
        root.create_image,
        "begin_animation_image",
        w * 0.65 - w * im_size * 0.5, h * 0.5 - h * im_size * 0.5,
        width = w * im_size,
        height = h * im_size,
        wait_execute = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate(-{all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(root.run_js_wait_code)
    return Task

def BeginJudgeLineAnimation(p: float, vals: dict) -> Chart_Objects_Phi.FrameRenderTask:
    draw_ui: typing.Callable
    root: webcvapis.WebCanvas
    w: int; h: int
    audio_length: float
    JUDGELINE_WIDTH: float
    render_range_more_scale: float
    render_range_more: bool
    
    (
        draw_ui,
        root,
        w, h,
        audio_length,
        JUDGELINE_WIDTH,
        render_range_more_scale,
        render_range_more
    ) = (
        vals["draw_ui"],
        vals["root"],
        vals["w"], vals["h"],
        vals["audio_length"],
        vals["JUDGELINE_WIDTH"],
        vals["render_range_more_scale"],
        vals["render_range_more"]
    )
    
    Task = Chart_Objects_Phi.FrameRenderTask([], [])
    val = rpe_easing.ease_funcs[12](p)
    Task(
        draw_ui,
        animationing = True,
        now_time = f"{Tool_Functions.Format_Time(0.0)}/{Tool_Functions.Format_Time(audio_length)}",
        dy = h / 7 * val
    )
    Task(
        root.create_line,
        w / 2 - (val * w / 2), h / 2,
        w / 2 + (val * w / 2), h / 2,
        strokeStyle = Const.JUDGELINE_PERFECT_COLOR,
        lineWidth = JUDGELINE_WIDTH / render_range_more_scale if render_range_more else JUDGELINE_WIDTH,
        wait_execute = True
    )
    Task(root.run_js_wait_code)
    return Task