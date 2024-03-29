import sublime
import sublime_plugin
import subprocess
import os.path

gofmt = ["goimports"]
godef = ["godef"]

def exec(args, input=None, cwd=None):
    if input:
        input = input.encode()
    p = subprocess.Popen(args, cwd=cwd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate(input)
    return p.returncode, output.decode(), error.decode().strip()

def substr(view, a=0, b=None):
    b = b if b is not None else view.size()
    return view.substr(sublime.Region(a, b))

def replace(edit, view, string, a=0, b=None):
    b = b if b is not None else view.size()
    view.replace(edit, sublime.Region(a, b), string)

def selection_offset(view):
    return view.sel()[0].begin()

def selection_offset_bytes(view):
    return len(substr(view, b=selection_offset(view)).encode())

class GofmtCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        folder = os.path.dirname(self.view.file_name())
        code, output, error = exec(gofmt, substr(self.view), cwd=folder)
        if code != 0:
            print("{}: {}".format(gofmt, error))
            return
        replace(edit, self.view, output)

class GofmtListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.score_selector(0, 'source.go') > 0:
            view.run_command('gofmt')

class GodefCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        offset = selection_offset_bytes(view)
        cmd = godef + ["-i", "-f", view.file_name(), "-o", str(offset)]
        code, output, error = exec(cmd, substr(view), cwd=os.path.dirname(view.file_name()))
        if code != 0:
            self.window.status_message(error)
            return
        filename, *_ = output.split(":")
        if not os.path.isfile(filename):
            self.window.status_message("path not found: " + output)
            return
        self.window.open_file(output, sublime.ENCODED_POSITION)
