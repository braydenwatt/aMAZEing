execute as @e[tag=backtrack] at @s run setblock ~ ~ ~ yellow_concrete
execute as @e[tag=backtrack] at @s anchored feet facing entity @e[tag=backtrack_2,limit=1] feet run setblock ^ ^ ^1 yellow_concrete
execute as @e[tag=backtrack_2] at @s run setblock ~ ~ ~ yellow_concrete

data modify storage maze curr_solve_pos set from entity @e[tag=backtrack,limit=1] Pos
execute store result score SolveVars maze_curr_x run data get storage minecraft:maze curr_solve_pos[0]
execute store result score SolveVars maze_curr_y run data get storage minecraft:maze curr_solve_pos[2]

data modify storage maze maze_end_pos set from entity @e[tag=maze_seed,limit=1] Pos
execute store result score SolveVars maze_end_x run data get storage minecraft:maze maze_end_pos[0]
execute store result score SolveVars maze_end_y run data get storage minecraft:maze maze_end_pos[2]

execute if score SolveVars maze_curr_x = SolveVars maze_end_x if score SolveVars maze_curr_y = SolveVars maze_end_y run function mazegen:bfs_end

execute as @e[tag=backtrack,limit=1] at @s run data modify entity @s Pos set from entity @e[tag=parent_tracker,limit=1,sort=nearest] data.target
execute as @e[tag=backtrack_2,limit=1] at @s run data modify entity @s Pos set from entity @e[tag=parent_tracker,limit=1,sort=nearest] data.target

schedule function mazegen:bfs_backtrack 1t