import sublime
import sublime_plugin

import sys
import os
import difflib

path = os.path.dirname(os.path.realpath(__file__))
history = os.path.join(path, "history.log")
temp_a = os.path.join(path, "temp.log")
txt_track = ""
phantoms = []

def getReg(self, view, idx):
	ret = sublime.Region(-1,-1)
	row = view.text_point(idx - 1, 0)
	ret = view.full_line(row)
	return ret
	pass

def getTxt(self):
	txt = ""
	line_total = self.view.rowcol(self.view.size())[0]+1
	for indx in range(line_total):
		txt = txt + self.view.substr(self.view.line(sublime.Region(self.view.text_point(indx, 0), self.view.text_point(indx, 0))))
	return txt

def getFilename(self):
	name = ""
	ext = ""
	if self.view.file_name() != None:
		full = os.path.basename(self.view.file_name())
		name = os.path.splitext(full)[0]
		ext = os.path.splitext(full)[1]
	return name, ext
	pass

def historyAdd(nome, txt_track):
	arquivo = open(history, "a")
	arquivo.write(nome+"\n")
	arquivo.close()
	file_track = os.path.join(path, nome+".txt")
	arquivo = open(file_track, "w")
	arquivo.write(txt_track)
	arquivo.close()
	pass

def historyDel():
	arquivo = open(history, "r")
	temp = arquivo.readlines()
	arquivo.close()

	for t in temp:
		arquivo = os.path.join(path, t.replace("\n", "")+".txt")
		if os.path.exists(arquivo):
			os.remove(arquivo)

	arquivo = open(history, "w")
	arquivo.write("")
	arquivo.close()

	arquivo = open(temp_a, "w")
	arquivo.write("")
	arquivo.close()
	pass

def fix(arq_1, arq_2):
	ret_1 = arq_1
	ret_2 = arq_2
	arq_1_size = len(arq_1)
	arq_2_size = len(arq_2)
	size = abs(arq_1_size - arq_2_size)
	if arq_1_size < arq_2_size:
		for a in range(size):
			ret_1.append("")
	if arq_2_size < arq_1_size:
		for a in range(size):
			ret_2.append("")
	return ret_1, ret_2

def getIdx(arr):
	ret = 0
	if arr[0].find(",") > 0:
		ret = arr[0].split(",")[0]
	else:
		ret = arr[0]
	return int(ret)

def render_parse(self, tab, cmd):
	idx = 0
	cor = ""
	sinal = ""
	tipo = 0
	print(cmd)
	cmd_spt = cmd.split("\n")
	for l in cmd_spt:
		if l.startswith("<") or l.startswith(">") or l.startswith("-"):
			if tipo == 1 or tipo == 2:
				idx += 1
				tab.run_command("append",{"characters": l[2:]+"\n"})
				tab_line = tab.rowcol(tab.size())[0]
				phantoms.append( tab.add_phantom("diff", getReg(self, tab, tab_line), "<div style='padding: 5px; background-color: "+cor+";'>"+sinal+" </div>", sublime.LAYOUT_INLINE) )
			if tipo == 3:
				if l.startswith("<"):
					idx += 1
					tab.run_command("append",{"characters": l[2:]+"\n"})
					tab_line = tab.rowcol(tab.size())[0]
					phantoms.append( tab.add_phantom("diff", getReg(self, tab, tab_line), "<div style='padding: 5px; background-color: "+cor+";'>"+sinal+" </div>", sublime.LAYOUT_INLINE) )
			pass
		else:
			if l != "":
				a = l.split("a")
				d = l.split("d")
				c = l.split("c")
				if len(a) > 1:
					tipo = 1
					sinal = "-"
					cor = "#FFE6E6"
					idx = getIdx(a)
					tab.run_command("append",{"characters": "deleted...\n"})
				if len(d) > 1:
					tipo = 2
					sinal = "+"
					cor = "#EEFDEE"
					idx = getIdx(d)
					tab.run_command("append",{"characters": "added...\n"})
				if len(c) > 1:
					tipo = 3
					cor = "#E8FBFF"
					sinal = "?"
					idx = getIdx(c)
					tab.run_command("append",{"characters": "changed...\n"})
				tab_line = tab.rowcol(tab.size())[0]
				phantoms.append( tab.add_phantom("diff", getReg(self, tab, tab_line), "<div style='padding: 5px; background-color: "+cor+";'>"+str(idx)+sinal+" </div>", sublime.LAYOUT_INLINE) )
			pass
	return False
	pass

