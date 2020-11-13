import sublime
import sublime_plugin
from subprocess import Popen, PIPE

godef = ["godef"]

class GodefCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()

        offset = view.sel()[0].begin()
        cmd = godef + ["-f", view.file_name(), "-o", str(offset)]

        input = None
        if view.is_dirty():
            cmd.append("-i")
            input = view.substr(sublime.Region(0, view.size())).encode()

        p = Popen(cmd, cwd=self.window.folders()[0], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(input)
        if p.returncode != 0:
            print("{}: {}".format(p.args, err.decode()))
            return

        target = output.decode()
        self.window.open_file(target, sublime.ENCODED_POSITION)
