from typing import Union
from game_state import GameState
import asyncio
import random
import os
import time
import copy

uri = os.environ.get(
    'GAME_CONNECTION_STRING') or "ws://127.0.0.1:3000/?role=agent&agentId=agentId&name=defaultName"


actions = ["up", "down", "left", "right", "bomb", "detonate"]
l_bombs = []


class Move_coor( ):
    def __init__(self,unit_id,current_pos):
        self.action="ac1"
        self.x= current_pos[0]
        self.y = current_pos[1]
        self.bomb_around = False 
        

    def set_coor(l,self):
        [x,y]=l
        self.pos=[x,y]
    def move_to_pos(coor_w):
        actions1=["up","down","left","right"]

        
    def move_away_from_bomb(bomb_radius ):


        def check_bomb_around ():                   #######
            
            transit = [ [0,0] [1,0], [-1,0] , [0,1] , [0,-1] ] 

            for i in range(0,5):
                check_pos = pos + transit[i] 
                if( check_pos in l_bombs ):
                    move_away_from_bomb()


    def move(action,coor,obs,l_actions):
        l_actions.remove(action)
        [x, y] = coor
        new_coor = [0,0]
        if action == "up":
            new_coor =  [x, y+1]
        elif action == "down":
            new_coor = [x, y-1]
        elif action == "right":
            new_coor = [x+1, y]
        elif action == "left":
            new_coor = [x-1, y]
        
        if new_coor not in obs:
            return action
        else:
            if len(l_actions)==0:
                return "bomb"
            action=random.choice(l_actions)
            return move(action,coor,obs,l_actions)
        

            
    def move_to_pos(pos,coor,obs):
        actions1=["up","down","left","right"]
        if coor[0]<pos[0]:
            action="right"
        elif coor[0]>pos[0]:
            action="left"
        elif coor[1]<pos[1]:
            action="up"
        elif coor[1]>pos[1]:
            action="down"
        else:
            pass
            

        #action=random.choice(actions1)
        action = "bomb"
        return action
        action=move(action,coor,obs,actions1)
        return action

    def move_to_pos(unit_coor,pow_coor,l_obs_coor):
        if pow_coor==[]:
            return move_to_pos([7,7],unit_coor,l_obs_coor)
        else:
            coor=copy.deepcopy(pow_coor[0][0])
            for pow in pow_coor:
                if ((abs(pow[0][0]-unit_coor[0])+abs(pow[0][1]-unit_coor[1]))<(abs(coor[0]-unit_coor[0])+abs(coor[1]-unit_coor[1])) and (abs(pow[0][0]-unit_coor[0])+abs(pow[0][1]-unit_coor[1]))<=pow[1]):
                    coor=copy.deepcopy(pow[0])
            return move_to_pos(coor,unit_coor,l_obs_coor)

m=[Move_coor(),Move_coor(),Move_coor()]


class Agent():
    def __init__(self):
        self._client = GameState(uri)

        # any initialization code can go here
        self._client.set_game_tick_callback(self._on_game_tick)

        loop = asyncio.get_event_loop()
        connection = loop.run_until_complete(self._client.connect())
        tasks = [
            asyncio.ensure_future(self._client._handle_messages(connection)),
        ]
        loop.run_until_complete(asyncio.wait(tasks))

    # returns coordinates of the first bomb placed by a unit
    def _get_bomb_to_detonate(self, unit) -> Union[int, int] or None:
        entities = self._client._state.get("entities")
        bombs = list(filter(lambda entity: entity.get(
            "unit_id") == unit and entity.get("type") == "b", entities))
        bomb = next(iter(bombs or []), None)
        if bomb != None:
            return [bomb.get("x"), bomb.get("y")]
        else:
            return None

    async def _on_game_tick(self, tick_number, game_state):
        
        global m
        i=1
        # get my units
        my_agent_id = game_state.get("connection").get("agent_id")
        my_units = game_state.get("agents").get(my_agent_id).get("unit_ids")

        # send each unit a random action
        for unit_id in my_units:

            coor=game_state.get("unit_state").get(unit_id).get("coordinates")
            m[i-1].set_coor(coor)
            action=m[i-1].bomb_crate(game_state)
            action=m[i-1].get_away_from_bomb(game_state,action)
            i+=1
            if action in ["up", "left", "right", "down"]:
                await self._client.send_move(action, unit_id)
            elif action == "bomb":
                await self._client.send_bomb(unit_id)
            elif action == "detonate":
                bomb_coordinates = self._get_bomb_to_detonate(unit_id)
                if bomb_coordinates != None:
                    x, y = bomb_coordinates
                    await self._client.send_detonate(x, y, unit_id)
            else:
                print(f"Unhandled action: {action} for unit {unit_id}")


def main():
    for i in range(0,10):
        while True:
            try:
                Agent()
            except:
                time.sleep(5)
                continue
            break


if __name__ == "__main__":
    main()