import time
import picar_4wd as fc


# Motor contorl constants
DIRECITONS = ['W', 'N', 'E', 'S']
FORWARD_SPEED = 8
FORWARD_TIME = 0.4
TURN_SPEED = 30
TURN_TIME = 1


class Picar:
    def __init__(self):
        self.dist_trav = 0  # in cm
        self.direction = 'S'
        self.status = 'stop'
        self.move_start_time = None
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        fc.stop()
        pass
    
    def __del__(self):
        self.__exit__()
        
    def get_speed(self):
        return fc.speed_val()
        
    def get_pi_data(self):
        return fc.pi_read()
        
    def update_distance(self):
        if self.status in ['forward', 'backward']:
            self.dist_trav += round(10*(time.time() - self.move_start_time)/FORWARD_TIME, 2)
            self.move_start_time = time.time()
        return self.dist_trav

    def stop(self):
        fc.stop()
        self.update_distance()
        self.move_start_time = None
        self.status = 'stop'
        
    def forward(self):
        if self.status == 'stop':
            self.move_start_time = time.time()
        self.status = 'forward'
        fc.forward(FORWARD_SPEED)
        
    def backward(self):
        if self.status == 'stop':
            self.move_start_time = time.time()
        self.status = 'backward'
        fc.backward(FORWARD_SPEED)
        
    def turnright(self):
        self.stop()
        fc.turn_right(TURN_SPEED)
        self.status = 'turning'
        time.sleep(TURN_TIME)
        self.stop()
        cur_dir_idx = DIRECITONS.index(self.direction)
        self.direction = DIRECITONS[(cur_dir_idx+1)%4]
        
    def turnleft(self):
        self.stop()
        fc.turn_left(TURN_SPEED)
        self.status = 'turning'
        time.sleep(TURN_TIME)
        self.stop()
        cur_dir_idx = DIRECITONS.index(self.direction)
        self.direction = DIRECITONS[(cur_dir_idx-1)%4]
        
    def turnaround(self):
        self.stop()
        fc.turn_left(TURN_SPEED)
        self.status = 'turning'
        time.sleep(2*TURN_TIME)
        self.stop()
        cur_dir_idx = DIRECITONS.index(self.direction)
        self.direction = DIRECITONS[(cur_dir_idx+2)%4]
