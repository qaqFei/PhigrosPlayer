var _ctx = null;
var _w = null;
var _h = null;
var _background = null;
var _ProcessBar = null;
var _sound_name = null;
var _level = null;

function init(
    ctx,w,h,background,
    ProcessBar,sound_name,level
) {
    _ctx = ctx;
    _w = w;
    _h = h;
    _background = background;
    _ProcessBar = ProcessBar;
    _sound_name = sound_name;
    _level = level;
}

function clear_canvas() {
    ctx.clearRect(0, 0, w, h);
}

function create_line(
    x1, y1, x2, y2,
    lineWidth = 1,
    fillStyle = null,
    strokeStyle = null
) {
    _ctx.save()
    _ctx.beginPath();
    _ctx.moveTo(x1, y1);
    _ctx.lineTo(x2, y2);
    _ctx.lineWidth = lineWidth;
    if (strokeStyle != null){
        _ctx.strokeStyle = strokeStyle;
    }
    if (fillStyle != null){
        _ctx.fillStyle = fillStyle;
    }
    _ctx.stroke();
    _ctx.restore();
}

function create_text(
    x, y,
    text,font = null,
    textAlign = "start",
    textBaseline = "alphabetic",
    direction = "inherit",
    fillStyle = null,
    strokeStyle = null
) {
    _ctx.save()
    _ctx.textAlign = textAlign;
    _ctx.textBaseline = textBaseline;
    _ctx.direction = direction;
    if (font != null){
        _ctx.font = font;
    }
    if (fillStyle != null){
        _ctx.fillStyle = fillStyle;
    }
    if (strokeStyle != null){
        _ctx.strokeStyle = strokeStyle;
    }
    _ctx.fillText(text, x, y);
    _ctx.restore();
}

function create_image(
    im, x, y,
    width, height
) {
    _ctx.drawImage(im, x, y, width, height);
}

function draw_background() {
    create_image(_background, 0, 0, _w, _h);
}

function draw_ui(
    process = 0.0,
    score = "0000000",
    combo_state = false,
    combo = 0,
    now_time = "0:00/0:00",
    clear = true,
    background = true
) {
    if (clear) {
        clear_canvas();
    }
    if (background) {
        draw_background();
    }
    create_image(
        _ProcessBar,
        -w + w * process,0,
        w,parseInt(h / 125)
    )
    create_text(
        text=score,
        x=w * 0.99,
        y=h * 0.01,
        textBaseline="top",
        textAlign="right",
        strokeStyle="white",
        fillStyle="white",
        font=`${parseInt((w + h) / 75 / 0.75)}px sans-serif`
    )
    if (combo_stat){
        create_text(
            text=`${combo}`,
            x=w / 2,
            y=h * 0.01,
            textBaseline="top",
            textAlign="center",
            strokeStyle="white",
            fillStyle="white",
            font=`${int((w + h) / 75 / 0.75)}px sans-serif`
        )
        create_text(
            text="Autoplay",
            x=w / 2,
            y=h * 0.1,
            textBaseline="bottom",
            textAlign="center",
            strokeStyle="white",
            fillStyle="white",
            font=`${int((w + h) / 100 / 0.75)}px sans-serif`
        )
    }
    create_text(
        text=now_time,
        x=0,
        y=h * 0.01,
        textBaseline="top",
        textAlign="left",
        strokeStyle="white",
        fillStyle="white",
        font=`${int((w + h) / 75175 / 0.75)}px sans-serif`
    )
    create_text(
        text=_sound_name,
        x=w * 0.01,
        y=h * 0.99,
        textBaseline="bottom",
        textAlign="left",
        strokeStyle="white",
        fillStyle="white",
        font=`${int((w + h) / 125 / 0.75)}px sans-serif`
    )
    create_text(
        text=_level,
        x=w * 0.99,
        y=h * 0.99,
        textBaseline="bottom",
        textAlign="right",
        strokeStyle="white",
        fillStyle="white",
        font=`${int((w + h) / 125 / 0.75)}px sans-serif`
    )
}

module.exports.init = init;
module.exports.clear_canvas = clear_canvas;
module.exports.create_line = create_line;
module.exports.create_text = create_text;
module.exports.create_image = create_image;
module.exports.draw_ui = draw_ui;
module.exports.draw_background = draw_background;