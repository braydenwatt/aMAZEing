data modify storage maze solve_stack set value [1]
data modify storage maze solve_stack_pos set value []
scoreboard players operation MazeVars maze_speed = MazeConst maze_speed
data modify storage maze solving set value 1b

execute if data storage maze solving unless data storage maze solve_stack_pos[0] run data modify storage maze solve_stack_pos append from entity @e[tag=maze_seed,limit=1] Pos
execute as @e[tag=maze_seed] at @s run function mazegen:solve_step