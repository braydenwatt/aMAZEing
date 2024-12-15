# bfs_explore_next.mcfunction
# Take the first position from the explore queue
data modify storage maze curr_explore_pos set from storage maze explore_queue[0]

# Summon a new marker at the current position
summon minecraft:armor_stand ~ ~ ~ {Tags:['maze_solve_next'],CustomName:'{"text":"Next Position"}',CustomNameVisible:1b}
data modify entity @e[tag=maze_solve_next,limit=1] Pos set from storage maze curr_explore_pos

# Remove this position from the explore queue
data remove storage maze explore_queue[0]

# Mark this position
execute as @e[tag=maze_solve_next] at @s run setblock ~ ~ ~ minecraft:red_concrete

# Add to solve queue (queue, not stack like in DFS)
data modify storage maze solve_queue_pos append from storage maze curr_explore_pos

# Check if we've reached the end
execute store result score SolveVars maze_curr_x run data get storage minecraft:maze curr_explore_pos[0]
execute store result score SolveVars maze_curr_y run data get storage minecraft:maze curr_explore_pos[2]

execute if data storage maze explore_queue[0] run function mazegen:bfs_explore_next
#execute unless data storage maze explore_queue[0] run schedule function mazegen:bfs_solve_step 20t