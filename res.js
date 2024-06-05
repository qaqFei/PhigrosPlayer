const { loadImage } = require("canvas");

async function LoadResources() {
    var res = {};

    res["Start"] = await loadImage("./Resources/Start.png");

    for (var i = 1; i <= 30; i++) {
        res[`Note_Click_Effect_Perfect_${i}`] = await loadImage(`./Resources/Note_Click_Effect/Perfect/${i}.png`);
    }

    for (var key of ["Tap","Drag","Flick","Hold_Head","Hold_End","Hold_Body"]) {
        res[`Note_${key}`] = await loadImage(`./Resources/Notes/${key}.png`);
        res[`Note_${key}_dub`] = await loadImage(`./Resources/Notes/${key}_dub.png`);
    }

    return res;
}

module.exports.LoadResources = LoadResources