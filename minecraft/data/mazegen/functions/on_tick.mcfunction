# If new markers have been placed, kill the old ones
execute if entity @e[tag=maze_seed,tag=maze_tracked] if entity @e[tag=maze_seed,tag=!maze_tracked] run kill @e[tag=maze_seed,tag=maze_tracked]
execute if entity @e[tag=maze_end,tag=maze_tracked] if entity @e[tag=maze_end,tag=!maze_tracked] run kill @e[tag=maze_end,tag=maze_tracked]

# Check for Start/Reset potions
execute if entity @e[type=potion,nbt={Item:{tag:{MazeCreate:1b}}}] run function mazegen:start
execute if entity @e[type=potion,nbt={Item:{tag:{MazeBuild:1b}}}] run function mazegen:build
execute if entity @e[type=potion,nbt={Item:{tag:{MazeReset:1b}}}] run function mazegen:clear
execute if entity @e[type=potion,nbt={Item:{tag:{MazeSolve:1b}}}] run function mazegen:solve

kill @e[type=potion,nbt={Item:{tag:{MazeCreate:1b}}}]
kill @e[type=potion,nbt={Item:{tag:{MazeBuild:1b}}}]
kill @e[type=potion,nbt={Item:{tag:{MazeReset:1b}}}]
kill @e[type=potion,nbt={Item:{tag:{MazeSolve:1b}}}]

# Get the positions of relevant entities
tag @e[tag=maze_seed] add maze_tracked
tag @e[tag=maze_end] add maze_tracked

execute run function mazegen:pausable