def render(self, diff, tab, tipo_flag, cor_final, sinal_final, delta):
	idx = 0
	cor = "#ffffff"
	tipo = 0
	for l in diff:
		idx += 1
		flag = False
		if l.startswith("- "):
			tipo = 1
			cor = "#FFE6E6"
			flag = True
		if l.startswith("+ "):
			tipo = 2
			cor = "#EEFDEE"
			flag = True
		if flag and tipo == tipo_flag and l != "- ":
			#print(l, idx)
			l_temp = ""+l[2:]
			tab.run_command("append",{"characters": l_temp+"\n"})
			tab_line = tab.rowcol(tab.size())[0]
			phantoms.append( tab.add_phantom("diff", getReg(self, tab, tab_line), "<div style='padding: 5px; background-color: "+cor_final+";'>"+str(idx)+sinal_final+"</div>", sublime.LAYOUT_INLINE) )
	pass

class TimeshifttrackCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global txt_track
		txt_track = self.view.substr(sublime.Region(0, self.view.size()))
		nome, ext = getFilename(self)
		if nome != "":
			historyAdd(nome, txt_track)
		pass

class TimeshiftdonttrackCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global phantoms
		global txt_track
		txt_track = ""
		self.view.erase_phantoms("diff")
		historyDel()
		pass

class TimeshiftcompareCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global txt_track
		#if txt_track == "":
			#return False

		nome, ext = getFilename(self)
		if nome == "":
			return False
			
		file_track = os.path.join(path, nome+".txt")
		arquivo = open(file_track, "r")
		txt_track = "".join(arquivo.readlines())
		arquivo.close()

		txt = self.view.substr(sublime.Region(0, self.view.size()))

		arquivo = open(temp_a, "w")
		arquivo.write(txt)
		arquivo.close()

		win = self.view.window()
		tab = win.new_file()

		arq_1 = txt_track.split("\n")
		arq_2 = txt.split("\n")
		#arq_1, arq_2 = fix(arq_1, arq_2)

		#cmd = os.popen("diff "+file_track+" "+temp_a).read()
		cmd = os.popen("diff "+temp_a+" "+file_track).read()
		render_parse(self, tab, cmd)

		#diff = difflib.HtmlDiff().make_file(arq_1, arq_2, "arq_1", "arq_2")
		#arquivo = open(os.path.join(path, "debug.html"), "w")
		#arquivo.write(diff)
		#arquivo.close()

		#delta = len(arq_1) - len(arq_2)
		#d = difflib.Differ()
		#diff = d.compare(arq_1, arq_2)
		#diff = difflib.ndiff(arq_1, arq_2)
		#render(self, diff, tab, 1, "#FFE6E6", "- ", delta)

		#delta = len(arq_2) - len(arq_1)
		#d = difflib.Differ()
		#diff = d.compare(arq_2, arq_1)
		#diff = difflib.ndiff(arq_2, arq_1)
		#render(self, diff, tab, 1, "#EEFDEE", "+ ", delta)

		#match = patience_diff(arq_1, arq_2)
		#print(match)
		pass

class TimeshiftrestoreCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global txt_track
		#txt_track = self.view.substr(sublime.Region(0, self.view.size()))
		nome, ext = getFilename(self)
		if nome != "":
			arquivo = open(os.path.join(path, nome+".txt"))
			txt_temp = arquivo.readlines()
			arquivo.close()
			self.view.replace(edit, sublime.Region(0, self.view.size()), "".join(txt_temp))
		pass