HELP_EN = '''
Usage: Main <chart_file> [<args>...] [<kwargs>...]

<Args>
  --hideconsole: Hide the console window.
  --debug: Display webview debug window, and show judgeLine position points.
  --fullscreen: Make the window fullscreen.
  --nojudgeline: No display judgeLine.
  --judgeline-notransparent: Make the judgeLine not transparent. (Disappear value forever is 1.0.)
  --noclickeffect-randomblock: Disable random block of click effect.
  --loop: Auto loop the chart.
  --lfdaot: Load frame data ahead of time, and output a *.lfdaot file.
  --noclicksound: Disable click sound.
  --render-range-more: Render range more, can render out of the screen, and display at screen.
  --lfdaot-render-video: Output a video file when using --lfdaot and --lfdaot-file.
  --ease-event-interpolation: Use easing when interpolating events.
  --frameless: Make the window frameless.
  --no-mixer-reset-chart-time: If there is a large discrepancy between the mixer's time and the chart's playback time, it will not be corrected.
  --noautoplay: Disable auto play.
  --rtacc: Enable real-time accuracy.

<Kwargs>
  --combotips <string-value>: Set the combo tips text.
  --random-block-num <integer-value>: Set the random block of click effect number.
  --scale-note <number-value>: Set the note scale.
  --lfdaot-file <path-string-value>: Set the *.lfdaot file path, and load it and play it. (Front-loaded arg: --lfdaot)
  --size <integer-value> <integer-value>: Set the window size.
  --lfdaot-frame-speed <integer-value>: Set the frame speed of *.lfdaot file. (Front-loaded arg: --lfdaot, Invalid when using --lfdaot-file)
  --render-range-more-scale <number-value>: Set the render range more scale. (Front-loaded arg: --render-range-more)
  --window-host <integer-hwnd-value>: Set the window host hwnd.
  --extend <python_file>: To use the extension, see docs/docs.md for details.
  --res <folder-path>: Set the resource folder path, only image, ppr will be loaded from it, if cannot find resoure file, ppr will be loaded from default resoure.
'''

HELP_CN = '''

'''