import sublime
import sublime_plugin
import subprocess
from os.path import dirname

gofmt = ["goimports"]
godef = ["godef"]

def exec(args, input=None, cwd=None):
    if input:
        input = input.encode()
    p = subprocess.Popen(args, cwd=cwd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate(input)
    return p.returncode, output.decode(), error.decode().strip()

def regionAll(view):
    return sublime.Region(0, view.size())

def substrAll(view):
    return view.substr(regionAll(view))

def replaceAll(edit, view, string):
    view.replace(edit, regionAll(view), string)

def selectionOffset(view):
    return view.sel()[0].begin()

class GofmtCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        code, output, error = exec(gofmt, substrAll(self.view))
        if code != 0:
            return print("{}: {}".format(gofmt, error))
        replaceAll(edit, self.view, output)

class GofmtListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.score_selector(0, 'source.go') > 0:
            view.run_command('gofmt')

class GodefCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()

        cmd = godef + ["-f", view.file_name(), "-o", str(selectionOffset(view))]
        input = None
        if view.is_dirty():
            cmd.append("-i")
            input = substrAll(view)
        code, output, error = exec(cmd, input, cwd=dirname(view.file_name()))
        if code != 0:
            return print("{}: {}".format(cmd, error))

        self.window.open_file(output, sublime.ENCODED_POSITION)
