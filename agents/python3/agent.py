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

class Move_coor:
    def __init__(self):
        self.target=""
        self.actions_taken =[]
        self.x=0
        self.y=0
        self.move_away = 0
        self.is_dead=False
        self.id=''
    def set_target(self,game_state,available_targets):
        _,self.target = self.find_nearest_enemy(game_state,available_targets)
        return self.target
    def set_id(self,id):
        self.id=id
    def set_coor(self,coor):
        self.x=coor[0]
        self.y=coor[1]

    def move(self,action,game_state,l_actions):
        l_actions.remove(action)
        obs_coors=[]
        entities=game_state.get("entities")
        for entity in entities:
            if entity.get("type") not in ['a','bp','fp','b']:
                x=entity.get("x")
                y=entity.get("y")
                obs_coor=[x,y]
                obs_coors.append(obs_coor)
        new_coor=[0,0]
        if action=='left':
            new_coor=[self.x-1,self.y]
        elif action=='right':
            new_coor=[self.x+1,self.y]
        elif action=='up':
            new_coor=[self.x,self.y+1]
        elif action=='down':
            new_coor=[self.x,self.y-1]
        if new_coor not in obs_coors:
            return action
        else:
            if len(l_actions)==0:
                return "bomb"
            action=random.choice(l_actions)
            if  len(self.actions_taken)>0:
                if self.enc(action)== -self.enc(self.actions_taken[-1]):
                    # print(self.actions_taken[-1],action)
                    l_actions.remove(action)
                    if len(l_actions)==0:
                        return "bomb"
                    action=random.choice(l_actions)
            return self.move(action,game_state,l_actions) 
    def move_diag(self,game_state,b_coor):
        [x,y,dia]=b_coor
        obs_coors=[]
        entities=game_state.get("entities")
        for entity in entities:
            

    def move_away_from_pos(self,b_coor,game_state):
        self.move_diag(game_state,b_coor)
        if len(self.actions_taken)<4:
            [x,y,dia]=b_coor
            action=self.move_to_pos([x+1,y+1],game_state)
            print(action)
            return action ############in place of 1 there was dia
        else:
            [x,y,dia]=b_coor
            if(self.move_away==0):
                self.move_away+=1
                action=self.dec(-int(self.enc(self.actions_taken[-2])))
                if action==" ":
                    action=self.move_to_pos([x+1,y+1],game_state)
                print(self.id,action)
                return action
            elif(self.move_away==1):
                self.move_away+=1
                action=self.dec(-int(self.enc(self.actions_taken[-4])))
                if action==" ":
                    action=self.move_to_pos([x+1,y+1],game_state)
                print(self.id,action)
                return action
            elif(self.move_away<=4):
                self.move_away +=1                
                print(self.id,"stay")
                return ''
            elif(self.move_away==5):
                self.move_away+=1
                print(self.id,"detonate")
                return 'detonate'
            elif(self.move_away<=10):
                self.move_away +=1
                print(self.id,"stay")
                return " "
            else:
                self.move_away=0

                return ' '

            
    
    def enc(self,action):
        if action == 'right':
            return 1
        if action == 'left':
            return -1
        if action =='up':
            return 2
        if action =='down':
            return -2
        # if action =='bomb':
        #     return 3
        # if action =='detonate':
        #     return -3
        return 0
    def dec(self,enc):
        if enc==1:
            return 'right'
        if enc==-1:
            return 'left'
        if enc==2:
            return 'up'
        if enc==-2:
            return 'down'
        # if enc==3:
        #     return 'bomb'
        # if enc==-3:
        #     return 'detonate'
        return ' '
    def move_away_from_bomb(self,game_state,action):
        b_coors=[]
        entities=game_state.get("entities")
        for entity in entities:
            a=entity.get("type")
            if a=="b":
                x=entity.get("x")
                y=entity.get("y")
                dia=entity.get("blast_diameter")
                b_coor=[x,y,dia]
                b_coors.append(b_coor)
        for b_coor in b_coors:
            x_dist=abs(b_coor[0]-self.x)
            y_dist=abs(b_coor[1]-self.y)
            if ((x_dist==0 and y_dist==1) or (x_dist==0 and y_dist==0) or (x_dist==1 and y_dist==0)):
                action=self.move_away_from_pos(b_coor,game_state)
        return action
            

    def move_to_pos(self,coor_w,game_state):
        actions1=["up","down","left","right"]
        if(random.random()<0.5):
            if self.x<coor_w[0]:
                action="right"
            elif self.x>coor_w[0]:
                action="left"
            elif self.y<coor_w[1]:
                action="up"
            elif self.y>coor_w[1]:
                action="down"
            else:
                return "bomb"
        else:
            if self.y<coor_w[1]:
                action="up"
            elif self.y>coor_w[1]:
                action="down"
            elif self.x<coor_w[0]:
                action="right"
            elif self.x>coor_w[0]:
                action="left"
            else:
                return "bomb"
        action=self.move(action,game_state,actions1)
        return action

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
                coor_w=l
        action=self.move_to_pos(coor_w,game_state)
        if min_d==1:
            action="bomb"
        return action 

    def find_nearest_enemy(self,game_state,available_targets):
        min_d = 100
        agent_id=game_state.get("connection").get("agent_id")
        nearest_enemy= ''
        if agent_id=='a':
            opp_agent_id='b'
        else:
            opp_agent_id='a'
        opp_unit_ids=game_state.get("agents").get(opp_agent_id).get("unit_ids")
        # print(opp_unit_ids)
        opp_coors=[]
        enemy = []
        for opp_unit_id in opp_unit_ids:
            if(opp_unit_id in available_targets):
                opp_coor=game_state.get("unit_state").get(opp_unit_id).get("coordinates")
                opp_coors.append(opp_coor)
                enemy.append(opp_unit_id)
        # print(len(opp_coors))
        for i,l in enumerate(opp_coors):
            d= self.find_distance(l)
            if d<min_d:
                nearest_enemy = enemy[i]
                min_d=d
                coor_w=l 
        return coor_w,nearest_enemy
    def bomb_enemy(self,game_state):
        
        coor_w = game_state.get("unit_state").get(self.target).get("coordinates")
        
        action=self.move_to_pos(coor_w,game_state)
        d = self.find_distance(coor_w)
        if d==1:
            action="bomb"
        return action 
    def find_distance(self,pos):
        d=abs(pos[0]-self.x)
        d += abs(pos[1]-self.y)
        return d
    def find_uavail(self,unit_coor):
        nearest_pos = [] 
        x = unit_coor[0]
        y= unit_coor[1] 
        if(x==0 and y==0) :
            nearest_pos.append([x+1,y]) 
            nearest_pos.append([x,y+1])  
        elif(x==14 and y==14) : 
            nearest_pos.append([x,y-1]) 
            nearest_pos.append([x-1,y])  
        elif(x==0 and y==14) : 
            nearest_pos.append([x+1,y]) 
            nearest_pos.append([x,y-1])      
        elif(x==14 and y==0) : 
            nearest_pos.append([x-1,y]) 
            nearest_pos.append([x,y+1])  
        elif(x==0) : 
            nearest_pos.append([x+1,y]) 
            nearest_pos.append([x,y+1]) 
            nearest_pos.append([x,y-1])       
        elif(x==14) :
            nearest_pos.append([x-1,y]) 
            nearest_pos.append([x,y+1]) 
            nearest_pos.append([x,y-1])  
        elif(y==14) :
            nearest_pos.append([x,y-1]) 
            nearest_pos.append([x-1,y]) 
            nearest_pos.append([x+1,y])  
        elif(y==0) :
            nearest_pos.append([x,y+1]) 
            nearest_pos.append([x-1,y]) 
            nearest_pos.append([x+1,y])    
        else : 
            nearest_pos.append([x,y-1]) 
            nearest_pos.append([x-1,y]) 
            nearest_pos.append([x+1,y])  
            nearest_pos.append([x,y+1])
        
    
    

