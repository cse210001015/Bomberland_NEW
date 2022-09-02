from typing import Union
from game_state import GameState
import asyncio
import random
import os
import time

uri = os.environ.get(
    'GAME_CONNECTION_STRING') or "ws://127.0.0.1:3000/?role=agent&agentId=agentId&name=defaultName"

actions = ["up", "down", "left", "right", "bomb", "detonate"]
l_bombs = []

class Move_coor:
    def __init__(self,unit_id,current_pos):
        self.actions_taken =[]
        self.x= current_pos[0]
        self.y = current_pos[1]
        self.bomb_around = False 
        

    def set_coor(l,self):
        [x,y]=l
        self.pos=[x,y]
    def move(action,game_state):
        
    def move_to_pos(self,coor_w):
        actions1=["up","down","left","right"]
        if self.x<coor_w[0]:
            action="right"
        elif self.x>coor_w[0]:
            action="left"
        elif self.y<coor_w[1]:
            action="up"
        elif self.y>coor_w[1]:
            action="down"
        else:
            action="bomb"
            return action
        action=self.move(action,game_state)
    
    



        # for obs in obstacles :
            
        #     if( obs.get("type") in l_obs_id ):
        #         t_coord = [obs.get("x"), obs.get("y") ]

        #         if( obs.get("type") =='b' ): 
        #             l_bombs.append(t_coord)

        #         l_t_coord_obs.append(t_coord) 


    def move_away_from_bomb(bomb_radius ):


    def check_bomb_around ():                   #######
        
        transit = [ [0,0] [1,0], [-1,0] , [0,1] , [0,-1] ] 

        for i in range(0,5):
            check_pos = pos + transit[i] 
            if( check_pos in l_bombs ):
                move_away_from_bomb()

        
    def bomb_crate(self,game_state):
        min_d=100
        entities_lst=game_state.get("entities")
        pos_crate=[]
        coor_w=[]
        for en in entities_lst:
            a=en.get("type")
            if a=='w':
                x=en.get("x")
                y=en.get("y")
                pos_crate.append([x,y])
        for l in pos_crate:
            d=abs(l[0]-self.x)
            d += abs(l[1]-self.y)
            if d<min_d:
                min_d=d
                [x,y]=l
                coor_w=[x,y]
        action=self.move_to_pos(coor_w)
        if min_d==1:
            action="bomb"
        return action 

    
    

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