from functools import cache
from dataclasses import fields, asdict

import Chart_Objects_Rep

upn_rpeobj = {i.upper().replace("ExtraVar_".upper(), ""): i for i in dir(Chart_Objects_Rep)}

@cache
def get_shader_cnf_cls(name:str):
    name = name.title()
    upn = name.upper()
    if upn in upn_rpeobj.keys():
        return getattr(Chart_Objects_Rep, upn_rpeobj[upn])

    return None

def load_extra(data):
    Extra = Chart_Objects_Rep.Extra(
        bpm = [
            Chart_Objects_Rep.BPMEvent(
                startTime = Chart_Objects_Rep.Beat(*bpm_item["time"]),
                bpm = bpm_item["bpm"]
            )
            for bpm_item in data["bpm"]
        ],
        effects = [
            Chart_Objects_Rep.ExtraEffect(
                start = (ms := Chart_Objects_Rep.Beat(*effect_item["start"])),
                end = (me := Chart_Objects_Rep.Beat(*effect_item["end"])),
                shader = effect_item["shader"],
                global_ = effect_item.get("global", False),
                vars = get_shader_cnf_cls(effect_item["shader"])(
                    **effect_item["vars"],
                    master_start = ms,
                    master_end = me
                ) if get_shader_cnf_cls(effect_item["shader"]) is not None else None
            )
            for effect_item in data["effects"]
        ]
    )
    
    Extra.effects = [i for i in Extra.effects if i.vars is not None]
    
    return Extra

def process_extra(data):
    res = {
        "effects": []
    }
    
    Extra = load_extra(data)
    
    def efctvars_asdict(obj):
        r = {}
        for field in fields(obj):
            if field.name in ("master_start", "master_end", "color"):
                continue
            
            i = getattr(obj, field.name)
            r[field.name] = []
            for j in i:
                setattr(j, "startTime", Extra.getReal(j.startTime))
                setattr(j, "endTime", Extra.getReal(j.endTime))
                r[field.name].append(asdict(j))
        
        return r
    
    for effect in Extra.effects:
        startTime = Extra.getReal(effect.start)
        endTime = Extra.getReal(effect.end)
        
        delattr(effect.vars, "master_start")
        delattr(effect.vars, "master_end")
        
        res["effects"].append({
            "startTime": startTime,
            "endTime": endTime,
            "shader": effect.shader,
            "global": effect.global_,
            "vars": efctvars_asdict(effect.vars)
        })
    
    return res