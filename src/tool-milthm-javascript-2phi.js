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
                RPEVersion: 140,
                background: "",
                charter: "",
                composer: "",
                id: "",
                level: "",
                name: "",
                offset: 0,
                song: ""
            },
            judgeLineGroup: ["Default"],
            judgeLineList: [],
            multiLineString: "",
            multiScale: 1.0
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
        MilizeBeatmap[key] = value;

        switch (key) {
            case "AudioFile":
                MilizeBeatmap.rpe.META.song = value.substring(0, value.length - 4);
            case "Beatmapper":
                MilizeBeatmap.rpe.META.charter = value;
            case "Composer":
                MilizeBeatmap.rpe.META.composer = value;
            case "Difficulty":
                MilizeBeatmap._Difficulty = value;
            case "DifficultyValue":
                MilizeBeatmap._DifficultyValue = value;
            case "IllustrationFile":
                MilizeBeatmap.rpe.META.background = value;
            case "Title":
                MilizeBeatmap.rpe.META.name = value;
        }

        return MilizeBeatmap;
    }

    line() {

    }

    save() {
        MilizeBeatmap.rpe.META.level = `${self._Difficulty} Lv.${self._DifficultyValue}`;
        return MilizeBeatmap.rpe;
    }
}

const MilizeBeatmap = new MilizeBeatmapClass();
eval(milmth_chart);
const rpeResult = MilizeBeatmap.save();
fs.writeFileSync(argv[1], JSON.stringify(rpeResult, null, 4));