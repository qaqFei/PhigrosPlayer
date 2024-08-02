from dataclasses import dataclass
from urllib.request import Request, urlopen
import json
import typing

APIURL = "https://api.phira.cn/"
GETCHATR_MAXPAGENUM = 30 # if > this value, api.phira.cn will return {"error":"单页实体数量过多"}
orderType = typing.Literal["updated", "-updated", "rating", "-rating", "name", "-name"]
divisionType = typing.Literal["regular", "troll", "plain", "visual"]
numberType = int|float

@dataclass
class PhiraChart:
    id: int
    name: str
    level: str
    difficulty: numberType
    charter: str
    composer: str
    illustrator: str
    description: str
    ranked: bool
    reviewed: bool
    stable: bool
    stableRequest: bool
    illustration: str
    preview: str
    file: str
    uploader: int
    tags: list[str]
    rating: numberType
    ratingCount: int
    created: str
    updated: str
    chartUpdated: str
    
    def getDownloadPath(self, path: str) -> str:
        return path.replace("api.phira.cn/files", "files-cf.phira.cn")
    
    def downloadIllustration(self) -> bytes:
        return _request(self.getDownloadPath(self.illustration))
    
    def downloadPreview(self) -> bytes:
        return _request(self.getDownloadPath(self.preview))
    
    def downloadChart(self) -> bytes:
        return _request(self.getDownloadPath(self.file))

@dataclass
class PhiraUser:
    avatar: str
    badges: list[str]
    banned: bool
    bio: str
    exp: int
    follower_count: int
    following_count: int
    id: int
    joined: str
    language: str
    last_login: str
    login_banned: bool
    name: str
    rks: bool
    roles: int

@dataclass
class PhiraUserStats:
    numRecords: int
    avgAccuracy: float

@dataclass
class PhiraRecord:
    accuracy: float
    bad: int
    best: bool
    best_std: bool
    chart: int
    full_combo: bool
    good: int
    id: int
    max_combo: int
    miss: int
    mods: int
    perfect: int
    player: int
    score: numberType
    speed: numberType
    std: float
    std_score: numberType
    
def _request(url: str, api: bool = False) -> bytes:
    while True:
        try:
            return urlopen(Request(url), timeout = 1.0 if api else 60.0).read()
        except Exception as e:
            print("Warning: request failed, retrying... ", url, repr(e))

def getCharts(
    pageNum: int,
    page: int,
    order: orderType = "-updated",
    division: divisionType = "regular",
    search: str = "",
    tags: list[str] = [],
    notTags: list[str] = [],
    rating_leftrange: float = 0.0,
    rating_rightrange: float = 1.0,
    uploader: int|None = None
) -> list[PhiraChart]:
    data = _request(f"{APIURL}chart?\
pageNum={pageNum}&\
page={page}&\
order={order}&\
division={division}&\
search={search}&\
tags={','.join(tags + list(map(lambda x: f"-{x}", notTags)))}&\
rating={rating_leftrange},{rating_rightrange}&\
{f"uploader={uploader}&" if uploader is not None else ""}\
", True).decode("utf-8")
    json_data = json.loads(data)
    return [PhiraChart(**chart) for chart in json_data["results"]]

def getUserStats(id: int) -> PhiraUserStats:
    data = _request(f"{APIURL}user/{id}/stats", True).decode("utf-8")
    json_data = json.loads(data)
    return PhiraUserStats(**json_data)

def getChartByIds(ids: list[int]) -> list[PhiraChart]:
    data = _request(f"{APIURL}chart/multi-get?ids={",".join(map(str, ids))}", True).decode("utf-8")
    json_data = json.loads(data)
    return [PhiraChart(**chart) for chart in json_data]

def getChartById(id: int) -> PhiraChart:
    return getChartByIds([id])[0]

def getUserById(id: int) -> PhiraUser:
    data = _request(f"{APIURL}user/{id}", True).decode("utf-8")
    json_data = json.loads(data)
    return PhiraUser(**json_data)

def getUserRecords(user: int) -> list[PhiraRecord]:
    data = _request(f"{APIURL}record?player={user}", True).decode("utf-8")
    json_data = json.loads(data)
    return [PhiraRecord(**record) for record in json_data]

def getUsers(
    pageNum: int,
    page: int,
    search: str = ""
):
    data = _request(f"{APIURL}user?\
pageNum={pageNum}&\
page={page}&\
search={search}\
", True).decode("utf-8")
    json_data = json.loads(data)
    return [PhiraUser(**user) for user in json_data["results"]]

def getAllCharts(
    order: orderType = "-updated",
    division: divisionType = "regular"
) -> list[PhiraChart]:
    charts = []
    page = 0
    while True:
        page += 1
        pageCharts = getCharts(GETCHATR_MAXPAGENUM, page, order, division)
        if not pageCharts:
            break
        charts.extend(pageCharts)
    return charts

if __name__ == "__main__":
    while True:
        code = input("Phira Api >>> ")
        try:
            result = eval(code)
            if result is not None: print(result)
        except Exception:
            try:
                exec(code)
            except Exception as e:
                print(repr(e))