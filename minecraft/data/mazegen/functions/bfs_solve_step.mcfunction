# bfs_solve_step.mcfunction
summon minecraft:armor_stand ~ ~ ~ {Tags:['active_solve_marker'],CustomName:'{"text":"Active Solve Marker"}',CustomNameVisible:1b}

data modify storage maze maze_end_pos set from entity @e[tag=maze_end,limit=1] Pos
execute store result score SolveVars maze_end_x run data get storage minecraft:maze maze_end_pos[0]
execute store result score SolveVars maze_end_y run data get storage minecraft:maze maze_end_pos[2]

# Summon a new marker at the current position
data modify storage maze solve_queue_pos set from storage maze solve_queue[0]
data modify entity @e[tag=active_solve_marker,limit=1] Pos set from storage maze solve_queue_pos
data remove storage maze solve_queue[0]

# Mark current tile as visited

# Check and summon armor stands with names for valid next positions
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~01 ~00 ~00 minecraft:white_concrete unless block ~02 ~00 ~00 blue_concrete positioned ~02 ~00 ~00 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:0b,Invisible:1b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~-1 ~00 ~00 minecraft:white_concrete unless block ~-2 ~00 ~00 blue_concrete positioned ~-2 ~00 ~00 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:0b,Invisible:1b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~00 ~00 ~01 minecraft:white_concrete unless block ~00 ~00 ~02 blue_concrete positioned ~00 ~00 ~02 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:0b,Invisible:1b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~00 ~00 ~-1 minecraft:white_concrete unless block ~00 ~00 ~-2 blue_concrete positioned ~00 ~00 ~-2 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:0b,Invisible:1b,NoGravity:1b}

execute as @e[tag=valid_next] at @s if block ~ ~ ~ minecraft:blue_concrete run kill @s
execute as @e[tag=valid_next] run data modify storage maze solve_queue append from entity @s Pos

execute as @e[tag=valid_next] at @s run summon minecraft:marker ~ ~ ~ {Tags:["parent_tracker"]}

execute as @e[tag=valid_next] at @s run data modify entity @e[tag=parent_tracker,tag=!maze_tracked,sort=nearest,limit=1] data.target set from entity @e[tag=active_solve_marker,limit=1] Pos
tag @e[tag=parent_tracker] add maze_tracked

execute as @e[tag=valid_next] at @s run setblock ~ ~ ~ blue_concrete
execute as @e[tag=valid_next] at @s anchored feet facing entity @e[tag=active_solve_marker,limit=1] feet run setblock ^ ^ ^1 blue_concrete

kill @e[tag=active_solve_marker]

data modify storage maze curr_solve_pos set from entity @e[tag=valid_next,limit=1] Pos
execute store result score SolveVars maze_curr_x run data get storage minecraft:maze curr_solve_pos[0]
execute store result score SolveVars maze_curr_y run data get storage minecraft:maze curr_solve_pos[2]

# Process each neighbor
execute unless score SolveVars maze_curr_x = SolveVars maze_end_x run schedule function mazegen:bfs_solve_step 1t
execute unless score SolveVars maze_curr_y = SolveVars maze_end_y run schedule function mazegen:bfs_solve_step 1t

execute if score SolveVars maze_curr_x = SolveVars maze_end_x if score SolveVars maze_curr_y = SolveVars maze_end_y run function mazegen:bfs_complete