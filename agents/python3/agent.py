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
available_targets = ["c","d","e","f","g","h"]
tick=0

class Move_coor:
    def __init__(self):
        self.target=""
        self.actions_taken =[]
        self.x=0
        self.y=0
        self.move_away = 0
        self.is_dead=False
        self.id=''
        self.invulnerable=False
        #self.is_bombing = False
        self.bombing_sequence = 0
        self.near_bomb=False
    def set_target(self,game_state,available_targets):
        _,self.target = self.find_nearest_enemy(game_state,available_targets)

        return self.target
    def set_id(self,id):
        self.id=id
    def set_coor(self,coor):
        self.x=coor[0]
        self.y=coor[1]

    def check_pos_bomb(self,game_state):
        bomb_coors=[]
        bomb_dias=[]
        entities=game_state.get("entities")
        for entity in entities:
            a=entity.get("type")
            if a=='b':
                x=entity.get("x")
                y=entity.get("y")
                bomb_coor=[x,y]
                bomb_coors.append(bomb_coor)
                bomb_dias.append(entity.get("blast_diameter"))
        for i,b_coor in enumerate(bomb_coors):
            d=self.find_distance(b_coor)
            if (d<=3 and bomb_dias[i]>3) or d<=2:
                self.near_bomb=True
                return b_coor
        return []

    def move(self,action,game_state,l_actions):
        l_actions.remove(action)
        obs_coors=[]
        entities=game_state.get("entities")
        for entity in entities:
            if self.invulnerable:
                if entity.get("type") not in ['a',"bp",'fp','b','x']:
                    x=entity.get("x")
                    y=entity.get("y")
                    obs_coor=[x,y]
                    obs_coors.append(obs_coor)
            else:
                if entity.get("type") not in ['a',"bp",'fp','b']:
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
                action = "bomb"
                #self.is_bombing=True
                return action
            action=random.choice(l_actions)
            if  len(self.actions_taken)>0:
                if self.enc(action)== -self.enc(self.actions_taken[-1]):
                    # print(self.actions_taken[-1],action)
                    l_actions.remove(action)
                    if len(l_actions)==0:
                        #self.is_bombing=True
                        action = "bomb"
                        return action
                    action=random.choice(l_actions)
            return self.move(action,game_state,l_actions) 
    def move_diag(self,game_state,b_coor):
        [x,y,dia]=b_coor
        obs_coors=[]
        entities=game_state.get("entities")
        for entity in entities:
            pass
            

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

    def place_bomb(self):
        if(self.bombing_sequence==0):
            action = self.prev_action(1)
            if action == " " or action == "low":
                action = next(self.move_away_from_blast())
            print(self.id,action)
            self.bombing_sequence+=1
            return action
        if(self.bombing_sequence==1):
            action = self.prev_action(2)
            if action == " " or action == "low":
                action = next(self.move_away_from_blast())
            self.bombing_sequence+=1
            return action
        if self.bombing_sequence in [2,3,4]:
            self.bombing_sequence+=1
            return " "
        if self.bombing_sequence==5:
            self.bombing_sequence+=1
            return "detonate"
        if self.bombing_sequence in [6,7,8,9]:
            self.bombing_sequence+=1
            return " "
        if self.bombing_sequence==10:
            self.bombing_sequence=0
            return "done"
        
    def move_away_from_blast(self):
        # spots = self.diagonal_positions([self.x,self.y])
        # available_spot = self.nearest_avaialable_spot(spots)
        # self.go_to(available_spot)
        while True:
            yield " "
    def diagonal_positions(self,pos):
        x,y = pos
        positions = []
        positions.append([x+1,y+1])
        positions.append([x-1,y+1])
        positions.append([x+1,y-1])
        positions.append([x-1,y-1])
        return positions
    def prev_action(self,n):
        if len(self.actions_taken)>2*n-1:
            action = self.dec(-int(self.enc(self.actions_taken[-2*n])))
            return action
        else:
            return "low"
      
        

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
                return " "
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
                return " "
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
    def collect_pwp(self,game_state,action):
        min_d=100
        entities_lst=game_state.get("entities")
        pos_crate=[]
        coor_w=[]
        for en in entities_lst:
            a=en.get("type")
            if a=='bp' or a=='fp':
                x=en.get("x")
                y=en.get("y")
                pos_crate.append([x,y])
        if len(pos_crate)>0:
            for l in pos_crate:
                d=abs(l[0]-self.x)
                d += abs(l[1]-self.y)
                if d<min_d:
                    min_d=d
                    coor_w=l
            action=self.move_to_pos(coor_w,game_state)
        return action
    def is_target_stunned(self,opp_state):
        if tick<opp_state:
            return True
        return False

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
        stun=False
        for opp_unit_id in opp_unit_ids:
            if(opp_unit_id in available_targets):
                opp_coor=game_state.get("unit_state").get(opp_unit_id).get("coordinates")
                opp_state=game_state.get("unit_state").get(opp_unit_id).get("stunned")
                stun=self.is_target_stunned(opp_state)
                hp=game_state.get("unit_state").get(opp_unit_id).get("hp")
                if hp<=0:
                    available_targets.remove(opp_unit_id)
                else:
                    if stun:
                        coor_w=opp_coor
                        nearest_enemy=opp_unit_id
                    opp_coors.append(opp_coor)
                    enemy.append(opp_unit_id)
        # print(len(opp_coors))
        if not stun:
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
            self.is_bombing=True
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
        return nearest_pos

    def escape_enemy_bomb(self,game_state):
        obs_coors=[]
        v=0
        diag=False
        min_d=100
        bomb_coors=[]
        bomb_dias=[]
        entities=game_state.get("entities")
        for entity in entities:
            a=entity.get("type")
            if a=='b':
                x=entity.get("x")
                y=entity.get("y")
                dia=entity.get("blast_diameter")
                bomb_dias.append(dia)
                bomb_coor=[x,y]
                bomb_coors.append(bomb_coor)
        for i,b_coor in enumerate(bomb_coors):
            d=self.find_distance(b_coor)
            if (d<=3 and bomb_dias[i]>3) or (d<=2):
                if d<min_d:
                    min_d=d
                    [x,y]=b_coor 
                    if [self.x,self.y] in [[x+1,y+1],[x-1,y+1],[x-1,y-1],[x+1,y-1]]:
                        diag=True
                    dia=bomb_dias[i]
                v=1
        if v==0:
            return "done"
        if min_d==2 and dia==3:
            return ""
        elif min_d==3 or diag:
            return ""
        else:
            entities=game_state.get("entities")
            for entity in entities:
                if entity.get("type") not in ['a','fp']:
                    x=entity.get("x")
                    y=entity.get("y")
                    obs_coor=[x,y]
                    obs_coors.append(obs_coor)
            unit_ids=[]
            for unit_id in game_state.get("agents").get("a").get("unit_ids"):
                unit_ids.append(unit_id)
            for unit_id in game_state.get("agents").get("b").get("unit_ids"):
                unit_ids.append(unit_id)
            unit_ids.remove(self.id)
            for unit_id in unit_ids:
                coor=game_state.get("unit_state").get(unit_id).get("coordinates")
                obs_coors.append(coor)
            possible_coors=[]
            poss_coors=[]
            action="a"

            for i in range(-1,2):
                for j in range(-1,2):
                    n_coor=[x+i,y+j]
                    if not (n_coor[0]>=15 or n_coor[1]>=15):
                        if not (n_coor[0]<0 or n_coor[1]<0):
                            poss_coors.append(n_coor)
                    possible_coors.append(n_coor)

            if possible_coors[7] not in obs_coors and possible_coors[7] in poss_coors:
                if possible_coors[8] not in obs_coors and possible_coors[8] in poss_coors:
                    action=self.move_to_pos(possible_coors[8],game_state)
                elif possible_coors[6] not in obs_coors and possible_coors[6] in poss_coors:
                    action=self.move_to_pos(possible_coors[6],game_state)
            elif possible_coors[1] not in obs_coors and possible_coors[1] in poss_coors:
                if possible_coors[0] not in obs_coors and possible_coors[0] in poss_coors:
                    action=self.move_to_pos(possible_coors[0],game_state)
                elif possible_coors[2] not in obs_coors and possible_coors[2] in poss_coors:
                    action=self.move_to_pos(possible_coors[2],game_state)
            elif possible_coors[3] not in obs_coors and possible_coors[3] in poss_coors:
                if possible_coors[0] not in obs_coors and possible_coors[0] in poss_coors:
                    action=self.move_to_pos(possible_coors[0],game_state)
                elif possible_coors[6] not in obs_coors and possible_coors[6] in poss_coors:
                    action=self.move_to_pos(possible_coors[6],game_state)
            elif possible_coors[5] not in obs_coors and possible_coors[5] in poss_coors:
                if possible_coors[2] not in obs_coors and possible_coors[2] in poss_coors:
                    action=self.move_to_pos(possible_coors[2],game_state)
                elif possible_coors[8] not in obs_coors and possible_coors[8] in poss_coors:
                    action=self.move_to_pos(possible_coors[8],game_state)
            if action=="a":
                possible_coors.append([x+2,y])
                possible_coors.append([x-2,y])
                possible_coors.append([x,y+2])
                possible_coors.append([x,y-2])
                possible_coors.append([x+3,y])
                possible_coors.append([x-3,y])
                possible_coors.append([x,y+3])
                possible_coors.append([x,y-3])  
                for poss_coor in possible_coors:
                    if poss_coor[0]<15 and poss_coor[0]>=0 and poss_coor[1]<15 and poss_coor[1]>=0 and (poss_coor not in poss_coors):
                        poss_coors.append(poss_coor)
                if possible_coors[7] not in obs_coors and possible_coors[7] in poss_coors:
                    if possible_coors[9] not in obs_coors and possible_coors[9] in poss_coors:
                        if dia==3:
                            action=self.move_to_pos(possible_coors[9],game_state)
                        else:
                            if possible_coors[13] not in obs_coors and possible_coors[13] in poss_coors:
                                action=self.move_to_pos(possible_coors[13],game_state)
                elif possible_coors[1] not in obs_coors and possible_coors[1] in poss_coors:
                    if possible_coors[10] not in obs_coors and possible_coors[10] in poss_coors:
                        if dia==3:
                            action=self.move_to_pos(possible_coors[10],game_state)
                        else:
                            if possible_coors[14] not in obs_coors and possible_coors[14] in poss_coors:
                                action=self.move_to_pos(possible_coors[14],game_state)
                elif possible_coors[3] not in obs_coors and possible_coors[3] in poss_coors:
                    if possible_coors[12] not in obs_coors and possible_coors[12] in poss_coors:
                        if dia==3:
                            action=self.move_to_pos(possible_coors[12],game_state)
                        else:
                            if possible_coors[16] not in obs_coors and possible_coors[16] in poss_coors:
                                action=self.move_to_pos(possible_coors[16],game_state)
                elif possible_coors[5] not in obs_coors and possible_coors[5] in poss_coors:
                    if possible_coors[11] not in obs_coors and possible_coors[11] in poss_coors:
                        if dia==3:
                            action=self.move_to_pos(possible_coors[11],game_state)
                        else:
                            if possible_coors[15] not in obs_coors and possible_coors[15] in poss_coors:
                                action=self.move_to_pos(possible_coors[15],game_state)
            if action==" ":
                action="detonate"
            return action
            
    def find_enemy_pos(self,game_state):
        agent_id=game_state.get("connection").get("agent_id")
        if agent_id=='a':
            opp_agent_id='b'
        else:
            opp_agent_id='a'
        opp_unit_ids=game_state.get("agents").get(opp_agent_id).get("unit_ids")
        # print(opp_unit_ids)
        opp_coors=[]
        enemy = []
        for opp_unit_id in opp_unit_ids:
            opp_coor=game_state.get("unit_state").get(opp_unit_id).get("coordinates")
            opp_coors.append(opp_coor)
            enemy.append(opp_unit_id)
        return opp_coors
        
    def make_ur_own_way(self,coor_w,game_state):
        actions1=["up","down","left","right"]
        action_list=[]
        if self.x<coor_w[0]:
            action_list.append("right")
        if self.x>coor_w[0]:
            action_list.append("left")
        if self.y<coor_w[1]:
            action_list.append("up")
        if self.y>coor_w[1]:
            action_list.append("down")
        if action_list==[]:
          return " "
        obs_coors=self.find_enemy_pos(game_state)
        # to_ignore=[]
        entities=game_state.get("entities")
        for entity in entities:
            if entity.get("type") not in ['a','fp','b','bp']:
            # if entity.get("type") not in ['a','fp','b','m']:
                x=entity.get("x")
                y=entity.get("y")
                obs_coor=[x,y]
                obs_coors.append(obs_coor)
            # elif entity.get("type")=='m':
            #     to_ignore.append([entity.get("x"),entity.get("y")])
        for action in action_list:
            new_coor=[0,0]
            if action=='left':
                new_coor=[self.x-1,self.y]
            elif action=='right':
                new_coor=[self.x+1,self.y]
            elif action=='up':
                new_coor=[self.x,self.y+1]
            elif action=='down':
                new_coor=[self.x,self.y-1]
            # if new_coor in to_ignore:
            #     return self.ignore(actions1,new_coor,game_state)
            if new_coor not in obs_coors:
                return action
        if random.random()<0.85:
            return self.move(action,game_state,actions1)
        action="bomb"
        #self.is_bombing=True
        return action


            
        

        

