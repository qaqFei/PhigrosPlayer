const { createCanvas } = require("canvas");
const fs = require("fs");
const Jimp = require("jimp");
const pywebcanvas_api = require("./pywebcanvas_api.js");
const argv = process.argv.splice(2);

const lfdaot_fp = argv[0];
const audio_fp = argv[1];
const background_fp = argv[2];
const sound_name = argv[3];
const level = argv[4];

const lfdaot_object = JSON.parse(fs.readFileSync(lfdaot_fp));
const screen_size = lfdaot_object["meta"]["size"];
const screen_width = screen_size[0];
const screen_height = screen_size[1];
const fps = lfdaot_object["meta"]["frame_speed"];

var canvas = createCanvas(screen_width, screen_height);
var ctx = canvas.getContext("2d");
const render_function_mapping = {
    clear_canvas:pywebcanvas_api.clear_canvas,
    create_line:pywebcanvas_api.create_line,
    create_text:pywebcanvas_api.create_text,
    create_image:pywebcanvas_api.create_image
}
pywebcanvas_api.init(
    ctx,screen_width,screen_height,
    null,sound_name,level
);

for (frame_data of lfdaot_object["data"]) {
    for (render_tasks of frame_data["render"]) {
        // console.log(render_tasks);
    }
}