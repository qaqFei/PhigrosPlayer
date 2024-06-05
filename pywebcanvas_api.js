var _ctx = undefined;
var _w = undefined;
var _h = undefined;
var _background = undefined;
var _sound_name = undefined;
var _level = undefined;
var _res = undefined;
var ctx = undefined; // give ctx val to eval_api

function init(
    ctx_,w,h,background,
    sound_name,level,
    res
) {
    _ctx = ctx_;
    _w = w;
    _h = h;
    _background = background;
    _sound_name = sound_name;
    _level = level;
    _res = res;

    for (var key in _res){
        eval(`${key}_img = _res.${key};`);
    }

    ctx = ctx_;
}

function clear_canvas() {
    _ctx.clearRect(0, 0, _w, _h);
}

function create_line(
    x1, y1, x2, y2,
    optinos = {}
) {
    now_options = Object.assign(
        {
            fillStyle:null,
            strokeStyle:null,
            lineWidth:1
        },
        optinos
    )
    _ctx.save()
    _ctx.beginPath();
    if (now_options.strokeStyle != null){
        _ctx.strokeStyle = now_options.strokeStyle;
    }
    if (now_options.fillStyle != null){
        _ctx.fillStyle = now_options.fillStyle;
    }
    _ctx.lineWidth = now_options.lineWidth;
    _ctx.moveTo(x1, y1);
    _ctx.lineTo(x2, y2);
    _ctx.stroke();
    _ctx.restore();
}

function create_text(
    x, y,text,
    optinos = {}
) {
    now_options = Object.assign(
        {
            font:null,
            textAlign:"start",
            textBaseline:"alphabetic",
            direction:"inherit",
            fillStyle:null,
            strokeStyle:null,
        },
        optinos
    )
    _ctx.save()
    _ctx.textAlign = now_options.textAlign;
    _ctx.textBaseline = now_options.textBaseline;
    _ctx.direction = now_options.direction;
    if (now_options.font != null){
        _ctx.font = now_options.font;
    }
    if (now_options.fillStyle != null){
        _ctx.fillStyle = now_options.fillStyle;
    }
    if (now_options.strokeStyle != null){
        _ctx.strokeStyle = now_options.strokeStyle;
    }
    _ctx.fillText(text, x, y);
    _ctx.restore();
}

function create_image(
    imname, x, y,
    width, height
) {
    _ctx.drawImage(_res[imname], x, y, width, height);
}

function create_rectangle(
    x0, y0, x1, y1,
    optinos = {}
) {
    now_options = Object.assign(
        {
            fillStyle:null,
            strokeStyle:null,
            lineWidth:1
        },
        optinos
    )
    _ctx.save();
    if (now_options.strokeStyle != null){
        _ctx.strokeStyle = now_options.strokeStyle;
    }
    if (now_options.fillStyle != null){
        _ctx.fillStyle = now_options.fillStyle;
    }
    _ctx.lineWidth = now_options.lineWidth;
    _ctx.fillRect(x0, y0, x1-x0, y1-y0);
    _ctx.restore();
}

function draw_background() {
    _ctx.drawImage(_background, 0, 0, _w, _h);
}

function draw_ui(
    optinos = {}
) {
    now_options = Object.assign(
        {
            process:0.0,
            score:"0000000",
            combo_state:false,
            combo:0,
            now_time:"0:00/0:00",
            clear:true,
            background:true
        },
        optinos
    )
    if (now_options.clear) {
        clear_canvas();
    }
    if (now_options.background) {
        draw_background();
    }
    create_rectangle(
        0,0,
        _w * now_options.process,_h / 125,
        {fillStyle:"rgba(145, 145, 145, 0.85)"}
    )
    create_rectangle(
        _w * now_options.process - _w * 0.002,0,
        _w * now_options.process,_h / 125,
        {fillStyle:"rgba(255, 255, 255, 0.9)"}
    )
    create_text(
        _w * 0.99,
        _h * 0.01,
        now_options.score,
        {
            textBaseline:"top",
            textAlign:"right",
            strokeStyle:"white",
            fillStyle:"white",
            font:`${parseInt((_w + _h) / 75 / 0.75)}px sans-serif`
        }
    )
    if (now_options.combo_state){
        create_text(
            _w / 2,
            _h * 0.01,
            `${now_options.combo}`,
            {
                textBaseline:"top",
                textAlign:"center",
                strokeStyle:"white",
                fillStyle:"white",
                font:`${parseInt((_w + _h) / 75 / 0.75)}px sans-serif`
            }
        )
        create_text(
            _w / 2,
            _h * 0.1,
            "Autoplay",
            {
                textBaseline:"bottom",
                textAlign:"center",
                strokeStyle:"white",
                fillStyle:"white",
                font:`${parseInt((_w + _h) / 100 / 0.75)}px sans-serif`
            }
        )
    }
    create_text(
        0,
        _h * 0.01,
        now_options.now_time,
        {
            textBaseline:"top",
            textAlign:"left",
            strokeStyle:"white",
            fillStyle:"white",
            font:`${parseInt((_w + _h) / 75175 / 0.75)}px sans-serif`
        }
    )
    create_text(
        _w * 0.01,
        _h * 0.99,
        _sound_name,
        {
            textBaseline:"bottom",
            textAlign:"left",
            strokeStyle:"white",
            fillStyle:"white",
            font:`${parseInt((_w + _h) / 125 / 0.75)}px sans-serif`
        }
    )
    create_text(
        _w * 0.99,
        _h * 0.99,
        _level,
        {
            textBaseline:"bottom",
            textAlign:"right",
            strokeStyle:"white",
            fillStyle:"white",
            font:`${parseInt((_w + _h) / 125 / 0.75)}px sans-serif`
        }
    )
}

module.exports.init = init;
module.exports.clear_canvas = clear_canvas;
module.exports.create_line = create_line;
module.exports.create_text = create_text;
module.exports.create_image = create_image;
module.exports.create_rectangle = create_rectangle;
module.exports.draw_ui = draw_ui;
module.exports.draw_background = draw_background;
module.exports.eval_api = (c) => {eval(c)};