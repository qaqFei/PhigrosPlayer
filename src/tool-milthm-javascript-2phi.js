const argv = process.argv.slice(2);
const fs = require("fs");

if (argv.length < 2) {
    console.log('Usage: tool-milthm-javascript-2phi <input> <output>');
    process.exit(1);
}

const milmth_chart = fs.readFileSync(argv[0], "utf-8");

class MilizeBeatmapClass {
    constructor () {
        this.rpe = {
            
        };
    }

    timing () {

    }

    storyboardObject () {

    }

    note () {

    }

    animation () {

    }

    withProperty (key, value) {
        MilizeBeatmap[key] = value;
        return MilizeBeatmap;
    }

    line () {
        
    }
}

const MilizeBeatmap = new MilizeBeatmapClass();
eval(milmth_chart);