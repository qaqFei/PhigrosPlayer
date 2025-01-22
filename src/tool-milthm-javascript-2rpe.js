const argv = process.argv.slice(2);
const fs = require("fs");

if (argv.length < 2) {
    console.log("Usage: tool-milthm-javascript-2phi <input> <output>");
    process.exit(1);
}

const milmth_chart = fs.readFileSync(argv[0], "utf-8");

class MilizeBeatmapClass {
    constructor() {
        this.rpe = {
            BPMList: [],
            META: {
                RPEVersion: 160,
                background: "",
                charter: "",
                composer: "",
                id: "",
                level: "",
                name: "",
                offset: 0,
                song: ""
            },
            judgeLineList: []
        };

        this.mil = {

        };
    }

    timing() {

    }

    storyboardObject() {

    }

    note() {

    }

    animation() {

    }

    withProperty(key, value) {
        beatmap[key] = value;

        switch (key) {
            case "AudioFile":
                beatmap.rpe.META.song = value.substring(0, value.length - 4);
            case "Beatmapper":
                beatmap.rpe.META.charter = value;
            case "Composer":
                beatmap.rpe.META.composer = value;
            case "Difficulty":
                beatmap._Difficulty = value;
            case "DifficultyValue":
                beatmap._DifficultyValue = value;
            case "IllustrationFile":
                beatmap.rpe.META.background = value;
            case "Title":
                beatmap.rpe.META.name = value;
        }

        return beatmap;
    }

    line() {

    }

    save() {
        beatmap.rpe.META.level = `${self._Difficulty} Lv.${self._DifficultyValue}`;
        return beatmap.rpe;
    }
}

const beatmap = new MilizeBeatmapClass();

const MilizeBeatmap = beatmap;
eval(milmth_chart);

const rpeResult = beatmap.save();
fs.writeFileSync(argv[1], JSON.stringify(rpeResult, null, 4));