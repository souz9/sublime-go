import sublime
import sublime_plugin
from subprocess import Popen, PIPE

gofmt = ["goimports"]

class GofmtCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        p = Popen(gofmt, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        input = view.substr(sublime.Region(0, view.size())).encode()
        output, err = p.communicate(input)
        if p.returncode != 0:
            print("{}: {}".format(p.args, err.decode()))
            return

        view.replace(edit, sublime.Region(0, view.size()), output.decode())

class GofmtListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.score_selector(0, 'source.go') > 0:
            view.run_command('gofmt')
