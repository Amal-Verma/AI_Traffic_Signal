class Manager:
  def __init__(self):
    self.counter = 0
    self.cycle_time = 20
    self.min_time = 5
    self.max_time = 30
    
  def call(self,cars):
    # cycle = [(True, False, False, False), (False, True, False, False), (False, False, True, False), (False, False, False, True)]

    cycle = [(True, False, False, False, False, False, False,False, False, False, False, False,),
             (False, True, False, False, False, False, False,False, False, False, False, False,),
             (False, False, True, False, False, False, False,False, False, False, False, False,),
             (False, False, False, True, False, False, False,False, False, False, False, False,),
             (False, False, False, False, True, False, False,False, False, False, False, False,),
             (False, False, False, False, False, True, False,False, False, False, False, False,),
             (False, False, False, False, False, False, True,False, False, False, False, False,),
             (False, False, False, False, False, False, False,True, False, False, False, False,),
             (False, False, False, False, False, False, False,False, True, False, False, False,),
             (False, False, False, False, False, False, False,False, False, True, False, False,),
             (False, False, False, False, False, False, False,False, False, False, True, False,),
             (False, False, False, False, False, False, False,False, False, False, False, True,)]
      

    # timer =  [(self.min_time + ((self.cycle_time - len(cars) * self.min_time) * car / (sum(cars) + 1))) for car in cars]
    timer = [self.cycle_time // 12] * 12 
    print(timer, cars)
    timer = self.prefix_sum(timer)  

    return cycle, timer

  
  def prefix_sum(self, arr):
    for i in range(1, len(arr)): arr[i] += arr[i-1]
    return arr