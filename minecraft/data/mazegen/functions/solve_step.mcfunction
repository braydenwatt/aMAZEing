summon minecraft:armor_stand ~ ~ ~ {Tags:['active_solve_marker'],CustomName:'{"text":"Active Solve Marker"}',CustomNameVisible:1b}

data modify entity @e[tag=active_solve_marker,limit=1] Pos set from storage maze solve_stack_pos[-1]
data modify storage maze maze_end_pos set from entity @e[tag=maze_end,limit=1] Pos
execute store result score SolveVars maze_end_x run data get storage minecraft:maze maze_end_pos[0]
execute store result score SolveVars maze_end_y run data get storage minecraft:maze maze_end_pos[2]

#execute as @e[tag=active_marker,limit=1] at @s run tp ~0.5 ~ ~0.5

# Check and summon armor stands with names
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~01 ~00 ~00 minecraft:white_concrete positioned ~02 ~00 ~00 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:1b,Invisible:0b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~-1 ~00 ~00 minecraft:white_concrete positioned ~-2 ~00 ~00 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:1b,Invisible:0b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~00 ~00 ~01 minecraft:white_concrete positioned ~00 ~00 ~02 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:1b,Invisible:0b,NoGravity:1b}
execute as @e[tag=active_solve_marker,limit=1] at @s if block ~00 ~00 ~-1 minecraft:white_concrete positioned ~00 ~00 ~-2 run summon minecraft:armor_stand ~0 ~ ~0 {Tags:['valid_next'],CustomName:'{"text":"Valid Next"}',CustomNameVisible:1b,Invisible:0b,NoGravity:1b}

# Randomly add maze_solve_next tag
tag @e[tag=valid_next,sort=random,limit=1] add maze_solve_next

# If there's a valid next marker, add it to the stack and go to it
execute if entity @e[tag=maze_solve_next] as @e[tag=active_solve_marker] at @s run setblock ~ ~ ~ blue_concrete
execute if entity @e[tag=maze_solve_next] as @e[tag=active_solve_marker] at @s anchored feet facing entity @e[tag=maze_solve_next,limit=1] feet run setblock ^ ^ ^1 blue_concrete
execute as @e[tag=maze_solve_next] at @s run setblock ~ ~ ~ minecraft:blue_concrete

execute if entity @e[tag=maze_solve_next] run data modify storage maze solve_stack_next_pos set from entity @e[tag=maze_solve_next,limit=1] Pos
execute if entity @e[tag=maze_solve_next] run data modify storage maze solve_stack_pos append from storage maze solve_stack_next_pos

# If not, mark this tile as done and remove it from the stack
execute unless entity @e[tag=maze_solve_next] as @e[tag=active_solve_marker] at @s run setblock ~ ~ ~ light_blue_concrete
execute unless entity @e[tag=maze_solve_next] run data remove storage maze solve_stack_pos[-1]

# Backtrack to the previous item on the stack
execute unless entity @e[tag=maze_solve_next] if data storage maze solve_stack_pos[0] run summon minecraft:marker ~ ~ ~ {Tags:['last_marker']}
execute unless entity @e[tag=maze_solve_next] if data storage maze solve_stack_pos[0] run data modify entity @e[tag=last_marker,limit=1] Pos set from storage maze solve_stack_pos[-1]
execute unless entity @e[tag=maze_solve_next] if entity @e[tag=last_marker] as @e[tag=active_solve_marker] at @s anchored feet facing entity @e[tag=last_marker,limit=1] feet run setblock ^ ^ ^1 light_blue_concrete

data modify storage maze curr_solve_pos set from entity @e[tag=maze_solve_next,limit=1] Pos
execute store result score SolveVars maze_curr_x run data get storage minecraft:maze curr_solve_pos[0]
execute store result score SolveVars maze_curr_y run data get storage minecraft:maze curr_solve_pos[2]

kill @e[tag=active_solve_marker]
kill @e[tag=valid_next]
kill @e[tag=last_marker]

execute unless score SolveVars maze_curr_x = SolveVars maze_end_x run schedule function mazegen:solve_step 1t
execute unless score SolveVars maze_curr_y = SolveVars maze_end_y run schedule function mazegen:solve_step 1t

execute if score SolveVars maze_curr_x = SolveVars maze_end_x if score SolveVars maze_curr_y = SolveVars maze_end_y run function mazegen:solve_complete