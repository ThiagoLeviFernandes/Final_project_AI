"""
MazeStudio.py
Desc:

Maze Studio
With:
 - Maze Generator
 - Maze Editor
 - Maze Solver (BFS, DFS, A*)
 - CSV History Recorder
 - LIVE History Viewer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import csv
import heapq
from collections import deque
from PIL import Image, ImageDraw


# ============================================================
#  Utility
# ============================================================

def duplicate_maze(maze):
    return [list(row) for row in maze]

def read_maze_from_file(filename):
    with open(filename) as f:
        return [list(line.rstrip("\n")) for line in f]

def write_maze_to_file(filename, maze):
    with open(filename, "w") as f:
        for row in maze:
            f.write("".join(row) + "\n")

def find_start_end(maze):
    start = end = None
    for r,row in enumerate(maze):
        for c,val in enumerate(row):
            if val == "A": start = (r,c)
            if val == "B": end = (r,c)
    return start, end

def reconstruct_path(parent, start, end):
    if end not in parent:
        return []
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


# ============================================================
#  Search Algorithms
# ============================================================

def bfs(maze, start, end):
    events = []
    parent = {start: None}
    q = deque([start])
    step = 0

    events.append(dict(step=step, event="DISCOVER", row=start[0], col=start[1]))
    step+=1

    while q:
        cur = q.popleft()
        events.append(dict(step=step, event="EXPAND", row=cur[0], col=cur[1]))
        step+=1
        if cur == end: break

        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr,nc = cur[0]+dr, cur[1]+dc
            if (0<=nr<len(maze) and 0<=nc<len(maze[0])
                and maze[nr][nc]!="X"
                and (nr,nc) not in parent):
                parent[(nr,nc)] = cur
                q.append((nr,nc))
                events.append(dict(step=step, event="DISCOVER",
                                   row=nr, col=nc))
                step+=1

    path = reconstruct_path(parent, start, end)
    return path, events


def dfs(maze, start, end):
    events = []
    parent = {start: None}
    stack = [start]
    step = 0

    events.append(dict(step=step, event="DISCOVER", row=start[0], col=start[1]))
    step+=1

    while stack:
        cur = stack.pop()
        events.append(dict(step=step, event="EXPAND", row=cur[0], col=cur[1]))
        step+=1
        if cur == end: break

        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr,nc = cur[0]+dr, cur[1]+dc
            if (0<=nr<len(maze) and 0<=nc<len(maze[0])
                and maze[nr][nc]!="X"
                and (nr,nc) not in parent):
                parent[(nr,nc)] = cur
                stack.append((nr,nc))
                events.append(dict(step=step, event="DISCOVER",
                                   row=nr, col=nc))
                step+=1

    path = reconstruct_path(parent, start, end)
    return path, events


def heuristic(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(maze, start, end):
    events = []
    parent = {start: None}
    g = {start:0}
    openh=[]
    heapq.heappush(openh,(heuristic(start,end),start))
    closed=set()
    step=0

    events.append(dict(step=step, event="DISCOVER", row=start[0], col=start[1]))
    step+=1

    while openh:
        f,cur = heapq.heappop(openh)
        if cur in closed: continue
        closed.add(cur)

        events.append(dict(step=step, event="EXPAND", row=cur[0], col=cur[1]))
        step+=1

        if cur==end: break

        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr,nc = cur[0]+dr, cur[1]+dc
            if not(0<=nr<len(maze) and 0<=nc<len(maze[0])): continue
            if maze[nr][nc]=="X": continue

            t_g = g[cur] + 1
            if (nr,nc) not in g or t_g < g[(nr,nc)]:
                g[(nr,nc)] = t_g
                parent[(nr,nc)] = cur
                nf = t_g + heuristic((nr,nc),end)
                heapq.heappush(openh,(nf,(nr,nc)))
                events.append(dict(step=step,
                                   event="DISCOVER",
                                   row=nr,col=nc))
                step+=1

    path = reconstruct_path(parent, start, end)
    return path, events


# ============================================================
#  CSV History Writer
# ============================================================

def write_history_csv(filename, maze, start, end, events, path, algorithm):
    with open(filename, "w", newline="") as f:
        fieldnames = ["record_type","algorithm","step","event","row","col",
                      "maze_rows","maze_cols","start_row","start_col",
                      "end_row","end_col","cell_value"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        rows = len(maze)
        cols = len(maze[0])

        # META
        w.writerow(dict(record_type="META",
                        algorithm=algorithm,
                        maze_rows=rows, maze_cols=cols,
                        start_row=start[0], start_col=start[1],
                        end_row=end[0], end_col=end[1]))

        # CELL
        for r in range(rows):
            for c in range(cols):
                w.writerow(dict(record_type="CELL",
                                algorithm=algorithm,
                                row=r,col=c,cell_value=maze[r][c]))

        # EVENTS
        for e in events:
            w.writerow(dict(record_type="EVENT",
                            algorithm=algorithm,
                            step=e["step"],
                            event=e["event"],
                            row=e["row"],
                            col=e["col"]))

        # PATH
        for i,(r,c) in enumerate(path):
            w.writerow(dict(record_type="PATH",
                            algorithm=algorithm,
                            step=i,
                            row=r,col=c))



# ============================================================
# Maze Generator
# ============================================================

class MazeGeneratorFrame(ttk.Frame):
    def __init__(self, parent, shared_maze):
        super().__init__(parent)
        self.shared_maze = shared_maze

        self.row_var = tk.IntVar(value=20)
        self.col_var = tk.IntVar(value=30)
        self.percent_var = tk.IntVar(value=30)

        frm = ttk.Frame(self)
        frm.pack(padx=10,pady=10)

        ttk.Label(frm,text="Rows:").grid(row=0,column=0,sticky="w")
        ttk.Entry(frm,textvariable=self.row_var,width=8).grid(row=0,column=1)

        ttk.Label(frm,text="Cols:").grid(row=1,column=0,sticky="w")
        ttk.Entry(frm,textvariable=self.col_var,width=8).grid(row=1,column=1)

        ttk.Label(frm,text="Percent X:").grid(row=2,column=0,sticky="w")
        ttk.Entry(frm,textvariable=self.percent_var,width=8).grid(row=2,column=1)

        ttk.Button(frm,text="Generate Maze", command=self.generate).grid(
            row=3,column=0,columnspan=2,pady=10
        )

    def generate(self):
        rows = self.row_var.get()
        cols = self.col_var.get()
        p = self.percent_var.get() / 100

        maze = []
        for _ in range(rows):
            row=[]
            for _ in range(cols):
                row.append("X" if random.random() < p else ".")
            maze.append(row)

        self.shared_maze.clear()
        self.shared_maze.extend(maze)

        # Auto-switch to Editor tab
        self.tabs.select(self.editor_index)



# ============================================================
# Maze Editor
# ============================================================

class MazeEditorFrame(ttk.Frame):
    CELL = 25

    def __init__(self, parent, shared_maze):
        super().__init__(parent)
        
        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)
        
        ttk.Button(top, text="Open Maze", command=self.open_maze).pack(side="left", padx=5)
        ttk.Button(top, text="Save Maze", command=self.save_maze).pack(side="left", padx=5)
        ttk.Button(top, text="Export PNG", command=self.export_png).pack(side="left", padx=5)
        ttk.Button(top, text="Zoom +", command=self.zoom_in).pack(side="left", padx=5)
        ttk.Button(top, text="Zoom -", command=self.zoom_out).pack(side="left", padx=5)
        
        self.shared_maze = shared_maze

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_click)

        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill="x")

        self.mode = tk.StringVar(value="wall")
        ttk.Radiobutton(self.toolbar, text="Draw Walls", variable=self.mode, value="wall").pack(side="left")
        ttk.Radiobutton(self.toolbar, text="Erase", variable=self.mode, value="erase").pack(side="left")
        ttk.Radiobutton(self.toolbar, text="Set A", variable=self.mode, value="A").pack(side="left")
        ttk.Radiobutton(self.toolbar, text="Set B", variable=self.mode, value="B").pack(side="left")

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        
    def open_maze(self):
        path = filedialog.askopenfilename(filetypes=[("Text Maze","*.txt")])
        if not path: return
        maze = read_maze_from_file(path)
        self.shared_maze.clear()
        self.shared_maze.extend(maze)
        self.redraw()

    def save_maze(self):
        if not self.shared_maze:
            messagebox.showerror("Error","Maze is empty.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Maze","*.txt")])
        if not path: return
        write_maze_to_file(path, self.shared_maze)
        messagebox.showinfo("Saved", f"Maze saved to {path}")
        
    def export_png(self):
        if not self.shared_maze:
            messagebox.showerror("Error","Maze is empty.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Image","*.png")])
        if not path: return

        rows = len(self.shared_maze)
        cols = len(self.shared_maze[0])
        cell_size = self.CELL

        img = Image.new("RGB", (cols*cell_size, rows*cell_size), "white")
        draw = ImageDraw.Draw(img)

        colors = {"X":"black", ".":"white", "A":"red", "B":"blue"}

        # Draw cells and gridlines
        for r in range(rows):
            for c in range(cols):
                x1 = c*cell_size
                y1 = r*cell_size
                x2 = x1+cell_size
                y2 = y1+cell_size

                # Fill cell
                draw.rectangle([x1,y1,x2,y2], fill=colors.get(self.shared_maze[r][c],"white"))

                # Draw gridlines
                draw.rectangle([x1,y1,x2,y2], outline="gray")

                # Draw labels for A and B
                val = self.shared_maze[r][c]
                if val in ("A","B"):
                    text_x = x1 + cell_size//2
                    text_y = y1 + cell_size//2
                    draw.text((text_x, text_y), val, fill="white", anchor="mm")

        img.save(path)
        messagebox.showinfo("Exported", f"Maze exported as PNG to {path}")
        
    def zoom_in(self):
        self.CELL = min(self.CELL + 2, 80)
        self.redraw()

    def zoom_out(self):
        self.CELL = max(self.CELL - 2, 4)
        self.redraw()

    def on_click(self, event):
        if not self.shared_maze: return
        r = int(event.y // self.CELL)
        c = int(event.x // self.CELL)
        rows=len(self.shared_maze)
        cols=len(self.shared_maze[0])
        if not(0<=r<rows and 0<=c<cols): return

        mode=self.mode.get()

        if mode=="wall":          self.shared_maze[r][c]="X"
        elif mode=="erase":       self.shared_maze[r][c]="."
        elif mode=="A":
            for i in range(rows):
                for j in range(cols):
                    if self.shared_maze[i][j]=="A":
                        self.shared_maze[i][j]="."
            self.shared_maze[r][c]="A"
        elif mode=="B":
            for i in range(rows):
                for j in range(cols):
                    if self.shared_maze[i][j]=="B":
                        self.shared_maze[i][j]="."
            self.shared_maze[r][c]="B"

        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        if not self.shared_maze:
            return

        rows=len(self.shared_maze)
        cols=len(self.shared_maze[0])

        self.canvas.config(scrollregion=(0,0,cols*self.CELL, rows*self.CELL))

        for r in range(rows):
            for c in range(cols):
                x1,y1 = c*self.CELL, r*self.CELL
                x2,y2 = x1+self.CELL, y1+self.CELL

                val=self.shared_maze[r][c]
                color = {
                    "X":"black",
                    "A":"red",
                    "B":"blue"
                }.get(val,"white")

                self.canvas.create_rectangle(x1,y1,x2,y2, fill=color, outline="gray")
                if val in ("A","B"):
                    self.canvas.create_text((x1+x2)//2,(y1+y2)//2,
                                            text=val,font=("Arial",14,"bold"))



# ============================================================
# Maze Solver
# ============================================================

class MazeSolverFrame(ttk.Frame):
    def __init__(self, parent, shared_maze):
        super().__init__(parent)
        self.shared_maze = shared_maze

        frm = ttk.Frame(self)
        frm.pack(pady=15)

        ttk.Label(frm, text="Algorithm:").grid(row=0,column=0,padx=5)
        self.algo = tk.StringVar(value="BFS")
        ttk.Combobox(frm, textvariable=self.algo,
                     values=["BFS","DFS","A*"], width=5).grid(row=0,column=1,padx=5)

        ttk.Button(frm,text="Run Solver", command=self.run_solver).grid(
            row=1,column=0,columnspan=2,pady=12
        )

        self.output = tk.Text(self, height=10)
        self.output.pack(fill="both", expand=True)

    def run_solver(self):
        if not self.shared_maze:
            messagebox.showerror("Error","Maze is empty.")
            return

        start,end = find_start_end(self.shared_maze)
        if not start or not end:
            messagebox.showerror("Error", "Maze must contain A and B")
            return

        maze = duplicate_maze(self.shared_maze)

        algo = self.algo.get()
        if algo=="BFS": path,events = bfs(maze,start,end)
        elif algo=="DFS": path,events = dfs(maze,start,end)
        else: path,events = a_star(maze,start,end)

        self.output.delete("1.0", "end")
        if path:
            self.output.insert("end", f"Path length: {len(path)-1}\n")
        else:
            self.output.insert("end", "No path found.\n")

        if messagebox.askyesno("Write History?","Save history CSV for viewer?"):
            fname = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV","*.csv")])
            if fname:
                write_history_csv(fname, maze, start, end, events, path, algo)
                self.output.insert("end", f"History saved to {fname}\n")



# ============================================================
#  History Viewer
# ============================================================

class MazeHistoryViewerFrame(ttk.Frame):
    CELL = 20

    def __init__(self, parent):
        super().__init__(parent)
        self.events=[]
        self.path=[]
        self.grid=[]
        self.current=0
        self.running=False

        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)

        ttk.Button(top,text="Open CSV",command=self.open_csv).pack(side="left")
        ttk.Button(top,text="Step",command=self.step).pack(side="left")
        ttk.Button(top,text="Run",command=self.run).pack(side="left")
        ttk.Button(top,text="Pause",command=self.pause).pack(side="left")
        ttk.Button(top,text="Reset",command=self.reset).pack(side="left")
        ttk.Button(top, text="Zoom +", command=self.zoom_in).pack(side="left", padx=5)
        ttk.Button(top, text="Zoom -", command=self.zoom_out).pack(side="left", padx=5)

        ttk.Label(top,text="Speed:").pack(side="left", padx=5)
        self.speed = tk.DoubleVar(value=1.0)
        ttk.Scale(top, from_=0.25, to=200.0, variable=self.speed, orient="horizontal").pack(side="left")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        
        self.path_label = ttk.Label(self, text="Final Path Length: -")
        self.path_label.pack(pady=5)

    def open_csv(self):
        path=filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
        if not path: return
        self.load(path)
        self.redraw()

    def load(self,filename):
        self.events=[]
        self.path=[]
        self.grid=[]
        with open(filename) as f:
            r=csv.DictReader(f)
            cells=[]
            ev=[]
            pat=[]
            rows=cols=0
            for row in r:
                t=row["record_type"]
                if t=="META":
                    rows=int(row["maze_rows"])
                    cols=int(row["maze_cols"])
                elif t=="CELL":
                    cells.append(row)
                elif t=="EVENT":
                    ev.append(row)
                elif t=="PATH":
                    pat.append(row)

            self.grid=[["." for _ in range(cols)] for _ in range(rows)]
            for c in cells:
                rr=int(c["row"]); cc=int(c["col"])
                self.grid[rr][cc]=c["cell_value"]

            self.events=[(int(e["step"]), e["event"], int(e["row"]), int(e["col"])) for e in ev]
            self.events.sort()

            self.path=[(int(p["row"]),int(p["col"])) for p in sorted(pat,key=lambda x:int(x["step"]))]

            self.current=0

    def reset(self):
        self.current=0
        self.running=False
        self.redraw()

    def pause(self):
        self.running=False

    def run(self):
        if not self.events:
            return
        self.running=True
        self._run_loop()

    def _run_loop(self):
        if not self.running:
            return
        if self.current < len(self.events):
            self.current+=1
            self.redraw()
            delay = int(200 / self.speed.get())
            self.after(delay, self._run_loop)
        else:
            self.running=False

    def step(self):
        if self.current < len(self.events):
            self.current+=1
            self.redraw()
            
    def zoom_in(self):
        self.CELL = min(self.CELL + 2, 80)
        self.redraw()

    def zoom_out(self):
        self.CELL = max(self.CELL - 2, 4)
        self.redraw()

    def cell_color(self,r,c):
        base=self.grid[r][c]
        if base=="X": return "black"

        tried=set()
        frontier=set()

        for i in range(self.current):
            _,ev,rr,cc = self.events[i]
            if ev=="EXPAND": tried.add((rr,cc))
            if ev=="DISCOVER": frontier.add((rr,cc))

        if (r,c) in tried: return "lightgray"
        if (r,c) in frontier: return "khaki"

        return "white"

    def redraw(self):
        self.canvas.delete("all")
        if not self.grid:
            return

        rows=len(self.grid)
        cols=len(self.grid[0])

        # draw exploration
        for r in range(rows):
            for c in range(cols):
                x1,y1 = c*self.CELL, r*self.CELL
                x2,y2 = x1+self.CELL, y1+self.CELL
                color = self.cell_color(r,c)

                self.canvas.create_rectangle(x1,y1,x2,y2,
                                             fill=color,
                                             outline="gray")

                val=self.grid[r][c]
                if val in ("A","B"):
                    self.canvas.create_text((x1+x2)//2,(y1+y2)//2,
                                            text=val, font=("Arial",12,"bold"))

        # final path highlight (GREEN)
        if self.current >= len(self.events):
            for r,c in self.path:
                x1,y1 = c*self.CELL, r*self.CELL
                x2,y2 = x1+self.CELL, y1+self.CELL
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="lightgreen",
                    outline="green", width=2
                )

            self.path_label.config(text=f"Final Path Length: {len(self.path)-1}")
        else:
            self.path_label.config(text="Final Path Length: -")



# ============================================================
#  MAIN APPLICATION
# ============================================================

class MazeStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Studio")
        self.geometry("1100x750")

        self.shared_maze=[]

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)

        gen = MazeGeneratorFrame(tabs, self.shared_maze)
        edit = MazeEditorFrame(tabs, self.shared_maze)
        solve = MazeSolverFrame(tabs, self.shared_maze)
        view = MazeHistoryViewerFrame(tabs)

        tabs.add(gen, text="Generator")
        tabs.add(edit, text="Editor")
        tabs.add(solve, text="Solver")
        tabs.add(view, text="History Viewer")
        
        gen.tabs = tabs
        gen.editor_index = 1   # Editor tab index

        def on_tab_changed(event):
            tab = event.widget.tab(event.widget.select(), "text")
            if tab == "Editor":
                edit.redraw()

        tabs.bind("<<NotebookTabChanged>>", on_tab_changed)


if __name__ == "__main__":
    MazeStudioApp().mainloop()