unit=[Move_coor(),Move_coor(),Move_coor()]


is_first = True
tick = 0
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
        global unit
        global tick
        i=0
        # get my units
        my_agent_id = game_state.get("connection").get("agent_id")
        my_units = game_state.get("agents").get(my_agent_id).get("unit_ids")
        tick+=1
        #game_tick=game_state.get("tick")
        # send each unit a random action
        for unit_id in my_units:
            unit[i].invulnerable=True if game_state.get("unit_state").get(unit_id).get("invulnerable")==1 else False
            coor=game_state.get("unit_state").get(unit_id).get("coordinates")
            unit[i].set_coor(coor)   
            if is_first:
                target = unit[i].set_target(game_state,available_targets)
                unit[i].set_id(unit_id)
            hp=game_state.get("unit_state").get(unit_id).get("hp")
            if hp==0:
                unit[i].is_dead=True
            # # print("Targets",len(available_targets))
            if not unit[i].is_dead:
                
                
                b_coor=unit[i].check_pos_bomb(game_state)
                # action=unit[i].my(game_state)
                # # action=unit[i].bomb_crate(game_state)
                # action=unit[i].move_away_from_bomb(game_state,action)
                # if unit[i].is_bombing:
                #     pass
                    # action = unit[i].place_bomb()
                    # if action == "done":
                    #     unit[i].is_bombing = False
                # else:-----------------------------------------------------------------------------------------------------------
                if(tick<150):
                    action= unit[i].move_to_pos([7,7],game_state)
                elif(tick<250):
                    # action=unit[i].bomb_enemy(game_state)
                    action=unit[i].bomb_crate(game_state)
                else:
                    action= unit[i].move_to_pos([7,7],game_state)
                # action=unit[i].bomb_enemy(game_state)
                # if tick<200:
                #     if len(unit[i].actions_taken)>=1:
                #         if "bomb" in unit[i].actions_taken:
                #                 action=unit[i].collect_pwp(game_state,action)
                if unit[i].near_bomb:
                    action=unit[i].escape_enemy_bomb(game_state)
                    if action== "done":
                        unit[i].near_bomb=False
                    
                    if(tick>200):
                        action= unit[i].move_to_pos([7,7],game_state)
                    else:
                        action=unit[i].bomb_enemy(game_state)
                    #action=unit[i].bomb_enemy(game_state)

                unit[i].actions_taken.append(action)
                
            else:
                action=""
            i+=1
            # action=unit[i].move_to_pos([7,7],game_state)
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
        tick+=1
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