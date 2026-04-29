# Navigating AI Search Structures

## How To Use The Materials

- First download this file: [MazeStudio.py](../code/MazeStudio.py)
- Next, open the file in the IDE of your choice, or download Thonny if you do not already have an IDE.
- Finally run the program.

- In the activity, your job is to solve the maze as efficently as possible in 40 seconds. You can then compare your result (and time, but AI takes fractions of a second to solve) to AI using whatever algorithm you chose to solve it in the viewer.
- For further learning this can be used to reinforce search algorithm learning by giving the student a algorithm to try to solve the maze in, then comparing their result with a live demo in the viewer. This does not necessarily need to be timed.

---

## Navigate The Program
Once Running there are tabs along the top for navigation. The tabs are:
- Generator
  - Here you can change the size of the maze or the amount of obstacles. You can also generate that maze.
- Editor
  - In the editor you can draw your own obstacles, remove them, and set the start and stop points for the maze to solve.
  - Also in this tab you can save or open existing mazes. You can also export PNGs for printing for class assignments.
- Solver
  - Here you select the algorithm you want and run the solver.
- History Viewer
  - In the viewer you open the solved csv, and can start, stop, or pause the visual. You can change the speed or zoom in and out.

---

## Supporting Document for AI Search Based Reasoning

The topic Thiago and I will be covering is search-based reasoning in AI. Search-based reasoning in AI is becoming increasingly prevalent. It's used in many systems to solve complex problems and provide useful solutions. In this topic, we cover the two main types of search-based reasoning in AI and how they function. We demonstrate both and tie them to a real-world example: a service called Timefold that uses search-based reasoning to reach the optimal conclusion. We also provide a Python and tkinter search graph program that allows you to visualize different search algorithms in real time.

Let's first look at search-based reasoning as a whole. In AI, search-based reasoning is the process of exploring many possible states or solutions in order to solve a problem. Search-based reasoning is valuable because “AI enables faster, more accurate predictions and reliable, data-driven decisions” (Stryker & Kavlakoglu, 2024). Many AI problems are search problems. Problems like GPS routing, shift management, or schedule generation can all use search-based reasoning to solve for their optimal solutions. Throughout search-based reasoning, AI explores several possible solutions. In this process, it evaluates each option, prunes bad ones, and optimizes by selecting the best move or solution. The goal is to ultimately find the optimal solution for the given problem.

The two main types of search-based reasoning are graph searches and solution-space searches. In graph searches, you can think of the problem like a maze. Each move in the maze is a node, and the AI has to visit nodes while exploring possible paths until it finally finds the solution. These nodes are connected like branches in a tree or roads on a map. Graph search techniques are widely used to solve navigation and pathfinding problems by exploring connected states until a solution is reached (Russel & Norvig, 2021). For example, a GPS system searches roads and intersections to find the fastest route to a destination.

In contrast, solution-space searches can be visualized as a landscape of solutions. As AI goes up the hill, the solution is worse; as it goes down into the valley, the solution improves. The lower you go, the better the score (less penalties); the higher you go, the higher the penalties of the solution. This method is used in several solving services that involve many combinations to compare. Examples include staff scheduling, classroom assignment, planning delivery routes, and balancing workloads among workers.

One of these services is a tool called Timefold. Timefold uses solution space to help solve problems efficiently. As discussed, the solution space contains complete solutions rather then pieces of a solution. To solve, it iterates through these solutions to find the best one. How it determines the best solution is with a score. “The score is an objective way to compare two solutions. The solution with the higher score is better. The solver aims to find the solution with the highest score of all possible solutions. The best solution is the solution with the highest score that the solver has encountered during solving, which might be the optimal solution” (Timefold). Each solution is assigned a score based on the problem's constraints. A problem can have hard constraints, meaning that if broken, the solution is not viable, or soft constraints, meaning that if ignored, the solution is less optimal. Breaking a soft constraint is a penalty aka -1 to the score; the higher the score, the more effective the solution. Timefold also has settings to increase the efficiency or the accuracy of the results. By limiting the time Timefold has to solve, you can increase the efficiency, but also give it less time to find the optimal solution, meaning you may end up with a subpar result if the complexity of the problem is too much for the time constraint. Increasing the time may mean it takes longer to find a final solution, but the output may be the best possible outcome.

One of the tools we recommend for learning search graph concepts is the Python program attached to this submission. The Python program allows you to visualize different algorithms and how AI goes through solving them. Included is a feature to export a picture of a maze that can be printed. This can be passed out to students, with their job being to solve it with the algorithm they are trying to learn, to help reinforce their knowledge. The Algorithms available are BFS, DFS, and A*. You can also modify mazes to test how different algorithms will react to each obstacle.

To sum up the differences between the two forms of search-based reasoning in AI, let's look at some terms. A node in graph searches would be just a single puzzle piece, whereas in the solution space, it would be the complete puzzle. A step in graph searches would be moving to the next node, whereas in solution space, it would be a puzzle piece swap to the final solution. In graph searching, the end goal is to reach the target. In the solution space, the goal is to improve the quality of the target.

In conclusion, both forms of search-based reasoning are viable, and they are both commonly used in a number of services. The main difference is how they search and the structures that they use. In the end, they are both trying to achieve the same goal, and they both can be highly effective solutions.
