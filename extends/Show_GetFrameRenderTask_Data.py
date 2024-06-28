import typing
from time import time

render_data_times = []
to_last_times = []
webview_times = [0.0]
min_render_data_time = float("inf")

def get_average_render_data_time():
    return sum(render_data_times) / len(render_data_times) # this list not possible is empty.

def get_average_to_last_time():
    return sum(to_last_times) / len(to_last_times) # this list not possible is empty.

def get_average_webview_time():
    return sum(webview_times) / len(webview_times) # this list not possible is empty.

class PhigrosPlayer_Extend:
    def __init__(
        self,
        get_globals: typing.Callable[[], typing.Any]
    ) -> None:
        self._get_globals = get_globals
        self.last_call_update = None
    
    def update(self, locals_dict):
        global min_render_data_time
        
        if self.last_call_update is not None:
            to_last_time = time() - self.last_call_update
            to_last_times.append(to_last_time)
            all_time_average = get_average_to_last_time()
        else:
            to_last_time = float("NAN")
            all_time_average = float("NAN")
            
        try:
            all_time_average_fps = 1 / all_time_average
        except ZeroDivisionError:
            all_time_average_fps = float("INF")
            
        output = "GetFrameRenderTask:\n"
        
        use_time = time() - locals_dict["GetFrameRenderTask_Phi_CallTime"]
        render_data_times.append(use_time)
        average = get_average_render_data_time()
        try:
            fps = 1 / use_time
        except ZeroDivisionError:
            fps = float("INF")
        try:
            average_fps = 1 / average
        except ZeroDivisionError:
            average_fps = float("INF")
        if use_time < min_render_data_time:
            min_render_data_time = use_time
        try:
            min_render_data_time_fps = 1 / min_render_data_time
        except ZeroDivisionError:
            min_render_data_time_fps = float("INF")
        
        webview_render_use_time = to_last_time - use_time
        if webview_render_use_time == webview_render_use_time: # != nan
            webview_times.append(webview_render_use_time)
        webview_render_use_time_average = get_average_webview_time()
        try:
            webview_render_use_time_fps = 1 / webview_render_use_time
        except ZeroDivisionError:
            webview_render_use_time_fps = float("INF")
        try:
            webview_render_use_time_average_fps = 1 / webview_render_use_time_average
        except ZeroDivisionError:
            webview_render_use_time_average_fps = float("INF")
            
        if len(render_data_times) > 3600:
            render_data_times.clear()
        if len(to_last_times) > 3600:
            to_last_times.clear()
        if len(webview_times) > 3600:
            webview_times.clear()
            webview_times.append(0.0)
        
        output += f"\tGetFrameRenderTask use time(this): {use_time:.5f}s/item = {fps:.2f}fps,\n"
        output += f"\tGetFrameRenderTask use time(average): {average:.5f}s/item = {average_fps:.2f}fps ({len(render_data_times)}sample),\n"
        output += f"\tGetFrameRemderTask min time: {min_render_data_time:.5f}s/item = {min_render_data_time_fps:.2f}fps,\n"
        output += f"\tAll use time(this): {to_last_time:.5f}s/tiem = {(1 / to_last_time):.2f}fps,\n"
        output += f"\tAll use time(average): {all_time_average:.5f}s/tiem = {all_time_average_fps:.2f}fps ({len(to_last_times)}sample),\n"
        output += f"\tWebView Render use time(this): {webview_render_use_time:.5f}s/item = {webview_render_use_time_fps:.2f}fps,\n"
        output += f"\tWebView Render use time(average): {webview_render_use_time_average:.5f}s/item = {webview_render_use_time_average_fps:.2f}fps ({len(webview_times)}sample),\n"
        
        task = locals_dict["Task"]
        output += f"\tRender_Task_Count: {len(task.RenderTasks)},\n"
        
        Render_JudgeLine_Count = locals_dict["Render_JudgeLine_Count"]
        output += f"\tRender_JudgeLine_Count: {Render_JudgeLine_Count},\n"
        
        Render_Note_Count = locals_dict["Render_Note_Count"]
        output += f"\tRender_Note_Count: {Render_Note_Count},\n"
        
        Render_ClickEffect_Count = locals_dict["Render_ClickEffect_Count"]
        output += f"\tRender_ClickEffect_Count: {Render_ClickEffect_Count},\n"
        
        print(output)
        
        self.last_call_update = time()
    
    def __getattribute__(self, name: str) -> typing.Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return lambda *args, **kwargs: None