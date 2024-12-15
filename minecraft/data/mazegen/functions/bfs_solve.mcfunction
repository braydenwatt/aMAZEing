# bfs_solve.mcfunction - Initializes BFS maze solving
data modify storage maze solve_queue set value []
data modify storage maze solve_queue_pos set value []
data modify storage maze explore_queue set value []
scoreboard players operation MazeVars maze_speed = MazeConst maze_speed
scoreboard objectives add time_taken dummy

execute if data storage maze solving unless data storage maze solve_queue_pos[0] run data modify storage maze solve_queue append from entity @e[tag=maze_seed,limit=1] Pos
execute as @e[tag=maze_seed] at @s run function mazegen:bfs_solve_step
execute as @e[tag=maze_seed] at @s run setblock ~ ~ ~ blue_concrete