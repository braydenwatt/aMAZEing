tellraw @a ["",{"text":"BFS Solve Complete! ","color":"green","bold":true},{"text":"Backtracking!","color":"gold"}]
execute as Arco23 at @s run playsound minecraft:entity.player.levelup master Arco23 ~ ~ ~ 1

execute as @e[tag=maze_end] at @s run summon minecraft:armor_stand ~ ~-1 ~ {Tags:['backtrack'],CustomName:'{"text":"Backtrack Marker"}',CustomNameVisible:0b,Invisible:1b}
execute as @e[tag=maze_end] at @s run summon minecraft:armor_stand ~ ~-1 ~ {Tags:['backtrack_2'],CustomName:'{"text":"Backtrack Marker 2"}',CustomNameVisible:0b,Invisible:1b}
execute as @e[tag=backtrack,limit=1] at @s run data modify entity @s Pos set from entity @e[tag=parent_tracker,limit=1,sort=nearest] data.target

function mazegen:bfs_backtrack