m=[Move_coor(),Move_coor(),Move_coor()]
available_targets = ["c","d","e","f","g","h"]
is_first = True
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
        bombs = list(filter(lambda entity: entity.get("unit_id") == unit and entity.get("type") == "b", entities))
        bomb = next(iter(bombs or []), None)
        if bomb != None:
            return [bomb.get("x"), bomb.get("y")]
        else:
            return None

    async def _on_game_tick(self, tick_number, game_state):

        global is_first
        global m
        i=1
        # get my units
        my_agent_id = game_state.get("connection").get("agent_id")
        my_units = game_state.get("agents").get(my_agent_id).get("unit_ids")
        # game_tick=game_state.get("tick")
        # send each unit a random action
        for unit_id in my_units:
            
            if is_first:
                target = m[i-1].set_target(game_state,available_targets)
                available_targets.remove(target)
                m[i-1].set_id(unit_id)
            hp=game_state.get("unit_state").get(unit_id).get("hp")
            if hp==0:
                m[i-1].is_dead=True
            # # print("Targets",len(available_targets))
            if not m[i-1].is_dead:
                coor=game_state.get("unit_state").get(unit_id).get("coordinates")
                m[i-1].set_coor(coor)
                action=m[i-1].bomb_enemy(game_state)
                # action=m[i-1].bomb_crate(game_state)
                action=m[i-1].move_away_from_bomb(game_state,action)

                m[i-1].actions_taken.append(action)
            else:
                action=""
            i+=1
            
            # action=m[i-1].move_to_pos([7,7],game_state)
            # i+=1
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
                pass
                #print(f"Unhandled action: {action} for unit {unit_id}")
        is_first=False


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